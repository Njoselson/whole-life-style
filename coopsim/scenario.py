from __future__ import annotations

from coopsim.ledger import LumpSum, MemberSchedule
from coopsim.instruments import Instrument, TermLifePool, SavingsPool, CreditUnionFund, WholeLifePool, HybridPool


def build_members(
    num_regular: int = 50,
    monthly: float = 20.0,
    num_whales: int = 2,
    whale_lump: float | list[float] = 100_000.0,
    whale_lump2: float = 20_000.0,
    whale_lump2_month: int = 24,
    whale_monthly: float = 20.0,
) -> list[MemberSchedule]:
    members: list[MemberSchedule] = []

    # Normalize whale_lump to a list
    if isinstance(whale_lump, (int, float)):
        whale_lumps_list = [float(whale_lump)] * num_whales
    else:
        whale_lumps_list = list(whale_lump)
        if len(whale_lumps_list) < num_whales:
            whale_lumps_list.extend([0.0] * (num_whales - len(whale_lumps_list)))

    for i in range(1, num_regular + 1):
        members.append(MemberSchedule(name=f"member_{i}", monthly=monthly))

    for i in range(1, num_whales + 1):
        lump = whale_lumps_list[i - 1]
        lump_sums = [LumpSum(month=1, amount=lump)] if lump > 0 else []
        if whale_lump2 > 0:
            lump_sums.append(LumpSum(month=whale_lump2_month, amount=whale_lump2))
        members.append(
            MemberSchedule(
                name=f"whale_{i}",
                monthly=whale_monthly,
                lump_sums=lump_sums,
            )
        )

    return members


def build_instruments(
    which: list[str] | None = None,
    lending_rate: float = 0.08,
    deposit_rate: float = 0.02,
    savings_return: float = 0.04,
    operating_cost: float = 0.01,
    coverage_per_member: float = 100_000.0,
    founder_coverage: float | None = None,
    avg_member_age: int = 35,
    death_benefit_leverage: float = 0.5,
) -> list[Instrument]:
    _founder_coverage = founder_coverage if founder_coverage is not None else coverage_per_member * 2.5
    available = {
        "term_life": lambda: TermLifePool(
            coverage_per_member=coverage_per_member,
            avg_member_age=avg_member_age,
            savings_rate=savings_return,
            death_benefit_leverage=death_benefit_leverage,
        ),
        "savings": lambda: SavingsPool(
            return_rate=savings_return,
        ),
        "credit_union": lambda: CreditUnionFund(
            deposit_rate=deposit_rate,
            lending_rate=lending_rate,
            operating_cost_pct=operating_cost,
        ),
        "whole_life": lambda: WholeLifePool(
            coverage_per_member=_founder_coverage,
            avg_member_age=avg_member_age,
            savings_rate=savings_return,
            death_benefit_leverage=death_benefit_leverage,
        ),
        "hybrid": lambda: HybridPool(
            coverage_per_member=coverage_per_member,
            founder_coverage=_founder_coverage,
            avg_member_age=avg_member_age,
            savings_rate=savings_return,
            death_benefit_leverage=death_benefit_leverage,
        ),
    }

    if which is None:
        which = list(available.keys())

    instruments = []
    for key in which:
        if key in available:
            instruments.append(available[key]())
        else:
            raise ValueError(f"Unknown instrument: {key!r}. Choose from: {list(available.keys())}")

    return instruments
