from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.ledger import MemberSchedule

# Approximate monthly premium per $100K coverage by age bracket (20-year term, healthy non-smoker)
# Based on 2026 market rates from multiple carriers
DEFAULT_PREMIUM_TABLE: dict[tuple[int, int], float] = {
    (18, 29): 8.0,
    (30, 34): 10.0,
    (35, 39): 13.0,
    (40, 44): 17.0,
    (45, 49): 25.0,
    (50, 54): 38.0,
    (55, 59): 55.0,
    (60, 64): 85.0,
}


def premium_for_age(age: int, coverage: float, table: dict[tuple[int, int], float] | None = None) -> float:
    """Monthly premium for a given age and coverage amount."""
    if table is None:
        table = DEFAULT_PREMIUM_TABLE
    for (lo, hi), rate_per_100k in table.items():
        if lo <= age <= hi:
            return rate_per_100k * (coverage / 100_000)
    # Default fallback for ages outside table
    return 20.0 * (coverage / 100_000)


class TermLifePool(Instrument):
    """Term life insurance + collective investment fund.

    Cheap premiums go to term life policies (pure death benefit).
    Remaining contributions go into a shared pool (savings account).

    Key insight: bundled death benefits make the group creditworthy.
    The pool itself earns modest savings-account returns. The real
    borrowing power comes from the death benefit collateral.

    Group discount: group term life premiums are ~30% cheaper than individual.
    Discount scales with member count (no discount under 10 members).
    """

    name = "Term Life Pool"

    def __init__(
        self,
        coverage_per_member: float = 100_000.0,
        avg_member_age: int = 35,
        savings_rate: float = 0.04,
        group_discount: float = 0.30,
        pool_leverage: float = 0.8,
        death_benefit_leverage: float = 0.5,
    ) -> None:
        super().__init__()
        self.coverage_per_member = coverage_per_member
        self.avg_member_age = avg_member_age
        self.savings_rate = savings_rate
        self.group_discount = group_discount
        self.pool_leverage = pool_leverage
        self.death_benefit_leverage = death_benefit_leverage

        self._monthly_return = (1 + savings_rate) ** (1 / 12) - 1
        self._pool: dict[int, float] = {}
        self._total_costs: dict[int, float] = {}
        self._member_count: dict[int, int] = {}
        individual_premium = premium_for_age(avg_member_age, coverage_per_member)
        self._individual_premium = individual_premium
        # Base group-rate premium (full discount) — used when member count >= 25
        self._premium_per_member = individual_premium * (1 - group_discount)

    def effective_group_discount(self, member_count: int) -> float:
        """Group discount scales with size. No discount under 10 members."""
        if member_count < 10:
            return 0.0  # individual rates
        elif member_count < 25:
            return self.group_discount * 0.5  # partial discount
        else:
            return self.group_discount  # full group rate

    def effective_premium(self, member_count: int) -> float:
        """Premium per member adjusted for group size."""
        discount = self.effective_group_discount(member_count)
        return self._individual_premium * (1 - discount)

    def step(self, month: int, members: list[MemberSchedule]) -> None:
        prev_pool = self._pool.get(month - 1, 0.0)
        prev_costs = self._total_costs.get(month - 1, 0.0)

        total_contributions = 0.0
        total_premiums = 0.0
        premium = self.effective_premium(len(members))

        for m in members:
            contribution = m.contribution_at(month)
            net = contribution - premium
            if net < 0:
                net = 0.0
                premium = contribution

            self.ledger.record(m.name, month, contribution)
            total_contributions += net
            total_premiums += premium

        new_pool = (prev_pool + total_contributions) * (1 + self._monthly_return)
        self._pool[month] = new_pool
        self._total_costs[month] = prev_costs + total_premiums
        self._member_count[month] = len(members)

    def pool_value(self, month: int) -> float:
        return self._pool.get(month, 0.0)

    def total_death_benefit(self, month: int) -> float:
        count = self._member_count.get(month, 0)
        return count * self.coverage_per_member

    def borrowing_power(self, month: int) -> float:
        pool_component = self.pool_value(month) * self.pool_leverage
        death_benefit_component = self.total_death_benefit(month) * self.death_benefit_leverage
        return pool_component + death_benefit_component

    def member_equity(self, member: str, month: int) -> float:
        total_contrib = self.ledger.contributions_through(month)
        if total_contrib == 0:
            return 0.0
        member_contrib = self.ledger.contributions_through(month, member)
        return self.pool_value(month) * (member_contrib / total_contrib)

    def monthly_cost(self, member: MemberSchedule, month: int) -> float:
        return self._premium_per_member

    def total_costs_through(self, month: int) -> float:
        return self._total_costs.get(month, 0.0)
