"""Growth scenario: model a cooperative starting from 1-2 founders and growing over time.

Instead of a fixed member list, this module defines a schedule of when
members join, so we can see the cooperative's trajectory from day one.
"""

from __future__ import annotations

from dataclasses import dataclass

from coopsim.ledger import LumpSum, MemberSchedule
from coopsim.instruments.base import Instrument
from coopsim.instruments.term_life_pool import TermLifePool
from coopsim.instruments.whole_life_pool import WholeLifePool
from coopsim.instruments.hybrid_pool import HybridPool


@dataclass
class MemberJoinEvent:
    month: int
    member: MemberSchedule


def build_growth_schedule(
    num_founders: int = 2,
    founder_lump: float | list[float] = 100_000.0,
    founder_monthly: float = 20.0,
    # Recruitment waves: (month, count) — how many regular members join at each month
    recruitment_waves: list[tuple[int, int]] | None = None,
    regular_monthly: float = 20.0,
) -> list[MemberJoinEvent]:
    """Build a growth schedule starting from founders.

    Default schedule:
    - Month 1: 2 founders with $100K each
    - Month 3: 5 friends/family (inner circle)
    - Month 6: 10 more (word of mouth, first results visible)
    - Month 12: 15 more (after 1 year track record)
    - Month 18: 20 more (approaching full cooperative)

    founder_lump can be a single float (broadcast to all founders) or a list
    with one amount per founder.
    """
    events: list[MemberJoinEvent] = []

    # Normalize founder_lump to a list
    if isinstance(founder_lump, (int, float)):
        founder_lumps_list = [float(founder_lump)] * num_founders
    else:
        founder_lumps_list = list(founder_lump)
        if len(founder_lumps_list) < num_founders:
            founder_lumps_list.extend([0.0] * (num_founders - len(founder_lumps_list)))

    # Founders join month 1
    for i in range(1, num_founders + 1):
        lump = founder_lumps_list[i - 1]
        events.append(MemberJoinEvent(
            month=1,
            member=MemberSchedule(
                name=f"founder_{i}",
                monthly=founder_monthly,
                lump_sums=[LumpSum(month=1, amount=lump)] if lump > 0 else [],
            ),
        ))

    if recruitment_waves is None:
        recruitment_waves = [
            (3, 5),     # month 3: inner circle
            (6, 10),    # month 6: word of mouth
            (12, 15),   # month 12: track record proven
            (18, 20),   # month 18: approaching scale
        ]

    member_id = 1
    for join_month, count in recruitment_waves:
        for _ in range(count):
            events.append(MemberJoinEvent(
                month=join_month,
                member=MemberSchedule(
                    name=f"member_{member_id}",
                    monthly=regular_monthly,
                ),
            ))
            member_id += 1

    return events


@dataclass
class GrowthWave:
    """A named recruitment wave for micro growth."""
    month: int
    name: str
    count: int


DEFAULT_MICRO_WAVES: list[GrowthWave] = [
    GrowthWave(month=6, name="Inner Circle", count=5),
    GrowthWave(month=12, name="Word of Mouth", count=5),
    GrowthWave(month=24, name="Track Record", count=10),
    GrowthWave(month=36, name="Community Expansion", count=15),
    GrowthWave(month=48, name="Full Scale", count=15),
]


