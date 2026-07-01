"""Tests for Transaction and Account models."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from finance.models import Transaction, Account


class TestTransactionId:
    """Test Transaction.id hash generation."""

    def test_id_is_deterministic(self):
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        assert txn1.id == txn2.id

    def test_id_is_16_chars(self):
        txn = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        assert len(txn.id) == 16

    def test_id_is_hex(self):
        txn = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        assert all(c in "0123456789abcdef" for c in txn.id)

    def test_id_changes_with_date(self):
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-16", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        assert txn1.id != txn2.id

    def test_id_changes_with_description(self):
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-15", description="TEA HOUSE", amount=4.50, account_mask="5832")
        assert txn1.id != txn2.id

    def test_id_changes_with_amount(self):
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=5.00, account_mask="5832")
        assert txn1.id != txn2.id

    def test_id_changes_with_account_mask(self):
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="1023")
        assert txn1.id != txn2.id

    def test_id_case_insensitive_description(self):
        """Description is lowercased before hashing."""
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-15", description="coffee shop", amount=4.50, account_mask="5832")
        assert txn1.id == txn2.id

    def test_id_strips_description(self):
        """Description is stripped before hashing."""
        txn1 = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50, account_mask="5832")
        txn2 = Transaction(date="2025-03-15", description="  COFFEE SHOP  ", amount=4.50, account_mask="5832")
        assert txn1.id == txn2.id

    def test_id_empty_mask(self):
        """Default empty mask still produces a valid hash."""
        txn = Transaction(date="2025-03-15", description="COFFEE SHOP", amount=4.50)
        assert len(txn.id) == 16


class TestAccount:
    """Test Account dataclass."""

    def test_account_creation(self):
        acct = Account(
            account_id="acct_001",
            name="Checking",
            type="depository",
            mask="5832",
        )
        assert acct.account_id == "acct_001"
        assert acct.name == "Checking"
        assert acct.balance_current is None
