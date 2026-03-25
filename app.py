"""Cooperative Finance — What You Need to Know.

Three views: what founders put in, what members get, what living here costs.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from coopsim.instruments.hybrid_pool import HybridPool
from coopsim.instruments.term_life_pool import premium_for_age
from coopsim.growth import (
    build_micro_growth_schedule,
    run_growth_simulation,
    GrowthWave,
)
from coopsim.scenario import build_instruments
from coopsim.property import PropertyConfig

st.set_page_config(page_title="Cooperative Finance", page_icon="🏠", layout="wide")

st.title("Cooperative Finance")
st.caption(
    "Families pool money + term life insurance for collective leverage. "
    "You own the bank. The spread stays with you."
)

# ── Sidebar ─────────────────────────────────────────────────────────────────

st.sidebar.title("Parameters")

num_couples = st.sidebar.number_input("Founding couples", 1, 10, 3)
lump_per_couple = st.sidebar.number_input(
    "Lump sum per couple ($)", 0, 500_000, 66_000, step=1_000,
    help="3 couples × $66K = ~$200K down payment",
)
monthly = st.sidebar.number_input("Monthly dues (everyone)", 10, 500, 20, step=5)
coverage = st.sidebar.number_input("Term life per person ($)", 50_000, 2_000_000, 500_000, step=50_000,
    help="Founders: $500K. Regular members: $100K.")
member_coverage = st.sidebar.number_input("Regular member coverage ($)", 50_000, 500_000, 100_000, step=25_000)
avg_age = st.sidebar.slider("Average age", 25, 55, 35)
pool_return = st.sidebar.slider("Pool return (%/yr)", 0.0, 10.0, 4.0, 0.5) / 100

# Growth
months = 60
new_members_yr1 = st.sidebar.number_input("New members year 1", 0, 50, 10)
new_members_yr2 = st.sidebar.number_input("New members year 2", 0, 50, 20)
new_members_yr3 = st.sidebar.number_input("New members year 3+", 0, 50, 20)

# ── Run sim ─────────────────────────────────────────────────────────────────

num_founders = num_couples * 2
founder_lump = lump_per_couple // 2  # per person


@st.cache_data
def run_sim(nf, fl, fm, fc, mm, mc, age, m, w1, w2, w3, pr):
    waves = []
    if w1 > 0:
        waves.append(GrowthWave(month=6, name="Y1", count=w1))
    if w2 > 0:
        waves.append(GrowthWave(month=18, name="Y2", count=w2))
    if w3 > 0:
        waves.append(GrowthWave(month=30, name="Y3", count=w3))

    schedule = build_micro_growth_schedule(
        num_founders=nf, founder_lump=fl,
        founder_monthly=fm, regular_monthly=mm,
        recruitment_waves=waves,
    )
    instruments = build_instruments(
        which=["hybrid"], coverage_per_member=mc,
        founder_coverage=fc, avg_member_age=age,
        savings_return=pr, death_benefit_leverage=0.50,
    )
    results = run_growth_simulation(schedule, instruments, months=m)
    return schedule, instruments, results


schedule, instruments, results = run_sim(
    num_founders, founder_lump, monthly, coverage,
    monthly, member_coverage, avg_age, months,
    new_members_yr1, new_members_yr2, new_members_yr3, pool_return,
)

inst = instruments[0]
sim_data = results[inst.name]
df = pd.DataFrame(sim_data)
final = df.iloc[-1]

# ── Tabs ────────────────────────────────────────────────────────────────────

tab_founders, tab_members, tab_living = st.tabs([
    "🔑 Founders", "👤 Members", "🏠 Living Here",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: FOUNDERS
# ═══════════════════════════════════════════════════════════════════════════

with tab_founders:
    st.header("What Founders Put In")

    total_lump = num_couples * lump_per_couple
    founder_premium = premium_for_age(avg_age, coverage)
    monthly_premiums_founders = founder_premium * num_founders

    st.markdown(f"""
### Day 1

