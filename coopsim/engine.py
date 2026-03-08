from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.instruments.term_life_pool import TermLifePool
from coopsim.instruments.whole_life_pool import WholeLifePool
from coopsim.instruments.hybrid_pool import HybridPool
from coopsim.ledger import MemberSchedule


def _has_death_benefit(inst: Instrument) -> bool:
    return isinstance(inst, (TermLifePool, WholeLifePool, HybridPool))


def _get_cash_value(inst: Instrument, month: int) -> float:
    if isinstance(inst, (WholeLifePool, HybridPool)):
        return inst.cash_value(month)
    return 0.0


def run_simulation(
    members: list[MemberSchedule],
    instruments: list[Instrument],
    months: int = 120,
) -> dict[str, list[dict]]:
    """Run month-by-month simulation across all instruments.

    Returns a dict mapping instrument name to a list of monthly snapshots.
    Each snapshot contains: month, pool_value, borrowing_power, total_costs,
    death_benefit, cash_value.
    """
    results: dict[str, list[dict]] = {inst.name: [] for inst in instruments}

    for month in range(1, months + 1):
        for inst in instruments:
            inst.step(month, members)
            snapshot = {
                "month": month,
                "pool_value": inst.pool_value(month),
                "borrowing_power": inst.borrowing_power(month),
                "total_costs": inst.total_costs_through(month),
                "death_benefit": inst.total_death_benefit(month) if _has_death_benefit(inst) else 0.0,
                "cash_value": _get_cash_value(inst, month),
            }
            results[inst.name].append(snapshot)

    return results
