---
name: sync-data
description: >
  Sync fresh financial data from Plaid. Use when the user asks to refresh data,
  pull latest transactions, update balances, or before running any analysis
  on data that might be stale (more than a day old).
allowed-tools: Bash
---

## Instructions

Run the sync script to pull fresh data from all linked Plaid accounts:

```bash
bash scripts/sync.sh
```

After syncing, confirm what was updated and note the date. If the sync fails because Plaid CLI is not installed or not logged in, tell the user the setup steps:

1. `brew install plaid/plaid-cli/plaid`
2. `plaid login` (or `plaid register` for new accounts)
3. `plaid link` (to connect bank accounts)
