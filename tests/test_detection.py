"""Tests for CSV format detection."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from finance.detection import detect_csv_format


class TestDetectCsvFormat:
    """Test detect_csv_format with various header configurations."""

    def test_amex_by_card_member(self):
        headers = ["Date", "Description", "Card Member", "Account #", "Amount"]
        assert detect_csv_format(headers) == "amex"

    def test_amex_by_statement_as(self):
        headers = ["Date", "Description", "Amount", "Appears On Your Statement As"]
        assert detect_csv_format(headers) == "amex"

    def test_chase_by_posting_date(self):
        headers = ["Posting Date", "Description", "Amount", "Type", "Balance"]
        assert detect_csv_format(headers) == "chase"

    def test_capital_one_by_transaction_date(self):
        headers = ["Transaction Date", "Posted Date", "Card No.", "Description", "Category", "Debit", "Credit"]
        assert detect_csv_format(headers) == "capital_one"

    def test_chase_manual_format(self):
        headers = ["Date", "Description", "Amount", "Account"]
        assert detect_csv_format(headers) == "chase_manual"

    def test_generic_fallback(self):
        headers = ["Date", "Memo", "Amount"]
        assert detect_csv_format(headers) == "generic"

    def test_unknown_headers(self):
        headers = ["foo", "bar", "baz"]
        assert detect_csv_format(headers) == "generic"

    def test_empty_headers(self):
        assert detect_csv_format([]) == "generic"

    def test_case_insensitivity_amex(self):
        headers = ["date", "description", "CARD MEMBER", "account #", "amount"]
        assert detect_csv_format(headers) == "amex"

    def test_case_insensitivity_chase(self):
        headers = ["POSTING DATE", "Description", "Amount"]
        assert detect_csv_format(headers) == "chase"

    def test_case_insensitivity_capital_one(self):
        headers = ["TRANSACTION DATE", "Posted Date", "Description", "Debit", "Credit"]
        assert detect_csv_format(headers) == "capital_one"

    def test_whitespace_in_headers(self):
        headers = [" Card Member ", "Date", "Amount"]
        assert detect_csv_format(headers) == "amex"
