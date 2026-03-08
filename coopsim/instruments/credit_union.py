from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.ledger import MemberSchedule


class CreditUnionFund(Instrument):
    """Credit union-style fund.

    Pooled savings with formal lending operations. Members earn interest
    on deposits. The fund makes loans at higher rates. The spread between
    deposit rate and lending rate generates cooperative income. Operating
    costs and reserve requirements reduce available capital.
    """

    name = "Credit Union Fund"

    def __init__(
        self,
        deposit_rate: float = 0.02,
        lending_rate: float = 0.07,
        operating_cost_pct: float = 0.01,
        reserve_requirement: float = 0.10,
        loan_deployment_pct: float = 0.70,
    ) -> None:
        super().__init__()
        self.deposit_rate = deposit_rate
        self.lending_rate = lending_rate
        self.operating_cost_pct = operating_cost_pct
        self.reserve_requirement = reserve_requirement
        self.loan_deployment_pct = loan_deployment_pct

        self._monthly_deposit_rate = (1 + deposit_rate) ** (1 / 12) - 1
        self._monthly_lending_rate = (1 + lending_rate) ** (1 / 12) - 1
        self._monthly_operating_cost = (1 + operating_cost_pct) ** (1 / 12) - 1

        self._pool: dict[int, float] = {}
        self._total_costs: dict[int, float] = {}

    def step(self, month: int, members: list[MemberSchedule]) -> None:
        prev_pool = self._pool.get(month - 1, 0.0)
        prev_costs = self._total_costs.get(month - 1, 0.0)

        total_contributions = 0.0
        for m in members:
            contribution = m.contribution_at(month)
            self.ledger.record(m.name, month, contribution)
            total_contributions += contribution

        total_deposits = prev_pool + total_contributions

        # Reserve sits idle
        reserves = total_deposits * self.reserve_requirement
        deployable = total_deposits - reserves

        # Loans earn lending rate, deployed portion
        loans_out = deployable * self.loan_deployment_pct
        idle_cash = deployable - loans_out

        loan_income = loans_out * self._monthly_lending_rate
        # Idle cash earns nothing (or a minimal rate — we'll say 0)

        # Interest owed to depositors
        deposit_interest = total_deposits * self._monthly_deposit_rate

        # Operating costs
        operating_cost = total_deposits * self._monthly_operating_cost

        # Net: pool grows by loan income, shrinks by deposit interest & costs
        # But deposit interest stays in the pool (credited to members)
        # So net pool = deposits + loan_income - operating_cost
        new_pool = total_deposits + loan_income - operating_cost
        self._pool[month] = new_pool
        self._total_costs[month] = prev_costs + operating_cost

    def pool_value(self, month: int) -> float:
        return self._pool.get(month, 0.0)

    def borrowing_power(self, month: int) -> float:
        # Can lend up to the non-reserved, non-deployed portion
        pool = self.pool_value(month)
        available = pool * (1 - self.reserve_requirement)
        return available

    def member_equity(self, member: str, month: int) -> float:
        total_contrib = self.ledger.contributions_through(month)
        if total_contrib == 0:
            return 0.0
        member_contrib = self.ledger.contributions_through(month, member)
        return self.pool_value(month) * (member_contrib / total_contrib)

    def monthly_cost(self, member: MemberSchedule, month: int) -> float:
        return 0.0  # Operating costs are paid from the fund, not directly by members

    def total_costs_through(self, month: int) -> float:
        return self._total_costs.get(month, 0.0)
