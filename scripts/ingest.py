#!/usr/bin/env python3
"""
Ingest all financial data into a unified SQLite ledger.

Sources:
  - Plaid JSON files (data/snapshots/, data/latest/)
  - CSV statements (data/statements/)
  - Chase PDF statements (parsed manually, stored as JSON)

Deduplicates by (date, description, amount, account_hint).
Run after every Plaid sync or when new CSVs are added.

Usage: python3 scripts/ingest.py
"""

import csv
import json
import os
import sqlite3
import hashlib
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DB_PATH = PROJECT_DIR / "data" / "finance.db"
SNAPSHOTS_DIR = PROJECT_DIR / "data" / "snapshots"
LATEST_DIR = PROJECT_DIR / "data" / "latest"
STATEMENTS_DIR = PROJECT_DIR / "data" / "statements"


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT,
            category TEXT,
            account_name TEXT,
            account_mask TEXT,
            account_type TEXT,
            institution TEXT,
            source TEXT,
            source_file TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            name TEXT,
            official_name TEXT,
            type TEXT,
            subtype TEXT,
            mask TEXT,
            institution_id TEXT,
            balance_current REAL,
            balance_available REAL,
            balance_limit REAL,
            last_updated TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_txn_category ON transactions(category);
        CREATE INDEX IF NOT EXISTS idx_txn_merchant ON transactions(merchant);
        CREATE INDEX IF NOT EXISTS idx_txn_amount ON transactions(amount);
        CREATE INDEX IF NOT EXISTS idx_txn_account ON transactions(account_mask);
    """)


def make_txn_id(date, description, amount, account_hint=""):
    raw = f"{date}|{description.strip().lower()}|{amount:.2f}|{account_hint}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def ingest_plaid_json(conn, filepath):
    """Ingest a Plaid transactions JSON file."""
    inserted = 0
    with open(filepath) as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if "items" not in obj:
                    continue
                for item in obj["items"]:
                    inst = item.get("item", {}).get("institution_id", "")
                    accounts = {a["account_id"]: a for a in item.get("accounts", [])}

                    for t in item.get("transactions", []):
                        acct = accounts.get(t.get("account_id", ""), {})
                        desc = t.get("name") or t.get("merchant_name") or ""
                        merchant = t.get("merchant_name") or ""
                        amount = t.get("amount", 0)
                        date = t.get("date", "")
                        mask = acct.get("mask", "")

                        pfc = t.get("personal_finance_category", {}) or {}
                        category = pfc.get("primary", "")

                        txn_id = make_txn_id(date, desc, amount, mask)

                        try:
                            conn.execute("""
                                INSERT OR IGNORE INTO transactions
                                (id, date, description, amount, merchant, category,
                                 account_name, account_mask, account_type, institution,
                                 source, source_file)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                txn_id, date, desc, amount, merchant, category,
                                acct.get("name", ""), mask,
                                acct.get("type", ""), inst,
                                "plaid", filepath.name
                            ))
                            inserted += 1
                        except sqlite3.IntegrityError:
                            pass
            except json.JSONDecodeError:
                continue
    return inserted


def detect_csv_format(headers):
    headers_lower = [h.lower().strip() for h in headers]
    if "card member" in headers_lower or "appears on your statement as" in headers_lower:
        return "amex"
    if "posting date" in headers_lower:
        return "chase"
    if "transaction date" in headers_lower:
        return "capital_one"
    if headers_lower == ["date", "description", "amount", "account"]:
        return "chase_manual"
    return "generic"


