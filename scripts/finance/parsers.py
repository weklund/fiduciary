"""Parsers for Plaid JSON and bank CSV files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Protocol

from .detection import detect_csv_format
from .models import Transaction


class Parser(Protocol):
    """Protocol for all file parsers."""

    def parse(self, filepath: Path) -> list[Transaction]: ...


def normalize_date(date_raw: str) -> str:
    """Normalize a date string to ISO YYYY-MM-DD format.

    Handles:
      - MM/DD/YYYY -> YYYY-MM-DD
      - MM/DD/YY   -> YYYY-MM-DD (assumes 2000s)
      - YYYY-MM-DD -> passthrough
    """
    date = date_raw.strip()
    if "/" in date:
        parts = date.split("/")
        if len(parts) == 3:
            m, d, y = parts
            if len(y) == 2:
                y = "20" + y
            date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return date


def clean_amount(amount_str: str) -> float:
    """Clean an amount string (remove $, commas) and convert to float.

    Raises ValueError if the string is empty or not a valid number.
    """
    cleaned = str(amount_str).replace("$", "").replace(",", "").strip()
    if not cleaned:
        raise ValueError("Empty amount string")
    return float(cleaned)


class PlaidParser:
    """Parse Plaid NDJSON transaction files."""

    def parse(self, filepath: Path) -> list[Transaction]:
        """Parse a Plaid NDJSON file into Transaction objects.

        Each line is a JSON object with an 'items' key containing
        accounts and transactions.
        """
        transactions = []
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

                        transactions.append(
                            Transaction(
                                date=date,
                                description=desc,
                                amount=amount,
                                merchant=merchant,
                                category=category,
                                account_name=acct.get("name", ""),
                                account_mask=mask,
                                account_type=acct.get("type", ""),
                                institution=inst,
                                source="plaid",
                                source_file=filepath.name,
                            )
                        )

        return transactions


class CsvParser:
    """Parse bank statement CSV files (auto-detects format)."""

    def parse(self, filepath: Path) -> list[Transaction]:
        """Parse a bank CSV file into Transaction objects.

        Auto-detects the bank format (Amex, Chase, Capital One, etc.)
        based on column headers.
        """
        transactions = []
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            fmt = detect_csv_format(headers)

            for row in reader:
                try:
                    txn = self._parse_row(row, fmt, filepath)
                    if txn is not None:
                        transactions.append(txn)
                except (ValueError, TypeError):
                    continue

        return transactions

    def _parse_row(self, row: dict, fmt: str, filepath: Path) -> Transaction | None:
        """Parse a single CSV row based on detected format."""
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
            date_raw = row.get("Date", next(iter(row.values())) if row else "")
            desc = row.get("Description", row.get("Name", ""))
            amount_str = row.get("Amount", row.get("Debit", "0"))
            mask = ""
            institution = "unknown"

        amount = clean_amount(amount_str)
        date = normalize_date(date_raw)

        if not date or not desc:
            return None

        return Transaction(
            date=date,
            description=desc,
            amount=amount,
            merchant="",
            category="",
            account_name="",
            account_mask=mask,
            account_type="",
            institution=institution,
            source="csv",
            source_file=filepath.name,
        )
