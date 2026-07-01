# Fiduciary

[![Agent Skills](https://skills.sh/b/weklund/fiduciary)](https://skills.sh/weklund/fiduciary)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

Skills follow the [Agent Skills open standard](https://agentskills.io) — also compatible with Hermes Agent, Gemini CLI, Cursor, GitHub Copilot, and 42+ other tools.

## Setup (5 minutes)

### Prerequisites

- macOS or Linux (Windows via WSL)
- Python 3.8+
- One of:
  - [Claude Code](https://claude.ai/code) installed and authenticated, OR
  - [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed

### 1. Clone and enter the project

```bash
git clone https://github.com/weklund/fiduciary.git
cd fiduciary
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

### 4. Connect your agent

#### Option A: Claude Code

Open Claude Code in this directory. Skills are auto-discovered from `.claude/skills/`.

```
/onboard
```

This conducts a financial advisor intake — asks about your goals, situation, risk tolerance, and concerns — then writes a personalized context file so all future advice is tailored to you.

#### Option B: Hermes Agent

Point Hermes at this directory and install the skills:

```bash
# Copy advisory frameworks to Hermes persona
cp CLAUDE.md ~/.hermes/SOUL.md

# Install skills (Hermes reads the Agent Skills format directly)
hermes skills add ./\.claude/skills/onboard
hermes skills add ./\.claude/skills/finance-query
hermes skills add ./\.claude/skills/spending-audit
hermes skills add ./\.claude/skills/weekly-report
hermes skills add ./\.claude/skills/sync-data
```

Then run the intake:

```
/onboard
```

Hermes stores your profile in `~/.hermes/USER.md` and `~/.hermes/MEMORY.md` instead of Claude Code's memory system. The skills work the same way.

### 5. Start asking questions

Works the same in both agents:

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
| `/next-dollar` | "What should I do with $X?" — applies order of operations to YOUR situation |
| `/health-check` | Quarterly full assessment — pyramid status, ratios, goal progress, action plan |
| `/spending-audit` | Find waste, unused subscriptions, overspending |
| `/weekly-report` | Generate a weekly spending summary |

## Adding Historical Data

Plaid gives you ~30 days of history. For deeper analysis, add bank statement CSVs:

1. Download CSV from your bank's website (Activity → Download → CSV)
2. Drop into `data/statements/`
3. Run `python3 scripts/ingest.py`

Supported formats: Amex, Chase, Capital One, or any CSV with `Date,Description,Amount` columns.

## How It Thinks

A certified financial planner doesn't just look at your bank balance and tell you to save more. The CFP Board mandates a 7-step process that starts with understanding your complete situation — circumstances, values, behavioral patterns — before ever making a recommendation. Generic advice violates the fiduciary duty of care.

This system encodes that process. When you run `/onboard`, it conducts the same structured intake a $400/hour advisor would: who are you, what does money mean to you, what are you building toward, how do you behave under stress. When you ask `/next-dollar`, it doesn't just say "pay off debt" — it walks your actual balances and rates through a priority hierarchy, checks your constraints ("never touch the emergency fund"), and accounts for your behavioral profile ("you said you tend to freeze under pressure, so here's one simple action, not five").

The framework underneath is the **Financial Planning Pyramid** — a layered model where you never optimize a higher layer while a lower one is unstable:

```
Layer 5: LEGACY         — Estate planning, wealth transfer
Layer 4: FREEDOM        — Aspirational goals, early retirement
Layer 3: ACCUMULATION   — Investing, retirement, goal funding
Layer 2: SAFETY         — Emergency fund, insurance, stable cash flow
Layer 1: PROTECTION     — Expenses covered, high-interest debt managed, no fees bleeding
```

Every recommendation maps to a layer. If your Layer 1 is unstable (late fees hitting, no autopay, high-interest debt growing), the system won't suggest optimizing your 401(k) allocation. It fixes the foundation first.

On top of the pyramid sits the **Order of Operations** — a decision tree for "what to do with the next dollar." It's not a budget. It's a priority sequence: capture the employer match (instant 50-100% return) before paying 7% debt, pay 7% debt before building an emergency fund beyond the starter cushion, and so on. The math is the math — but the system also knows when to deviate (carry debt during an income transition because runway > optimization).

The behavioral layer is what separates this from a spreadsheet. The system tracks whether you prefer automation or control, whether you panic-sell or freeze, whether you overspend on things or experiences. It uses that to frame recommendations in ways that actually stick — because the best financial plan is the one you'll follow, not the one that's mathematically optimal on paper.

### Frameworks Encoded

- **Financial Planning Pyramid** — prioritize protection → safety → accumulation → freedom → legacy
- **Order of Operations** — what to do with the next dollar (employer match → high-interest debt → emergency fund → HSA → Roth → 401k → ...)
- **Decision Rules** — when to pay debt vs. invest, emergency fund sizing, tax-advantaged account priority
- **Behavioral Finance** — automate over willpower, loss aversion framing, pre-commitment devices
- **Conscious Spending Framework** — fixed costs <60%, investments 15-20%, guilt-free spending 20-35%

These aren't opinions — they're synthesized from CFP Board standards, the fiduciary duty of care, and decades of evidence-based personal finance research.

## Privacy & Security

- **All data is local.** `data/` is gitignored. Nothing financial is ever committed.
- **Your profile stays on your machine.** The `/onboard` intake writes to Claude Code's local memory system (`~/.claude/projects/`), not to the repository. The `## Client Context` section in CLAUDE.md is a placeholder — if you populate it, add it to your local `.git/info/exclude` to prevent accidental commits.
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
  next-dollar/         ← "Where should my next $X go?"
  health-check/        ← Quarterly full financial assessment
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

## Works With

Built for [Claude Code](https://claude.ai/code). Also compatible with any tool supporting the [Agent Skills standard](https://agentskills.io):

- Hermes Agent (NousResearch)
- Gemini CLI
- Cursor
- GitHub Copilot
- OpenAI Codex
- JetBrains Junie
- [42+ others](https://agentskills.io/clients)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Issues and PRs welcome.

Good first contributions:
- Add CSV parsers for new banks (see `scripts/ingest.py`)
- Improve category detection in spending-audit
- Add new advisory frameworks to CLAUDE.md
- Write new skills for specific financial planning tasks

## License

MIT
