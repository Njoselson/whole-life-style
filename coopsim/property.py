"""Housing cooperative property model.

Models a cooperative that buys brownstones for members to live in together.
No landlord role — members pay carrying charges that cover costs.

- Purchase price, down payment, mortgage terms
- All units are member housing (no market-rate rental by default)
- Carrying charges = mortgage + taxes + insurance + maintenance, split per unit
- Net cashflow is ~$0 by design (the coop isn't a profit center, it's a cost center)
- Value proposition: members pay $700/mo carrying charge instead of $2,500/mo rent
- DSCR for lenders: carrying charges + pool contributions backing the mortgage

Multi-property: the cooperative can acquire multiple brownstones over time.
Each property is modeled independently. The pool + death benefit collateral
backs all of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PropertyConfig:
    purchase_price: float = 500_000.0
    down_payment_pct: float = 0.20
    mortgage_rate: float = 0.05
    mortgage_years: int = 30
    total_units: int = 4
    housing_units: int = 4   # default: all units are member housing
    rental_units: int = 0    # default: no market-rate rental
    market_rent: float = 2_500.0  # what members WOULD pay on the open market
    monthly_taxes: float = 500.0
    monthly_insurance: float = 200.0
    monthly_maintenance: float = 300.0
    monthly_management: float = 200.0

    @property
    def down_payment(self) -> float:
        return self.purchase_price * self.down_payment_pct

    @property
    def loan_amount(self) -> float:
        return self.purchase_price - self.down_payment

    @property
    def monthly_mortgage(self) -> float:
        """Monthly mortgage payment (P&I) using standard amortization formula."""
        r = self.mortgage_rate / 12
        n = self.mortgage_years * 12
        if r == 0:
            return self.loan_amount / n
        return self.loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    @property
    def monthly_operating_expenses(self) -> float:
        return (
            self.monthly_taxes
            + self.monthly_insurance
            + self.monthly_maintenance
            + self.monthly_management
        )

    @property
    def total_monthly_cost(self) -> float:
        return self.monthly_mortgage + self.monthly_operating_expenses

    @property
    def carrying_charge(self) -> float:
        """Monthly carrying charge per housing member unit.

        This is the cost to live in the cooperative. It covers your share
        of mortgage, taxes, insurance, and maintenance. Not rent — you're
        an owner, not a tenant.
        """
        if self.housing_units == 0:
            return 0.0
        # Carrying charges cover costs for housing units only.
        # If there are rental units, their income offsets the total cost first.
        net_cost = self.total_monthly_cost - self.rental_income
        return max(0.0, net_cost / self.housing_units)

    @property
    def rental_income(self) -> float:
        """Monthly rental income from non-member units (if any)."""
        return self.rental_units * self.market_rent

    @property
    def housing_income(self) -> float:
        """Monthly income from housing member carrying charges."""
        return self.housing_units * self.carrying_charge

    @property
    def total_income(self) -> float:
        return self.rental_income + self.housing_income

    @property
    def net_operating_income(self) -> float:
        """Monthly NOI = total income - operating expenses."""
        return self.total_income - self.monthly_operating_expenses

    @property
    def monthly_net_cashflow(self) -> float:
        """Monthly net after all expenses including mortgage.

        For an all-housing cooperative, this is ~$0 by design.
        Carrying charges are set to exactly cover costs.
        """
        return self.total_income - self.total_monthly_cost

    @property
    def annual_net_cashflow(self) -> float:
        return self.monthly_net_cashflow * 12

    @property
    def dscr_traditional(self) -> float:
        """Traditional DSCR = annual NOI / annual debt service."""
        annual_debt = self.monthly_mortgage * 12
        if annual_debt == 0:
            return float("inf")
        annual_noi = self.net_operating_income * 12
        return annual_noi / annual_debt

    def dscr_adjusted(self, monthly_member_contributions: float) -> float:
        """Adjusted DSCR = (NOI + member contributions) / annual debt service.

        For cooperative structures where member pool contributions
        provide additional debt service coverage beyond carrying charges.
        """
        annual_debt = self.monthly_mortgage * 12
        if annual_debt == 0:
            return float("inf")
        annual_noi = self.net_operating_income * 12
        annual_contributions = monthly_member_contributions * 12
        return (annual_noi + annual_contributions) / annual_debt

    @property
    def savings_vs_market(self) -> float:
        """Monthly savings for a housing member vs market rent."""
        return self.market_rent - self.carrying_charge

    @property
    def share_purchase(self) -> float:
        """Cost for a housing member to buy into a unit (share of down payment)."""
        if self.total_units == 0:
            return 0.0
        return self.down_payment / self.total_units

    @property
    def annual_savings_vs_market(self) -> float:
        """Annual savings per housing member vs renting."""
        return self.savings_vs_market * 12

    def equity_at_year(self, year: int) -> float:
        """Rough estimate of mortgage principal paid down after N years.

        This is the cooperative's equity in the property from mortgage payments.
        Members own this collectively through their housing shares.
        """
        r = self.mortgage_rate / 12
        n = self.mortgage_years * 12
        months_paid = year * 12
        if r == 0:
            return self.monthly_mortgage * months_paid

        # Remaining balance after months_paid
        remaining = self.loan_amount * ((1 + r) ** n - (1 + r) ** months_paid) / ((1 + r) ** n - 1)
        principal_paid = self.loan_amount - remaining
        return principal_paid


def print_property_summary(config: PropertyConfig, monthly_contributions: float = 0.0) -> None:
    """Print a summary of property financials."""
    is_all_housing = config.rental_units == 0

    print()
    print("=" * 70)
    if is_all_housing:
        print("HOUSING COOPERATIVE — BROWNSTONE MODEL")
        print("Members live here. No landlord. Everyone pays their share.")
    else:
        print("PROPERTY ACQUISITION — MIXED USE MODEL")
    print("=" * 70)

    print(f"\n--- Purchase ---")
    print(f"  Purchase Price:    ${config.purchase_price:>12,.0f}")
    print(f"  Down Payment:      ${config.down_payment:>12,.0f} ({config.down_payment_pct:.0%})")
    print(f"  Loan Amount:       ${config.loan_amount:>12,.0f}")
    print(f"  Mortgage Rate:     {config.mortgage_rate:.2%} / {config.mortgage_years} years")
    print(f"  Monthly Mortgage:  ${config.monthly_mortgage:>12,.2f}")

    print(f"\n--- Unit Mix ---")
    print(f"  Total Units:       {config.total_units}")
    print(f"  Member Housing:    {config.housing_units} units @ ${config.carrying_charge:,.2f}/mo carrying charge")
    if config.rental_units > 0:
        print(f"  Rental Units:      {config.rental_units} units @ ${config.market_rent:,.2f}/mo market rent")

    print(f"\n--- Monthly Costs ---")
    print(f"  Mortgage (P&I):    ${config.monthly_mortgage:>12,.2f}")
    print(f"  Taxes:             ${config.monthly_taxes:>12,.2f}")
    print(f"  Insurance:         ${config.monthly_insurance:>12,.2f}")
    print(f"  Maintenance:       ${config.monthly_maintenance:>12,.2f}")
    print(f"  Management:        ${config.monthly_management:>12,.2f}")
    print(f"  Total:             ${config.total_monthly_cost:>12,.2f}")

    if is_all_housing:
        print(f"\n--- How Costs Are Covered ---")
        print(f"  {config.housing_units} members × ${config.carrying_charge:,.2f}/mo = ${config.housing_income:,.2f}/mo")
        print(f"  Carrying charges cover 100% of costs. Net cashflow: ${config.monthly_net_cashflow:,.2f}/mo")
    else:
        print(f"\n--- Monthly Revenue ---")
        print(f"  Housing Income:    ${config.housing_income:>12,.2f}")
        print(f"  Rental Income:     ${config.rental_income:>12,.2f}")
        print(f"  Total Income:      ${config.total_income:>12,.2f}")
        print(f"\n--- Net Cashflow ---")
        print(f"  Monthly Net:       ${config.monthly_net_cashflow:>12,.2f}")
        print(f"  Annual Net:        ${config.annual_net_cashflow:>12,.2f}")

    if monthly_contributions > 0:
        print(f"\n--- Lender Metrics ---")
        print(f"  Traditional DSCR:  {config.dscr_traditional:>12.2f}")
        print(f"  Adjusted DSCR:     {config.dscr_adjusted(monthly_contributions):>12.2f}")
        print(f"    (includes ${monthly_contributions:,.2f}/mo member contributions from pool)")
        if is_all_housing:
            print(f"\n  Why lenders should approve this:")
            print(f"    1. Death benefit collateral backing the loan (via collateral assignment)")
            print(f"    2. Carrying charges are a binding member obligation")
            print(f"    3. Pool contributions provide additional debt service coverage")
            print(f"    4. Members have skin in the game (share purchase + monthly)")
            print(f"    5. Pool cash available as additional reserve")
    else:
        print(f"\n--- Lender Metrics ---")
        print(f"  Traditional DSCR:  {config.dscr_traditional:>12.2f}")
        print(f"  (use --lender-view to include pool contributions in DSCR)")

    print(f"\n--- What Members Pay vs. Renting ---")
    print(f"  Carrying Charge:   ${config.carrying_charge:>12,.2f}/mo (you're an owner, not a tenant)")
    print(f"  Market Rent:       ${config.market_rent:>12,.2f}/mo (what you'd pay a landlord)")
    print(f"  Monthly Savings:   ${config.savings_vs_market:>12,.2f}/mo")
    print(f"  Annual Savings:    ${config.annual_savings_vs_market:>12,.2f}/yr")
    print(f"  Share Purchase:    ${config.share_purchase:>12,.2f} (your buy-in for the unit)")

    # Equity buildup over time
    print(f"\n--- Your Equity Grows (Mortgage Gets Paid Down) ---")
    per_unit_equity_label = f"Per-unit share (1/{config.total_units})"
    for year in [5, 10, 15, 20, 30]:
        if year <= config.mortgage_years:
            eq = config.equity_at_year(year)
            per_unit = eq / config.total_units if config.total_units > 0 else 0
            print(f"  Year {year:>2}: ${eq:>10,.0f} cooperative equity | ${per_unit:>10,.0f} {per_unit_equity_label}")

    if is_all_housing:
        total_savings_10yr = config.savings_vs_market * 120
        eq_10 = config.equity_at_year(10)
        per_unit_10 = eq_10 / config.total_units if config.total_units > 0 else 0
        print(f"\n--- The Real Math (10 Years) ---")
        print(f"  Rent savings:      ${total_savings_10yr:>10,.0f} (money you kept)")
        print(f"  Property equity:   ${per_unit_10:>10,.0f} (your share of the building)")
        print(f"  Total wealth:      ${total_savings_10yr + per_unit_10:>10,.0f}")
        print(f"  What renting gets: $0")

    print()
    print("=" * 70)