| | Per Couple | Total ({num_couples} couples) |
|---|---|---|
| Lump sum (zero-interest loan to coop) | ${lump_per_couple:,} | ${total_lump:,} |
| Term life ($500K each, both partners) | 2 × ${founder_premium:.0f}/mo | ${monthly_premiums_founders:.0f}/mo |
| Monthly dues | 2 × ${monthly}/mo | ${monthly * num_founders}/mo |

**Your lump sum is a loan, not a gift.** Returned over 5 years (20%/yr vesting).
If you leave at year 3, you get 60% back. If you die, your family gets it all back
plus the death benefit minus any outstanding loans.

### What the lump sum becomes

The ${total_lump:,} is the cooperative's **down payment on a brownstone**.
Combined with ${num_founders} × $500K in death benefit = **${num_founders * 500_000 / 1_000_000:.1f}M in collateral**,
this is what secures the mortgage.
""")

    # Timeline
    st.subheader("5-Year Timeline")

    milestones = []
    for m in [1, 6, 12, 24, 36, 48, 60]:
        if m <= months:
            row = df[df["month"] == m].iloc[0]
            milestones.append({
                "Month": m,
                "Members": int(row["member_count"]),
                "Pool": f"${row['pool_value']:,.0f}",
                "Death Benefit": f"${row['death_benefit']:,.0f}",
                "Borrowing Power": f"${row['borrowing_power']:,.0f}",
            })
    st.dataframe(pd.DataFrame(milestones), hide_index=True, width=800)

    # Vesting
    st.subheader("Founder Vesting Schedule")
    vest_data = []
    for yr in range(1, 6):
        vested_pct = min(yr * 20, 100)
        vested_amt = lump_per_couple * vested_pct / 100
        vest_data.append({
            "Year": yr,
            "Vested": f"{vested_pct}%",
            "You can take back": f"${vested_amt:,.0f}",
            "Still locked": f"${lump_per_couple - vested_amt:,.0f}",
        })
    st.dataframe(pd.DataFrame(vest_data), hide_index=True, width=600)

    st.info(
        "After 5 years your full lump sum is vested. You can leave and take it back, "
        "or keep it in and earn interest on your available credit."
    )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: MEMBERS
# ═══════════════════════════════════════════════════════════════════════════

with tab_members:
    st.header(f"What You Get for ${monthly}/Month")

    term_prem = inst.effective_term_premium(int(final["member_count"]))
    individual_prem = premium_for_age(avg_age, member_coverage)
    net_to_pool = monthly - term_prem

    c1, c2, c3 = st.columns(3)
    c1.metric("Life Insurance", f"${member_coverage:,}")
    c2.metric("Group Premium", f"${term_prem:.2f}/mo")
    c3.metric("To Your Pool Share", f"${net_to_pool:.2f}/mo")

    st.markdown(f"""
### Where your ${monthly} goes

| | Amount | What it does |
|---|---|---|
| Term life premium | ${term_prem:.2f}/mo | ${member_coverage:,} life insurance (group rate) |
| To pool | ${net_to_pool:.2f}/mo | Your ownership share, grows at {pool_return*100:.0f}%/yr |
| **Buying alone would cost** | **${individual_prem:.2f}/mo** | You save ${individual_prem - term_prem:.2f}/mo on insurance alone |
""")

    # ── Credit & Loans ──────────────────────────────────────────────────
    st.subheader("Zero-Interest Loans")

    st.markdown(f"""
Your credit limit grows with your contributions: **5× what you've paid in**,
capped at 75% of your death benefit (${member_coverage * 0.75:,.0f}).
""")

    credit_data = []
    for yr in [1, 2, 3, 4, 5]:
        contrib = monthly * yr * 12
        limit = min(contrib * 5, member_coverage * 0.75)
        credit_data.append({
            "Year": yr,
            "You've paid in": f"${contrib:,}",
            "Credit limit": f"${limit:,.0f}",
            "Multiplier": f"{limit / contrib:.1f}×",
        })
    st.dataframe(pd.DataFrame(credit_data), hide_index=True, width=600)

    # ── Interest on available credit ────────────────────────────────────
    st.subheader("Interest You Earn")

    interest_rate = pool_return
    st.markdown(f"""
You earn **{interest_rate*100:.0f}% annually** on your available credit
(credit limit minus any outstanding loans). This interest can:

