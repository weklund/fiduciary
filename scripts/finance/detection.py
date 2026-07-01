"""CSV format detection based on header columns."""

from __future__ import annotations


def detect_csv_format(headers: list[str]) -> str:
    """Detect the bank CSV format from header column names.

    Returns one of: 'amex', 'chase', 'capital_one', 'chase_manual', 'generic'.
    Detection is case-insensitive.
    """
    headers_lower = [h.lower().strip() for h in headers]

    if "card member" in headers_lower or "appears on your statement as" in headers_lower:
        return "amex"
    if "posting date" in headers_lower:
        return "chase"
    if "transaction date" in headers_lower:
        return "capital_one"
    if headers_lower == ["date", "description", "amount", "account"]:
        return "chase_manual"
    return "generic"
