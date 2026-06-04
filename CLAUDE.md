# Personal Finance Project

Personal financial analysis toolkit using Plaid CLI + Claude Code.

## Architecture

- **Data source:** Plaid CLI (`plaid balance --json`, `plaid transactions list --json`, `plaid liabilities --json`)
- **Storage:** JSON snapshots in `data/snapshots/` (gitignored), synced via `scripts/sync.sh`
- **Analysis:** Claude Code skills that read the latest snapshot and answer questions

## Workflow

1. Run `scripts/sync.sh` to pull fresh data from Plaid (or use skills that call it automatically)
2. Ask questions conversationally — skills know where the data lives
3. Weekly reports generated to `reports/weekly/`

## Plaid CLI Setup (one-time)

```bash
brew install plaid/plaid-cli/plaid
plaid register          # or plaid login
plaid link              # connects bank accounts via browser
```

## Key Commands

```bash
plaid balance --json                      # all account balances
plaid transactions list --json            # recent transactions
plaid transactions list --count 500 --json  # more history
plaid liabilities --json                  # credit card details
plaid investments holdings --json         # investment positions
plaid investments transactions --json     # investment activity
```

## Data Location

All financial data lives in `data/` (gitignored):
- `data/snapshots/balances-YYYY-MM-DD.json`
- `data/snapshots/transactions-YYYY-MM-DD.json`
- `data/snapshots/liabilities-YYYY-MM-DD.json`
- `data/snapshots/investments-YYYY-MM-DD.json`
- `data/latest/` — symlinks or copies of the most recent snapshot

## Conventions

- All amounts from Plaid are POSITIVE for debits (money spent) and NEGATIVE for credits (income/refunds)
- Dates are ISO 8601 (YYYY-MM-DD)
- Categories come from Plaid's enriched category taxonomy
- Never commit financial data or secrets to git
