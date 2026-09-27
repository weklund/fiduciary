#!/usr/bin/env python3
"""
Ingest all financial data into a unified SQLite ledger.

Sources:
  - Plaid JSON files (data/snapshots/, data/latest/)
  - CSV statements (data/statements/)

Plaid rows deduplicate by Plaid transaction_id; CSV rows by
(date, description, amount, account_mask). Pending Plaid transactions are
kept only from the latest sync, since they change ID when they post.
Run after every Plaid sync or when new CSVs are added.

Usage: python3 scripts/ingest.py
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from finance import CsvParser, PlaidParser, TransactionRepository

PROJECT_DIR = Path(__file__).parent.parent
DB_PATH = PROJECT_DIR / "data" / "finance.db"
SNAPSHOTS_DIR = PROJECT_DIR / "data" / "snapshots"
LATEST_DIR = PROJECT_DIR / "data" / "latest"
STATEMENTS_DIR = PROJECT_DIR / "data" / "statements"


def main() -> None:
    os.umask(0o077)
    os.makedirs(DB_PATH.parent, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    repo = TransactionRepository(conn, db_path=DB_PATH)

    if not repo.check_integrity():
        print("WARNING: Database integrity check failed.")
        print("Consider deleting data/finance.db and re-running to rebuild.")

    repo.init_schema()

    plaid_parser = PlaidParser()
    csv_parser = CsvParser()

    total_before = repo.get_summary()["total"]

    # Pending rows are rebuilt from the latest sync on every run
    repo.delete_pending("plaid")

    # Ingest latest first, then snapshots newest-first: the first version of a
    # transaction_id wins, so each row reflects its most recent sync.
    print("Ingesting Plaid snapshots...")
    latest_txn = LATEST_DIR / "transactions.json"
    if latest_txn.exists():
        txns = plaid_parser.parse(latest_txn)
        count = repo.insert_transactions(txns)
        if count > 0:
            print(f"  latest/transactions.json: {count} new")

    for f in sorted(SNAPSHOTS_DIR.glob("transactions-*.json"), reverse=True):
        txns = [t for t in plaid_parser.parse(f) if not t.pending]
        count = repo.insert_transactions(txns)
        if count > 0:
            print(f"  {f.name}: {count} new")

    # Ingest CSVs
    print("Ingesting CSV statements...")
    for f in sorted(STATEMENTS_DIR.glob("*.csv")):
        txns = csv_parser.parse(f)
        count = repo.insert_transactions(txns)
        if count > 0:
            print(f"  {f.name}: {count} new")

    # Update accounts
    print("Updating account balances...")
    balances_file = LATEST_DIR / "balances.json"
    acct_count = repo.update_accounts(balances_file)
    print(f"  {acct_count} accounts updated")

    repo.commit()

    # Summary
    summary = repo.get_summary()
    print()
    print(f"Database: {DB_PATH}")
    print(f"Total transactions: {summary['total']}")
    print(f"Date range: {summary['min_date']} to {summary['max_date']}")
    print(f"New this run: {summary['total'] - total_before}")

    repo.close()
    repo.secure()


if __name__ == "__main__":
    main()
