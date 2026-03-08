from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LumpSum:
    month: int
    amount: float


@dataclass
class MemberSchedule:
    name: str
    monthly: float = 0.0
    lump_sums: list[LumpSum] = field(default_factory=list)

    def contribution_at(self, month: int) -> float:
        total = self.monthly
        for ls in self.lump_sums:
            if ls.month == month:
                total += ls.amount
        return total


@dataclass
class ContributionRecord:
    member: str
    month: int
    amount: float


class Ledger:
    def __init__(self) -> None:
        self.records: list[ContributionRecord] = []

    def record(self, member: str, month: int, amount: float) -> None:
        self.records.append(ContributionRecord(member, month, amount))

    def total_contributions(self, member: str | None = None) -> float:
        if member is None:
            return sum(r.amount for r in self.records)
        return sum(r.amount for r in self.records if r.member == member)

    def contributions_through(self, month: int, member: str | None = None) -> float:
        recs = (r for r in self.records if r.month <= month)
        if member is not None:
            recs = (r for r in recs if r.member == member)
        return sum(r.amount for r in recs)

    def members(self) -> set[str]:
        return {r.member for r in self.records}
