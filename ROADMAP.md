# Founding Roadmap

## The Model

A founding couple puts in $150K + $20/mo. Everyone else pays $20/mo. The $150K seeds the pool and eventually becomes the down payment on a brownstone. Term life death benefit is collateral-assigned to the cooperative. Internal zero-interest loans build the balance sheet. The track record of performing loans + death benefit collateral unlocks external credit — first a CDFI relationship, then a mortgage.

**Two member types:**
- **Housing members**: $20/mo + carrying charges (~$2,064/mo). Save ~$436/mo vs market rent. Build property equity.
- **Non-housing members**: $20/mo only. Get zero-interest loans, future housing priority, community.

**The flow:**
1. Form entity → pool $150K + monthly dues
2. Buy term life policies, collateral assign to coop
3. Make internal loans to members → loans = assets on balance sheet
4. Performing loans + collateral → CDFI approves first external loan
5. Build track record (12-24 months on-time payments)
6. Get mortgage → buy brownstone
7. 4 members move in, pay carrying charges
8. Pool funds zero-interest loans to all members
9. As coop grows → buy more brownstones → more housing for members

---

## Phase 1: Seed (Weeks 1-2)

- [ ] Get term life quotes from 2-3 A-rated carriers
  - You and your wife: $500K each, 20-year term
  - Ask about group/association discount for future members
  - Carriers: Northwestern Mutual, New York Life, MassMutual
- [ ] Find a cooperative law attorney ($3-5K budget)
  - Search: "cooperative attorney" or "fraternal benefit society attorney"
  - NOT a general business lawyer — they won't know the structure
- [ ] Form mutual benefit corporation
  - File articles of incorporation in your state (~$200-500)
  - Or have attorney handle it
- [ ] Get EIN from IRS (free, same day, IRS.gov)
- [ ] Open business bank account
- [ ] Deposit $150K

**Balance sheet: $150K cash. $1M death benefit collateral (off-balance-sheet).**
**Internal loans: $500-$2K test loans between founders.**
**External loans: NONE — build internal track record first.**

## Phase 2: Insurance + Legal (Weeks 2-6)

- [ ] Buy term life policies ($500K each)
- [ ] Execute collateral assignments to the cooperative
  - Standard AMA/ACLI form (insurance company has it)
  - You sign, they acknowledge, copies to cooperative records
- [ ] Attorney finalizes operating agreement
  - Starting point: `coopsim/legal/operating_agreement_outline.md`
  - **Key question for attorney**: does the capital return model (not equity) keep us out of securities regulation?
  - Capital return: $150K is a zero-interest loan, returned via 5yr vesting
  - Common equity: time-weighted (member-months), not dollar-weighted
  - Credit limits: 5x contributions, capped at 75% of death benefit
  - Voting: one person, one vote
- [ ] Attorney finalizes buy-sell agreement
  - Starting point: `coopsim/legal/buy_sell_outline.md`
  - Covers: death, disability, departure, forced buyout
  - **This protects your family. Don't skip it.**
- [ ] Draft member application form

**Milestone: cooperative exists. $150K in the bank, $1M death benefit collateral.**

## Phase 3: Inner Circle (Months 1-6)

- [ ] Recruit 5 members (family first, then close friends)
  - The pitch: $20/mo gets you:
    - $100K life insurance at group rates
    - Zero-interest loans (credit unlocks with contributions)
    - Future housing priority
    - Cooperative membership + governance vote
  - Show them the simulator: `uv run python -m coopsim --growth --micro --instruments hybrid --months 60 --founders 2 --founder-amounts "150000" --founder-monthly 20 --founder-coverage 500000 --founder-view --loans --roadmap`
- [ ] Each new member: buy $100K term life, sign collateral assignment, sign operating agreement
- [ ] Start the contribution ledger — every payment documented
- [ ] Monthly statements to all members
- [ ] Hold first member meeting (governance starts now)
- [ ] Issue first internal loans ($1K-$5K) — test the credit unlock model
  - Each loan = asset on the balance sheet, backed by $100K death benefit
  - This is the track record that unlocks everything else

**Balance sheet: ~$155K cash + loans receivable. $1.5M death benefit collateral.**
**Internal loans: $1K-$5K to members. Testing the system.**
**External loans: NONE — still too early.**
**Milestone: 7 members. Group discount kicks in at 10.**

## Phase 4: Track Record (Months 6-12)

- [ ] Recruit 5 more members (word of mouth)
- [ ] 6+ months of on-time contributions documented
- [ ] Internal loans performing — members borrowing and repaying on schedule
- [ ] Clean books: monthly statements, meeting minutes, contribution ledger
- [ ] All policies active, all assignments in force
- [ ] Reserve requirements met (15% liquid)
- [ ] Research CDFIs in your area
  - Mission-aligned, understand cooperative structures
  - Examples: community development financial institutions, community banks
  - Do NOT approach large national banks

