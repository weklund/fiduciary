---
name: spending-audit
description: >
  Audit spending for waste, unused subscriptions, and overspending by category.
  Use when the user asks to find waste, cut spending, review subscriptions,
  check for recurring charges they forgot about, or do a financial audit.
allowed-tools: Bash, Read
---

## Instructions

Perform a spending audit to find waste and optimization opportunities.

### Data locations

- Transactions: `data/latest/transactions.json`
- Liabilities: `data/latest/liabilities.json`

### Analysis to perform

#### 1. Recurring charges / Subscriptions
- Find transactions that repeat monthly (same merchant, similar amount, ~30 day intervals)
- List each with: merchant name, amount, frequency, total annual cost
- Flag any that appear to be services/tools/subscriptions (streaming, SaaS, memberships)

#### 2. Category spending breakdown
- Group all spending by Plaid category
- Show monthly average per category
- Flag categories where spending is significantly above the median month

#### 3. Dining & delivery analysis
- Sum spending on restaurants, fast food, food delivery (DoorDash, UberEats, Grubhub, etc.)
- Calculate weekly average
- Compare to grocery spending as a ratio

#### 4. High-frequency merchants
- Find merchants where you transact most frequently
- Show count and total spend per merchant

### Output format

Present findings as:
1. **Subscriptions to review** — list with monthly cost, annual cost, last charge date
2. **Category red flags** — categories with unusually high spend
3. **Quick wins** — specific, actionable cuts with estimated monthly savings
4. **Dining/delivery score** — dining-to-grocery ratio with a recommendation

Be direct and specific. Name exact dollar amounts and merchants. Don't hedge — if something looks like waste, say so.
