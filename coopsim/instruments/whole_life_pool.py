from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.ledger import MemberSchedule


# Approximate monthly premium per $100K coverage for permanent (whole) life
# by age bracket. Much higher than term due to cash value accumulation.
DEFAULT_WHOLE_LIFE_PREMIUM_TABLE: dict[tuple[int, int], float] = {
    (18, 29): 80.0,
    (30, 34): 100.0,
    (35, 39): 130.0,
    (40, 44): 170.0,
    (45, 49): 220.0,
    (50, 54): 300.0,
    (55, 59): 400.0,
    (60, 64): 550.0,
}


def whole_life_premium_for_age(
    age: int, coverage: float, table: dict[tuple[int, int], float] | None = None
) -> float:
    """Monthly premium for permanent life at a given age and coverage amount."""
    if table is None:
        table = DEFAULT_WHOLE_LIFE_PREMIUM_TABLE
    for (lo, hi), rate_per_100k in table.items():
        if lo <= age <= hi:
            return rate_per_100k * (coverage / 100_000)
    return 200.0 * (coverage / 100_000)


class WholeLifePool(Instrument):
    """Permanent life insurance pool for founders/whales.

    Founders carry whole/universal life policies through the Life Insurance LLC.
    Higher premiums (~$355/mo) but builds cash value over time.

    Cash value serves as:
    - Loanable asset (policy loans up to 90% of cash value)
    - Secondary collateral for lenders
    - Funding for living buyouts (lifecycle buy-sell)

    Death benefit provides primary collateral, same as term life.
    Premiums are funded from lump sum contributions.
    """

    name = "Whole Life Pool"

    def __init__(
        self,
        coverage_per_member: float = 250_000.0,
        avg_member_age: int = 35,
        savings_rate: float = 0.04,
        cash_value_growth_rate: float = 0.04,
        cash_value_start_pct: float = 0.0,
        cash_value_annual_pct: float = 0.03,
        pool_leverage: float = 0.8,
        death_benefit_leverage: float = 0.5,
        cash_value_leverage: float = 0.9,
    ) -> None:
        super().__init__()
        self.coverage_per_member = coverage_per_member
        self.avg_member_age = avg_member_age
        self.savings_rate = savings_rate
        self.cash_value_growth_rate = cash_value_growth_rate
        self.cash_value_start_pct = cash_value_start_pct
        self.cash_value_annual_pct = cash_value_annual_pct
        self.pool_leverage = pool_leverage
        self.death_benefit_leverage = death_benefit_leverage
        self.cash_value_leverage = cash_value_leverage

        self._monthly_return = (1 + savings_rate) ** (1 / 12) - 1
        self._monthly_cv_growth = (1 + cash_value_growth_rate) ** (1 / 12) - 1
        self._pool: dict[int, float] = {}
        self._cash_value: dict[int, float] = {}
        self._total_costs: dict[int, float] = {}
        self._member_count: dict[int, int] = {}
        self._premium_per_member = whole_life_premium_for_age(
            avg_member_age, coverage_per_member
        )

    def step(self, month: int, members: list[MemberSchedule]) -> None:
        prev_pool = self._pool.get(month - 1, 0.0)
        prev_cv = self._cash_value.get(month - 1, 0.0)
        prev_costs = self._total_costs.get(month - 1, 0.0)

        total_contributions = 0.0
        total_premiums = 0.0

        for m in members:
            contribution = m.contribution_at(month)
            premium = self._premium_per_member
            net = contribution - premium
            if net < 0:
                net = 0.0
                premium = contribution

            self.ledger.record(m.name, month, contribution)
            total_contributions += net
            total_premiums += premium

        # Pool grows from net contributions + interest
        new_pool = (prev_pool + total_contributions) * (1 + self._monthly_return)
        self._pool[month] = new_pool
        self._total_costs[month] = prev_costs + total_premiums
        self._member_count[month] = len(members)

        # Cash value accumulates: a portion of premiums becomes cash value
        # after initial years. Simplified: cash_value_annual_pct of total premiums
        # paid to date becomes cash value, growing at guaranteed rate.
        cv_contribution = total_premiums * self.cash_value_annual_pct
        new_cv = (prev_cv + cv_contribution) * (1 + self._monthly_cv_growth)
        self._cash_value[month] = new_cv

    def pool_value(self, month: int) -> float:
        return self._pool.get(month, 0.0)

    def cash_value(self, month: int) -> float:
        return self._cash_value.get(month, 0.0)

    def total_death_benefit(self, month: int) -> float:
        count = self._member_count.get(month, 0)
        return count * self.coverage_per_member

    def borrowing_power(self, month: int) -> float:
        pool_component = self.pool_value(month) * self.pool_leverage
        death_benefit_component = (
            self.total_death_benefit(month) * self.death_benefit_leverage
        )
        cash_value_component = self.cash_value(month) * self.cash_value_leverage
        return pool_component + death_benefit_component + cash_value_component

    def member_equity(self, member: str, month: int) -> float:
        total_contrib = self.ledger.contributions_through(month)
        if total_contrib == 0:
            return 0.0
        member_contrib = self.ledger.contributions_through(month, member)
        # Equity includes share of pool + share of cash value
        pool_share = self.pool_value(month) * (member_contrib / total_contrib)
        cv_share = self.cash_value(month) * (member_contrib / total_contrib)
        return pool_share + cv_share

    def monthly_cost(self, member: MemberSchedule, month: int) -> float:
        return self._premium_per_member

    def total_costs_through(self, month: int) -> float:
        return self._total_costs.get(month, 0.0)