def build_micro_growth_schedule(
    num_founders: int = 2,
    founder_lump: float | list[float] = 0.0,
    founder_monthly: float = 50.0,
    regular_monthly: float = 20.0,
    recruitment_waves: list[GrowthWave] | None = None,
) -> list[MemberJoinEvent]:
    """Micro-cooperative: start with a couple, grow group by group.

    Default schedule (realistic organic growth):
    - Month 1:  2 founders (the couple) — buy term life, start paying in
    - Month 6:  5 family/close friends (Group 1 — "Inner Circle")
    - Month 12: 5 more (Group 2 — "Word of Mouth")
    - Month 24: 10 more (Group 3 — "Track Record")
    - Month 36: 15 more (Group 4 — "Community Expansion")
    - Month 48: 15 more (Group 5 — "Full Scale")
    Total: 52 members over 4 years (not 18 months)

    founder_lump can be a single float (broadcast to all founders) or a list
    with one amount per founder.
    """
    events: list[MemberJoinEvent] = []

    if recruitment_waves is None:
        recruitment_waves = DEFAULT_MICRO_WAVES

    # Normalize founder_lump to a list
    if isinstance(founder_lump, (int, float)):
        founder_lumps_list = [float(founder_lump)] * num_founders
    else:
        founder_lumps_list = list(founder_lump)
        if len(founder_lumps_list) < num_founders:
            founder_lumps_list.extend([0.0] * (num_founders - len(founder_lumps_list)))

    # Founders join month 1
    for i in range(1, num_founders + 1):
        lump = founder_lumps_list[i - 1]
        lump_sums = []
        if lump > 0:
            lump_sums = [LumpSum(month=1, amount=lump)]
        events.append(MemberJoinEvent(
            month=1,
            member=MemberSchedule(
                name=f"founder_{i}",
                monthly=founder_monthly,
                lump_sums=lump_sums,
            ),
        ))

    member_id = 1
    for wave in recruitment_waves:
        for _ in range(wave.count):
            events.append(MemberJoinEvent(
                month=wave.month,
                member=MemberSchedule(
                    name=f"member_{member_id}",
                    monthly=regular_monthly,
                ),
            ))
            member_id += 1

    return events


def get_micro_waves(schedule: list[MemberJoinEvent]) -> list[tuple[int, str, int]]:
    """Extract wave info from a micro schedule for reporting.

    Returns list of (month, wave_name, count) tuples.
    """
    # Group events by month, excluding month 1 (founders)
    month_counts: dict[int, int] = {}
    for e in schedule:
        month_counts[e.month] = month_counts.get(e.month, 0) + 1

    waves: list[tuple[int, str, int]] = []

    # Founders are always first
    if 1 in month_counts:
        waves.append((1, "Founders", month_counts[1]))

    # Match remaining months to known wave names
    wave_names = {w.month: w.name for w in DEFAULT_MICRO_WAVES}
    for m in sorted(month_counts):
        if m == 1:
            continue
        name = wave_names.get(m, f"Group (Month {m})")
        waves.append((m, name, month_counts[m]))

    return waves


