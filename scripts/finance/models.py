"""Data models for financial transactions and accounts."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass
class Transaction:
    """A single financial transaction, normalized across all sources."""

    date: str  # ISO YYYY-MM-DD
    description: str
    amount: float
    merchant: str = ""
    category: str = ""
    account_name: str = ""
    account_mask: str = ""
    account_type: str = ""
    institution: str = ""
    source: str = ""
    source_file: str = ""
    external_id: str = ""  # source's own stable ID (Plaid transaction_id)
    pending: bool = False

    @property
    def id(self) -> str:
        """Compute SHA-256 dedup key (truncated to 16 chars).

        When the source provides a stable ID (Plaid transaction_id), hash that:
        Plaid can report the same transaction with a different description or
        date across syncs. Otherwise hash date, description (lowercased/stripped),
        amount, and account_mask — matching the original make_txn_id() behavior.
        """
        if self.external_id:
            raw = f"{self.source}|{self.external_id}"
        else:
            raw = f"{self.date}|{self.description.strip().lower()}|{self.amount:.2f}|{self.account_mask}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class Account:
    """Account balance snapshot from Plaid."""

    account_id: str
    name: str = ""
    official_name: str = ""
    type: str = ""
    subtype: str = ""
    mask: str = ""
    institution_id: str = ""
    balance_current: float | None = None
    balance_available: float | None = None
    balance_limit: float | None = None