**Balance sheet: ~$163K cash + $15K-$30K loans receivable. $2M death benefit collateral.**
**Internal loans: up to $5K per member. ~$15K-$30K total outstanding.**
**External loans: preparing CDFI package.**
**Milestone: 12 members, $2M death benefit, 6-12 month track record.**

## Phase 5: CDFI Relationship (Months 12-24)

- [ ] Approach 2-3 CDFIs with your package:
  - Business plan explaining the cooperative model
  - 12+ months of contribution history
  - $150K+ pool + $2M death benefit collateral
  - Internal loan portfolio: performing loans as balance sheet assets
  - Legal docs (operating agreement, buy-sell, collateral assignments)
  - Member roster with coverage amounts
  - Bank-style balance sheet: `uv run python -m coopsim --growth --micro --instruments hybrid --months 60 --founders 2 --founder-amounts "150000" --founder-monthly 20 --founder-coverage 500000 --balance-sheet --roadmap`
- [ ] Establish lending relationship — borrow $10K-$25K (capacity building)
  - Borrow small. Repay perfectly. This is the foot in the door.
  - Purpose: prove the cooperative can service external debt
- [ ] Continue recruiting — target 20+ members
- [ ] Internal loans growing: up to $10K per member, ~$50K-$80K total outstanding

**How internal loans help here:**
A cooperative with $163K in cash is fine. A cooperative with $133K in cash + $30K in performing loans backed by $2M in death benefit collateral is *better*. It proves the institution can underwrite, service, and collect debt. This is what the CDFI evaluates.

**Balance sheet: ~$170K cash + $50K-$80K loans receivable. $3M death benefit collateral.**
**External loans: CDFI relationship loan $10K-$25K. Repay perfectly.**
**Milestone: CDFI relationship established, 22+ members, lending credibility.**

## Phase 6: Credibility → Mortgage Pipeline (Months 24-36)

- [ ] Recruit to 37+ members
- [ ] Apply for credit union line of credit ($50K-$100K)
  - Demonstrates ability to manage revolving credit
  - Borrow, repay, repeat — discipline builds the record
- [ ] Begin mortgage conversations with CDFI
- [ ] Form Property Holding LLC (when brownstone is under contract)
- [ ] Identify $1.2M brownstone (4 units)
- [ ] Lender package for mortgage:
  - Run: `uv run python -m coopsim --growth --micro --instruments hybrid --months 60 --founders 2 --founder-amounts "150000" --founder-monthly 20 --founder-coverage 500000 --property 1200000 --units 4 --lender-view --mortgage-track --roadmap`
  - Pro forma: ~$2,064 carrying charge vs $2,500 market rent
  - Death benefit collateral backing the mortgage ($4.5M+)
  - 2+ years of on-time member contributions
  - Performing internal loan portfolio
  - CDFI loan repaid or current
  - Mortgage reliability timeline showing path to better rates
- [ ] Down payment from pool ($150K founder capital + accumulated contributions)
- [ ] Close on property

**Balance sheet: ~$183K cash + $80K-$120K loans receivable. $4.5M death benefit collateral.**
**External loans: $960K mortgage on $1.2M brownstone (20% down).**
**DSCR: carrying charges ($8,256/mo) + dues ($660/mo) = $8,916 vs $8,256 costs = 1.08x**
**What makes this work: $4.5M in death benefit collateral + performing loan track record.**
**Milestone: brownstone acquired. 4 members move in.**

## Phase 7: Housing + Growth (Months 36-48)

- [ ] 4 housing members pay carrying charges (~$2,064/mo)
- [ ] Carrying charges cover mortgage + taxes + insurance + maintenance
- [ ] Zero-interest loans available to all members from pool
- [ ] Continue recruiting — every new member adds $100K death benefit collateral
- [ ] Monthly loan repayments flow back to pool
- [ ] Build on-time mortgage payment record for better terms on next property
- [ ] The drip never stops: 37+ members × $20/mo = $740+/mo flowing in

**Balance sheet: ~$183K cash + loans receivable + property equity (~$15K/yr). $4.5M+ collateral.**
**Internal loans: up to $15K per member. Loans = assets backed by death benefit.**
**External: mortgage performing. Building toward refinance or second property.**
**Milestone: 37+ members, $4.5M death benefit, pool replenishing from carrying charges + dues.**

## Phase 8: Expansion (Year 3+)

- [ ] Apply for 501(c)(8) fraternal benefit society status (25+ members required)
  - Tax-exempt status
  - Authority to provide insurance directly
  - Path to CDFI certification
- [ ] Refinance at lower rate (5.5% → 5.0% with 2+ year track record)
  - 0.5% lower rate on $960K = ~$300/mo savings = $108K over 30yr
