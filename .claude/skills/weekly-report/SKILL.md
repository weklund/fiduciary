---
name: weekly-report
description: >
  Generate a weekly personal finance report. Use when the user asks for a
  weekly report, spending summary, finance review, or budget status.
allowed-tools: Bash, Read, Write
---

## Instructions

Generate a weekly finance report from the unified SQLite ledger.

### Data source

Primary: `data/finance.db` (SQLite)

Before generating, check if data is fresh: 
```bash
sqlite3 data/finance.db "SELECT MAX(date) FROM transactions"
```
If older than 2 days, suggest running `bash scripts/sync.sh` first.

### Report sections

#### 1. Account Summary
```sql
SELECT name, mask, type, balance_current, balance_limit,
       CASE WHEN balance_limit > 0 
            THEN ROUND(balance_current * 100.0 / balance_limit, 0) 
            ELSE NULL END as utilization_pct
FROM accounts ORDER BY type, balance_current DESC;
```

#### 2. Weekly Cash Flow (last 7 days)
```sql
SELECT 
  SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as income,
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as spending,
  SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) - 
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as net
FROM transactions 
WHERE date >= date('now', '-7 days');
```

#### 3. Spending by Category (top 10, last 7 days)
```sql
SELECT description, SUM(amount) as total, COUNT(*) as txns
FROM transactions 
WHERE amount > 0 AND date >= date('now', '-7 days')
GROUP BY description
ORDER BY total DESC LIMIT 15;
```

#### 4. Notable Transactions
- Largest single purchases (top 5)
- Any new recurring charges detected
- Fees or interest charges

```sql
-- Fees/interest this week
SELECT date, description, amount FROM transactions
WHERE date >= date('now', '-7 days') AND amount > 0
  AND (LOWER(description) LIKE '%fee%' 
    OR LOWER(description) LIKE '%interest%'
    OR LOWER(description) LIKE '%overdraft%')
ORDER BY amount DESC;
```

#### 5. Week-over-Week Comparison
```sql
-- This week vs last week
SELECT 
  'This week' as period,
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as spent
FROM transactions WHERE date >= date('now', '-7 days')
UNION ALL
SELECT 
  'Last week',
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END)
FROM transactions WHERE date >= date('now', '-14 days') AND date < date('now', '-7 days');
```

#### 6. Progress vs Goals
Track against debt elimination plan:
- Fees this week (target: $0)
- Dining spend (target: <$75/week)
- Subscription charges (flag any that should have been canceled)

### Output

Save to `reports/weekly/YYYY-MM-DD.md` AND display to the user.
Keep it concise — bullet points, not paragraphs. Lead with the most important numbers.
