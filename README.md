# Finance Copilot

A personal financial advisor that runs locally on your machine. Connects to your bank accounts via Plaid, stores everything in a local SQLite database, and uses Claude Code as a conversational advisor — grounded in your real transaction data, not generic platitudes.

Built on the CFP Board's fiduciary planning process. No data leaves your machine. No subscriptions. No product recommendations. Just you, your data, and an advisor that works in your interest.

```
You: "What did I spend on dining this month?"
Advisor: queries your local DB, shows the answer with merchants and totals

You: "Should I pay off my credit card or keep cash reserves?"
Advisor: looks at your actual balances, rates, income stability — gives a personalized recommendation with the math
```

## What This Is

- **Plaid CLI** pulls live transactions from your bank accounts
- **SQLite** stores everything locally in a single unified ledger
- **Claude Code skills** provide conversational access to your finances
- **Advisory frameworks** (encoded in CLAUDE.md) ensure recommendations follow evidence-based financial planning principles

It's not an app. It's a toolkit that turns Claude Code into a fiduciary financial advisor with access to your actual data.

## Setup (5 minutes)

### Prerequisites

- [Claude Code](https://claude.ai/code) installed and authenticated
- macOS or Linux (Windows via WSL)
- Python 3.8+

### 1. Clone and enter the project

```bash
git clone <this-repo>
cd finance-copilot
```

### 2. Install Plaid CLI

```bash
brew install plaid/plaid-cli/plaid
plaid login
plaid link    # connects your bank accounts — runs locally, data stays on your machine
```

### 3. First sync

```bash
bash scripts/sync.sh
```

This pulls transactions from Plaid and builds the SQLite database at `data/finance.db`.

### 4. Run the intake

Open Claude Code in this directory and run:

```
/onboard
```

This conducts a financial advisor intake — asks about your goals, situation, risk tolerance, and concerns — then writes a personalized context file so all future advice is tailored to you.

### 5. Start asking questions

```
"What are my biggest expenses this month?"
"How much am I spending on subscriptions?"
"Should I pay off this card or build savings first?"
"Give me a weekly spending report"
```

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Plaid CLI  │────▶│  SQLite DB   │◀────│  CSV Statements │
│  (live sync)│     │  (unified    │     │  (historical    │
└─────────────┘     │   ledger)    │     │   backfill)     │
                    └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────▼───────┐
                    │  Claude Code │
                    │  (skills +   │
                    │   CLAUDE.md  │
                    │   frameworks)│
                    └──────────────┘
```

**Your data never leaves your machine.** Plaid CLI runs locally. The database is local. Claude Code reads the DB directly. Nothing is uploaded, shared, or transmitted to third parties beyond what Plaid requires to authenticate with your bank.

## Skills (Slash Commands)

| Command | What it does |
|---------|-------------|
| `/onboard` | Financial advisor intake — sets up your personalized profile |
| `/sync-data` | Pull fresh transactions from Plaid |
| `/finance-query` | Ask any question about your finances (auto-triggered) |
| `/spending-audit` | Find waste, unused subscriptions, overspending |
| `/weekly-report` | Generate a weekly spending summary |

## Adding Historical Data

Plaid gives you ~30 days of history. For deeper analysis, add bank statement CSVs:

1. Download CSV from your bank's website (Activity → Download → CSV)
2. Drop into `data/statements/`
3. Run `python3 scripts/ingest.py`

Supported formats: Amex, Chase, Capital One, or any CSV with `Date,Description,Amount` columns.

## Advisory Frameworks

The system uses evidence-based financial planning principles encoded in CLAUDE.md:

- **Financial Planning Pyramid** — prioritize protection → safety → accumulation → freedom → legacy
- **Order of Operations** — what to do with the next dollar (employer match → high-interest debt → emergency fund → HSA → Roth → 401k → ...)
- **Decision Rules** — when to pay debt vs. invest, emergency fund sizing, tax-advantaged account priority
- **Behavioral Finance** — automate over willpower, loss aversion framing, pre-commitment devices
- **Conscious Spending Framework** — fixed costs <60%, investments 15-20%, guilt-free spending 20-35%

These aren't opinions — they're synthesized from CFP Board standards, the fiduciary duty of care, and decades of evidence-based personal finance research.

## Privacy & Security

- **All data is local.** `data/` is gitignored. Nothing financial is ever committed.
- **Your profile stays on your machine.** The `/onboard` intake writes to Claude Code's local memory system (`~/.claude/projects/`), not to the repository.
- **No API keys in the repo.** Plaid CLI handles authentication separately.
- **No tracking, no analytics, no telemetry.** This is a local tool, not a service.

## Project Structure

```
CLAUDE.md              ← Advisory frameworks + project conventions (committed)
scripts/
  sync.sh              ← Pull from Plaid + rebuild DB
  ingest.py            ← Rebuild DB from all sources (Plaid snapshots + CSVs)
  parse-statements.py  ← Find HSA-eligible expenses in CSVs
.claude/skills/        ← Conversational finance skills
  onboard/             ← First-time intake interview
  finance-query/       ← Query your finances
  sync-data/           ← Sync fresh data
  spending-audit/      ← Find waste and subscriptions
  weekly-report/       ← Weekly spending summary
data/                  ← (gitignored) Your financial data
  finance.db           ← Unified SQLite ledger
  snapshots/           ← Raw Plaid JSON responses
  statements/          ← Bank CSVs for historical backfill
  latest/              ← Most recent Plaid snapshot
reports/               ← (gitignored) Generated dashboards and reports
```

## Updating Your Profile

Life changes. Run `/onboard` again anytime:
- You get a new job or lose one
- Income changes significantly
- Major life event (marriage, kids, divorce, inheritance)
- Your goals or priorities shift
- You want to add accounts or update metrics

The skill detects existing context and offers to update rather than start from scratch.

## Philosophy

> Track everything. Automate the boring stuff. Spend deliberately on what builds the future. Cut ruthlessly what doesn't.

This tool exists because:
1. Most financial apps sell you products or harvest your data
2. Generic advice ("save more, spend less") doesn't account for YOUR situation
3. A fiduciary advisor costs $200-400/hour and meets quarterly at best
4. Your bank has the data — you should too, queryable, on your terms

## License

MIT
