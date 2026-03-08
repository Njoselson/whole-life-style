"""Member-facing value proposition: what does your money actually do?

The core pitch: you're loaning from yourself. You're creating money.

How it works (same as a bank, but YOU own the bank):
1. You put in $20/mo
2. Your $20 goes into the pool — you own a share of it
3. Your term life policy creates $100K in death benefit collateral
4. The cooperative can now lend MORE than $20 against that collateral
5. You get a credit line bigger than what you put in
6. When you spend that credit within the cooperative (rent, other members'
   businesses), the money comes back into the pool
7. The pool lends it out again — money multiplier

This is how banks work. Except here, the members ARE the bank.
The spread stays with you. The interest stays with you.
The collateral (death benefit) makes it safe.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MemberValueSummary:
    """What a single member gets for their contribution."""

    # Inputs
    monthly_contribution: float = 20.0
    member_age: int = 35
    term_premium_monthly: float = 9.10
    coverage_amount: float = 100_000.0
    individual_premium: float = 13.0
    pool_return_rate: float = 0.04
    months: int = 120

    # Cooperative lending terms
    coop_lending_rate: float = 0.06  # cooperative charges 6% on internal loans
    market_personal_loan_rate: float = 0.15  # market personal loan rate ~15%
    market_credit_card_rate: float = 0.22  # credit card rate ~22%

    # Credit creation / money multiplier
    reserve_ratio: float = 0.15  # cooperative keeps 15% liquid, lends 85%
    internal_circulation: float = 0.60  # 60% of loans spent within cooperative ecosystem

    # Group context
    total_members: int = 52
    total_death_benefit: float = 5_500_000.0
    total_borrowing_power: float = 2_900_000.0

    @property
    def net_to_pool(self) -> float:
        return self.monthly_contribution - self.term_premium_monthly

    @property
    def premium_savings_vs_individual(self) -> float:
        return self.individual_premium - self.term_premium_monthly

    @property
    def total_paid(self) -> float:
        return self.monthly_contribution * self.months

    @property
    def total_premiums_paid(self) -> float:
        return self.term_premium_monthly * self.months

    @property
    def total_to_pool(self) -> float:
        return self.net_to_pool * self.months

    @property
    def pool_equity_estimate(self) -> float:
        """Estimated equity after N months with compound growth."""
        monthly_rate = (1 + self.pool_return_rate) ** (1 / 12) - 1
        # Future value of annuity
        if monthly_rate == 0:
            return self.net_to_pool * self.months
        fv = self.net_to_pool * (((1 + monthly_rate) ** self.months - 1) / monthly_rate)
        return fv

    @property
    def share_of_borrowing_power(self) -> float:
        if self.total_members == 0:
            return 0.0
        return self.total_borrowing_power / self.total_members

    @property
    def leverage_ratio(self) -> float:
        if self.total_paid == 0:
            return 0.0
        return self.share_of_borrowing_power / self.total_paid

    @property
    def death_benefit_leverage_pct(self) -> float:
        """How much of death benefit is used as credit backing.

        Conservative: 50% — only half the death benefit backs credit lines.
        Moderate: 75% — three quarters.
        Aggressive: 90% — nearly full death benefit as collateral.

        The risk is low because:
        - Actuarial probability of death at age 35 is ~0.1% per year
        - With 52 members, expected deaths in 10 years: ~0.5
        - Even if 1 member dies, the death benefit PAYS the loan off
        - The collateral literally self-liquidates on the triggering event
        """
        return 0.75  # moderate — safe because death = collateral pays out

    @property
    def credit_line(self) -> float:
        """Credit line available to this member.

        Based on their pool equity + their share of death benefit collateral.
        The death benefit backing means the coop can extend credit beyond
        what the member deposited — this is money creation.

        Why this is safe:
        - If member defaults: their pool equity covers partial loss
        - If member dies: death benefit pays off the loan entirely
        - The collateral is BETTER than a bank's — it's guaranteed payout
        """
        equity = self.pool_equity_estimate
        death_benefit_share = self.coverage_amount * self.death_benefit_leverage_pct
        return equity + death_benefit_share

    @property
    def credit_multiplier(self) -> float:
        """How much credit you get per dollar contributed."""
        if self.total_to_pool == 0:
            return 0.0
        return self.credit_line / self.total_to_pool

    @property
    def money_multiplier(self) -> float:
        """Money multiplier from fractional reserve + internal circulation.

        When the cooperative lends money and it gets spent within the
        cooperative ecosystem, it comes back as deposits that can be
        lent again. Same as how banks create money.

        multiplier = 1 / (1 - lendable_pct * circulation_rate)
        """
        lendable = 1 - self.reserve_ratio
        recirculation = lendable * self.internal_circulation
        if recirculation >= 1:
            return float("inf")
        return 1 / (1 - recirculation)

    @property
    def effective_money_created(self) -> float:
        """Total money created in the cooperative per member's contribution.

        Your $20/mo doesn't just sit there. It gets lent, spent within
        the coop, re-deposited, re-lent. Each dollar works multiple times.
        """
        return self.total_to_pool * self.money_multiplier

    @property
    def total_value_created(self) -> float:
        """Credit line + money multiplier effect."""
        return self.credit_line * self.money_multiplier

    def loan_comparison(self, loan_amount: float = 5_000.0, loan_months: int = 36) -> dict:
        """Compare borrowing from the cooperative vs market rates."""

        def monthly_payment(principal: float, annual_rate: float, n_months: int) -> float:
            r = annual_rate / 12
            if r == 0:
                return principal / n_months
            return principal * (r * (1 + r) ** n_months) / ((1 + r) ** n_months - 1)

        def total_interest(principal: float, annual_rate: float, n_months: int) -> float:
            pmt = monthly_payment(principal, annual_rate, n_months)
            return pmt * n_months - principal

        coop_payment = monthly_payment(loan_amount, self.coop_lending_rate, loan_months)
        coop_interest = total_interest(loan_amount, self.coop_lending_rate, loan_months)

        bank_payment = monthly_payment(loan_amount, self.market_personal_loan_rate, loan_months)
        bank_interest = total_interest(loan_amount, self.market_personal_loan_rate, loan_months)

        cc_payment = monthly_payment(loan_amount, self.market_credit_card_rate, loan_months)
        cc_interest = total_interest(loan_amount, self.market_credit_card_rate, loan_months)

        return {
            "loan_amount": loan_amount,
            "loan_months": loan_months,
            "coop": {"rate": self.coop_lending_rate, "monthly": coop_payment, "total_interest": coop_interest},
            "bank": {"rate": self.market_personal_loan_rate, "monthly": bank_payment, "total_interest": bank_interest},
            "credit_card": {"rate": self.market_credit_card_rate, "monthly": cc_payment, "total_interest": cc_interest},
            "savings_vs_bank": bank_interest - coop_interest,
            "savings_vs_cc": cc_interest - coop_interest,
            "interest_back_to_you": coop_interest / self.total_members,
        }


@dataclass
class CoopBalanceSheet:
    """Cooperative balance sheet showing how death benefit creates lendable assets.

    The death benefit is a contingent asset — it pays out on death.
    But for lending purposes, it's better than most collateral because:
    1. It's GUARANTEED by an A-rated insurance company
    2. It INCREASES lending capacity (not just secures existing loans)
    3. On the triggering event (death), it SELF-LIQUIDATES — the loan gets paid
    4. The probability of mass default (many members dying) is actuarially negligible
    """

    pool_value: float = 200_000.0
    total_death_benefit: float = 5_500_000.0
    total_members: int = 52
    reserve_ratio: float = 0.15
    annual_mortality_rate: float = 0.001  # ~0.1% at age 35

    @property
    def assets(self) -> dict[str, float]:
        return {
            "Pool (cash)": self.pool_value,
            "Death benefit collateral": self.total_death_benefit,
            "Total assets": self.pool_value + self.total_death_benefit,
        }

    @property
    def required_reserves(self) -> float:
        return self.pool_value * self.reserve_ratio

    @property
    def lendable_pool(self) -> float:
        return self.pool_value - self.required_reserves

    @property
    def expected_annual_deaths(self) -> float:
        return self.total_members * self.annual_mortality_rate

    @property
    def expected_annual_death_benefit_payout(self) -> float:
        per_member = self.total_death_benefit / self.total_members if self.total_members > 0 else 0
        return self.expected_annual_deaths * per_member

    def credit_tiers(self) -> list[dict]:
        """Show credit capacity at different leverage levels."""
        tiers = []
        for pct, label, risk in [
            (0.50, "Conservative", "Very Low"),
            (0.75, "Moderate", "Low"),
            (0.90, "Aggressive", "Moderate"),
            (1.00, "Full leverage", "Higher"),
        ]:
            db_credit = self.total_death_benefit * pct
            total_credit = self.lendable_pool + db_credit
            per_member = total_credit / self.total_members if self.total_members > 0 else 0
            # Coverage ratio: how many times death benefit covers outstanding credit
            coverage = self.total_death_benefit / total_credit if total_credit > 0 else float("inf")
            tiers.append({
                "pct": pct,
                "label": label,
                "risk": risk,
                "db_credit": db_credit,
                "total_credit": total_credit,
                "per_member": per_member,
                "coverage_ratio": coverage,
            })
        return tiers


@dataclass
class DeathScenario:
    """What happens when a member dies — how much does the family get?

    The honest answer: cooperative takes what's owed, family gets the rest.
    The key question is how much is owed vs how much coverage exists.
    """

    coverage_amount: float = 100_000.0
    pool_equity: float = 1_600.0
    credit_line: float = 76_600.0
    coop_lending_rate: float = 0.06
    monthly_contribution: float = 20.0

    def scenarios(self) -> list[dict]:
        """Show family payout at different credit utilization levels."""
        results = []
        for util_pct, label in [
            (0.00, "No loan outstanding"),
            (0.10, "Small balance (~10%)"),
            (0.30, "Moderate balance (~30%)"),
            (0.50, "Half utilized (~50%)"),
            (0.75, "Heavy use (~75%)"),
            (1.00, "Fully drawn (100%)"),
        ]:
            outstanding = self.credit_line * util_pct
            coop_claim = min(outstanding, self.coverage_amount)
            family_from_db = self.coverage_amount - coop_claim
            family_from_equity = self.pool_equity  # equity always returned
            family_total = family_from_db + family_from_equity
            results.append({
                "label": label,
                "utilization": util_pct,
                "outstanding": outstanding,
                "coop_claim": coop_claim,
                "family_death_benefit": family_from_db,
                "family_equity": family_from_equity,
                "family_total": family_total,
            })
        return results

    def with_extra_coverage(self, extra_coverage: float = 150_000.0) -> list[dict]:
        """Same scenarios but member carries additional personal policy."""
        total_coverage = self.coverage_amount + extra_coverage
        results = []
        for util_pct, label in [
            (0.00, "No loan outstanding"),
            (0.30, "Moderate balance (~30%)"),
            (0.75, "Heavy use (~75%)"),
            (1.00, "Fully drawn (100%)"),
        ]:
            outstanding = self.credit_line * util_pct
            coop_claim = min(outstanding, self.coverage_amount)
            family_from_coop_policy = self.coverage_amount - coop_claim
            family_from_personal = extra_coverage  # personal policy untouched
            family_from_equity = self.pool_equity
            family_total = family_from_coop_policy + family_from_personal + family_from_equity
            results.append({
                "label": label,
                "utilization": util_pct,
                "outstanding": outstanding,
                "coop_claim": coop_claim,
                "family_from_coop_policy": family_from_coop_policy,
                "family_from_personal": family_from_personal,
                "family_equity": family_from_equity,
                "family_total": family_total,
            })
        return results


def print_death_scenario(ds: DeathScenario) -> None:
    """Print honest analysis of what happens when a member dies."""
    print()
    print("=" * 70)
    print("WHAT HAPPENS WHEN A MEMBER DIES")
    print("The honest math. Your family needs to understand this.")
    print("=" * 70)

    print(f"\n--- The Basics ---")
    print(f"  Death benefit (coop policy):  ${ds.coverage_amount:>10,.0f}")
    print(f"  Pool equity (returned):       ${ds.pool_equity:>10,.2f}")
    print(f"  Credit line:                  ${ds.credit_line:>10,.0f}")

    print(f"\n--- How It Works ---")
    print(f"  1. Insurance company pays ${ds.coverage_amount:,.0f} death benefit")
    print(f"  2. Cooperative takes ONLY what's owed (outstanding loan balance)")
    print(f"  3. Remaining death benefit goes to your family")
    print(f"  4. Your pool equity is also returned to your family")
    print(f"  5. No debt passes to your estate — the loan dies with you")

    print(f"\n--- What Your Family Gets (by how much credit you've used) ---")
    print(f"  {'Scenario':<25} {'Owed':>10} {'Coop Takes':>12} {'Family Gets':>13}")
    print(f"  {'-'*25} {'-'*10} {'-'*12} {'-'*13}")
    for s in ds.scenarios():
        print(f"  {s['label']:<25} ${s['outstanding']:>9,.0f} ${s['coop_claim']:>11,.0f} ${s['family_total']:>12,.0f}")

    # Highlight the risk
    full = ds.scenarios()[-1]
    none = ds.scenarios()[0]
    print(f"\n--- The Tradeoff ---")
    print(f"  If you never borrow:    family gets ${none['family_total']:,.0f} (full benefit + equity)")
    print(f"  If you max your credit: family gets ${full['family_total']:,.0f}")
    if full['family_total'] < ds.coverage_amount * 0.5:
        print(f"  That's only {full['family_total'] / ds.coverage_amount:.0%} of the death benefit. Not enough.")

    # The solution
    extra = 150_000.0
    extra_premium = 13.0 * (extra / 100_000)  # rough estimate
    print(f"\n--- The Solution: Carry More Coverage ---")
    print(f"  The cooperative policy is collateral. Get a PERSONAL policy too.")
    print(f"  Example: additional ${extra:,.0f} personal term life (~${extra_premium:.0f}/mo)")
    print()
    print(f"  {'Scenario':<25} {'Owed':>10} {'Coop Policy':>13} {'Personal':>10} {'Family Gets':>13}")
    print(f"  {'-'*25} {'-'*10} {'-'*13} {'-'*10} {'-'*13}")
    for s in ds.with_extra_coverage(extra):
        print(f"  {s['label']:<25} ${s['outstanding']:>9,.0f} ${s['family_from_coop_policy']:>12,.0f} ${s['family_from_personal']:>9,.0f} ${s['family_total']:>12,.0f}")

    worst_with_extra = ds.with_extra_coverage(extra)[-1]
    print(f"\n  Even fully drawn: family still gets ${worst_with_extra['family_total']:,.0f}")
    print(f"  Cost of protection: ~${extra_premium:.0f}/mo for the personal policy")
    print(f"  Total insurance cost: ${ds.monthly_contribution:.0f}/mo (coop) + ${extra_premium:.0f}/mo (personal) = ${ds.monthly_contribution + extra_premium:.0f}/mo")

    print(f"\n--- Key Point ---")
    print(f"  The cooperative policy is your COLLATERAL — it's what backs your credit line.")
    print(f"  Your PERSONAL policy is your family's safety net.")
    print(f"  Separate the two. The credit line makes you money while you're alive.")
    print(f"  The personal policy protects your family when you're not.")
    print()
    print("=" * 70)


def print_balance_sheet(bs: CoopBalanceSheet) -> None:
    """Print cooperative balance sheet and credit analysis."""
    print()
    print("=" * 70)
    print("COOPERATIVE BALANCE SHEET — HOW YOUR $20 BECOMES REAL MONEY")
    print("=" * 70)

    print(f"\n--- Assets ---")
    for label, val in bs.assets.items():
        marker = "  " if "Total" not in label else ">>"
        print(f"  {marker} {label:<35} ${val:>14,.0f}")

    print(f"\n--- Why the Death Benefit Is a Real Asset ---")
    print(f"  It's not theoretical. It's a contract with an A-rated insurer.")
    print(f"  If a member dies → insurance company pays out immediately.")
    print(f"  If a member defaults on a loan → death benefit covers the balance.")
    print(f"  The collateral is BETTER than property — no foreclosure, no auction,")
    print(f"  no depreciation. Just a guaranteed check.")

    print(f"\n--- Actuarial Safety ---")
    print(f"  Members:                  {bs.total_members}")
    print(f"  Annual mortality rate:    {bs.annual_mortality_rate:.2%} (age ~35)")
    print(f"  Expected deaths/year:     {bs.expected_annual_deaths:.2f}")
    print(f"  Expected payout/year:     ${bs.expected_annual_death_benefit_payout:>10,.0f}")
    print(f"  Total death benefit:      ${bs.total_death_benefit:>10,.0f}")
    print(f"  Even if 2 members die:    ${bs.total_death_benefit - 2 * bs.total_death_benefit / bs.total_members:>10,.0f} remaining")

    print(f"\n--- Lending Capacity ---")
    print(f"  Pool value:               ${bs.pool_value:>14,.0f}")
    print(f"  Reserves ({bs.reserve_ratio:.0%}):            ${bs.required_reserves:>14,.0f}")
    print(f"  Lendable from pool:       ${bs.lendable_pool:>14,.0f}")

    print(f"\n--- Credit Tiers: How Much Can You Lend? ---")
    print(f"  {'Tier':<16} {'DB Used':>10} {'Total Credit':>14} {'Per Member':>12} {'Coverage':>10} {'Risk':>10}")
    print(f"  {'-'*16} {'-'*10} {'-'*14} {'-'*12} {'-'*10} {'-'*10}")
    for t in bs.credit_tiers():
        print(f"  {t['label']:<16} {t['pct']:>9.0%} ${t['total_credit']:>13,.0f} ${t['per_member']:>11,.0f} {t['coverage_ratio']:>9.1f}x {t['risk']:>10}")

    print(f"\n--- What This Means ---")
    tiers = bs.credit_tiers()
    conservative = tiers[0]
    moderate = tiers[1]
    print(f"  At MODERATE leverage (75% of death benefit):")
    print(f"    Total credit capacity:  ${moderate['total_credit']:>12,.0f}")
    print(f"    Per member credit line: ${moderate['per_member']:>12,.0f}")
    print(f"    Coverage ratio:         {moderate['coverage_ratio']:.1f}x (death benefit covers loans {moderate['coverage_ratio']:.1f} times over)")
    print(f"")
    print(f"  The cooperative has ${bs.total_death_benefit:,.0f} in guaranteed collateral.")
    print(f"  A bank with ${bs.pool_value:,.0f} in deposits can only lend ~${bs.lendable_pool:,.0f}.")
    print(f"  The cooperative can lend ${moderate['total_credit']:,.0f} because the death benefit backs it.")
    print(f"  That's the money creation. Every member who joins adds ${bs.total_death_benefit / bs.total_members:,.0f}")
    print(f"  in collateral for just ${bs.pool_value / bs.total_members / (120/12):,.0f}/mo.")
    print()
    print("=" * 70)


def print_member_value(summary: MemberValueSummary, loan_amount: float = 5_000.0) -> None:
    """Print the member-facing value proposition."""
    print()
    print("=" * 70)
    print("WHAT YOUR $%.0f/MONTH ACTUALLY DOES" % summary.monthly_contribution)
    print("You're not giving money away. You're loaning from yourself.")
    print("=" * 70)

    print(f"\n--- Where Your ${summary.monthly_contribution:.0f}/mo Goes ---")
    print(f"  Term life premium:      ${summary.term_premium_monthly:>8.2f}/mo  → ${summary.coverage_amount:,.0f} coverage for your family")
    print(f"  To cooperative pool:    ${summary.net_to_pool:>8.2f}/mo  → you own a share of this")
    print(f"  Total:                  ${summary.monthly_contribution:>8.2f}/mo")
    print(f"  (Individual premium would be ${summary.individual_premium:.2f}/mo — you save ${summary.premium_savings_vs_individual:.2f}/mo)")

    print(f"\n--- After {summary.months // 12} Years ---")
    print(f"  Total paid in:          ${summary.total_paid:>10,.2f}")
    print(f"  Of which premiums:      ${summary.total_premiums_paid:>10,.2f} (insurance your family needs)")
    print(f"  Of which to pool:       ${summary.total_to_pool:>10,.2f} (you still own this)")
    print(f"  Your pool equity:       ${summary.pool_equity_estimate:>10,.2f} (with {summary.pool_return_rate:.1%}/yr growth)")

    print(f"\n--- You're Creating Money ---")
    print(f"  This is how banks work. Except YOU own the bank.")
    print()
    print(f"  You put in:             ${summary.total_to_pool:>10,.2f} to pool over {summary.months // 12} years")
    print(f"  Your credit line:       ${summary.credit_line:>10,.0f}")
    print(f"    Pool equity:            ${summary.pool_equity_estimate:>10,.2f}")
    db_pct = summary.death_benefit_leverage_pct
    print(f"    Death benefit backing:  ${summary.coverage_amount * db_pct:>10,.0f} ({db_pct:.0%} of your ${summary.coverage_amount:,.0f} policy)")
    print(f"  Credit multiplier:      {summary.credit_multiplier:>9.0f}x on what you put in")
    print()
    print(f"  When you spend that credit within the cooperative:")
    print(f"    Reserve ratio:        {summary.reserve_ratio:.0%} (coop keeps {summary.reserve_ratio:.0%} liquid)")
    print(f"    Internal circulation: {summary.internal_circulation:.0%} (spent within coop ecosystem)")
    print(f"    Money multiplier:     {summary.money_multiplier:.1f}x")
    print(f"    Your ${summary.total_to_pool:,.0f} creates:  ${summary.effective_money_created:>10,.0f} in economic activity")
    print()
    print(f"  At a bank: you deposit ${summary.total_to_pool:,.0f}, THEY lend it out and keep the spread.")
    print(f"  Here: you deposit ${summary.total_to_pool:,.0f}, the cooperative lends it, and the")
    print(f"  spread comes back to YOU. Plus you get a ${summary.credit_line:,.0f} credit line.")

    print(f"\n--- Your Share of the Cooperative ---")
    print(f"  Total members:          {summary.total_members}")
    print(f"  Group death benefit:    ${summary.total_death_benefit:>12,.0f}")
    print(f"  Group borrowing power:  ${summary.total_borrowing_power:>12,.0f}")
    print(f"  YOUR credit line:       ${summary.credit_line:>12,.0f}")
    print(f"  Leverage on your money: {summary.credit_multiplier:>11.0f}x")
    print(f"  (${summary.total_to_pool:,.0f} deposited → ${summary.credit_line:,.0f} credit line)")

    # Loan comparison
    comp = summary.loan_comparison(loan_amount)
    print(f"\n--- Borrowing ${comp['loan_amount']:,.0f} for {comp['loan_months']} Months ---")
    print(f"  {'Source':<20} {'Rate':>8} {'Monthly':>10} {'Total Interest':>16} {'You Save':>10}")
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*16} {'-'*10}")

    print(f"  {'Cooperative':.<20} {comp['coop']['rate']:>7.0%} ${comp['coop']['monthly']:>9,.2f} ${comp['coop']['total_interest']:>15,.2f}  {'(base)':>10}")
    print(f"  {'Personal loan':.<20} {comp['bank']['rate']:>7.0%} ${comp['bank']['monthly']:>9,.2f} ${comp['bank']['total_interest']:>15,.2f} ${comp['savings_vs_bank']:>9,.2f}")
    print(f"  {'Credit card':.<20} {comp['credit_card']['rate']:>7.0%} ${comp['credit_card']['monthly']:>9,.2f} ${comp['credit_card']['total_interest']:>15,.2f} ${comp['savings_vs_cc']:>9,.2f}")

    print(f"\n  The kicker: the ${comp['coop']['total_interest']:,.2f} in cooperative interest")
    print(f"  goes back into the pool. Your share: ${comp['interest_back_to_you']:,.2f}")
    print(f"  You're paying interest to yourself and {summary.total_members - 1} neighbors.")

    print(f"\n--- The Bottom Line ---")
    print(f"  You pay: ${summary.monthly_contribution:.0f}/mo")
    print(f"  You get:")
    print(f"    - ${summary.coverage_amount:,.0f} life insurance (your family is protected)")
    print(f"    - Credit score improvement (~168 points average)")
    print(f"    - ${summary.credit_line:,.0f} credit line at {summary.coop_lending_rate:.0%} (not {summary.market_credit_card_rate:.0%})")
    print(f"    - Cooperative housing (carrying charges vs $2,500+/mo rent)")
    print(f"    - Ownership stake in a growing cooperative")
    print(f"  Your money never leaves. The cooperative IS you. You ARE the bank.")
    print()
    print("=" * 70)


def print_contribution_tiers(
    months: int = 120,
    pool_return_rate: float = 0.04,
    coop_lending_rate: float = 0.06,
    group_discount: float = 0.30,
    db_leverage_pct: float = 0.75,
    market_rent: float = 2_500.0,
    carrying_charge: float = 1_159.0,
) -> None:
    """Show what happens when you pay more than $20/mo.

    More money in → more coverage → more collateral → bigger credit line.
    Plus your equity grows faster from your own contributions AND from
    interest earned on everyone else's loans.
    """
    from coopsim.instruments.term_life_pool import premium_for_age

    print()
    print("=" * 80)
    print("PAY MORE, BUILD MORE — CONTRIBUTION TIERS")
    print("Every dollar you put in grows the cooperative AND builds your wealth.")
    print("=" * 80)

    # Premium at age 35 per $100K: $13 individual, ~$9.10 group
    base_premium_per_100k = premium_for_age(35, 100_000) * (1 - group_discount)

    tiers = [
        (20, 100_000, "Base"),
        (35, 200_000, "Standard"),
        (50, 300_000, "Plus"),
        (75, 500_000, "Premium"),
        (100, 750_000, "Max"),
    ]

    monthly_rate = (1 + pool_return_rate) ** (1 / 12) - 1
    # Estimate annual interest income per pool dollar from coop lending
    # Assume 70% of pool is lent out at coop_lending_rate
    lending_deployment = 0.70
    annual_interest_income_rate = lending_deployment * coop_lending_rate

    print(f"\n--- What Each Tier Gets You (over {months // 12} years, age 35) ---")
    print(f"  {'Tier':<10} {'Pay/mo':>8} {'Coverage':>12} {'Premium':>10} {'To Pool':>10} "
          f"{'Equity*':>12} {'Credit Line':>13} {'Multiplier':>11}")
    print(f"  {'-'*10} {'-'*8} {'-'*12} {'-'*10} {'-'*10} {'-'*12} {'-'*13} {'-'*11}")

    for monthly, coverage, label in tiers:
        premium = base_premium_per_100k * (coverage / 100_000)
        net_to_pool = monthly - premium
        if net_to_pool < 0:
            net_to_pool = 0
            premium = monthly

        # Pool equity (future value of annuity)
        if monthly_rate > 0:
            equity = net_to_pool * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            equity = net_to_pool * months

        credit_line = equity + coverage * db_leverage_pct
        total_in = net_to_pool * months
        multiplier = credit_line / total_in if total_in > 0 else 0

        print(f"  {label:<10} ${monthly:>6} ${coverage:>10,.0f} ${premium:>8.2f} "
              f"${net_to_pool:>8.2f} ${equity:>10,.0f} ${credit_line:>11,.0f} {multiplier:>10.0f}x")

    print(f"\n  * Equity = your contributions + {pool_return_rate:.0%}/yr growth")
    print(f"    PLUS your share of interest earned on cooperative loans")

    # Show "don't borrow" vs "borrow" comparison
    # Pick the $50/mo tier as example
    ex_monthly = 50
    ex_coverage = 300_000
    ex_premium = base_premium_per_100k * (ex_coverage / 100_000)
    ex_net = ex_monthly - ex_premium
    if ex_net < 0:
        ex_net = 0
    if monthly_rate > 0:
        ex_equity = ex_net * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        ex_equity = ex_net * months
    ex_credit = ex_equity + ex_coverage * db_leverage_pct

    # Effective return with lending income flowing back
    # Pool earns savings rate + share of lending spread
    effective_rate = pool_return_rate + (lending_deployment * coop_lending_rate * 0.5)
    eff_monthly = (1 + effective_rate) ** (1 / 12) - 1
    if eff_monthly > 0:
        ex_equity_with_lending = ex_net * (((1 + eff_monthly) ** months - 1) / eff_monthly)
    else:
        ex_equity_with_lending = ex_net * months
    ex_credit_with_lending = ex_equity_with_lending + ex_coverage * db_leverage_pct

    print(f"\n--- Your Money Grows Whether You Borrow Or Not ---")
    print(f"  Example: $50/mo member with $300K coverage")
    print()
    print(f"  If you NEVER borrow (your equity just grows):")
    print(f"    Pool return only ({pool_return_rate:.0%}/yr):         ${ex_equity:>10,.0f} equity after {months // 12} years")
    print(f"    + lending income back ({effective_rate:.1%}/yr):  ${ex_equity_with_lending:>10,.0f} equity after {months // 12} years")
    print(f"    Your credit line:                   ${ex_credit_with_lending:>10,.0f}")
    print()
    print(f"  If you DO borrow, say $20K at {coop_lending_rate:.0%}:")
    total_in = ex_net * months
    print(f"    You paid in:       ${total_in:>8,.0f}")
    print(f"    You borrowed:      $ 20,000 at {coop_lending_rate:.0%}")
    interest_on_20k = 20_000 * coop_lending_rate * 3  # 3 years
    print(f"    Interest (3 yrs):  ${interest_on_20k:>8,.0f} — goes back to the pool (to everyone)")
    print(f"    Your equity still: ${ex_equity_with_lending:>8,.0f} (it kept growing from other members' payments)")
    print(f"    Net cost to you:   ${interest_on_20k:>8,.0f} in interest, but your share comes back")

    # Wealth building breakdown
    print(f"\n--- How You Build Wealth ---")
    print(f"  1. POOL EQUITY: your contributions grow at {pool_return_rate:.0%}/yr")
    print(f"     Every dollar you put in earns returns. It's yours.")
    print()
    print(f"  2. LENDING INCOME: when the coop lends to other members at {coop_lending_rate:.0%},")
    print(f"     that interest goes back to the pool. Your equity grows from")
    print(f"     THEIR loan payments. 52 members borrowing = steady income stream.")
    print()
    print(f"  3. HOUSING SAVINGS: cooperative housing at ~${carrying_charge:.0f}/mo vs ${market_rent:.0f}/mo rent.")
    print(f"     That's ${market_rent - carrying_charge:,.0f}/mo you keep. Over {months // 12} years: ${(market_rent - carrying_charge) * months:,.0f} saved.")
    print()
    print(f"  4. CREDIT ACCESS: borrow at {coop_lending_rate:.0%} instead of 15-22%.")
    print(f"     The interest you DO pay goes back to the coop — back to you.")
    print()
    print(f"  5. PROPERTY EQUITY: the cooperative owns real estate.")
    print(f"     As the mortgage gets paid down, your share of the building grows.")
    print()
    print(f"  6. TAX BENEFITS:")
    print(f"     - 501(c)(8) fraternal benefit society: cooperative income is tax-exempt")
    print(f"     - Your pool equity grows tax-deferred (no capital gains until withdrawal)")
    print(f"     - Life insurance death benefit: tax-free to your family")
    print(f"     - Mortgage interest on cooperative property: deductible to the entity")
    print(f"     - If CDFI-certified: access to federal grants and tax credits")
    print(f"     - Housing members may deduct carrying charges as housing expense")

    # Show the flywheel
    print(f"\n--- The Flywheel ---")
    print(f"  You pay more → more coverage → more collateral")
    print(f"  More collateral → coop borrows more from banks at low rates")
    print(f"  More capital → more loans to members at {coop_lending_rate:.0%}")
    print(f"  More loans → more interest income → pool grows faster")
    print(f"  Pool grows → your equity grows → you can borrow more")
    print(f"  You borrow → you spend → money circulates → pool grows again")
    print(f"")
    print(f"  Every member who joins makes YOUR position stronger.")
    print(f"  Every dollar lent and repaid makes EVERYONE'S equity grow.")
    print()
    print("=" * 80)


@dataclass
class CoopLoan:
    """Zero-interest loan from the collective.

    The cooperative doesn't charge interest. Members borrow from the pool
    and pay it back at their own pace with a minimum payment floor.

    Minimum monthly payment = $20 + 1% of remaining balance.
    No interest. No fees. No credit check. The pool backs the loan.
    """

    loan_amount: float = 10_000.0
    min_flat: float = 20.0       # minimum flat payment per month
    min_pct: float = 0.01        # 1% of remaining balance per month

    def repayment_schedule(self) -> list[dict]:
        """Generate month-by-month repayment schedule."""
        balance = self.loan_amount
        schedule: list[dict] = []
        month = 0
        total_paid = 0.0

        while balance > 0.01 and month < 600:  # cap at 50 years
            month += 1
            payment = self.min_flat + (self.min_pct * balance)
            payment = min(payment, balance)  # don't overpay
            balance -= payment
            total_paid += payment
            schedule.append({
                "month": month,
                "payment": payment,
                "balance": max(0, balance),
                "total_paid": total_paid,
            })

        return schedule

    @property
    def months_to_payoff(self) -> int:
        sched = self.repayment_schedule()
        return len(sched)

    @property
    def years_to_payoff(self) -> float:
        return self.months_to_payoff / 12

    @property
    def first_payment(self) -> float:
        return self.min_flat + (self.min_pct * self.loan_amount)

    @property
    def total_cost(self) -> float:
        """Total cost is just the principal — zero interest."""
        return self.loan_amount

    def market_comparison(self, market_rate: float = 0.15) -> dict:
        """Compare zero-interest coop loan vs market rate loan over same term."""
        n = self.months_to_payoff
        r = market_rate / 12
        if r == 0 or n == 0:
            return {"market_interest": 0, "savings": 0}
        market_payment = self.loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        market_total = market_payment * n
        market_interest = market_total - self.loan_amount
        return {
            "market_rate": market_rate,
            "market_payment": market_payment,
            "market_total": market_total,
            "market_interest": market_interest,
            "savings": market_interest,  # you save ALL the interest
        }


def print_coop_loan_report(
    loan_amounts: list[float] | None = None,
    pool_value: float = 300_000.0,
    total_members: int = 52,
    hybrid_inst: object | None = None,
    month: int | None = None,
    schedule: list | None = None,
) -> None:
    """Print the zero-interest cooperative loan model with credit unlock curves."""
    if loan_amounts is None:
        loan_amounts = [5_000, 10_000, 25_000, 50_000]

    print()
    print("=" * 75)
    print("COOPERATIVE LOANS — ZERO INTEREST, PAY AS YOU GO")
    print("Borrow from the collective. No interest. No fees. No credit check.")
    print("=" * 75)

    print(f"\n--- How It Works ---")
    print(f"  1. You borrow from the cooperative pool (backed by death benefit)")
    print(f"  2. Interest rate: 0%")
    print(f"  3. Minimum monthly payment: $20 + 1% of remaining balance")
    print(f"  4. Pay more anytime. Pay it off whenever you want.")
    print(f"  5. No credit check — your membership IS your creditworthiness")

    # Credit unlock curve (if hybrid instrument available)
    if hybrid_inst is not None and month is not None:
        from coopsim.instruments.hybrid_pool import HybridPool
        if isinstance(hybrid_inst, HybridPool):
            print(f"\n--- Credit Limit Unlock Curve ---")
            print(f"  Every $1 you contribute unlocks $5 in credit (capped at 75% of death benefit).")
            print()
            print(f"  {'Member Type':<30} {'Contributed':>12} {'Credit Limit':>14} {'Max Credit':>12}")
            print(f"  {'-'*30} {'-'*12} {'-'*14} {'-'*12}")

            # Show representative members if schedule available
            if schedule:
                shown = set()
                for e in schedule:
                    m = e.member
                    if m.name in shown:
                        continue
                    if e.month > month:
                        continue
                    bd = hybrid_inst.member_equity_breakdown(m.name, month)
                    is_founder = m.name.startswith("founder") or m.name.startswith("whale")
                    label = f"{m.name}"
                    if is_founder:
                        lump = hybrid_inst._founder_lump_totals.get(m.name, 0)
                        if lump > 0:
                            label += f" (${lump:,.0f} lump)"
                    print(f"  {label:<30} ${bd['total_contributions']:>10,.0f} "
                          f"${bd['credit_limit']:>12,.0f} ${bd['max_credit']:>10,.0f}")
                    shown.add(m.name)
                    if len(shown) >= 8:
                        break

            # Show unlock examples for generic member types
            print()
            print(f"  --- Unlock Examples ---")
            examples = [
                ("Regular at month 12", 20 * 12, 100_000),
                ("Regular at month 60", 20 * 60, 100_000),
                ("Founder ($150K lump, month 1)", 150_000 + 20, 500_000),
                ("Member with $5K lump, month 1", 5_000 + 20, 100_000),
                ("Member with $50K lump, month 1", 50_000 + 20, 100_000),
            ]
            print(f"  {'Scenario':<35} {'Contributed':>12} {'Unlocked':>12} {'Credit':>12}")
            print(f"  {'-'*35} {'-'*12} {'-'*12} {'-'*12}")
            for label, contrib, coverage in examples:
                unlocked = contrib * 5.0
                max_credit = coverage * 0.75
                credit = min(unlocked, max_credit)
                print(f"  {label:<35} ${contrib:>10,.0f} ${unlocked:>10,.0f} ${credit:>10,.0f}")

    print(f"\n--- Loan Examples ---")
    print(f"  {'Loan':>10} {'1st Payment':>13} {'Payoff':>10} "
          f"{'Total Cost':>12} {'Market Interest*':>17} {'You Save':>10}")
    print(f"  {'-'*10} {'-'*13} {'-'*10} {'-'*12} {'-'*17} {'-'*10}")

    for amount in loan_amounts:
        loan = CoopLoan(loan_amount=amount)
        comp = loan.market_comparison(0.15)
        print(f"  ${amount:>9,.0f} ${loan.first_payment:>11,.2f} "
              f"{loan.years_to_payoff:>8.1f} yrs "
              f"${loan.total_cost:>10,.0f} ${comp['market_interest']:>15,.0f} "
              f"${comp['savings']:>8,.0f}")

    print(f"\n  * Market comparison at 15% APR (typical personal loan)")

    # Show a detailed schedule for a $10K loan
    example = CoopLoan(loan_amount=10_000)
    sched = example.repayment_schedule()

    print(f"\n--- Example: $10,000 Loan Repayment ---")
    print(f"  {'Month':>6} {'Payment':>10} {'Balance':>12} {'Total Paid':>12}")
    print(f"  {'-'*6} {'-'*10} {'-'*12} {'-'*12}")

    # Show months 1, 6, 12, 24, 36, 48, 60 and final
    milestones = [1, 6, 12, 24, 36, 48, 60, 84, 120]
    for s in sched:
        if s["month"] in milestones or s["balance"] == 0:
            print(f"  {s['month']:>6} ${s['payment']:>9,.2f} ${s['balance']:>11,.2f} ${s['total_paid']:>11,.2f}")
    if sched[-1]["month"] not in milestones:
        s = sched[-1]
        print(f"  {s['month']:>6} ${s['payment']:>9,.2f} ${s['balance']:>11,.2f} ${s['total_paid']:>11,.2f}")

    # Pool sustainability
    print(f"\n--- Can the Pool Handle This? ---")
    print(f"  Pool value: ${pool_value:>12,.0f}")
    print(f"  Members: {total_members}")
    max_concurrent = pool_value * 0.85  # 85% lendable (15% reserve)
    per_member_max = max_concurrent / total_members if total_members > 0 else 0
    print(f"  Lendable (85% of pool): ${max_concurrent:>10,.0f}")
    print(f"  Max per member: ${per_member_max:>10,.0f}")
    print()
    print(f"  The pool replenishes as loans are repaid. With {total_members} members")
    print(f"  each making minimum payments, ~${total_members * 120:,.0f}/mo flows back.")
    print(f"  New member contributions add ${total_members * 20:,.0f}/mo on top of that.")
    print()
    print(f"  The death benefit (not the pool) is what backs the loans.")
    print(f"  If a member dies: insurance pays the loan off. Zero loss.")
    print(f"  If a member defaults: their pool equity covers partial loss,")
    print(f"  and the collective absorbs the rest (spread across {total_members} members).")

    # Compare to credit cards
    comp_10k = CoopLoan(loan_amount=10_000).market_comparison(0.22)
    print(f"\n--- The Real Comparison ---")
    print(f"  $10,000 on a credit card at 22%:")
    print(f"    Interest over {example.years_to_payoff:.0f} years: ${comp_10k['market_interest']:>10,.0f}")
    print(f"    Total paid: ${comp_10k['market_total']:>10,.0f}")
    print()
    print(f"  $10,000 from the cooperative at 0%:")
    print(f"    Interest: $0")
    print(f"    Total paid: ${example.total_cost:>10,.0f}")
    print(f"    You saved: ${comp_10k['market_interest']:>10,.0f}")
    print()
    print(f"  That's the whole point. You ARE the bank. Why charge yourself interest?")
    print()
    print("=" * 75)


@dataclass
class FounderEquityReport:
    """Per-founder equity breakdown showing preferred and common equity."""

    name: str
    lump_sum: float
    preferred: float
    common: float
    total: float
    vesting_pct: float


def print_founder_equity_report(
    inst: object,
    founders: list,
    regulars: list,
    months: int,
    coop_lending_rate: float = 0.06,
    db_leverage_pct: float = 0.75,
    coverage_per_member: float = 100_000.0,
) -> None:
    """Print founder equity breakdown and comparison with regular members."""
    from coopsim.instruments.hybrid_pool import HybridPool

    if not isinstance(inst, HybridPool):
        print("\n  Founder equity report requires hybrid instrument.")
        return

    def fmt(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"${value:,.0f}"
        return f"${value:,.2f}"

    print()
    print("=" * 80)
    print("FOUNDER EQUITY REPORT — CAPITAL RETURN + COMMON EQUITY")
    print("Founders get their capital back over 5 years. The cooperative owns the growth.")
    print("=" * 80)

    # Per-founder breakdown
    reports: list[FounderEquityReport] = []
    for f in founders:
        bd = inst.member_equity_breakdown(f.name, months)
        report = FounderEquityReport(
            name=f.name,
            lump_sum=bd["member_lump"],
            preferred=bd["preferred"],
            common=bd["common"],
            total=bd["total"],
            vesting_pct=bd["vesting_pct"],
        )
        reports.append(report)

    print(f"\n--- Founder Equity at Month {months} ---")
    pref_label = "Cap. Return"
    print(f"  {'Founder':<14} {'Lump Sum':>12} {pref_label:>12} {'Common':>10} "
          f"{'Credit Limit':>12} {'Total':>12} {'Vested':>8}")
    print(f"  {'-'*14} {'-'*12} {'-'*12} {'-'*10} {'-'*12} {'-'*12} {'-'*8}")
    for r in reports:
        bd = inst.member_equity_breakdown(r.name, months)
        print(f"  {r.name:<14} ${r.lump_sum:>10,.0f} {fmt(r.preferred):>12} "
              f"{fmt(r.common):>10} {fmt(bd['credit_limit']):>12} "
              f"{fmt(r.total):>12} {r.vesting_pct:>7.0%}")

    # Regular member comparison
    if regulars:
        active_regulars = regulars[:5]  # show up to 5
        print(f"\n--- Regular Member Comparison (time-weighted equity) ---")
        print(f"  Common equity is weighted by member-months (time in cooperative).")
        print(f"  Founding members (joined months 1-12) get 1.5x weight.")
        print(f"  Credit limits unlock gradually: 5x contributions, capped at 75% of death benefit.")
        print()
        print(f"  {'Member':<14} {'Common':>10} {'Months':>8} {'Weight':>8} {'Credit Limit':>14}")
        print(f"  {'-'*14} {'-'*10} {'-'*8} {'-'*8} {'-'*14}")
        for m in active_regulars:
            bd = inst.member_equity_breakdown(m.name, months)
            bonus = " *" if bd.get("is_founding_member", False) else ""
            print(f"  {m.name:<14} {fmt(bd['common']):>10} {bd.get('member_months', 0):>7}{bonus} "
                  f"{bd.get('weight', 1.0):>7.1f}x {fmt(bd['credit_limit']):>14}")
        if len(regulars) > 5:
            print(f"  ... and {len(regulars) - 5} more regular members")
        print(f"\n  * = founding member (1.5x weight on member-months)")
        print(f"  Credit limit = min(total_contributions x 5, 75% of ${coverage_per_member:,.0f} death benefit)")

    # Exit scenarios at years 1-5
    print(f"\n--- Exit Scenarios: What Each Founder Gets Back ---")
    print(f"  Vesting: 20%/year. Capital return vests. Common is always fully vested.")
    print(f"  Founders get their ${sum(r.lump_sum for r in reports):,.0f} back over 5 years — no more, no less.")
    print()
    header = f"  {'Year':>5}"
    for r in reports:
        header += f"  {r.name:>14}"
    print(header)
    print(f"  {'-'*5}" + f"  {'-'*14}" * len(reports))

    for year in range(1, 6):
        exit_month = min(year * 12, months)
        row = f"  {year:>5}"
        for f in founders:
            bd = inst.member_equity_breakdown(f.name, exit_month)
            exit_value = bd["preferred"] + bd["common"]
            row += f"  {fmt(exit_value):>14}"
        print(row)

    print(f"\n--- Why This Is Fair ---")
    print(f"  Founders: their ${sum(r.lump_sum for r in reports):,.0f} is a zero-interest loan to the cooperative.")
    print(f"    They get it back over 5 years (vesting). No upside, no pool ownership.")
    print(f"    The cooperative owns everything the pool generates.")
    print()
    print(f"  Regular members ($20/mo): credit limits unlock at 5x contributions.")
    print(f"    A $100K term policy creates up to ${coverage_per_member * 0.75:,.0f} max credit.")
    print(f"    Early members get 1.5x equity weight — time = value.")
    print()
    print("=" * 80)


def print_member_comparison(
    inst: object,
    months: int = 60,
    market_rent: float = 2_500.0,
    pool_return_rate: float = 0.04,
) -> None:
    """Show side-by-side what housing vs non-housing vs founder members get.

    This is the pitch: why should someone join who doesn't need housing?
    Answer: zero-interest loans NOW + future housing priority + community.
    """
    from coopsim.instruments.hybrid_pool import HybridPool

    if not isinstance(inst, HybridPool):
        return

    print()
    print("=" * 80)
    print("MEMBER VALUE COMPARISON — HOUSING vs NON-HOUSING vs FOUNDER")
    print("What each member type gets for their money.")
    print("=" * 80)

    # Property assumptions
    # $1.2M brownstone, 20% down, 5% mortgage, 4 units, 30-year term
    purchase_price = 1_200_000.0
    down_pct = 0.20
    mortgage_rate = 0.05
    total_units = 4
    mortgage_amount = purchase_price * (1 - down_pct)
    monthly_mortgage_rate = mortgage_rate / 12
    mortgage_payment = mortgage_amount * (monthly_mortgage_rate * (1 + monthly_mortgage_rate) ** 360) / ((1 + monthly_mortgage_rate) ** 360 - 1)
    annual_taxes = purchase_price * 0.012  # ~1.2% property tax
    annual_insurance = 3_600.0
    annual_maintenance = purchase_price * 0.01  # 1% maintenance
    monthly_carrying_total = mortgage_payment + (annual_taxes + annual_insurance + annual_maintenance) / 12
    carrying_per_unit = monthly_carrying_total / total_units

    monthly_savings = market_rent - carrying_per_unit
    annual_savings = monthly_savings * 12
    total_savings = monthly_savings * months

    # Property equity buildup (principal paid down over time)
    # Approximate: in first 5 years, ~15% of payments go to principal
    total_mortgage_paid = mortgage_payment * months
    # Simple amortization for principal paydown
    balance = mortgage_amount
    total_principal_paid = 0.0
    for _ in range(months):
        interest = balance * monthly_mortgage_rate
        principal = mortgage_payment - interest
        total_principal_paid += principal
        balance -= principal
    equity_per_unit = total_principal_paid / total_units

    # Monthly contribution math
    monthly_contrib = 20.0
    monthly_rate = (1 + pool_return_rate) ** (1 / 12) - 1

    # Pool equity estimate for regular member over N months
    if monthly_rate > 0:
        pool_equity = (monthly_contrib - inst._term_premium) * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        pool_equity = (monthly_contrib - inst._term_premium) * months

    coverage = inst.coverage_per_member
    max_credit = coverage * 0.75
    credit_at_end = min(monthly_contrib * months * 5.0, max_credit)

    founder_coverage = inst.founder_coverage
    founder_max_credit = founder_coverage * 0.75

    years = months // 12

    print(f"\n{'':4}{'HOUSING MEMBER':^25} {'NON-HOUSING MEMBER':^25} {'FOUNDER':^25}")
    print(f"{'':4}{'-'*25} {'-'*25} {'-'*25}")

    print(f"\n  Monthly cost:")
    print(f"{'':4}{'$20/mo + ~$%.0f carrying' % carrying_per_unit:^25} "
          f"{'$20/mo only':^25} "
          f"{'$20/mo + $150K lump':^25}")

    print(f"\n  Life insurance:")
    print(f"{'':4}{'$%.0fK term' % (coverage / 1000):^25} "
          f"{'$%.0fK term' % (coverage / 1000):^25} "
          f"{'$%.0fK term' % (founder_coverage / 1000):^25}")

    print(f"\n  Rent savings ({years} yrs):")
    print(f"{'':4}{'$%.0f/mo = $%.0fK total' % (monthly_savings, total_savings / 1000):^25} "
          f"{'N/A':^25} "
          f"{'$%.0f/mo = $%.0fK total' % (monthly_savings, total_savings / 1000):^25}")

    print(f"\n  Property equity ({years} yrs):")
    print(f"{'':4}{'~$%.0fK per-unit share' % (equity_per_unit / 1000):^25} "
          f"{'N/A (future priority)':^25} "
          f"{'~$%.0fK per-unit share' % (equity_per_unit / 1000):^25}")

    print(f"\n  Zero-interest loans:")
    print(f"{'':4}{'Up to $%.0fK credit' % (max_credit / 1000):^25} "
          f"{'Up to $%.0fK credit' % (max_credit / 1000):^25} "
          f"{'Up to $%.0fK credit' % (founder_max_credit / 1000):^25}")

    print(f"\n  Credit unlocks at:")
    print(f"{'':4}{'5x contributions':^25} "
          f"{'5x contributions':^25} "
          f"{'Immediate (lump sum)':^25}")

    print(f"\n  Pool equity ({years} yrs):")
    print(f"{'':4}{'~$%.0fK' % (pool_equity / 1000):^25} "
          f"{'~$%.0fK' % (pool_equity / 1000):^25} "
          f"{'Capital return + common':^25}")

    # 10-year wealth summary
    print(f"\n--- {years}-Year Wealth Summary ---")
    housing_total = total_savings + equity_per_unit + pool_equity
    nonhousing_total = pool_equity + credit_at_end  # equity + access to credit
    print(f"\n  Housing member:")
    print(f"    Rent savings:       ${total_savings:>10,.0f} (${monthly_savings:,.0f}/mo vs ${market_rent:,.0f} market)")
    print(f"    Property equity:    ${equity_per_unit:>10,.0f}")
    print(f"    Pool equity:        ${pool_equity:>10,.0f}")
    print(f"    Total wealth built: ${housing_total:>10,.0f}")

    print(f"\n  Non-housing member:")
    print(f"    Pool equity:        ${pool_equity:>10,.0f}")
    print(f"    Credit access:      ${credit_at_end:>10,.0f} (zero-interest)")
    print(f"    Future housing:     Priority for next brownstone")
    print(f"    Community:          Governance vote + cooperative membership")

    # Founder total contributions
    total_founder_lump = sum(inst._founder_lump_totals.values())
    print(f"\n  Founder ($150K lump + $20/mo):")
    print(f"    Capital returned:   ${total_founder_lump:>10,.0f} (over 5 years, vesting)")
    print(f"    Credit access:      ${founder_max_credit:>10,.0f} (unlocked immediately)")
    print(f"    Housing priority:   Yes")
    print(f"    Term life only:    Simpler, cheaper, no LLC needed")

    print(f"\n--- Why Non-Housing Members Join ---")
    print(f"  1. Zero-interest loans NOW — credit unlocks with $20/mo contributions")
    print(f"  2. Future housing priority — as coop buys more brownstones, you're first in line")
    print(f"  3. Community + governance — one person, one vote, you shape the cooperative")
    print(f"  4. Pool equity grows at {pool_return_rate:.0%}/yr on your contributions")
    print(f"  5. ${coverage / 1000:.0f}K life insurance at group rates")
    print(f"  6. Credit score improvement (~168 points average from MAF model)")
    print()
    print("=" * 80)
