#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="$(cd "$(dirname "$0")/../data" && pwd)"
SNAPSHOT_DIR="$DATA_DIR/snapshots"
LATEST_DIR="$DATA_DIR/latest"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$SNAPSHOT_DIR" "$LATEST_DIR"

echo "Syncing Plaid data for $TODAY..."

echo "  Fetching balances..."
plaid balance --json > "$SNAPSHOT_DIR/balances-$TODAY.json"
cp "$SNAPSHOT_DIR/balances-$TODAY.json" "$LATEST_DIR/balances.json"

echo "  Fetching transactions (last 500)..."
plaid transactions list --count 500 --json > "$SNAPSHOT_DIR/transactions-$TODAY.json"
cp "$SNAPSHOT_DIR/transactions-$TODAY.json" "$LATEST_DIR/transactions.json"

echo "  Fetching liabilities..."
plaid liabilities --json > "$SNAPSHOT_DIR/liabilities-$TODAY.json" 2>/dev/null || echo "    (no liabilities data or not supported)"
cp "$SNAPSHOT_DIR/liabilities-$TODAY.json" "$LATEST_DIR/liabilities.json" 2>/dev/null || true

echo "  Fetching investment holdings..."
plaid investments holdings --json > "$SNAPSHOT_DIR/investments-$TODAY.json" 2>/dev/null || echo "    (no investment data or not supported)"
cp "$SNAPSHOT_DIR/investments-$TODAY.json" "$LATEST_DIR/investments.json" 2>/dev/null || true

echo "Done. Data saved to $SNAPSHOT_DIR/"
echo "Latest snapshots in $LATEST_DIR/"
