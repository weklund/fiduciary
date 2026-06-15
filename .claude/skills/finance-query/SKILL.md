---
name: finance-query
description: >
  Answer questions about personal finances — balances, transactions, spending
  patterns, account status, recent purchases, merchant history, income tracking.
  Use when the user asks anything about their money, accounts, or transactions.
allowed-tools: Bash, Read
---

## Instructions

Answer the user's financial question using the unified SQLite ledger.

### Data source

Primary: `data/finance.db` (SQLite — unified ledger of all transactions from Plaid + CSVs)

Query with: `sqlite3 data/finance.db "SELECT ..."`

Fallback (if DB missing): `data/latest/*.json`

### Schema

```sql
transactions (
  id TEXT PRIMARY KEY,
  date TEXT,           -- ISO format YYYY-MM-DD
  description TEXT,
  amount REAL,         -- POSITIVE = debit (money spent), NEGATIVE = credit (income/refund)
  merchant TEXT,
  category TEXT,       -- Plaid category (may be empty for CSV-sourced)
  account_name TEXT,
  account_mask TEXT,   -- last 4 digits
  account_type TEXT,   -- depository, credit, loan, investment
  institution TEXT,
  source TEXT,         -- 'plaid' or 'csv'
  source_file TEXT
);

accounts (
  account_id TEXT PRIMARY KEY,
  name TEXT,
  type TEXT,
  subtype TEXT,
  mask TEXT,
  institution_id TEXT,
  balance_current REAL,
  balance_available REAL,
  balance_limit REAL,
  last_updated TEXT
);
```

### Steps

1. Check if `data/finance.db` exists. If not, suggest running `python3 scripts/ingest.py` first.
2. Query the database using sqlite3 to answer the user's question.
3. Present results clearly with specific numbers, dates, and merchant names.

### Query patterns

```bash
# Date range spending
sqlite3 data/finance.db "SELECT description, amount, date FROM transactions WHERE date >= '2026-06-01' AND amount > 0 ORDER BY amount DESC LIMIT 20"

# Spending by merchant
sqlite3 data/finance.db "SELECT description, SUM(amount), COUNT(*) FROM transactions WHERE amount > 0 GROUP BY description ORDER BY SUM(amount) DESC LIMIT 20"

# Monthly totals
sqlite3 data/finance.db "SELECT substr(date,1,7) as month, SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as spent, SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as income FROM transactions GROUP BY month ORDER BY month"

# Search by merchant
sqlite3 data/finance.db "SELECT date, description, amount FROM transactions WHERE LOWER(description) LIKE '%quills%' ORDER BY date DESC"

# Account balances
sqlite3 data/finance.db "SELECT name, mask, type, balance_current, balance_limit FROM accounts ORDER BY balance_current DESC"

# Income sources
sqlite3 data/finance.db "SELECT date, description, ABS(amount) FROM transactions WHERE amount < 0 AND ABS(amount) > 100 ORDER BY date DESC LIMIT 20"
```

### Conventions

- **amount > 0** = money spent (debit)
- **amount < 0** = money received (credit/income)
- Dates are ISO format (YYYY-MM-DD)
- Always clarify the time period in your response
- Round dollar amounts to 2 decimal places
- Use `-header -column` for readable output: `sqlite3 -header -column data/finance.db "..."`
