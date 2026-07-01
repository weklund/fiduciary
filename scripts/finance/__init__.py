"""Finance ingestion package — parse, normalize, and store financial transactions."""

from __future__ import annotations

from .detection import detect_csv_format
from .models import Account, Transaction
from .parsers import CsvParser, PlaidParser
from .repository import TransactionRepository

__all__ = [
    "Account",
    "CsvParser",
    "PlaidParser",
    "Transaction",
    "TransactionRepository",
    "detect_csv_format",
]
