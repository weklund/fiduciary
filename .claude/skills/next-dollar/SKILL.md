---
name: next-dollar
description: >
  Answer "what should I do with my next dollar?" Apply the financial order of
  operations to the user's ACTUAL situation. Use when someone asks what to do
  with money, how to allocate a paycheck, where to put savings, whether to pay
  debt or invest, what to do with a bonus/raise/windfall/tax refund, or any
  variant of "I have $X — what's the best use?" Also use for "should I pay off
  X or save?" questions. THIS IS THE MOST COMMON FINANCIAL QUESTION — trigger
  aggressively.
allowed-tools: Bash, Read
---

## Next Dollar Guidance

You are answering the most fundamental personal finance question: "What should I
do with my next dollar?" This isn't generic advice — you're applying the financial
order of operations to THIS PERSON's specific balances, rates, goals, and constraints.

### Process

1. Determine how much they're allocating (ask if not stated)
2. Gather their current financial state
3. Walk the order of operations, checking each step against reality
4. Identify where THEY are in the sequence
5. Give a specific, actionable recommendation with the math

---

### Step 1: Clarify the Amount

If the user didn't specify an amount, ask: "How much are we working with — a
specific amount like a bonus, or thinking about your ongoing monthly allocation?"

Common triggers and what they mean:
- "I have $X" → one-time allocation
- "Got a raise/bonus" → one-time + ongoing reallocation
- "Should I pay off X or invest?" → decision between two specific options
- "What should I do with my paycheck?" → recurring monthly allocation
- "Got a tax refund" → one-time windfall

---

### Step 2: Gather Current State

```bash
# Account balances (cash + debt)
sqlite3 data/finance.db "
SELECT name, mask, type, balance_current, balance_limit
FROM accounts
WHERE balance_current != 0
ORDER BY type, balance_current DESC;"
```

```bash
# Monthly income (average of last 3 months)
sqlite3 data/finance.db "
SELECT ROUND(AVG(monthly_income), 2) as avg_monthly_income FROM (
  SELECT strftime('%Y-%m', date) as month, SUM(ABS(amount)) as monthly_income
  FROM transactions WHERE amount < 0
    AND date >= date('now', '-90 days')
    AND description NOT LIKE '%TRANSFER%'
    AND description NOT LIKE '%EPAYMENT%'
    AND description NOT LIKE '%AUTOPAY%'
  GROUP BY month
);"
```

```bash
# Monthly essential expenses (average of last 3 months)
sqlite3 data/finance.db "
SELECT ROUND(AVG(monthly_spend), 2) as avg_monthly_spend FROM (
  SELECT strftime('%Y-%m', date) as month, SUM(amount) as monthly_spend
  FROM transactions WHERE amount > 0
    AND date >= date('now', '-90 days')
    AND description NOT LIKE '%AMERICAN EXPRESS ACH%'
    AND description NOT LIKE '%Coinbase Card Payment%'
    AND description NOT LIKE '%AUTOPAY%'
    AND description NOT LIKE '%AUTO PAY%'
    AND description NOT LIKE '%EPAYMENT%'
  GROUP BY month
);"
```

Also check Client Context / memory for:
- Debt interest rates (APRs — not in the database)
- Employer match details (percentage, cap)
- Tax-advantaged account status (maxed? room left?)
- Guardrails and constraints

---

### Step 3: Walk the Order of Operations

Go through each step sequentially. STOP at the first step that isn't fully satisfied.
That's where the next dollar goes.

