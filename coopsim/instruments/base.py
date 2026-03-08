from __future__ import annotations

from abc import ABC, abstractmethod

from coopsim.ledger import Ledger, MemberSchedule


class Instrument(ABC):
    name: str

    def __init__(self) -> None:
        self.ledger = Ledger()

    @abstractmethod
    def step(self, month: int, members: list[MemberSchedule]) -> None:
        """Advance one month: collect contributions, apply returns/costs."""

    @abstractmethod
    def pool_value(self, month: int) -> float:
        """Total cooperative pool value at end of given month."""

    @abstractmethod
    def borrowing_power(self, month: int) -> float:
        """How much the coop can borrow against at end of given month."""

    @abstractmethod
    def member_equity(self, member: str, month: int) -> float:
        """What a specific member could withdraw."""

    @abstractmethod
    def monthly_cost(self, member: MemberSchedule, month: int) -> float:
        """Overhead costs for a member in a given month (premiums, fees, etc.)."""

    @abstractmethod
    def total_costs_through(self, month: int) -> float:
        """Total overhead costs paid by all members through given month."""
