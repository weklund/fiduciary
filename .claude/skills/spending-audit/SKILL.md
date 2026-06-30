---
name: spending-audit
description: >
  Audit spending for waste, unused subscriptions, and overspending by category.
  Use when the user asks to find waste, cut spending, review subscriptions,
  check for recurring charges they forgot about, or do a financial audit.
allowed-tools: Bash, Read
---

## Instructions

Perform a spending audit using the unified SQLite ledger.

### Data source

Primary: `data/finance.db` (SQLite)

### Analysis to perform

#### 1. Recurring charges / Subscriptions
```sql
-- Find merchants that appear monthly with consistent amounts
SELECT description, 
       ROUND(AVG(amount),2) as avg_amount,
       COUNT(*) as occurrences,
       MIN(date) as first_seen,
       MAX(date) as last_seen
FROM transactions 
WHERE amount > 0 AND amount < 500
GROUP BY description 
HAVING COUNT(*) >= 2 
   AND (MAX(date) > date('now', '-60 days'))
ORDER BY avg_amount * 12 DESC;
```

#### 2. Category spending breakdown
```sql
-- Monthly spending by category
SELECT substr(date,1,7) as month,
       SUM(amount) as total_spent,
       COUNT(*) as txn_count
FROM transactions 
WHERE amount > 0
GROUP BY month
ORDER BY month;
```

#### 3. Dining & delivery analysis
```sql
-- Find all dining/delivery/coffee (common national chains + generic patterns)
SELECT date, description, amount 
FROM transactions 
WHERE amount > 0 
  AND (LOWER(description) LIKE '%restaurant%'
    OR LOWER(description) LIKE '%coffee%'
    OR LOWER(description) LIKE '%doordash%'
    OR LOWER(description) LIKE '%uber eats%'
    OR LOWER(description) LIKE '%grubhub%'
    OR LOWER(description) LIKE '%chipotle%'
    OR LOWER(description) LIKE '%starbucks%'
    OR LOWER(description) LIKE '%mcdonald%'
    OR LOWER(description) LIKE '%bar %'
    OR LOWER(description) LIKE '%grill%'
    OR LOWER(description) LIKE '%brewing%'
    OR LOWER(description) LIKE '%tavern%'
    OR LOWER(description) LIKE '%pizza%'
    OR LOWER(description) LIKE '%taqueria%'
    OR LOWER(description) LIKE '%sushi%'
    OR LOWER(description) LIKE '%cafe%'
    OR LOWER(description) LIKE '%pub %'
    OR LOWER(description) LIKE '%bistro%')
ORDER BY date DESC;
```
Note: This query catches common patterns but will miss local restaurants. Supplement
by checking the Plaid `category` field if available, or look at merchants with
amounts in the $8-$80 range that appear on evenings/weekends.

#### 4. High-frequency merchants
```sql
SELECT description, COUNT(*) as times, SUM(amount) as total
FROM transactions WHERE amount > 0
GROUP BY description
ORDER BY total DESC LIMIT 30;
```

### Output format

1. **Subscriptions to review** — list with monthly cost, annual cost, last charge date
2. **Category red flags** — categories with unusually high spend
3. **Quick wins** — specific, actionable cuts with estimated monthly savings
4. **Dining/delivery score** — dining-to-grocery ratio with a recommendation

Be direct and specific. Name exact dollar amounts and merchants.
