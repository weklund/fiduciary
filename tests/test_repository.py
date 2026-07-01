"""Tests for TransactionRepository."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from finance.models import Transaction
from finance.repository import TransactionRepository


class TestInsertTransactions:
    """Test inserting transactions into the repository."""

    def test_insert_returns_count(self, repo, sample_transactions):
        count = repo.insert_transactions(sample_transactions)
        assert count == 3

    def test_insert_persists_data(self, tmp_db, sample_transactions):
        repo = TransactionRepository(tmp_db)
        repo.insert_transactions(sample_transactions)
        cursor = tmp_db.execute("SELECT COUNT(*) FROM transactions")
        assert cursor.fetchone()[0] == 3

    def test_insert_correct_fields(self, tmp_db, sample_transactions):
        repo = TransactionRepository(tmp_db)
        repo.insert_transactions(sample_transactions)
        cursor = tmp_db.execute(
            "SELECT date, description, amount, merchant, category, "
            "account_name, account_mask, account_type, institution, source "
            "FROM transactions WHERE description = 'ACME COFFEE SHOP'"
        )
        row = cursor.fetchone()
        assert row == (
            "2025-03-15", "ACME COFFEE SHOP", 4.50, "ACME COFFEE SHOP",
            "FOOD_AND_DRINK", "Checking", "5832", "depository", "ins_123", "plaid"
        )


class TestDeduplication:
    """Test that duplicate transactions are ignored."""

    def test_duplicate_not_inserted_twice(self, repo, sample_transactions):
        repo.insert_transactions(sample_transactions)
        count = repo.insert_transactions(sample_transactions)
        assert count == 0

    def test_total_stays_same_after_duplicate(self, tmp_db, sample_transactions):
        repo = TransactionRepository(tmp_db)
        repo.insert_transactions(sample_transactions)
        repo.insert_transactions(sample_transactions)
        cursor = tmp_db.execute("SELECT COUNT(*) FROM transactions")
        assert cursor.fetchone()[0] == 3


class TestUpdateAccounts:
    """Test account balance updates."""

    def test_update_accounts_from_file(self, tmp_db, tmp_path):
        balances_file = tmp_path / "balances.json"
        data = {
            "items": [{
                "item": {"institution_id": "ins_109508"},
                "accounts": [
                    {
                        "account_id": "acct_001",
                        "name": "Checking",
                        "official_name": "TOTAL CHECKING",
                        "type": "depository",
                        "subtype": "checking",
                        "mask": "5832",
                        "balances": {"current": 2450.75, "available": 2400.00, "limit": None},
                    }
                ],
            }]
        }
        balances_file.write_text(json.dumps(data) + "\n")

        repo = TransactionRepository(tmp_db)
        count = repo.update_accounts(balances_file)
        assert count == 1

        cursor = tmp_db.execute(
            "SELECT name, balance_current, balance_available FROM accounts WHERE account_id = 'acct_001'"
        )
        row = cursor.fetchone()
        assert row == ("Checking", 2450.75, 2400.00)

    def test_update_accounts_nonexistent_file(self, tmp_db, tmp_path):
        repo = TransactionRepository(tmp_db)
        count = repo.update_accounts(tmp_path / "nonexistent.json")
        assert count == 0

    def test_update_accounts_replaces_existing(self, tmp_db, tmp_path):
        balances_file = tmp_path / "balances.json"

        def write_balance(current):
            data = {
                "items": [{
                    "item": {"institution_id": "ins_109508"},
                    "accounts": [{
                        "account_id": "acct_001",
                        "name": "Checking",
                        "official_name": "",
                        "type": "depository",
                        "subtype": "checking",
                        "mask": "5832",
                        "balances": {"current": current, "available": current, "limit": None},
                    }],
                }]
            }
            balances_file.write_text(json.dumps(data) + "\n")

        repo = TransactionRepository(tmp_db)
        write_balance(1000.00)
        repo.update_accounts(balances_file)

        write_balance(2000.00)
        repo.update_accounts(balances_file)

        cursor = tmp_db.execute(
            "SELECT balance_current FROM accounts WHERE account_id = 'acct_001'"
        )
        assert cursor.fetchone()[0] == 2000.00


class TestCheckIntegrity:
    """Test database integrity check."""

    def test_clean_db_passes(self, repo):
        assert repo.check_integrity() is True


class TestGetSummary:
    """Test summary reporting."""

    def test_summary_empty_db(self, repo):
        summary = repo.get_summary()
        assert summary["total"] == 0
        assert summary["min_date"] is None
        assert summary["max_date"] is None

    def test_summary_with_data(self, repo, sample_transactions):
        repo.insert_transactions(sample_transactions)
        summary = repo.get_summary()
        assert summary["total"] == 3
        assert summary["min_date"] == "2025-03-15"
        assert summary["max_date"] == "2025-03-17"
