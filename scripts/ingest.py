#!/usr/bin/env python3
"""
Ingest all financial data into a unified SQLite ledger.

Sources:
  - Plaid JSON files (data/snapshots/, data/latest/)
  - CSV statements (data/statements/)

Deduplicates by (date, description, amount, account_hint).
Run after every Plaid sync or when new CSVs are added.

Usage: python3 scripts/ingest.py
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from finance import PlaidParser, CsvParser, TransactionRepository

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
    total_inserted = 0

    # Ingest Plaid snapshots
    print("Ingesting Plaid snapshots...")
    for f in sorted(SNAPSHOTS_DIR.glob("transactions-*.json")):
        txns = plaid_parser.parse(f)
        count = repo.insert_transactions(txns)
        if count > 0:
            print(f"  {f.name}: {count} new")
        total_inserted += count

    # Ingest latest
    latest_txn = LATEST_DIR / "transactions.json"
    if latest_txn.exists():
        txns = plaid_parser.parse(latest_txn)
        count = repo.insert_transactions(txns)
        if count > 0:
            print(f"  latest/transactions.json: {count} new")
        total_inserted += count

    # Ingest CSVs
    print("Ingesting CSV statements...")
    for f in sorted(STATEMENTS_DIR.glob("*.csv")):
        txns = csv_parser.parse(f)
        count = repo.insert_transactions(txns)
        if count > 0:
            print(f"  {f.name}: {count} new")
        total_inserted += count

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
    print(f"New this run: {total_inserted}")

    repo.close()
    repo.secure()


if __name__ == "__main__":
    main()
