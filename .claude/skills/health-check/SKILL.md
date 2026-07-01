---
name: health-check
description: >
  Quarterly financial health assessment. Use when the user asks for a full
  financial review, health check, "how am I doing", quarterly review, ratio
  check, financial assessment, or wants to know if they're on track. Also use
  when more than 30 days have passed since the last health check. Compares
  current state against goals, checks all key ratios, identifies which layer
  of the financial pyramid needs attention, and produces a prioritized action plan.
  Spawns research agents for tactical implementation details.
allowed-tools: Bash, Read, Agent
---

## Quarterly Financial Health Assessment

You are conducting a comprehensive financial health review — the most important
thing a fiduciary advisor does. This is NOT a spending summary (that's /weekly-report).
This is a full diagnostic: are they on track, what's at risk, and what needs to change?

### Process

1. Gather current state from the database
2. Compare against their goals and targets (from Client Context or memory)
3. Assess each layer of the Financial Planning Pyramid
4. Check all key ratios
5. Identify the #1 priority
6. Deliver a structured assessment with specific next actions

---

### Step 1: Gather Current State

```bash
# Account balances
sqlite3 data/finance.db "SELECT name, mask, type, balance_current, balance_limit FROM accounts ORDER BY type, balance_current DESC;"
```

```bash
# Monthly income (last 3 months)
sqlite3 data/finance.db "
SELECT strftime('%Y-%m', date) as month, ROUND(SUM(ABS(amount)), 2) as income
FROM transactions WHERE amount < 0
  AND date >= date('now', '-90 days')
  AND description NOT LIKE '%TRANSFER%'
  AND description NOT LIKE '%Payment%Thank%'
  AND description NOT LIKE '%EPAYMENT%'
  AND description NOT LIKE '%AUTOPAY%'
GROUP BY month ORDER BY month;"
```

```bash
# Monthly spending (last 3 months)
sqlite3 data/finance.db "
SELECT strftime('%Y-%m', date) as month, ROUND(SUM(amount), 2) as spending
FROM transactions WHERE amount > 0
  AND date >= date('now', '-90 days')
  AND description NOT LIKE '%AMERICAN EXPRESS ACH%'
  AND description NOT LIKE '%Coinbase Card Payment%'
  AND description NOT LIKE '%Payment to Chase%'
  AND description NOT LIKE '%AMEX EPAYMENT%'
  AND description NOT LIKE '%APPLECARD GSBANK%'
  AND description NOT LIKE '%AUTOPAY%'
  AND description NOT LIKE '%AUTO PAY%'
GROUP BY month ORDER BY month;"
```

```bash
# Interest and fees (last 90 days)
sqlite3 data/finance.db "
SELECT strftime('%Y-%m', date) as month, ROUND(SUM(amount), 2) as fees_interest
FROM transactions WHERE amount > 0
  AND date >= date('now', '-90 days')
  AND (LOWER(description) LIKE '%interest%' OR LOWER(description) LIKE '%late fee%' OR LOWER(description) LIKE '%fee%')
GROUP BY month ORDER BY month;"
```

```bash
# Dining vs groceries (last 90 days for ratio)
sqlite3 data/finance.db "
SELECT
  ROUND(SUM(CASE WHEN LOWER(description) LIKE '%restaurant%' OR LOWER(description) LIKE '%bar %'
    OR LOWER(description) LIKE '%grill%' OR LOWER(description) LIKE '%doordash%'
    OR LOWER(description) LIKE '%uber eats%' OR LOWER(description) LIKE '%pizza%'
    OR LOWER(description) LIKE '%cafe%' OR LOWER(description) LIKE '%tavern%'
    OR LOWER(description) LIKE '%brewing%' OR LOWER(description) LIKE '%taqueria%'
    THEN amount ELSE 0 END), 2) as dining,
  ROUND(SUM(CASE WHEN LOWER(description) LIKE '%kroger%' OR LOWER(description) LIKE '%aldi%'
    OR LOWER(description) LIKE '%trader joe%' OR LOWER(description) LIKE '%whole foods%'
    OR LOWER(description) LIKE '%walmart%' OR LOWER(description) LIKE '%instacart%'
    OR LOWER(description) LIKE '%grocery%' OR LOWER(description) LIKE '%safeway%'
    OR LOWER(description) LIKE '%costco%' OR LOWER(description) LIKE '%publix%'
    THEN amount ELSE 0 END), 2) as groceries
FROM transactions WHERE amount > 0 AND date >= date('now', '-90 days');"
```

---

### Step 2: Load Goals and Targets

Read the Client Context from CLAUDE.md (the `## Client Context` section) and/or
check memory files for `user_financial-profile.md` or `project_financial-goals.md`.

If no goals are set, use the universal defaults from CLAUDE.md:
- Savings rate: 15-25% of gross
- Emergency fund: 3-6 months expenses
- Dining:Grocery ratio: ≤1.0x
- Interest/fees: $0 target
- DTI: <36%
- Housing: <28% of gross
- Credit utilization: <30% per card

---

### Step 3: Financial Planning Pyramid Assessment

Assess each layer bottom-up. The lowest unstable layer is the priority.

```
Layer 5: LEGACY         — Estate planning, wealth transfer
Layer 4: FREEDOM        — Aspirational goals, lifestyle choices
Layer 3: ACCUMULATION   — Investing, retirement, goal funding
Layer 2: SAFETY         — Emergency fund, insurance, stable cash flow
Layer 1: PROTECTION     — Basic expenses covered, high-interest debt managed, no fees
```

For each layer, assign: STABLE / AT RISK / UNSTABLE / NOT ASSESSED

**Layer 1 (Protection):**
- Are basic expenses covered by income? (income > fixed costs)
- Any high-interest debt (>7% APR) without a paydown plan?
- Fees/interest bleeding? ($0 is the target)
- All accounts on autopay?

**Layer 2 (Safety):**
- Emergency fund adequate? (months of expenses vs. target)
- Income stable or diversified?
- Health/life/disability insurance adequate?
- Cash flow positive or negative?

**Layer 3 (Accumulation):**
- Capturing employer match?
- Savings rate on target?
- Tax-advantaged accounts being utilized?
- Investment allocation age-appropriate?

**Layer 4 (Freedom):**
- Progress toward medium/long-term goals?
- Debt-free timeline on track?
- Income growth trajectory?

**Layer 5 (Legacy):**
- Estate docs in place?
- Beneficiaries updated?
- (Often N/A for younger clients)

---

### Step 4: Ratio Check

Calculate and present ALL applicable ratios:

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Savings rate | calc | from goals | ✅/⚠️/🔴 |
| Emergency fund (months) | calc | from goals | ✅/⚠️/🔴 |
| Dining:Grocery | calc | ≤1.0x | ✅/⚠️/🔴 |
| Interest & fees / month | calc | $0 | ✅/⚠️/🔴 |
| Worst card utilization | calc | <30% | ✅/⚠️/🔴 |
| Total debt-to-income | calc | <36% | ✅/⚠️/🔴 |

Use: ✅ on target, ⚠️ within 20% of red flag, 🔴 at or past red flag

---

### Step 5: Output Format

Present the assessment in this structure:

```
## Financial Health Check — [Date]

### Overall: [HEALTHY / CAUTION / ACTION NEEDED]

### Pyramid Status
| Layer | Status | Key Issue |
...

### Key Ratios
| Metric | Current | Target | Status |
...

### What's Working
- [2-3 things that are on track or improved since last check]

### What Needs Attention
- [Ranked by priority — the lowest unstable pyramid layer first]

### Top 3 Actions (This Quarter)
1. [Most important — addresses lowest pyramid layer]
2. [Second priority]
3. [Third priority]

### Comparison to Last Check
[If previous health check exists in reports/, compare key metrics]
```

---

### Step 6: Tactical Research for Top Actions

For each of the top 3 actions, spawn a research agent to find the best
implementation path using the user's specific accounts and tools.

Use the Agent tool:

```
For each priority action, spawn an agent with a prompt like:

"The user's top financial priority is: [action from Step 5, e.g., 'eliminate 
$130/month in credit card interest']. Their accounts are: [list relevant accounts 
with balances and limits]. Research the optimal tactical path:
- Which specific account to use and why
- Whether a balance transfer, refinance, or consolidation would be cheaper
- Current promo rates available on their existing cards
- Step-by-step execution instructions
- Timeline and milestone targets
Return a specific, actionable implementation plan — not generic advice."
```

Only research actions where the tactical path isn't obvious. "Set up autopay"
doesn't need research. "Reduce $600/month in interest charges" does.

Incorporate the tactical findings into the Top 3 Actions section:

```
### Top 3 Actions (This Quarter)

1. **[Strategic action]**
   - **Tactic:** [Specific implementation using their accounts]
   - **Saves:** $[amount]/month
   - **Steps:** [1, 2, 3]
   - **Timeline:** [When to complete by]

2. ...
```

---

### Step 7: Save

Save the report to `reports/health-check-YYYY-MM-DD.md` for future comparison.

---

### Behavioral Awareness

When presenting findings, account for the user's behavioral profile:
- If they tend to freeze under stress → lead with what's working, then the ONE most important fix
- If they're action-oriented → give them the ranked list and let them execute
- If they prefer automation → frame actions as "set up X once and never think about it again"
- Always frame in terms of their stated values (freedom, security, growth, legacy)

Never present more than 3 priority actions. Cognitive overload kills follow-through.
