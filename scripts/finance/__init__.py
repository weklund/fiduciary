"""Finance ingestion package — parse, normalize, and store financial transactions."""
from __future__ import annotations

from .models import Transaction, Account
from .parsers import PlaidParser, CsvParser
from .repository import TransactionRepository
from .detection import detect_csv_format

__all__ = [
    "Transaction",
    "Account",
    "PlaidParser",
    "CsvParser",
    "TransactionRepository",
    "detect_csv_format",
]
