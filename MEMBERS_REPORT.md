# Member Report — What You Get for $20/Month

## The Pitch

You pay $20/mo. You get life insurance, zero-interest loans, and a path to cooperative housing. Your money never leaves — you own a share of the pool. The cooperative IS you.

## What You Put In

$20/mo. That's it.

## Where Your $20 Goes

| Allocation | Amount | What It Does |
|-----------|--------|-------------|
| Term life premium | ~$9.10/mo | $100,000 life insurance for your family |
| Cooperative pool | ~$10.90/mo | You own a share of this — it grows at 4%/yr |

At individual rates, that same $100K policy costs ~$13/mo. The cooperative group rate saves you ~$4/mo.

## What You Get

### 1. Life Insurance ($100K)

Your family is protected. If you die:
- Insurance company pays $100K
- Cooperative takes only what you owe (loans)
- Rest goes to your family
- No debt passes to your estate

### 2. Zero-Interest Loans

Borrow from the cooperative pool. No interest. No fees. No credit check.

**Minimum payment**: $20 + 1% of remaining balance.

| Loan | 1st Payment | Payoff | You Save vs 15% APR |
|------|------------|--------|---------------------|
| $1,000 | $30/mo | 3.5 yrs | $267 |
| $5,000 | $70/mo | 10 yrs | $4,910 |
| $10,000 | $120/mo | 15 yrs | $15,090 |

**Your credit limit unlocks gradually**: every $1 you contribute unlocks $5 in credit, capped at $75,000 (75% of your $100K death benefit).

| Time In | Contributed | Credit Limit |
|---------|-----------|-------------|
| Month 6 | $120 | $600 |
| Month 12 | $240 | $1,200 |
| Month 24 | $480 | $2,400 |
| Month 60 | $1,200 | $6,000 |

Want more credit faster? Contribute a lump sum. $5K lump = $25K credit on day 1.

### 3. Cooperative Housing (When Available)

The cooperative buys brownstones. Members live there at cost.

| | You Pay | Market Rent | You Save |
|--|---------|-------------|----------|
| Monthly | ~$1,588 carrying charge | $2,500 | $912/mo |
| Yearly | ~$19,060 | $30,000 | $10,940/yr |
| 10 years | ~$190,600 | $300,000 | $109,400 |

Plus you build property equity: ~$45K per-unit share after 10 years.

Not everyone gets a unit right away. Non-housing members have **priority** for the next brownstone.

### 4. Pool Equity

Your contributions grow at 4%/yr. After 5 years of $20/mo:
- Total paid to pool: ~$654
- Pool equity: ~$714 (with growth)

Small individually, but the pool is collective. 52 members × $20/mo = $1,040/mo flowing in. The pool funds loans, property, and operations.

### 5. Credit Score Improvement

The cooperative reports your on-time contributions to credit bureaus (MAF model). Average improvement: ~168 credit score points.

### 6. Community + Governance

- One person, one vote — same as founders
- Attend meetings, serve on committees, shape the cooperative
- You're not a tenant or a customer — you're an owner

## Early Member Bonus

If you join in the first 12 months, you're a **founding member**. Your member-months count at 1.5× for common equity. A founding member at month 60 has 50% more common equity than someone who joined at month 13.

## If You Leave

You get your common equity back, minus anything you owe. Common equity is always fully vested — no waiting period. Housing members must vacate within 90 days.

## The Bottom Line

| What You Pay | What You Get |
|-------------|-------------|
| $20/mo | $100K life insurance |
| | Zero-interest loans (up to $75K) |
| | Credit score improvement |
| | Cooperative housing priority |
| | Pool equity (grows at 4%/yr) |
| | Governance vote |
| | Community membership |

A bank would charge you $13/mo just for the life insurance. Here you get insurance + loans + housing + equity + community for $20/mo.

## Run the Numbers

```bash
uv run python -m coopsim --growth --micro --instruments hybrid --months 60 \
  --founders 2 --founder-amounts "150000" --founder-monthly 20 \
  --founder-coverage 500000 --member-view --loans
```