1. **Pay down your loans automatically** (self-retiring loans)
2. **Accumulate as pool equity** if you have no loans

This is the cooperative paying you to be a member — funded by the pool's returns.
""")

    interest_data = []
    for yr in [1, 2, 3, 4, 5]:
        contrib = monthly * yr * 12
        limit = min(contrib * 5, member_coverage * 0.75)
        annual_interest = limit * interest_rate
        interest_data.append({
            "Year": yr,
            "Available credit": f"${limit:,.0f}",
            f"Interest earned ({interest_rate*100:.0f}%/yr)": f"${annual_interest:,.0f}/yr",
            "Per month": f"${annual_interest/12:,.0f}/mo",
        })
    st.dataframe(pd.DataFrame(interest_data), hide_index=True, width=600)

    # ── Loan comparison ─────────────────────────────────────────────────
    st.subheader("Coop Loan vs Market")

    loan_amt = st.select_slider("Loan amount", [1000, 2000, 5000, 10000, 25000, 50000], value=5000,
                                format_func=lambda x: f"${x:,}")
    loan_term = 36

    def monthly_payment(principal, rate, n):
        r = rate / 12
        if r == 0:
            return principal / n
        return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    coop_pmt = monthly_payment(loan_amt, 0, loan_term)
    bank_pmt = monthly_payment(loan_amt, 0.15, loan_term)
    cc_pmt = monthly_payment(loan_amt, 0.22, loan_term)

    st.markdown(f"""
| Source | Rate | Monthly | Total Interest | You Save |
|---|---|---|---|---|
| **Cooperative** | **0%** | **${coop_pmt:,.0f}** | **$0** | — |
| Bank personal loan | 15% | ${bank_pmt:,.0f} | ${bank_pmt * loan_term - loan_amt:,.0f} | **${bank_pmt * loan_term - loan_amt:,.0f}** |
| Credit card | 22% | ${cc_pmt:,.0f} | ${cc_pmt * loan_term - loan_amt:,.0f} | **${cc_pmt * loan_term - loan_amt:,.0f}** |
""")

    # ── If you die ──────────────────────────────────────────────────────
    st.subheader("If You Die")
    st.markdown(f"""
Your family gets **${member_coverage:,}** minus whatever you owe the coop.

| Scenario | You owe | Coop takes | Family gets |
|---|---|---|---|
| No loans | $0 | $0 | ${member_coverage:,} |
| $5K loan | $5,000 | $5,000 | ${member_coverage - 5_000:,} |
| Max loan (${member_coverage * 0.75:,.0f}) | ${member_coverage * 0.75:,.0f} | ${member_coverage * 0.75:,.0f} | ${member_coverage - member_coverage * 0.75:,.0f} |

No debt passes to your estate. The coop only takes what you owe.
""")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: LIVING HERE
# ═══════════════════════════════════════════════════════════════════════════

with tab_living:
    st.header("The Brownstone")
    st.caption("East Flatbush / Crown Heights / Bushwick — real numbers.")

    # Property inputs
    col1, col2 = st.columns(2)
    with col1:
        purchase_price = st.number_input("Purchase price ($)", 500_000, 3_000_000, 1_000_000, step=50_000)
        mortgage_rate = st.slider("Mortgage rate (%)", 3.0, 8.0, 5.0, 0.25) / 100
    with col2:
        member_rent = st.slider("Founders pay ($/person/mo)", 0, 2_000, 750, 50)
        rental_rate = st.number_input("Market rent per 1BR ($/mo)", 500, 5_000, 1_710, step=50,
            help="East Flatbush avg 1BR: $1,710")

    # Fixed layout
    num_couple_units = 3
    adults_per_unit = 2
    num_rentals = 2
    total_founder_adults = num_couple_units * adults_per_unit
    down_payment = total_lump  # founders' combined lump sum

    down_pct = down_payment / purchase_price
    prop = PropertyConfig(
        purchase_price=purchase_price,
        down_payment_pct=down_pct,
        mortgage_rate=mortgage_rate,
        total_units=5,
        housing_units=5,
        market_rent=rental_rate,
        monthly_taxes=500,
        monthly_insurance=200,
        monthly_maintenance=300,
        monthly_management=0,
    )

    # Income
    founder_income = total_founder_adults * member_rent
    rental_income = num_rentals * rental_rate
    total_income = founder_income + rental_income
    surplus = total_income - prop.total_monthly_cost

    # Layout
    st.markdown("---")
    st.markdown(f"""