def ingest_csv(conn, filepath):
    """Ingest a bank statement CSV."""
    inserted = 0
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        fmt = detect_csv_format(headers)

        for row in reader:
            try:
                if fmt == "amex":
                    date_raw = row.get("Date", "")
                    desc = row.get("Description", "")
                    amount_str = row.get("Amount", "0")
                    account_num = row.get("Account #", "")
                    mask = account_num[-4:] if account_num else ""
                    institution = "amex"
                elif fmt == "chase":
                    date_raw = row.get("Posting Date", row.get("Transaction Date", ""))
                    desc = row.get("Description", "")
                    amount_str = row.get("Amount", "0")
                    mask = ""
                    institution = "chase"
                elif fmt == "chase_manual":
                    date_raw = row.get("Date", "")
                    desc = row.get("Description", "")
                    amount_str = row.get("Amount", "0")
                    mask = row.get("Account", "")
                    institution = "chase"
                elif fmt == "capital_one":
                    date_raw = row.get("Transaction Date", "")
                    desc = row.get("Description", "")
                    amount_str = row.get("Debit", "") or row.get("Credit", "0")
                    mask = ""
                    institution = "capital_one"
                else:
                    date_raw = row.get("Date", list(row.values())[0] if row else "")
                    desc = row.get("Description", row.get("Name", ""))
                    amount_str = row.get("Amount", row.get("Debit", "0"))
                    mask = ""
                    institution = "unknown"

                amount_str = str(amount_str).replace("$", "").replace(",", "").strip()
                if not amount_str:
                    continue
                amount = float(amount_str)

                # Normalize date to ISO format (MM/DD/YYYY → YYYY-MM-DD)
                date = date_raw.strip()
                if "/" in date:
                    parts = date.split("/")
                    if len(parts) == 3:
                        m, d, y = parts
                        if len(y) == 2:
                            y = "20" + y
                        date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

                if not date or not desc:
                    continue

                txn_id = make_txn_id(date, desc, amount, mask)

                conn.execute("""
                    INSERT OR IGNORE INTO transactions
                    (id, date, description, amount, merchant, category,
                     account_name, account_mask, account_type, institution,
                     source, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    txn_id, date, desc, amount, "", "",
                    "", mask, "", institution,
                    "csv", filepath.name
                ))
                inserted += 1
            except (ValueError, TypeError):
                continue
    return inserted


def ingest_accounts(conn):
    """Update accounts table from latest balances."""
    balances_file = LATEST_DIR / "balances.json"
    if not balances_file.exists():
        return 0

    updated = 0
    with open(balances_file) as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if "items" not in obj:
                    continue
                for item in obj["items"]:
                    inst = item.get("item", {}).get("institution_id", "")
                    for acct in item.get("accounts", []):
                        bal = acct.get("balances", {})
                        conn.execute("""
                            INSERT OR REPLACE INTO accounts
                            (account_id, name, official_name, type, subtype, mask,
                             institution_id, balance_current, balance_available,
                             balance_limit, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        """, (
                            acct.get("account_id", ""),
                            acct.get("name", ""),
                            acct.get("official_name", ""),
                            acct.get("type", ""),
                            acct.get("subtype", ""),
                            acct.get("mask", ""),
                            inst,
                            bal.get("current"),
                            bal.get("available"),
                            bal.get("limit"),
                        ))
                        updated += 1
            except json.JSONDecodeError:
                continue
    return updated


def main():
    os.makedirs(DB_PATH.parent, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    init_db(conn)

    total_inserted = 0

    # Ingest Plaid snapshots
    print("Ingesting Plaid snapshots...")
    for f in sorted(SNAPSHOTS_DIR.glob("transactions-*.json")):
        count = ingest_plaid_json(conn, f)
        if count > 0:
            print(f"  {f.name}: {count} new")
        total_inserted += count

    # Ingest latest
    latest_txn = LATEST_DIR / "transactions.json"
    if latest_txn.exists():
        count = ingest_plaid_json(conn, latest_txn)
        if count > 0:
            print(f"  latest/transactions.json: {count} new")
        total_inserted += count

    # Ingest CSVs
    print("Ingesting CSV statements...")
    for f in sorted(STATEMENTS_DIR.glob("*.csv")):
        count = ingest_csv(conn, f)
        if count > 0:
            print(f"  {f.name}: {count} new")
        total_inserted += count

    # Update accounts
    print("Updating account balances...")
    acct_count = ingest_accounts(conn)
    print(f"  {acct_count} accounts updated")

    conn.commit()

    # Summary
    cursor = conn.execute("SELECT COUNT(*) FROM transactions")
    total = cursor.fetchone()[0]
    cursor = conn.execute("SELECT MIN(date), MAX(date) FROM transactions")
    min_date, max_date = cursor.fetchone()

    print()
    print(f"Database: {DB_PATH}")
    print(f"Total transactions: {total}")
    print(f"Date range: {min_date} to {max_date}")
    print(f"New this run: {total_inserted}")

    conn.close()


if __name__ == "__main__":
    main()
