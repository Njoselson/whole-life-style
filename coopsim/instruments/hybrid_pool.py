from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.instruments.term_life_pool import TermLifePool, premium_for_age
from coopsim.ledger import MemberSchedule


class HybridPool(Instrument):
    """Unified model: term life for ALL members.

    Regular members carry standard term coverage ($100K default).
    Founders carry higher term coverage ($250K default) and contribute
    lump sums as zero-interest loans to the cooperative, returned via vesting.

    Entity structure:
    - Fraternal Benefit Society [501(c)(8)] (parent)
      - Property Holding LLC (real estate)
      - Cooperative Pool (operating account)

    Equity model:
    - Preferred: founder lump sums returned over 5 years (capped at contribution)
    - Common: time-weighted (member-months), early members get 1.5x bonus
    - Credit limits: 5x contributions, capped at 75% of death benefit
    """

    name = "Hybrid Pool"

    def __init__(
        self,
        coverage_per_member: float = 100_000.0,
        founder_coverage: float = 250_000.0,
        avg_member_age: int = 35,
        avg_founder_age: int = 35,
        savings_rate: float = 0.04,
        group_discount: float = 0.30,
        pool_leverage: float = 0.8,
        death_benefit_leverage: float = 0.5,
    ) -> None:
        super().__init__()
        self.coverage_per_member = coverage_per_member
        self.founder_coverage = founder_coverage
        self.avg_member_age = avg_member_age
        self.avg_founder_age = avg_founder_age
        self.savings_rate = savings_rate
        self.group_discount = group_discount
        self.pool_leverage = pool_leverage
        self.death_benefit_leverage = death_benefit_leverage

        self._monthly_return = (1 + savings_rate) ** (1 / 12) - 1

        # Term life premium (regular members) — base individual rate
        self._individual_term_premium = premium_for_age(avg_member_age, coverage_per_member)
        self._term_premium = self._individual_term_premium * (1 - group_discount)

        # Founder term premium (higher coverage)
        individual_founder_term = premium_for_age(avg_founder_age, founder_coverage)
        self._founder_term_premium = individual_founder_term * (1 - group_discount)

        self._pool: dict[int, float] = {}
        self._total_costs: dict[int, float] = {}
        self._member_count: dict[int, int] = {}
        self._founder_count: dict[int, int] = {}

        # Preferred equity tracking
        self._founder_lump_totals: dict[str, float] = {}
        self._join_month: dict[str, int] = {}
        self._monthly_totals: dict[str, float] = {}  # cumulative monthly contributions
        self._member_months: dict[str, int] = {}  # time-weighted equity tracking
        self._founding_member: dict[str, bool] = {}  # early member bonus (1.5x)
        self._total_contributions: dict[str, float] = {}  # all money in (monthly + lump)
        self._last_month: int = 0

    def _is_founder(self, member: MemberSchedule) -> bool:
        return member.name.startswith("founder") or member.name.startswith("whale")

    def effective_group_discount(self, member_count: int) -> float:
        """Group discount scales with size. No discount under 10 members."""
        if member_count < 10:
            return 0.0
        elif member_count < 25:
            return self.group_discount * 0.5
        else:
            return self.group_discount

    def effective_term_premium(self, member_count: int) -> float:
        """Term premium adjusted for group size."""
        discount = self.effective_group_discount(member_count)
        return self._individual_term_premium * (1 - discount)

    def _lump_sum_at(self, member: MemberSchedule, month: int) -> float:
        """Get lump sum contribution for a member at a specific month."""
        return sum(ls.amount for ls in member.lump_sums if ls.month == month)

    def _vesting_pct(self, member_name: str, month: int) -> float:
        """Vesting percentage: 20%/year over 5 years (60 months)."""
        join = self._join_month.get(member_name)
        if join is None:
            return 0.0
        months_in = month - join
        return min(1.0, months_in / 60.0)

    def step(self, month: int, members: list[MemberSchedule]) -> None:
        prev_pool = self._pool.get(month - 1, 0.0)
        prev_costs = self._total_costs.get(month - 1, 0.0)

        self._last_month = month

        total_contributions = 0.0
        total_premiums = 0.0
        founder_count = 0
        term_premium = self.effective_term_premium(len(members))

        for m in members:
            # Track join month
            if m.name not in self._join_month:
                self._join_month[m.name] = month

            # Track member-months for time-weighted equity
            if m.name not in self._member_months:
                self._member_months[m.name] = 0
            self._member_months[m.name] += 1

            # Track founding member status (joined in months 1-12)
            if m.name not in self._founding_member:
                self._founding_member[m.name] = (month <= 12)

            # Track lump sums for founders
            lump_this_month = self._lump_sum_at(m, month)
            if lump_this_month > 0 and self._is_founder(m):
                self._founder_lump_totals[m.name] = (
                    self._founder_lump_totals.get(m.name, 0.0) + lump_this_month
                )
            contribution = m.contribution_at(month)
            is_founder = self._is_founder(m)

            if is_founder:
                premium = self._founder_term_premium
                founder_count += 1
            else:
                premium = term_premium

            net = contribution - premium
            if net < 0:
                net = 0.0
                premium = contribution

            self.ledger.record(m.name, month, contribution)
            total_contributions += net
            total_premiums += premium

            # Track monthly (non-lump) contributions for common equity
            monthly_only = m.monthly
            self._monthly_totals[m.name] = (
                self._monthly_totals.get(m.name, 0.0) + monthly_only
            )

            # Track total contributions (monthly + lump sums) for credit limits
            self._total_contributions[m.name] = (
                self._total_contributions.get(m.name, 0.0) + contribution
            )

        new_pool = (prev_pool + total_contributions) * (1 + self._monthly_return)
        self._pool[month] = new_pool
        self._total_costs[month] = prev_costs + total_premiums
        self._member_count[month] = len(members)
        self._founder_count[month] = founder_count

    def pool_value(self, month: int) -> float:
        return self._pool.get(month, 0.0)

    def total_death_benefit(self, month: int) -> float:
        total_members = self._member_count.get(month, 0)
        founders = self._founder_count.get(month, 0)
        regular = total_members - founders
        return (regular * self.coverage_per_member) + (
            founders * self.founder_coverage
        )

    def borrowing_power(self, month: int) -> float:
        pool_component = self.pool_value(month) * self.pool_leverage
        death_benefit_component = (
            self.total_death_benefit(month) * self.death_benefit_leverage
        )
        return pool_component + death_benefit_component

    def member_equity_breakdown(self, member: str, month: int) -> dict:
        """Break down a member's equity into capital return and common.

        Components:
        - Capital return (preferred): lump_sum * vesting_pct * min(1.0, pool / total_lumps)
          Founders get their lump sum back over 5 years, capped at original contribution.
          This is a zero-interest loan to the cooperative, not ownership.
        - Common: time-weighted by member-months (not dollar-weighted).
          Early members (months 1-12) get 1.5x weight.
          (pool - total_lumps) * (weighted_member_months / total_weighted_months)
        - Credit limit: min(total_contributions * unlock_rate, 75% of death benefit)
        """
        pool = self.pool_value(month)
        vesting = self._vesting_pct(member, month)

        total_lumps = sum(self._founder_lump_totals.values())
        member_lump = self._founder_lump_totals.get(member, 0.0)
        member_monthly = self._monthly_totals.get(member, 0.0)

        # Capital return (preferred) — capped at original lump sum
        if member_lump > 0 and total_lumps > 0:
            pool_coverage = min(1.0, pool / total_lumps) if total_lumps > 0 else 0.0
            preferred = member_lump * vesting * pool_coverage
        else:
            preferred = 0.0

        # Common equity — time-weighted by member-months
        member_months = self._member_months.get(member, 0)
        is_founding = self._founding_member.get(member, False)
        weight = 1.5 if is_founding else 1.0
        weighted_months = member_months * weight

        total_weighted_months = sum(
            self._member_months.get(m, 0) * (1.5 if self._founding_member.get(m, False) else 1.0)
            for m in self._member_months
        )

        pool_after_lumps = max(0.0, pool - total_lumps)
        if total_weighted_months > 0 and pool_after_lumps > 0:
            common = pool_after_lumps * (weighted_months / total_weighted_months)
        else:
            common = 0.0

        total = preferred + common

        # Credit limit calculation
        credit_info = self.member_credit_limit(member, month)

        return {
            "preferred": preferred,
            "common": common,
            "total": total,
            "vesting_pct": vesting,
            "member_lump": member_lump,
            "member_monthly": member_monthly,
            "member_months": member_months,
            "is_founding_member": is_founding,
            "weight": weight,
            "credit_limit": credit_info["credit_limit"],
            "total_contributions": credit_info["total_contributions"],
            "max_credit": credit_info["max_credit"],
        }

    def member_credit_limit(self, member: str, month: int) -> dict:
        """Calculate a member's credit limit based on contributions and death benefit.

        Formula: credit_limit = min(total_contributions x unlock_rate, max_credit_line)
        - total_contributions: all money this member has put in (monthly + lump sums)
        - unlock_rate: 5x — each $1 contributed unlocks $5 in credit
        - max_credit_line: 75% of death benefit (the ceiling)
        """
        unlock_rate = 5.0
        is_founder = member.startswith("founder") or member.startswith("whale")
        coverage = self.founder_coverage if is_founder else self.coverage_per_member
        max_credit = coverage * 0.75

        total_contrib = self._total_contributions.get(member, 0.0)
        unlocked = total_contrib * unlock_rate
        credit_limit = min(unlocked, max_credit)

        return {
            "credit_limit": credit_limit,
            "total_contributions": total_contrib,
            "unlock_rate": unlock_rate,
            "max_credit": max_credit,
            "coverage": coverage,
            "unlocked_raw": unlocked,
        }

    def member_equity(self, member: str, month: int) -> float:
        """Backward-compatible wrapper: returns total equity."""
        # If no founders have lump sums, fall back to simple pro-rata
        if not self._founder_lump_totals:
            total_contrib = self.ledger.contributions_through(month)
            if total_contrib == 0:
                return 0.0
            member_contrib = self.ledger.contributions_through(month, member)
            ratio = member_contrib / total_contrib
            return self.pool_value(month) * ratio
        return self.member_equity_breakdown(member, month)["total"]

    def monthly_cost(self, member: MemberSchedule, month: int) -> float:
        if self._is_founder(member):
            return self._founder_term_premium
        return self._term_premium

    def total_costs_through(self, month: int) -> float:
        return self._total_costs.get(month, 0.0)
