#!/usr/bin/env bash
set -euo pipefail
umask 077

DATA_DIR="$(cd "$(dirname "$0")/../data" && pwd)"
SNAPSHOT_DIR="$DATA_DIR/snapshots"
LATEST_DIR="$DATA_DIR/latest"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$SNAPSHOT_DIR" "$LATEST_DIR"
chmod 700 "$DATA_DIR" "$SNAPSHOT_DIR" "$LATEST_DIR"
touch "$DATA_DIR/.metadata_never_index"

echo "Syncing Plaid data for $TODAY..."

echo "  Fetching balances..."
plaid balance --all --json > "$SNAPSHOT_DIR/balances-$TODAY.json"
cp "$SNAPSHOT_DIR/balances-$TODAY.json" "$LATEST_DIR/balances.json"

echo "  Fetching transactions (last 500)..."
plaid transactions list --all --count 500 --json > "$SNAPSHOT_DIR/transactions-$TODAY.json"
cp "$SNAPSHOT_DIR/transactions-$TODAY.json" "$LATEST_DIR/transactions.json"

echo "  Fetching liabilities..."
if plaid liabilities --all --json > "$SNAPSHOT_DIR/liabilities-$TODAY.json" 2>&1; then
  cp "$SNAPSHOT_DIR/liabilities-$TODAY.json" "$LATEST_DIR/liabilities.json"
else
  echo "    WARNING: liabilities fetch failed (product may not be enabled for linked accounts)" >&2
  rm -f "$SNAPSHOT_DIR/liabilities-$TODAY.json"
fi

echo "  Fetching investment holdings..."
if plaid investments holdings --all --json > "$SNAPSHOT_DIR/investments-$TODAY.json" 2>&1; then
  cp "$SNAPSHOT_DIR/investments-$TODAY.json" "$LATEST_DIR/investments.json"
else
  echo "    WARNING: investments fetch failed (product may not be enabled for linked accounts)" >&2
  rm -f "$SNAPSHOT_DIR/investments-$TODAY.json"
fi

echo "Done. Data saved to $SNAPSHOT_DIR/"
echo "Latest snapshots in $LATEST_DIR/"

echo "  Updating ledger database..."
python3 "$(dirname "$0")/ingest.py"