### The Building

| | Units | People | Monthly Income |
|---|---|---|---|
| Founding couples (2BR each) | {num_couple_units} | {total_founder_adults} adults | {total_founder_adults} × ${member_rent:,} = **${founder_income:,}** |
| Market-rate 1BR rentals | {num_rentals} | — | {num_rentals} × ${rental_rate:,} = **${rental_income:,}** |
| **Total** | **5** | | **${total_income:,}/mo** |
""")

    # Costs
    c1, c2, c3 = st.columns(3)
    c1.metric("Building costs", f"${prop.total_monthly_cost:,.0f}/mo")
    c2.metric("Total income", f"${total_income:,.0f}/mo")
    if surplus >= 0:
        c3.metric("Surplus → pool", f"${surplus:,.0f}/mo", delta=f"+${surplus*12:,.0f}/yr")
    else:
        c3.metric("Gap", f"${-surplus:,.0f}/mo", delta=f"-${-surplus*12:,.0f}/yr", delta_color="inverse")

    st.markdown(f"""
| Cost | Monthly |
|---|---|
| Mortgage (${purchase_price - down_payment:,} @ {mortgage_rate*100:.1f}%) | ${prop.monthly_mortgage:,.0f} |
| Property tax | $500 |
| Insurance | $200 |
| Maintenance | $300 |
| **Total** | **${prop.total_monthly_cost:,.0f}** |
""")

    if surplus >= 0:
        st.success(
            f"Cash-flow positive. ${surplus:,.0f}/mo flows back to the cooperative pool "
            f"(${surplus * 12:,.0f}/yr). Rentals cover "
            f"{rental_income / prop.total_monthly_cost * 100:.0f}% of costs alone."
        )
    else:
        st.warning(
            f"Gap of ${-surplus:,.0f}/mo — pool contributions from "
            f"{int(final['member_count'])} members (${int(final['member_count']) * monthly:,}/mo) cover this."
        )

    # What founders save
    st.markdown("---")
    st.subheader("What You Save vs Renting")

    market_2br = 1_830  # East Flatbush avg
    market_per_person = market_2br // 2
    savings = market_per_person - member_rent

    st.markdown(f"""
East Flatbush 2BR market rent: ~${market_2br:,}/mo (${market_per_person}/person)

| | You pay | Market rent | You save |
|---|---|---|---|
| Per person/mo | ${member_rent:,} | ${market_per_person} | **${savings:,}** |
| Per couple/mo | ${member_rent * 2:,} | ${market_2br:,} | **${savings * 2:,}** |
| Per couple/yr | ${member_rent * 24:,} | ${market_2br * 12:,} | **${savings * 24:,}** |
| 10 years | ${member_rent * 240:,} | ${market_2br * 120:,} | **${savings * 240:,}** |

Plus you're building **equity in the property** — worth ~${prop.equity_at_year(10) / 5:,.0f} per unit after 10 years.
""")

    # Lender view
    st.markdown("---")
    st.subheader("Why a Lender Says Yes")

    death_benefit_total = final["death_benefit"]
    loan_amount = prop.loan_amount
    collateral_ratio = death_benefit_total / loan_amount if loan_amount > 0 else 0

    st.markdown(f"""
| Metric | Value |
|---|---|
| Mortgage | ${loan_amount:,.0f} |
| Death benefit collateral | ${death_benefit_total:,.0f} |
| **Collateral / mortgage** | **{collateral_ratio:.1f}×** |
| DSCR (income / costs) | {total_income / prop.total_monthly_cost:.2f}× |
| Pool reserve | ${final['pool_value']:,.0f} |
| Members backing this | {int(final['member_count'])} |

The death benefit is the key: if a member dies, the insurance pays off their
share of the mortgage automatically. The collateral **self-liquidates** on the
triggering event. This is better security than a house — houses can lose value,
death benefits don't.
""")
