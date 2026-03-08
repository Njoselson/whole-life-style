from __future__ import annotations

from coopsim.instruments.base import Instrument
from coopsim.instruments.term_life_pool import TermLifePool
from coopsim.instruments.whole_life_pool import WholeLifePool
from coopsim.instruments.hybrid_pool import HybridPool
from coopsim.ledger import MemberSchedule
from coopsim.property import PropertyConfig, print_property_summary


def fmt(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value:>12,.0f}"
    return f"${value:>12,.2f}"


def print_comparison(
    instruments: list[Instrument],
    members: list[MemberSchedule],
    results: dict[str, list[dict]],
    months: int,
) -> None:
    # Find a regular member and a whale for equity display
    regular = next((m for m in members if not m.name.startswith("whale")), None)
    whale = next((m for m in members if m.name.startswith("whale")), None)

    inst_names = [inst.name for inst in instruments]
    col_width = 18

    # Header
    print()
    print("=" * 80)
    print("COOPERATIVE FINANCE SIMULATOR — COMPARISON REPORT")
    print("=" * 80)
    print(f"Members: {len(members)} | Months: {months}")

    # Show instrument-specific details
    tl = next((i for i in instruments if isinstance(i, TermLifePool)), None)
    hybrid = next((i for i in instruments if isinstance(i, HybridPool)), None)
    wl = next((i for i in instruments if isinstance(i, WholeLifePool)), None)

    if tl:
        total_db = tl.coverage_per_member * len(members)
        savings_vs_individual = tl._individual_premium - tl._premium_per_member
        print(f"Term Life: ${tl.coverage_per_member:,.0f} coverage/member | "
              f"${tl._premium_per_member:.0f}/mo group premium (age ~{tl.avg_member_age}) | "
              f"${total_db:,.0f} total death benefit")
        print(f"  Group discount: {tl.group_discount:.0%} off → "
              f"saving ${savings_vs_individual:.0f}/mo vs individual (${tl._individual_premium:.0f}/mo)")
        net_per_regular = members[0].monthly - tl._premium_per_member
        print(f"  Regular member: ${members[0].monthly:.0f}/mo contribution - "
              f"${tl._premium_per_member:.0f}/mo premium = "
              f"${max(0, net_per_regular):.2f}/mo to pool")
        print(f"  Pool earns {tl.savings_rate:.1%}/yr (high-yield savings account)")

    if hybrid:
        print(f"Hybrid Pool: term life for regular members + permanent life for founders")
        print(f"  Regular: ${hybrid.coverage_per_member:,.0f} term coverage @ ${hybrid._term_premium:.0f}/mo")
        print(f"  Founders: ${hybrid.founder_coverage:,.0f} whole life coverage @ ${hybrid._whole_life_premium:.0f}/mo")

    if wl:
        print(f"Whole Life: ${wl.coverage_per_member:,.0f} coverage @ ${wl._premium_per_member:.0f}/mo")
        print(f"  Cash value grows at {wl.cash_value_growth_rate:.1%}/yr (guaranteed)")

    print()

    # Year-by-year table
    year_months = [m for m in range(12, months + 1, 12)]
    if months not in year_months:
        year_months.append(months)

    for metric_label, metric_key in [
        ("Pool Value", "pool_value"),
        ("Borrowing Power", "borrowing_power"),
        ("Total Costs Paid", "total_costs"),
    ]:
        print(f"--- {metric_label} ---")
        header = f"{'Year':>6}"
        for name in inst_names:
            header += f"  {name:>{col_width}}"
        print(header)

        for m in year_months:
            year = m // 12
            row = f"{year:>6}"
            for name in inst_names:
                snapshot = results[name][m - 1]
                row += f"  {fmt(snapshot[metric_key]):>{col_width}}"
            print(row)
        print()

    # Member equity comparison
    if regular or whale:
        print("--- Member Equity ---")
        for label, member in [("Regular Member", regular), ("Whale Member", whale)]:
            if member is None:
                continue
            print(f"\n  {label}: {member.name}")
            header = f"  {'Year':>6}"
            for name in inst_names:
                header += f"  {name:>{col_width}}"
            print(header)

            for m in year_months:
                year = m // 12
                row = f"  {year:>6}"
                for inst in instruments:
                    eq = inst.member_equity(member.name, m)
                    row += f"  {fmt(eq):>{col_width}}"
                print(row)
        print()

    # Net return summary at final month
    print("--- Final Summary (End of Simulation) ---")
    final = months
    total_contributed = sum(
        sum(m.contribution_at(mo) for mo in range(1, final + 1))
        for m in members
    )
    print(f"  Total Contributed: {fmt(total_contributed)}")
    print()
    header = f"  {'':>20}"
    for name in inst_names:
        header += f"  {name:>{col_width}}"
    print(header)

    def _death_benefit(inst: Instrument) -> float:
        if isinstance(inst, (TermLifePool, WholeLifePool, HybridPool)):
            return inst.total_death_benefit(final)
        return 0.0

    def _cash_value(inst: Instrument) -> float:
        if isinstance(inst, (WholeLifePool, HybridPool)):
            return inst.cash_value(final)
        return 0.0

    for row_label, fn in [
        ("Pool Value", lambda inst: inst.pool_value(final)),
        ("Cash Value", _cash_value),
        ("Death Benefit", _death_benefit),
        ("Borrowing Power", lambda inst: inst.borrowing_power(final)),
        ("Total Costs", lambda inst: inst.total_costs_through(final)),
        ("Net Return", lambda inst: inst.pool_value(final) - total_contributed),
        ("Return %", None),
    ]:
        row = f"  {row_label:>20}"
        for inst in instruments:
            if row_label == "Return %":
                ret = inst.pool_value(final) - total_contributed
                pct = (ret / total_contributed * 100) if total_contributed > 0 else 0
                row += f"  {pct:>{col_width}.1f}%"
            else:
                val = fn(inst)
                row += f"  {fmt(val):>{col_width}}"
        print(row)
    print()
    print("=" * 80)
