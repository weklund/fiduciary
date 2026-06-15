#!/usr/bin/env python3
"""
Parse bank statement CSVs and identify HSA-eligible expenses.

Supports: Chase, Amex, Ally, Capital One, Coinbase CSV formats.
Drop CSVs into data/statements/ and run this script.

Usage: python3 scripts/parse-statements.py
"""

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "statements"

# HSA-eligible merchants and categories
ELIGIBLE_NO_LMN = {
    'dexcom': 'Medical device (CGM)',
    'pharmacy': 'Prescription/OTC',
    'cvs': 'Pharmacy',
    'walgreens': 'Pharmacy',
    'rite aid': 'Pharmacy',
    'dentist': 'Dental',
    'dental': 'Dental',
    'orthodont': 'Dental',
    'optometri': 'Vision',
    'lenscrafters': 'Vision',
    'warby parker': 'Vision',
    'eye care': 'Vision',
    'vision': 'Vision',
    'urgent care': 'Medical visit',
    'hospital': 'Medical visit',
    'medical': 'Medical visit',
    'doctor': 'Medical visit',
    'physician': 'Medical visit',
    'clinic': 'Medical visit',
    'dermatolog': 'Medical visit',
    'therapist': 'Mental health',
    'therapy': 'Mental health',
    'counseling': 'Mental health',
    'psychiatr': 'Mental health',
    'chiropract': 'Chiropractic',
    'physical therapy': 'Physical therapy',
    'labcorp': 'Lab work',
    'quest diag': 'Lab work',
    'blood work': 'Lab work',
    'xray': 'Imaging',
    'radiology': 'Imaging',
    'mri': 'Imaging',
    'ambulance': 'Emergency',
    'hearing': 'Hearing',
    'acupunctur': 'Acupuncture',
    'ortho': 'Orthopedic',
}

ELIGIBLE_WITH_LMN = {
    'ymca': 'Gym/fitness (LMN needed)',
    'whoop': 'Health monitor (LMN needed)',
    'ouraring': 'Health monitor (LMN needed)',
    'oura': 'Health monitor (LMN needed)',
    'wonderfeel': 'Supplement (LMN needed)',
    'momentous': 'Supplement (LMN needed)',
    'insidetracker': 'Health testing (LMN needed)',
    'seed': 'Supplement/probiotic (LMN needed)',
    'athletic greens': 'Supplement (LMN needed)',
    'cronometer': 'Health tracking (LMN needed)',
    'polar': 'Fitness tracker (LMN needed)',
    'fitbit': 'Fitness tracker (LMN needed)',
    'peloton': 'Fitness (LMN needed)',
    'tonal': 'Fitness (LMN needed)',
    'noom': 'Weight management (LMN needed)',
    'headspace': 'Mental health app (LMN needed)',
    'calm': 'Mental health app (LMN needed)',
    'massage': 'Massage therapy (LMN needed)',
}


def detect_format(headers):
    """Detect which bank's CSV format this is."""
    headers_lower = [h.lower().strip() for h in headers]
    if 'posting date' in headers_lower and 'description' in headers_lower:
        return 'chase'
    if 'date' in headers_lower and 'description' in headers_lower and 'amount' in headers_lower:
        if 'card member' in headers_lower or 'appears on your statement as' in headers_lower:
            return 'amex'
        return 'generic'
    if 'transaction date' in headers_lower:
        return 'capital_one'
    return 'generic'


