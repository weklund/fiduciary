---
name: finance-query
description: >
  Answer questions about personal finances — balances, transactions, spending
  patterns, account status, recent purchases, merchant history, income tracking.
  Use when the user asks anything about their money, accounts, or transactions.
allowed-tools: Bash, Read
---

## Instructions

Answer the user's financial question using the latest Plaid data snapshots.

### Data locations

- Balances: `data/latest/balances.json`
- Transactions: `data/latest/transactions.json`
- Liabilities: `data/latest/liabilities.json`
- Investments: `data/latest/investments.json`

### Steps

1. Check if `data/latest/` has recent data. If files are missing or older than 1 day, suggest running `/sync-data` first.
2. Read the relevant JSON file(s) for the user's question.
3. Analyze and answer clearly. Include specific numbers, dates, and merchant names.

### Plaid data conventions

- **Transaction amounts:** POSITIVE = money spent (debit); NEGATIVE = income/refund (credit)
- **Categories:** Plaid provides `personal_finance_category.primary` and `.detailed`
- **Accounts:** Each has `type` (depository, credit, investment, loan) and `subtype` (checking, savings, credit card, etc.)

### Guidelines

- Default to the most recent data available
- For date-range questions, filter transactions by `date` field (ISO format YYYY-MM-DD)
- For "how much did I spend on X", sum positive transaction amounts matching that merchant/category
- Always clarify the time period you're reporting on
- If the data doesn't cover the requested period, say so and suggest a fresh sync with more history
- Round dollar amounts to 2 decimal places
- Group and sort results for readability (highest spend first, etc.)
