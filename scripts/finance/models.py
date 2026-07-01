"""Data models for financial transactions and accounts."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Optional


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

    @property
    def id(self) -> str:
        """Compute SHA-256 dedup key (truncated to 16 chars).

        Hash is based on date, description (lowercased/stripped), amount,
        and account_mask — matching the original make_txn_id() behavior.
        """
        raw = (
            f"{self.date}|{self.description.strip().lower()}"
            f"|{self.amount:.2f}|{self.account_mask}"
        )
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
    balance_current: Optional[float] = None
    balance_available: Optional[float] = None
    balance_limit: Optional[float] = None