def parse_csv(filepath):
    """Parse a CSV file and return normalized transactions."""
    transactions = []

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        fmt = detect_format(headers)

        for row in reader:
            try:
                if fmt == 'chase':
                    date = row.get('Posting Date', row.get('posting date', ''))
                    desc = row.get('Description', row.get('description', ''))
                    amount = row.get('Amount', row.get('amount', '0'))
                elif fmt == 'amex':
                    date = row.get('Date', row.get('date', ''))
                    desc = row.get('Description', row.get('description', ''))
                    amount = row.get('Amount', row.get('amount', '0'))
                elif fmt == 'capital_one':
                    date = row.get('Transaction Date', row.get('transaction date', ''))
                    desc = row.get('Description', row.get('description', ''))
                    amount = row.get('Debit', row.get('debit', '0')) or '0'
                else:
                    date = row.get('Date', row.get('date', list(row.values())[0] if row else ''))
                    desc = row.get('Description', row.get('description', row.get('Name', list(row.values())[1] if len(row) > 1 else '')))
                    amount = row.get('Amount', row.get('amount', row.get('Debit', list(row.values())[2] if len(row) > 2 else '0')))

                # Clean amount
                amount_str = str(amount).replace('$', '').replace(',', '').strip()
                if not amount_str or amount_str == '0':
                    continue
                amount_float = abs(float(amount_str))

                if amount_float > 0 and date and desc:
                    transactions.append({
                        'date': date,
                        'description': desc,
                        'amount': amount_float,
                        'source': filepath.name,
                    })
            except (ValueError, TypeError):
                continue

    return transactions


def classify_transaction(desc):
    """Check if a transaction is HSA-eligible."""
    desc_lower = desc.lower()

    for keyword, category in ELIGIBLE_NO_LMN.items():
        if keyword in desc_lower:
            return ('eligible', category)

    for keyword, category in ELIGIBLE_WITH_LMN.items():
        if keyword in desc_lower:
            return ('lmn_needed', category)

    return (None, None)


def main():
    if not DATA_DIR.exists():
        print(f"No statements directory found at {DATA_DIR}")
        sys.exit(1)

    csv_files = list(DATA_DIR.glob('*.csv')) + list(DATA_DIR.glob('*.CSV'))

    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        print(f"Drop your bank statement CSVs there and re-run.")
        sys.exit(0)

    print(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  {f.name}")
    print()

    # Parse all CSVs
    all_transactions = []
    for filepath in csv_files:
        txns = parse_csv(filepath)
        all_transactions.extend(txns)
        print(f"  Parsed {filepath.name}: {len(txns)} transactions")

    print(f"\nTotal transactions: {len(all_transactions)}")
    print()

    # Classify
    eligible = []
    lmn_needed = []

    for t in all_transactions:
        status, category = classify_transaction(t['description'])
        if status == 'eligible':
            eligible.append({**t, 'category': category})
        elif status == 'lmn_needed':
            lmn_needed.append({**t, 'category': category})

    # Report
    print("=" * 70)
    print("HSA-ELIGIBLE EXPENSES")
    print("=" * 70)
    print()

    print("DEFINITELY ELIGIBLE (no LMN needed):")
    print("-" * 70)
    total_eligible = 0
    for t in sorted(eligible, key=lambda x: x['date']):
        print(f"  {t['date']:12s} {t['description'][:40]:40s} ${t['amount']:>8.2f}  [{t['category']}]")
        total_eligible += t['amount']
    print(f"  {'SUBTOTAL':<52s} ${total_eligible:>8.2f}")
    print()

    print("ELIGIBLE WITH LETTER OF MEDICAL NECESSITY:")
    print("-" * 70)
    total_lmn = 0
    for t in sorted(lmn_needed, key=lambda x: x['date']):
        print(f"  {t['date']:12s} {t['description'][:40]:40s} ${t['amount']:>8.2f}  [{t['category']}]")
        total_lmn += t['amount']
    print(f"  {'SUBTOTAL':<52s} ${total_lmn:>8.2f}")
    print()

    print("=" * 70)
    print(f"  Total (no LMN):    ${total_eligible:>10.2f}")
    print(f"  Total (with LMN):  ${total_lmn:>10.2f}")
    print(f"  GRAND TOTAL:       ${total_eligible + total_lmn:>10.2f}")
    print(f"  HSA Balance:       $    16,000.00")
    print(f"  Reimbursable:      ${min(total_eligible + total_lmn, 16000):>10.2f}")
    print("=" * 70)


if __name__ == '__main__':
    main()
