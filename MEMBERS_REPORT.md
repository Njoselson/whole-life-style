# Member Report — What You Get for $20/Month

## The Pitch

You pay $20/mo. You get life insurance, zero-interest loans that pay themselves down, and a path to cooperative housing. Your money never leaves — you own a share of the pool. The cooperative IS you.

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

### 2. Zero-Interest Loans (That Pay Themselves Down)

Borrow from the cooperative pool. No interest. No fees. No credit check.

**Minimum payment**: $20 + 1% of remaining balance.

**Your credit limit unlocks gradually**: every $1 you contribute unlocks $5 in credit, capped at $75,000 (75% of your $100K death benefit).

| Time In | Contributed | Credit Limit |
|---------|-----------|-------------|
| Month 6 | $120 | $600 |
| Month 12 | $240 | $1,200 |
| Month 24 | $480 | $2,400 |
| Month 60 | $1,200 | $6,000 |

Want more credit faster? Contribute a lump sum. $5K lump = $25K credit on day 1.

### 3. Earn 4% on Your Available Credit

You earn **4%/yr on the portion of your credit limit you haven't borrowed**. This is the cooperative recognizing that your death benefit collateral has real value.

| At Month 60 | Available Credit | You Earn |
|-------------|-----------------|----------|
| No loan | $6,000 | $240/yr ($20/mo) |
| $1K loan | $5,000 | $200/yr |
| $3K loan | $3,000 | $120/yr |

**The kicker**: that interest auto-applies to your loan balance. Your loans literally pay themselves down just by being a member.

**Example**: Borrow $5,000 at month 60 (credit limit $6,000):
- Without interest credits: pay off in 10.4 years, pay $5,000 out of pocket
- With interest credits: pay off in 7.7 years, pay $3,881 out of pocket
- The cooperative's growth paid $1,119 of your loan

Compare: a bank charges $4,910 in interest on a $5K personal loan at 15% APR. Here you **earn** money that pays **down** your loan.

### 4. Cooperative Housing (When Available)

The cooperative buys brownstones. Members live there at cost.

| | You Pay | Market Rent | You Save |
|--|---------|-------------|----------|
| Monthly | ~$1,588 carrying charge | $2,500 | $912/mo |
| Yearly | ~$19,060 | $30,000 | $10,940/yr |
| 10 years | ~$190,600 | $300,000 | $109,400 |

Plus you build property equity: ~$45K per-unit share after 10 years.

Not everyone gets a unit right away. Non-housing members have **priority** for the next brownstone.

### 5. Pool Equity

Your contributions grow at 4%/yr. After 5 years of $20/mo:
- Total paid to pool: ~$654
- Pool equity: ~$714 (with growth)

Small individually, but the pool is collective. 52 members × $20/mo = $1,040/mo flowing in. The pool funds loans, property, and operations.

### 6. You're Growing the Cooperative's Balance Sheet

Every dollar you borrow and spend within the cooperative **grows the balance sheet**:
- You borrow $1K → that's a loan receivable (cooperative asset)
- You spend it at another member's business or pay rent → it comes back to the pool
- Pool can lend it again → money multiplier (2×)
- Your $20/mo creates ~$40/mo in economic activity

This is how banks work. Except here, YOU own the bank.

### 7. Credit Score Improvement

The cooperative reports your on-time contributions to credit bureaus (MAF model). Average improvement: ~168 credit score points.

### 8. Community + Governance

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
| | 4% earnings on available credit |
| | Loans that pay themselves down |
| | Credit score improvement |
| | Cooperative housing priority |
| | Pool equity (grows at 4%/yr) |
| | Governance vote |
| | Community membership |

A bank would charge you $13/mo just for the life insurance. Here you get insurance + self-retiring loans + housing + equity + community for $20/mo.

## Run the Numbers

```bash
uv run python -m coopsim --growth --micro --instruments hybrid --months 60 \
  --founders 2 --founder-amounts "150000" --founder-monthly 20 \
  --founder-coverage 500000 --member-view --loans --self-retiring
```
