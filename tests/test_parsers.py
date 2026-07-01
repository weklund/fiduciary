"""Tests for Plaid and CSV parsers."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from finance.parsers import PlaidParser, CsvParser, normalize_date, clean_amount
import pytest


class TestNormalizeDate:
    """Test date normalization utility."""

    def test_mm_dd_yyyy(self):
        assert normalize_date("03/15/2025") == "2025-03-15"

    def test_mm_dd_yy(self):
        assert normalize_date("03/17/25") == "2025-03-17"

    def test_iso_passthrough(self):
        assert normalize_date("2025-03-15") == "2025-03-15"

    def test_leading_zeros_added(self):
        assert normalize_date("1/5/2025") == "2025-01-05"

    def test_whitespace_stripped(self):
        assert normalize_date("  03/15/2025  ") == "2025-03-15"

    def test_empty_string(self):
        assert normalize_date("") == ""


class TestCleanAmount:
    """Test amount string cleaning."""

    def test_plain_number(self):
        assert clean_amount("4.50") == 4.50

    def test_dollar_sign(self):
        assert clean_amount("$29.99") == 29.99

    def test_commas(self):
        assert clean_amount("1,234.56") == 1234.56

    def test_dollar_and_commas(self):
        assert clean_amount("$1,234.56") == 1234.56

    def test_negative(self):
        assert clean_amount("-5.75") == -5.75

    def test_whitespace(self):
        assert clean_amount("  42.00  ") == 42.00

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            clean_amount("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            clean_amount("   ")


class TestPlaidParser:
    """Test PlaidParser with fixture data."""

    def test_parse_sample_file(self, fixtures_dir):
        parser = PlaidParser()
        txns = parser.parse(fixtures_dir / "sample_plaid.json")
        assert len(txns) == 3

    def test_transaction_fields(self, fixtures_dir):
        parser = PlaidParser()
        txns = parser.parse(fixtures_dir / "sample_plaid.json")
        coffee = txns[0]
        assert coffee.date == "2025-03-15"
        assert coffee.description == "ACME COFFEE SHOP"
        assert coffee.amount == 4.50
        assert coffee.merchant == "Acme Coffee"
        assert coffee.category == "FOOD_AND_DRINK"
        assert coffee.account_mask == "5832"
        assert coffee.account_type == "depository"
        assert coffee.institution == "ins_109508"
        assert coffee.source == "plaid"

    def test_multi_account(self, fixtures_dir):
        parser = PlaidParser()
        txns = parser.parse(fixtures_dir / "sample_plaid.json")
        masks = {t.account_mask for t in txns}
        assert "5832" in masks
        assert "1023" in masks

    def test_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")
        parser = PlaidParser()
        txns = parser.parse(empty_file)
        assert txns == []

    def test_malformed_json_skipped(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json\n{invalid\n")
        parser = PlaidParser()
        txns = parser.parse(bad_file)
        assert txns == []


class TestCsvParserChase:
    """Test CsvParser with Chase format."""

    def test_parse_chase(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_chase.csv")
        assert len(txns) == 3

    def test_chase_date_normalized(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_chase.csv")
        assert txns[0].date == "2025-03-10"

    def test_chase_amounts(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_chase.csv")
        assert txns[0].amount == -5.75
        assert txns[2].amount == 3200.00

    def test_chase_institution(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_chase.csv")
        assert all(t.institution == "chase" for t in txns)


class TestCsvParserAmex:
    """Test CsvParser with Amex format."""

    def test_parse_amex(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_amex.csv")
        assert len(txns) == 3

    def test_amex_account_mask(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_amex.csv")
        assert all(t.account_mask == "1007" for t in txns)

    def test_amex_two_digit_year(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_amex.csv")
        # Third row has 03/17/25
        assert txns[2].date == "2025-03-17"

    def test_amex_institution(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_amex.csv")
        assert all(t.institution == "amex" for t in txns)


class TestCsvParserCapitalOne:
    """Test CsvParser with Capital One format."""

    def test_parse_capital_one(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_capital_one.csv")
        assert len(txns) == 3

    def test_capital_one_debit_amount(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_capital_one.csv")
        assert txns[0].amount == 45.67

    def test_capital_one_credit_amount(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_capital_one.csv")
        # Third row has empty Debit, Credit=150.00
        assert txns[2].amount == 150.00

    def test_capital_one_dates_normalized(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_capital_one.csv")
        assert txns[0].date == "2025-03-20"

    def test_capital_one_institution(self, fixtures_dir):
        parser = CsvParser()
        txns = parser.parse(fixtures_dir / "sample_capital_one.csv")
        assert all(t.institution == "capital_one" for t in txns)