```
1. STARTER EMERGENCY FUND ($1,000-2,000 or one month's deductibles)
   → Is cash > $1,000? If no, STOP HERE.

2. EMPLOYER MATCH (instant 50-100% return)
   → Are they contributing enough to get the FULL match?
   → If no match available, skip.
   → If not capturing full match, STOP HERE.

3. HIGH-INTEREST DEBT (>7% APR)
   → Any debt above 7%? List them by rate.
   → If yes, STOP HERE — pay highest rate first (avalanche).
   → Exception: still capture employer match even with high-interest debt.

4. FULL EMERGENCY FUND (3-6 months expenses)
   → Calculate: cash reserves ÷ monthly essential expenses = months of runway
   → Target: 3 months (dual stable income), 6 months (single/variable income)
   → If below target, STOP HERE.

5. HSA (if eligible — triple tax advantage)
   → Are they maxing HSA? ($4,300 individual / $8,550 family for 2026)
   → If eligible and not maxed, STOP HERE.

6. ROTH IRA
   → Are they maxing Roth? ($7,000 for 2026, $8,000 if 50+)
   → Income limits: phase out at $150K single / $236K married
   → If eligible and not maxed, STOP HERE.

7. MAX 401(k)/403(b) (beyond the match)
   → Are they maxing? ($23,500 for 2026, $31,000 if 50+)
   → If not maxed, STOP HERE.

8. HYPER-ACCUMULATE (taxable brokerage)
   → Target 25% total savings rate across all accounts
   → If below 25%, direct here.

9. FUTURE GOALS (529, real estate, business)
   → Specific goals from their plan.

10. PREPAY LOW-INTEREST DEBT (<5% APR)
    → Only after everything above is satisfied.
    → Math: expected market return (~7-10%) minus debt rate = opportunity cost
    → If spread > 3%, invest. If spread < 2%, pay debt. Gray zone = split.
```

---

### Step 4: The Recommendation

Present the answer as:

```
## Where Your Next $[Amount] Should Go

### You're at Step [N]: [Step Name]

[One sentence explaining why the steps above are satisfied or skipped]

### The Recommendation

**Put $[amount] toward [specific action].**

Here's why:
- [Math/logic explaining this is the highest-return use]
- [What this accomplishes — debt paid by X date, fund reaches Y level, etc.]

### What This Means
- [Concrete outcome: "This gets your emergency fund to 4.2 months"]
- [Timeline impact: "At this rate, you're debt-free by March 2027"]

### After This Step Is Done
Your next priority becomes Step [N+1]: [brief description]
```

---

### Decision Rules (from CLAUDE.md)

Apply these when the user is choosing between two options:

**Debt vs. Invest:**
- Debt APR > 7%: Pay debt (guaranteed return beats uncertain market)
- Debt APR 5-7%: Gray zone — recommend splitting 50/50 or matching to risk profile
- Debt APR < 5%: Invest the difference (market historically wins)
- ALWAYS capture employer match regardless of debt level

**Lump Sum vs. Spread Out:**
- Mathematically: lump sum wins ~68% of the time (time in market)
- Behaviorally: if they'd panic-sell during a dip, DCA over 3-6 months
- Use their behavioral profile to decide which to recommend

**Pay Extra on Debt — Which One?**
- Avalanche (highest rate first): mathematically optimal
- Snowball (smallest balance first): psychologically motivating
- Recommend avalanche by default, snowball if they mention needing motivation or quick wins

---

### Guardrail Check

Before giving the final recommendation, verify against their constraints:
- Does this leave adequate runway? (check guardrails from Client Context)
- Does this violate any "never do X" rules?
- Is their income stable enough for this allocation?
- If income is transitioning/uncertain: bias toward liquidity over optimization

If the optimal action conflicts with a guardrail, say so explicitly:
"Mathematically, you should [X]. But given your guardrail of [Y], I'd recommend [Z] instead."

---

### Special Cases

**"Should I pay off my car or invest?"**
Calculate the spread. Show both scenarios over the remaining loan term. Account for tax advantages of investment accounts.

**"I got a windfall ($5K+)"**
Apply the Ramit Sethi windfall rule: decide BEFORE the emotion hits.
Suggest: 50% to highest priority (from order of operations), 25% to next priority, 25% guilt-free (or skip guilt-free if they have high-interest debt).

**"I got a raise"**
Lifestyle inflation is the enemy. Recommend: commit 50-100% of the INCREASE to savings/debt before they adjust spending. Set up the auto-transfer NOW before the raise hits.

**"Should I save or enjoy life?"**
Not a binary. Reference the Conscious Spending Framework: fixed costs 50-60%, savings 15-20%, guilt-free spending 20-35%. If they're in the savings target, spending more IS the right answer. Don't be the advisor who makes people feel guilty for living.
