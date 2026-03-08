from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.ledger import MemberSchedule


class SavingsPool(Instrument):
    """Simple savings pool (susu / lending circle).

    Direct pooling with no insurance overhead. Members contribute,
    pool earns a return rate. No death benefit protection.
    """

    name = "Savings Pool (Susu)"

    def __init__(
        self,
        return_rate: float = 0.04,
        borrowing_leverage: float = 0.9,
    ) -> None:
        super().__init__()
        self.return_rate = return_rate
        self.borrowing_leverage = borrowing_leverage

        self._monthly_return = (1 + return_rate) ** (1 / 12) - 1
        self._pool: dict[int, float] = {}

    def step(self, month: int, members: list[MemberSchedule]) -> None:
        prev_pool = self._pool.get(month - 1, 0.0)

        total_contributions = 0.0
        for m in members:
            contribution = m.contribution_at(month)
            self.ledger.record(m.name, month, contribution)
            total_contributions += contribution

        new_pool = (prev_pool + total_contributions) * (1 + self._monthly_return)
        self._pool[month] = new_pool

    def pool_value(self, month: int) -> float:
        return self._pool.get(month, 0.0)

    def borrowing_power(self, month: int) -> float:
        return self.pool_value(month) * self.borrowing_leverage

    def member_equity(self, member: str, month: int) -> float:
        total_contrib = self.ledger.contributions_through(month)
        if total_contrib == 0:
            return 0.0
        member_contrib = self.ledger.contributions_through(month, member)
        return self.pool_value(month) * (member_contrib / total_contrib)

    def monthly_cost(self, member: MemberSchedule, month: int) -> float:
        return 0.0

    def total_costs_through(self, month: int) -> float:
        return 0.0
