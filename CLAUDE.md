# Personal Finance Project

Personal financial analysis toolkit using Plaid CLI + SQLite ledger + Claude Code.

## Architecture

- **Data sources:** Plaid CLI (live sync) + bank statement CSVs (historical backfill)
- **Storage:** Unified SQLite ledger at `data/finance.db` (all transactions deduped)
- **Sync:** `scripts/sync.sh` pulls from Plaid AND rebuilds the database
- **Analysis:** Claude Code skills query the SQLite database directly

## Workflow

1. Run `bash scripts/sync.sh` to pull fresh data and update the ledger
2. Ask questions conversationally — skills query `data/finance.db`
3. To add historical data: drop CSVs into `data/statements/`, then run `python3 scripts/ingest.py`
4. Weekly reports generated to `reports/weekly/`

## Key Commands

```bash
bash scripts/sync.sh                      # sync from Plaid + rebuild DB
python3 scripts/ingest.py                 # rebuild DB from all sources (no Plaid call)
python3 scripts/parse-statements.py       # find HSA-eligible expenses in CSVs
sqlite3 data/finance.db "SELECT ..."      # direct query
```

## Database Schema

```sql
transactions (
  id TEXT PRIMARY KEY,        -- SHA256 hash for dedup
  date TEXT,                  -- ISO YYYY-MM-DD
  description TEXT,
  amount REAL,                -- POSITIVE = spent, NEGATIVE = income
  merchant TEXT,
  category TEXT,              -- Plaid category (may be empty for CSV)
  account_name TEXT,
  account_mask TEXT,          -- last 4 digits
  account_type TEXT,          -- depository, credit, loan, investment
  institution TEXT,
  source TEXT,                -- 'plaid' or 'csv'
  source_file TEXT
);

accounts (
  account_id TEXT PRIMARY KEY,
  name TEXT, type TEXT, subtype TEXT, mask TEXT,
  institution_id TEXT,
  balance_current REAL, balance_available REAL, balance_limit REAL,
  last_updated TEXT
);
```

## Data Coverage

- **Plaid (live):** March 6, 2026 – present (rolling 30-day sync window)
- **Amex CSVs:** January 2025 – February 2026 (Platinum + Gold)
- **Chase PDFs:** December 2025 – February 2026 (read manually, not in DB yet)
- **Total:** ~2,274 transactions, Jan 2025 – Jun 2026

## Adding Historical Data

1. Download CSV from bank website (Activity → Download → CSV)
2. Drop into `data/statements/`
3. Run `python3 scripts/ingest.py`
4. Supports: Amex, Chase, Capital One, generic CSV formats

## Conventions

- POSITIVE amounts = money spent (debits)
- NEGATIVE amounts = money received (credits/income)
- Dates are ISO 8601 (YYYY-MM-DD)
- Deduplication by hash of (date, description, amount, account_mask)
- Never commit financial data or secrets to git
