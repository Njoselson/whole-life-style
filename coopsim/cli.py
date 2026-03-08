from __future__ import annotations

import argparse

from coopsim.scenario import build_members, build_instruments
from coopsim.engine import run_simulation
from coopsim.report import print_comparison
from coopsim.growth import (
    build_growth_schedule,
    build_micro_growth_schedule,
    run_growth_simulation,
    print_growth_report,
    print_micro_growth_report,
)
from coopsim.property import PropertyConfig, print_property_summary
from coopsim.member_value import (
    MemberValueSummary,
    CoopBalanceSheet,
    DeathScenario,
    print_member_value,
    print_balance_sheet,
    print_death_scenario,
    print_contribution_tiers,
    print_founder_equity_report,
    print_coop_loan_report,
    print_member_comparison,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="coopsim",
        description="Simulate and compare cooperative financial structures",
    )

    # Mode selection
    parser.add_argument("--growth", action="store_true", help="Run growth scenario (start from founders, recruit over time)")

    # Common params
    parser.add_argument("--monthly", type=float, default=20.0, help="Monthly contribution per regular member (default: $20)")
    parser.add_argument("--months", type=int, default=120, help="Simulation duration in months (default: 120)")
    parser.add_argument("--instruments", nargs="+", default=None, choices=["term_life", "savings", "credit_union", "whole_life", "hybrid"], help="Instruments to compare")
    parser.add_argument("--savings-rate", type=float, default=0.04, help="Annual savings account rate for pool (default: 0.04)")
    parser.add_argument("--lending-rate", type=float, default=0.08, help="Annual lending rate for credit union (default: 0.08)")
    parser.add_argument("--deposit-rate", type=float, default=0.02, help="Annual deposit rate for credit union (default: 0.02)")
    parser.add_argument("--operating-cost", type=float, default=0.01, help="Annual operating cost pct for credit union (default: 0.01)")
    parser.add_argument("--coverage", type=float, default=100_000.0, help="Term life coverage per member (default: $100,000)")
    parser.add_argument("--founder-coverage", type=float, default=None, help="Permanent life coverage per founder (default: coverage × 2.5)")
    parser.add_argument("--avg-age", type=int, default=35, help="Average member age for premium calc (default: 35)")
    parser.add_argument("--death-benefit-leverage", type=float, default=0.5, help="Fraction of death benefit counted as borrowing power (default: 0.5)")

    # Standard mode params
    parser.add_argument("--members", type=int, default=50, help="Number of regular members (default: 50)")
    parser.add_argument("--whales", type=int, default=2, help="Number of whale members (default: 2)")
    parser.add_argument("--whale-amount", type=float, default=100_000.0, help="Initial whale lump sum (default: $100,000)")
    parser.add_argument("--whale-lump2", type=float, default=20_000.0, help="Second whale lump sum (default: $20,000)")
    parser.add_argument("--whale-lump2-month", type=int, default=24, help="Month for second whale lump sum (default: 24)")

    # Growth mode params
    parser.add_argument("--founders", type=int, default=2, help="Number of founding families (default: 2)")
    parser.add_argument("--founder-amount", type=float, default=None, help="Lump sum per founder (broadcast to all, default: $100,000 standard, $0 micro)")
    parser.add_argument("--founder-amounts", type=str, default=None, help="Comma-separated lump sums per founder (e.g. '200000,100000')")
    parser.add_argument("--micro", action="store_true", help="Use micro growth schedule (slow, group-by-group from a couple)")
    parser.add_argument("--founder-monthly", type=float, default=None, help="Monthly contribution per founder (default: same as --monthly, or $50 for --micro)")
    parser.add_argument("--founder-view", action="store_true", help="Show founder equity breakdown report")

    # Property mode params
    parser.add_argument("--property", type=float, default=None, metavar="PRICE", help="Property purchase price (enables property model)")
    parser.add_argument("--units", type=int, default=4, help="Total units in property (default: 4, brownstone)")
    parser.add_argument("--housing-members", type=int, default=None, help="Units for housing members (default: all units)")
    parser.add_argument("--rental-units", type=int, default=0, help="Units for market-rate rental (default: 0)")
    parser.add_argument("--market-rent", type=float, default=2_500.0, help="Comparable market rent per unit (default: $2,500)")
    parser.add_argument("--mortgage-rate", type=float, default=0.05, help="Annual mortgage rate (default: 0.05)")
    parser.add_argument("--down-pct", type=float, default=0.20, help="Down payment percentage (default: 0.20)")
    parser.add_argument("--lender-view", action="store_true", help="Show DSCR and lender metrics")

    # Member value view
    parser.add_argument("--member-view", action="store_true", help="Show what a single member gets (the pitch)")
    parser.add_argument("--loan-amount", type=float, default=5_000.0, help="Example loan amount for member view (default: $5,000)")
    parser.add_argument("--coop-rate", type=float, default=0.06, help="Cooperative internal lending rate (default: 0.06)")
    parser.add_argument("--balance-sheet", action="store_true", help="Show cooperative balance sheet and credit tiers")
    parser.add_argument("--loans", action="store_true", help="Show zero-interest cooperative loan model")
    parser.add_argument("--tiers", action="store_true", help="Show contribution tier comparison (pay more, build more)")
    return parser.parse_args(argv)


