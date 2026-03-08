# Founding Roadmap

## Phase 1: Formation (Weeks 1-2)

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

## Phase 3: Recruitment (Months 1-6)

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

**Milestone: 7 members, $1.5M death benefit, ~$155K pool.**

## Phase 4: Track Record (Months 6-12)

- [ ] Recruit 5 more members (word of mouth)
- [ ] 6+ months of on-time contributions documented
- [ ] Clean books: monthly statements, meeting minutes, contribution ledger
- [ ] All policies active, all assignments in force
- [ ] Reserve requirements met (15% liquid)
- [ ] Research CDFIs in your area
  - Mission-aligned, understand cooperative structures
  - Examples: community development financial institutions, community banks
  - Do NOT approach large national banks

**Milestone: 12 members, $2M death benefit, ~$163K pool, 6-12 month track record.**

## Phase 5: CDFI Relationship (Months 12-18)

- [ ] Approach 2-3 CDFIs with your package:
  - Business plan explaining the cooperative model
  - 12+ months of contribution history
  - $150K+ pool + $2M death benefit collateral
  - Legal docs (operating agreement, buy-sell, collateral assignments)
  - Member roster with coverage amounts
  - Bank-style balance sheet: `uv run python -m coopsim --growth --micro --instruments hybrid --months 60 --founders 2 --founder-amounts "150000" --founder-monthly 20 --founder-coverage 500000 --balance-sheet --mortgage-track`
- [ ] Establish lending relationship (small loan first to build credibility)
- [ ] Continue recruiting — target 20+ members

**Milestone: CDFI relationship established, 20+ members, lending credibility.**

## Phase 6: Property Acquisition (Months 18-36)

- [ ] Recruit to 22+ members
- [ ] Form Property Holding LLC (when brownstone is under contract)
- [ ] Identify $1.2M brownstone (4 units)
- [ ] Lender package for mortgage:
  - Run: `uv run python -m coopsim --growth --micro --instruments hybrid --months 60 --founders 2 --founder-amounts "150000" --founder-monthly 20 --founder-coverage 500000 --property 1200000 --units 4 --lender-view --mortgage-track`
  - Pro forma: ~$1,588 carrying charge vs $2,500 market rent
  - Death benefit collateral backing the mortgage
  - Track record of on-time member contributions
  - Mortgage reliability timeline showing path to better rates
- [ ] Down payment from pool ($150K founder capital + accumulated contributions)
- [ ] Close on property

**Milestone: brownstone acquired, 4 members move in.**

## Phase 7: Housing + Lending (Months 24-48)

- [ ] 4 housing members pay carrying charges (~$1,588/mo)
- [ ] Carrying charges cover mortgage + taxes + insurance + maintenance
- [ ] Zero-interest loans available to all members from pool
- [ ] Continue recruiting — every new member adds $100K death benefit collateral
- [ ] Monthly loan repayments flow back to pool
- [ ] Build on-time mortgage payment record for better terms on next property

**Milestone: 37+ members, $4.5M death benefit, pool replenishing from carrying charges + dues.**

## Phase 8: Expansion (Year 3+)

- [ ] Apply for 501(c)(8) fraternal benefit society status (25+ members required)
  - Tax-exempt status
  - Authority to provide insurance directly
  - Path to CDFI certification
- [ ] Save for brownstone #2 (carrying charges from building 1 fund down payment)
  - Better mortgage rate from 2+ year track record (est. 5.5% → 5.0%)
  - 30-year savings: $444K per $960K mortgage at 5% vs 7%
- [ ] More housing members, more carrying charges, more collateral
- [ ] Consider CDFI certification (federal grants, technical assistance)

**Milestone: 52 members, $6M death benefit, ~$198K pool, multiple properties.**

---

## Key Numbers

| When | Members | Death Benefit | Pool | Borrowing Power |
|------|---------|--------------|------|-----------------|
| Day 1 | 2 | $1M | $150K | $622K |
| Month 6 | 7 | $1.5M | $155K | $875K |
| Month 12 | 12 | $2M | $163K | $1.1M |
| Month 24 | 22 | $3M | $172K | $1.6M |
| Month 36 | 37 | $4.5M | $183K | $2.4M |
| Month 60 | 52 | $6M | $198K | $3.2M |

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
