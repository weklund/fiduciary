"""SQLite repository for financial transactions and accounts."""

from __future__ import annotations

import json
import os
import sqlite3
import stat
from pathlib import Path

from .models import Transaction


class TransactionRepository:
    """Manages all SQLite operations for the financial ledger."""

    def __init__(self, conn: sqlite3.Connection, db_path: Path | None = None):
        self._conn = conn
        self._db_path = db_path

    def init_schema(self) -> None:
        """Create tables and indexes if they don't exist."""
        self._conn.executescript("""
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

    def check_integrity(self) -> bool:
        """Run PRAGMA integrity_check. Returns True if DB is healthy."""
        result = self._conn.execute("PRAGMA integrity_check").fetchone()
        return result[0] == "ok"

    def insert_transactions(self, txns: list[Transaction]) -> int:
        """Bulk insert transactions with dedup via INSERT OR IGNORE.

        Returns the number of rows actually inserted (excludes duplicates).
        """
        inserted = 0
        for txn in txns:
            try:
                self._conn.execute(
                    """
                    INSERT OR IGNORE INTO transactions
                    (id, date, description, amount, merchant, category,
                     account_name, account_mask, account_type, institution,
                     source, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        txn.id,
                        txn.date,
                        txn.description,
                        txn.amount,
                        txn.merchant,
                        txn.category,
                        txn.account_name,
                        txn.account_mask,
                        txn.account_type,
                        txn.institution,
                        txn.source,
                        txn.source_file,
                    ),
                )
                if self._conn.execute("SELECT changes()").fetchone()[0] > 0:
                    inserted += 1
            except sqlite3.IntegrityError:
                pass
        return inserted

    def update_accounts(self, filepath: Path) -> int:
        """Update accounts table from a Plaid balances NDJSON file.

        Returns the number of accounts updated.
        """
        if not filepath.exists():
            return 0

        updated = 0
        with open(filepath) as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                if "items" not in obj:
                    continue

                for item in obj["items"]:
                    inst = item.get("item", {}).get("institution_id", "")
                    for acct in item.get("accounts", []):
                        bal = acct.get("balances", {})
                        self._conn.execute(
                            """
                            INSERT OR REPLACE INTO accounts
                            (account_id, name, official_name, type, subtype, mask,
                             institution_id, balance_current, balance_available,
                             balance_limit, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                            """,
                            (
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
                            ),
                        )
                        updated += 1
        return updated

    def get_summary(self) -> dict[str, object]:
        """Return a summary dict with count and date range."""
        cursor = self._conn.execute("SELECT COUNT(*) FROM transactions")
        total = cursor.fetchone()[0]
        cursor = self._conn.execute("SELECT MIN(date), MAX(date) FROM transactions")
        min_date, max_date = cursor.fetchone()
        return {
            "total": total,
            "min_date": min_date,
            "max_date": max_date,
        }

    def commit(self) -> None:
        """Commit the current transaction."""
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def secure(self) -> None:
        """Set restrictive file permissions on the database file (chmod 600)."""
        if self._db_path and self._db_path.exists():
            os.chmod(self._db_path, stat.S_IRUSR | stat.S_IWUSR)