def _resolve_housing_units(args: argparse.Namespace) -> int:
    """Housing members defaults to all units (no rental by default)."""
    if args.housing_members is not None:
        return args.housing_members
    return args.units - args.rental_units


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    instruments = build_instruments(
        which=args.instruments,
        lending_rate=args.lending_rate,
        deposit_rate=args.deposit_rate,
        savings_return=args.savings_rate,
        operating_cost=args.operating_cost,
        coverage_per_member=args.coverage,
        founder_coverage=args.founder_coverage,
        avg_member_age=args.avg_age,
        death_benefit_leverage=args.death_benefit_leverage,
    )

    if args.growth:
        # Determine founder monthly: explicit flag > micro default ($50) > regular monthly
        if args.founder_monthly is not None:
            founder_monthly = args.founder_monthly
        elif args.micro:
            founder_monthly = 50.0
        else:
            founder_monthly = args.monthly

        # Resolve founder lump sum(s): --founder-amounts (list) > --founder-amount (broadcast) > default
        if args.founder_amounts is not None:
            founder_lump: float | list[float] = [float(x.strip()) for x in args.founder_amounts.split(",")]
        elif args.founder_amount is not None:
            founder_lump = args.founder_amount
        else:
            founder_lump = 0.0 if args.micro else 100_000.0

        if args.micro:
            # Micro growth: couple bootstrapping, slow organic growth over 4 years
            schedule = build_micro_growth_schedule(
                num_founders=args.founders,
                founder_lump=founder_lump,
                founder_monthly=founder_monthly,
                regular_monthly=args.monthly,
            )
            results = run_growth_simulation(schedule, instruments, months=args.months)
            print_micro_growth_report(schedule, instruments, results, args.months)
        else:
            schedule = build_growth_schedule(
                num_founders=args.founders,
                founder_lump=founder_lump,
                founder_monthly=founder_monthly,
                regular_monthly=args.monthly,
            )
            results = run_growth_simulation(schedule, instruments, months=args.months)
            print_growth_report(schedule, instruments, results, args.months)

        if args.property is not None:
            _print_property_report(args, schedule, results, instruments)

        if args.member_view:
            _print_member_view(args, schedule, instruments, results)

        if args.balance_sheet:
            _print_balance_sheet(args, instruments, schedule=schedule)

        if args.founder_view:
            _print_founder_view(args, schedule, instruments)

        if args.loans:
            pool = instruments[0].pool_value(args.months)
            active = [e.member for e in schedule if e.month <= args.months]
            inst = instruments[0]
            from coopsim.instruments.hybrid_pool import HybridPool as _HP
            hybrid_inst = inst if isinstance(inst, _HP) else None
            print_coop_loan_report(
                pool_value=pool,
                total_members=len(active),
                hybrid_inst=hybrid_inst,
                month=args.months,
                schedule=schedule,
            )

        if args.tiers:
            print_contribution_tiers(months=args.months, pool_return_rate=args.savings_rate, coop_lending_rate=args.coop_rate)
    else:
        members = build_members(
            num_regular=args.members,
            monthly=args.monthly,
            num_whales=args.whales,
            whale_lump=args.whale_amount,
            whale_lump2=args.whale_lump2,
            whale_lump2_month=args.whale_lump2_month,
        )
        results = run_simulation(members, instruments, months=args.months)
        print_comparison(instruments, members, results, args.months)

        if args.member_view:
            from coopsim.instruments.term_life_pool import TermLifePool, premium_for_age
            from coopsim.instruments.hybrid_pool import HybridPool
            tl = next((i for i in instruments if isinstance(i, (TermLifePool, HybridPool))), None)
            term_premium = tl._term_premium if isinstance(tl, HybridPool) else (tl._premium_per_member if tl else 9.10)
            individual_prem = premium_for_age(args.avg_age, args.coverage)

            final = args.months
            inst = instruments[0]
            summary = MemberValueSummary(
                monthly_contribution=args.monthly,
                member_age=args.avg_age,
                term_premium_monthly=term_premium,
                coverage_amount=args.coverage,
                individual_premium=individual_prem,
                pool_return_rate=args.savings_rate,
                months=final,
                coop_lending_rate=args.coop_rate,
                total_members=len(members),
                total_death_benefit=inst.total_death_benefit(final) if hasattr(inst, 'total_death_benefit') else 0.0,
                total_borrowing_power=inst.borrowing_power(final),
            )
            print_member_value(summary, loan_amount=args.loan_amount)

            ds = DeathScenario(
                coverage_amount=args.coverage,
                pool_equity=summary.pool_equity_estimate,
                credit_line=summary.credit_line,
                coop_lending_rate=args.coop_rate,
                monthly_contribution=args.monthly,
            )
            print_death_scenario(ds)

        if args.balance_sheet:
            _print_balance_sheet(args, instruments, members=members)

        if args.loans:
            pool = instruments[0].pool_value(args.months)
            print_coop_loan_report(pool_value=pool, total_members=len(members))

        if args.tiers:
            print_contribution_tiers(months=args.months, pool_return_rate=args.savings_rate, coop_lending_rate=args.coop_rate)

        if args.property is not None:
            total_monthly = sum(m.monthly for m in members)
            prop = PropertyConfig(
                purchase_price=args.property,
                down_payment_pct=args.down_pct,
                mortgage_rate=args.mortgage_rate,
                total_units=args.units,
                housing_units=_resolve_housing_units(args),
                rental_units=args.rental_units,
                market_rent=args.market_rent,
            )
            print_property_summary(prop, monthly_contributions=total_monthly if args.lender_view else 0.0)