def print_micro_growth_report(
    schedule: list[MemberJoinEvent],
    instruments: list[Instrument],
    results: dict[str, list[dict]],
    months: int,
) -> None:
    """Print a micro-growth report showing stage-by-stage cooperative trajectory."""

    def fmt(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"${value:,.0f}"
        return f"${value:,.2f}"

    founders = [e.member for e in schedule if e.member.name.startswith("founder")]
    all_members = [e.member for e in schedule]
    waves = get_micro_waves(schedule)

    # Use first instrument for metrics
    inst_name = instruments[0].name
    inst_results = results[inst_name]

    print()
    print("=" * 80)
    print("MICRO-COOPERATIVE GROWTH: FROM COUPLE TO COMMUNITY")
    print("=" * 80)

    # Starting info
    founder_monthly = founders[0].monthly if founders else 50.0
    total_founder_monthly = sum(f.monthly for f in founders)
    lump_total = sum(ls.amount for f in founders for ls in f.lump_sums)
    print(f"\nStarting: {len(founders)} founder(s), "
          f"{'$' + f'{lump_total:,.0f} lump sum + ' if lump_total > 0 else ''}"
          f"${founder_monthly:.0f}/mo each = ${total_founder_monthly:.0f}/mo into the pool")

    # Build stage milestones from waves
    running_total = 0
    stage_months: list[int] = []
    for month, name, count in waves:
        running_total += count
        stage_months.append(month)

    # Show each stage
    running_total = 0
    stage_num = 0
    for month, wave_name, count in waves:
        running_total += count
        stage_num += 1

        # Determine the snapshot month (end of period before next wave, or end of sim)
        next_wave_idx = stage_months.index(month) + 1
        if next_wave_idx < len(stage_months):
            snapshot_month = stage_months[next_wave_idx] - 1
        else:
            snapshot_month = min(months, month + 11)  # show ~1 year after last wave
        snapshot_month = min(snapshot_month, months)

        snap = inst_results[snapshot_month - 1]

        print(f"\n--- Stage {stage_num}: {wave_name} "
              f"(Month {month}, +{count} = {running_total} total) ---")
        print(f"  Members: {snap['member_count']} | "
              f"Monthly in: {fmt(sum(e.member.monthly for e in schedule if e.month <= snapshot_month))}")

        db = snap.get('death_benefit', 0)
        cv = snap.get('cash_value', 0)
        pool = snap['pool_value']
        borrow = snap['borrowing_power']

        print(f"  Death benefit: {fmt(db)}")
        if cv > 0:
            print(f"  Cash value: {fmt(cv)}")
        print(f"  Pool after month {snapshot_month}: {fmt(pool)}")
        print(f"  Borrowing power: {fmt(borrow)}")

        if running_total > 0:
            per_member = borrow / running_total
            print(f"  Per-member credit capacity: {fmt(per_member)}")

    # Property readiness check
    print()
    print("--- Property Readiness ---")
    # Find first month where borrowing power exceeds various thresholds
    thresholds = [
        (200_000, "2-unit duplex (~$200K)"),
        (400_000, "4-unit building (~$400K)"),
        (750_000, "8-10 unit building (~$750K)"),
        (1_000_000, "10+ unit building (~$1M)"),
    ]
    for threshold, desc in thresholds:
        ready_month = None
        for snap in inst_results:
            if snap['borrowing_power'] >= threshold:
                ready_month = snap['month']
                members_at = snap['member_count']
                break
        if ready_month and ready_month <= months:
            years = ready_month / 12
            print(f"  {desc}: Ready at month {ready_month} ({years:.1f} years), {members_at} members")
        else:
            print(f"  {desc}: Not reached in {months} months")

    # Final summary
    final = inst_results[months - 1] if months <= len(inst_results) else inst_results[-1]
    print(f"\n--- Final State (Month {months}) ---")
    print(f"  Members: {final['member_count']}")
    print(f"  Pool value: {fmt(final['pool_value'])}")
    if final.get('death_benefit', 0) > 0:
        print(f"  Death benefit: {fmt(final['death_benefit'])}")
    if final.get('cash_value', 0) > 0:
        print(f"  Cash value: {fmt(final['cash_value'])}")
    print(f"  Borrowing power: {fmt(final['borrowing_power'])}")

    # Per-founder equity when founders have unequal lump sums
    founder_lumps = [sum(ls.amount for ls in f.lump_sums) for f in founders]
    if len(set(founder_lumps)) > 1:
        inst = instruments[0]
        print(f"\n--- Founder Equity Breakdown (Unequal Lump Sums) ---")
        for f in founders:
            lump = sum(ls.amount for ls in f.lump_sums)
            eq = inst.member_equity(f.name, months)
            print(f"  {f.name}: ${lump:,.0f} lump → {fmt(eq)} equity")
            if hasattr(inst, 'member_equity_breakdown'):
                bd = inst.member_equity_breakdown(f.name, months)
                cv_str = f" | Cash value: {fmt(bd['cash_value'])}" if 'cash_value' in bd else ""
                print(f"    Preferred: {fmt(bd['preferred'])} | "
                      f"Common: {fmt(bd['common'])}{cv_str} | "
                      f"Vested: {bd['vesting_pct']:.0%}")

    print()
    print("=" * 80)


def run_growth_simulation(
    schedule: list[MemberJoinEvent],
    instruments: list[Instrument],
    months: int = 120,
) -> dict[str, list[dict]]:
    """Run simulation where members join at different times."""
    results: dict[str, list[dict]] = {inst.name: [] for inst in instruments}

    for month in range(1, months + 1):
        # Determine active members this month
        active_members = [e.member for e in schedule if e.month <= month]

        for inst in instruments:
            inst.step(month, active_members)
            has_db = isinstance(inst, (TermLifePool, WholeLifePool, HybridPool))
            has_cv = isinstance(inst, WholeLifePool) or (hasattr(inst, 'cash_value') and callable(getattr(inst, 'cash_value', None)))
            snapshot = {
                "month": month,
                "pool_value": inst.pool_value(month),
                "borrowing_power": inst.borrowing_power(month),
                "total_costs": inst.total_costs_through(month),
                "death_benefit": inst.total_death_benefit(month) if has_db else 0.0,
                "cash_value": inst.cash_value(month) if has_cv else 0.0,
                "member_count": len(active_members),
            }
            results[inst.name].append(snapshot)

    return results


def print_growth_report(
    schedule: list[MemberJoinEvent],
    instruments: list[Instrument],
    results: dict[str, list[dict]],
    months: int,
) -> None:
    """Print a growth-focused report showing the cooperative's trajectory."""

    def fmt(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"${value:>12,.0f}"
        return f"${value:>12,.2f}"

    founders = [e.member for e in schedule if e.member.name.startswith("founder")]
    all_members = [e.member for e in schedule]

    print()
    print("=" * 90)
    print("COOPERATIVE GROWTH SIMULATOR — FROM FOUNDERS TO FULL COOPERATIVE")
    print("=" * 90)
    print(f"Founders: {len(founders)} | Target members: {len(all_members)} | Months: {months}")

    # Show founder details
    for f in founders:
        lump_total = sum(ls.amount for ls in f.lump_sums)
        print(f"  {f.name}: ${lump_total:,.0f} lump + ${f.monthly:.0f}/mo")

    # Show recruitment schedule
    print()
    print("--- Recruitment Schedule ---")
    seen_months: dict[int, int] = {}
    for e in schedule:
        seen_months[e.month] = seen_months.get(e.month, 0) + 1
    running_total = 0
    for m in sorted(seen_months):
        running_total += seen_months[m]
        print(f"  Month {m:>3}: +{seen_months[m]} members → {running_total} total")

    print()

    # Milestone table
    col_width = 16
    inst_names = [inst.name for inst in instruments]

    # Key months to show
    milestones = sorted(set(
        [1, 3, 6, 12, 18, 24, 36, 48, 60, 84, 120]
    ))
    milestones = [m for m in milestones if m <= months]

    print("--- Growth Trajectory ---")
    header = f"{'Month':>6} {'Members':>8}"
    for name in inst_names:
        header += f"  {'Pool':>{col_width}}  {'Borrow Pwr':>{col_width}}"
    print(header)

    sub_header = f"{'':>6} {'':>8}"
    for name in inst_names:
        label = name[:col_width]
        sub_header += f"  {label:>{col_width}}  {'':>{col_width}}"
    print(sub_header)
    print("-" * len(header))

    for m in milestones:
        snap = results[inst_names[0]][m - 1]
        row = f"{m:>6} {snap['member_count']:>8}"
        for name in inst_names:
            s = results[name][m - 1]
            row += f"  {fmt(s['pool_value']):>{col_width}}  {fmt(s['borrowing_power']):>{col_width}}"
        print(row)

    print()

    # Death benefit progression (instruments with death benefit)
    db_name = next((n for n in inst_names if any(x in n for x in ["Term Life", "Whole Life", "Hybrid"])), None)
    if db_name:
        has_cv = any(results[db_name][0].get("cash_value", 0) is not None for _ in [1])
        label = db_name
        header = f"{'Month':>6} {'Members':>8} {'Death Benefit':>16} {'Pool':>16}"
        if has_cv:
            header += f" {'Cash Value':>16}"
        header += f" {'Borrow Power':>16} {'Leverage':>10}"
        print(f"--- Death Benefit & Leverage ({label}) ---")
        print(header)
        print("-" * len(header))
        for m in milestones:
            s = results[db_name][m - 1]
            total_contrib_est = sum(
                sum(e.member.contribution_at(mo)
                    for mo in range(max(1, e.month), m + 1))
                for e in schedule if e.month <= m
            )
            leverage = s["borrowing_power"] / total_contrib_est if total_contrib_est > 0 else 0
            row = (f"{m:>6} {s['member_count']:>8} {fmt(s['death_benefit']):>16} "
                   f"{fmt(s['pool_value']):>16}")
            if has_cv:
                row += f" {fmt(s.get('cash_value', 0)):>16}"
            row += f" {fmt(s['borrowing_power']):>16} {leverage:>9.1f}x"
            print(row)

    # Founder equity tracking
    print()
    print("--- Founder Equity Over Time ---")
    print(f"{'Month':>6}", end="")
    for f in founders:
        for inst in instruments:
            print(f"  {f.name}/{inst.name[:8]:>20}", end="")
    print()

    for m in milestones:
        row = f"{m:>6}"
        for f in founders:
            for inst in instruments:
                eq = inst.member_equity(f.name, m)
                row += f"  {fmt(eq):>20}"
        print(row)

    print()
    print("=" * 90)
