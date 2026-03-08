# Founder Report — What You're Building and What You Get

## The Model

You and your wife put $150K into a cooperative. Everyone pays $20/mo. All members carry term life insurance. The cooperative uses the death benefit as collateral to borrow, buy property, and lend to members at zero interest.

Your $150K is a **zero-interest loan** to the cooperative — not equity, not ownership. You get it back over 5 years via vesting. The cooperative owns everything it generates.

## What You Put In

| Item | Amount |
|------|--------|
| Lump sum (one-time) | $150,000 |
| Monthly contribution | $20/mo |
| Term life premium (~$500K coverage) | ~$65/mo individually, ~$45/mo at group rate |
| Total monthly cost | $20/mo (premium comes out of this) |

## What You Get Back

### Capital Return (Vesting)

Your $150K comes back over 5 years at 20%/year.

| Year | Capital Returned | Vested % |
|------|-----------------|----------|
| 1 | ~$28K | 20% |
| 2 | ~$58K | 40% |
| 3 | ~$89K | 60% |
| 4 | ~$119K | 80% |
| 5 | ~$150K | 98% |

If you leave early, you get the vested portion. Unvested portion stays in the pool.

If the pool has declined below $150K (unlikely), your return is prorated: `$150K × vesting × min(1.0, pool / total_lumps)`.

### Common Equity

You also earn common equity like every other member — weighted by time (member-months), not dollars. Since you joined at month 1, you get 1.5× weight as a founding member.

### Credit Limit

Your $150K lump sum unlocks credit immediately:
- $150K × 5 = $750K unlocked
- Capped at 75% of $500K death benefit = **$375K credit limit**
- Available from day 1

You can borrow up to $375K from the cooperative at **zero interest**.

### Interest on Available Credit

You earn **4%/yr on your available credit** (credit limit minus any outstanding loans).

| Scenario | Available Credit | Annual Earnings |
|----------|-----------------|----------------|
| No loan outstanding | $375,000 | $15,000/yr |
| $100K loan | $275,000 | $11,000/yr |
| $200K loan | $175,000 | $7,000/yr |
| $375K loan (maxed) | $0 | $0/yr |

**The incentive**: borrow only what you need. The more available credit you leave, the more you earn.

### Self-Retiring Loans

Interest earned on your available credit **auto-applies to your loan balance**. Your loans pay themselves down over time:

- Borrow $50K → available credit = $325K → earn $13K/yr → $1,083/mo auto-applied to loan
- Combined with your minimum payment ($20 + 1% of balance), loans retire significantly faster
- The cooperative's growth pays part of your loan for you

### Housing Priority

As a founder, you have priority for cooperative housing. Carrying charge ~$1,588/mo vs $2,500 market rent = **$912/mo savings**.

### What You Don't Get

- No ownership of the pool beyond your capped capital return
- No dividends, no profit sharing, no upside on the $150K
- No special voting power — one person, one vote, same as everyone
- No cash value — term life only

**This is by design.** The founders shouldn't own the cooperative's growth. The cooperative owns the growth. Your $150K made it possible. You get it back. That's the deal.

## If You Die

1. Insurance company pays $500K death benefit
2. Cooperative takes only what you owe (outstanding loans)
3. Remaining death benefit goes to your family
4. Your pool equity is also returned to your family
5. No debt passes to your estate

If you owe $375K (fully drawn credit): family gets $125K from death benefit + pool equity.
If you owe $0: family gets $500K + pool equity.

**Recommendation**: carry a separate personal term life policy ($150-250K) as your family's safety net. The cooperative policy is collateral. The personal policy is protection.

## If You Leave

| Scenario | What You Get |
|----------|-------------|
| Year 1 exit | ~$28K capital return + common equity |
| Year 3 exit | ~$89K capital return + common equity |
| Year 5 exit | ~$150K capital return + common equity |
| Forced buyout (default) | Vested equity − amounts owed |

If the pool can't cover your capital return in one payment: installments over 36 months, zero interest.

## Other Couples Can Also Contribute

Any member can contribute a lump sum to get higher credit limits. Examples:

| Lump Sum | Credit Unlocked | Max Credit (75% of $100K) |
|----------|----------------|--------------------------|
| $5,000 | $25,000 | $25,000 |
| $15,000 | $75,000 | $75,000 (capped) |
| $50,000 | $75,000 | $75,000 (capped) |

To get a higher cap, they'd need higher coverage. A couple contributing $50K+ might consider $250K term coverage → $187K max credit.

## Run the Numbers

```bash
uv run python -m coopsim --growth --micro --instruments hybrid --months 60 \
  --founders 2 --founder-amounts "150000" --founder-monthly 20 \
  --founder-coverage 500000 --founder-view --loans --balance-sheet --self-retiring
```