def _print_member_view(
    args: argparse.Namespace,
    schedule: list,
    instruments: list,
    results: dict[str, list[dict]],
) -> None:
    """Print member value proposition in growth mode."""
    from coopsim.instruments.term_life_pool import TermLifePool, premium_for_age
    from coopsim.instruments.hybrid_pool import HybridPool

    tl = next((i for i in instruments if isinstance(i, (TermLifePool, HybridPool))), None)
    term_premium = tl._term_premium if isinstance(tl, HybridPool) else (tl._premium_per_member if tl else 9.10)
    individual_prem = premium_for_age(args.avg_age, args.coverage)

    final = args.months
    active = [e.member for e in schedule if e.month <= final]
    inst = instruments[0]

    has_db = hasattr(inst, 'total_death_benefit')
    summary = MemberValueSummary(
        monthly_contribution=args.monthly,
        member_age=args.avg_age,
        term_premium_monthly=term_premium,
        coverage_amount=args.coverage,
        individual_premium=individual_prem,
        pool_return_rate=args.savings_rate,
        months=final,
        coop_lending_rate=args.coop_rate,
        total_members=len(active),
        total_death_benefit=inst.total_death_benefit(final) if has_db else 0.0,
        total_borrowing_power=inst.borrowing_power(final),
    )
    print_member_value(summary, loan_amount=args.loan_amount)

    # Always show death scenario with member view — people need to see this
    ds = DeathScenario(
        coverage_amount=args.coverage,
        pool_equity=summary.pool_equity_estimate,
        credit_line=summary.credit_line,
        coop_lending_rate=args.coop_rate,
        monthly_contribution=args.monthly,
    )
    print_death_scenario(ds)


def _print_property_report(
    args: argparse.Namespace,
    schedule: list,
    results: dict[str, list[dict]],
    instruments: list,
) -> None:
    """Print property report in growth mode."""
    # Use final month data for member contributions
    final_month = args.months
    active_members = [e.member for e in schedule if e.month <= final_month]
    total_monthly = sum(m.monthly for m in active_members)

    prop = PropertyConfig(
        purchase_price=args.property,
        down_payment_pct=args.down_pct,
        mortgage_rate=args.mortgage_rate,
        total_units=args.units,
        housing_units=_resolve_housing_units(args),
        rental_units=args.rental_units,
        market_rent=args.market_rent,
    )
    print_property_summary(prop, monthly_contributions=total_monthly if args.lender_view else 0.0)


def _print_founder_view(
    args: argparse.Namespace,
    schedule: list,
    instruments: list,
) -> None:
    """Print founder equity breakdown report."""
    from coopsim.instruments.hybrid_pool import HybridPool

    inst = next((i for i in instruments if isinstance(i, HybridPool)), None)
    if inst is None:
        print("\n  Founder equity view requires hybrid instrument.")
        return

    founders = [e.member for e in schedule if e.member.name.startswith("founder") or e.member.name.startswith("whale")]
    regulars = [e.member for e in schedule if not (e.member.name.startswith("founder") or e.member.name.startswith("whale"))]

    print_founder_equity_report(
        inst=inst,
        founders=founders,
        regulars=regulars,
        months=args.months,
        coop_lending_rate=args.coop_rate,
    )

    # Show housing vs non-housing member comparison
    print_member_comparison(
        inst=inst,
        months=args.months,
        market_rent=args.market_rent,
    )


def _print_balance_sheet(
    args: argparse.Namespace,
    instruments: list,
    schedule: list | None = None,
    members: list | None = None,
) -> None:
    """Print cooperative balance sheet with credit tiers."""
    from coopsim.instruments.term_life_pool import TermLifePool
    from coopsim.instruments.whole_life_pool import WholeLifePool
    from coopsim.instruments.hybrid_pool import HybridPool

    final = args.months
    inst = instruments[0]

    has_db = isinstance(inst, (TermLifePool, WholeLifePool, HybridPool))

    if schedule:
        n_members = len([e for e in schedule if e.month <= final])
    elif members:
        n_members = len(members)
    else:
        n_members = 52

    bs = CoopBalanceSheet(
        pool_value=inst.pool_value(final),
        total_death_benefit=inst.total_death_benefit(final) if has_db else 0.0,
        total_members=n_members,
    )
    print_balance_sheet(bs)
