---
name: weekly-report
description: >
  Generate a weekly personal finance report. Use when the user asks for a
  weekly report, spending summary, finance review, or budget status.
allowed-tools: Bash, Read, Write
---

## Instructions

Generate a weekly finance report covering the last 7 days.

### Data locations

- Balances: `data/latest/balances.json`
- Transactions: `data/latest/transactions.json`
- Liabilities: `data/latest/liabilities.json`
- Investments: `data/latest/investments.json`

### Report sections

#### 1. Account Summary
- Current balances for all accounts (checking, savings, credit cards, investments)
- Net worth (total assets - total liabilities)

#### 2. Weekly Cash Flow
- Total income (negative amounts in transactions = credits/income)
- Total spending (positive amounts)
- Net cash flow

#### 3. Spending by Category (top 10)
- Category name, total spent, transaction count
- Sorted by amount descending

#### 4. Notable Transactions
- Largest single purchases (top 5)
- Any new recurring charges detected
- Unusual merchants (first-time or infrequent)

#### 5. Credit Card Status
- Balance vs. credit limit for each card
- Utilization percentage
- Payment due dates approaching

#### 6. Week-over-Week Comparison
- If prior week's data exists in `data/snapshots/`, compare spending totals

### Output

Save the report to `reports/weekly/YYYY-MM-DD.md` (using today's date) AND display it to the user.

Keep it concise — bullet points, not paragraphs. Lead with the most important numbers.