- [ ] Save for brownstone #2 (carrying charges from building 1 fund down payment)
  - Better mortgage rate from track record
- [ ] More housing members, more carrying charges, more collateral
- [ ] Consider CDFI certification (federal grants, technical assistance)

**Milestone: 52 members, $6M death benefit, ~$198K pool, multiple properties.**

---

## Key Numbers

| When | Members | Death Benefit | Pool | Loans Receivable | Borrowing Power |
|------|---------|--------------|------|-----------------|-----------------|
| Day 1 | 2 | $1M | $150K | $0 | $622K |
| Month 6 | 7 | $1.5M | $155K | ~$5K | $875K |
| Month 12 | 12 | $2M | $163K | ~$25K | $1.1M |
| Month 24 | 22 | $3M | $172K | ~$70K | $1.6M |
| Month 36 | 37 | $4.5M | $183K | ~$100K | $2.4M |
| Month 60 | 52 | $6M | $198K | ~$150K | $3.2M |

## Membership Targets — Why Each Number Matters

| Members | Collateral | Why | Monthly Drip |
|---------|-----------|-----|-------------|
| 2 | $1M | Minimum viable cooperative | $40/mo |
| 10 | $2M | Group insurance discount kicks in (saves ~15%) | $200/mo |
| 12 | $2M | Enough for CDFI conversation | $240/mo |
| 22 | $3M | Mortgage DSCR viable (4 housing + 18 non-housing) | $440/mo |
| 25 | $3.5M | Full group discount (30%). 501(c)(8) eligibility. | $500/mo |
| 37 | $4.5M | Comfortable DSCR margin | $740/mo |
| 52 | $6M | Multiple properties feasible. Self-sustaining. | $1,040/mo |
| 100 | $11M | Third property. Regional cooperative. | $2,000/mo |

## External Loan Targets by Phase

| Phase | When | Target Loan | Purpose |
|-------|------|------------|---------|
| Track Record | Month 12 | CDFI $10K-$25K | Capacity building. Borrow small, repay perfectly. |
| Credibility | Month 24 | Credit union LOC $50K-$100K | Revolving credit. Discipline builds the record. |
| Property | Month 36 | Mortgage $960K | $1.2M brownstone. Carrying charges cover costs. |
| Expansion | Month 60 | Refinance + 2nd mortgage | Lower rate on #1. Better terms on #2. |

## How Internal Loans Create Creditworthiness

When the cooperative lends $5K to a member:
- Cash goes down $5K, loans receivable goes up $5K — total assets unchanged
- The loan is backed by $100K death benefit (20x overcollateralized)
- Member repays $20 + 1% of balance each month — cash flows back
- When the next lender evaluates the coop: they see **performing loans**

A cooperative with $163K in cash is fine.
A cooperative with $133K in cash + $30K in performing loans is **better**.
It proves the institution can underwrite, service, and collect debt.
This is the track record that unlocks the mortgage.

## Attorney Questions (bring these to the first meeting)

1. Does the capital return model (zero-interest loan, not equity) avoid securities classification?
2. Can we use a mutual benefit corporation, or do we need a different entity type in our state?
3. Is the collateral assignment enforceable as written?
4. Any state-specific requirements for cooperative lending at 0% interest?
5. What triggers the need for 501(c)(8) status vs operating as a mutual benefit corp?
6. Any ERISA implications if housing members work for the cooperative?
7. Does the zero-interest loan model trigger any lending regulations?

## Costs

| Item | Cost | When |
|------|------|------|
| State filing (mutual benefit corp) | $200-500 | Week 1 |
| Attorney (operating agreement + buy-sell) | $3,000-5,000 | Weeks 2-6 |
| Term life (2 founders, $500K each) | ~$130/mo total | Week 2 |
| Business bank account | Free | Week 1 |
| EIN | Free | Week 1 |
| **Total startup** | **~$3,500-5,500 + $130/mo** | |

## Run the Simulator

```bash
# Full roadmap with creditworthiness evolution
uv run python -m coopsim --growth --micro --instruments hybrid --months 60 \
  --founders 2 --founder-amounts "150000" --founder-monthly 20 \
  --founder-coverage 500000 --roadmap

# With brownstone and lender metrics
uv run python -m coopsim --growth --micro --instruments hybrid --months 60 \
  --founders 2 --founder-amounts "150000" --founder-monthly 20 \
  --founder-coverage 500000 --property 1200000 --units 4 --lender-view --roadmap

# Full picture: founder equity + loans + balance sheet + roadmap
uv run python -m coopsim --growth --micro --instruments hybrid --months 60 \
  --founders 2 --founder-amounts "150000" --founder-monthly 20 \
  --founder-coverage 500000 --founder-view --loans --balance-sheet --roadmap
```
