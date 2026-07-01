"""Shared test fixtures for the finance package tests."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import the finance package
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from finance import TransactionRepository, Transaction


@pytest.fixture
def tmp_db():
    """Create an in-memory SQLite DB with the full schema initialized."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA journal_mode=WAL")
    repo = TransactionRepository(conn)
    repo.init_schema()
    yield conn
    conn.close()


@pytest.fixture
def repo(tmp_db):
    """TransactionRepository backed by the in-memory test DB."""
    return TransactionRepository(tmp_db)


@pytest.fixture
def sample_transactions():
    """A list of sample Transaction objects for testing."""
    return [
        Transaction(
            date="2025-03-15",
            description="ACME COFFEE SHOP",
            amount=4.50,
            merchant="ACME COFFEE SHOP",
            category="FOOD_AND_DRINK",
            account_name="Checking",
            account_mask="5832",
            account_type="depository",
            institution="ins_123",
            source="plaid",
            source_file="transactions-2025-03-15.json",
        ),
        Transaction(
            date="2025-03-16",
            description="MEGA GROCERY STORE",
            amount=67.23,
            merchant="MEGA GROCERY STORE",
            category="FOOD_AND_DRINK",
            account_name="Gold Card",
            account_mask="1023",
            account_type="credit",
            institution="ins_456",
            source="plaid",
            source_file="transactions-2025-03-15.json",
        ),
        Transaction(
            date="2025-03-17",
            description="NETFLIX.COM",
            amount=15.99,
            merchant="Netflix",
            category="ENTERTAINMENT",
            account_name="Platinum Card",
            account_mask="1007",
            account_type="credit",
            institution="ins_456",
            source="csv",
            source_file="amex_2025_03.csv",
        ),
    ]


@pytest.fixture
def fixtures_dir():
    """Path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"
