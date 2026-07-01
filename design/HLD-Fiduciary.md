# High-Level Design: Fiduciary — Local Personal Finance Advisor

## 1. Overview

Fiduciary is an open-source, local-first personal finance toolkit. It connects to bank accounts via Plaid CLI, stores all financial data in a local SQLite database, and exposes conversational analysis through Claude Code skills. No server, no cloud storage, no accounts — everything runs on the user's machine.

**Deployment model:** Local CLI tool (macOS/Linux). Users clone the repo, authenticate with Plaid, and run scripts locally.

## 2. System Context

```
┌─────────────────────────────────────────────────────┐
│                  User's Machine                       │
│                                                       │
│  ┌──────────┐    ┌──────────┐    ┌────────────────┐ │
│  │ Plaid CLI │───▶│ sync.sh  │───▶│ data/finance.db│ │
│  │ (binary) │    │          │    │   (SQLite)     │ │
│  └──────────┘    └──────────┘    └────────────────┘ │
│       │                                ▲             │
│       │                                │             │
│       ▼                          ┌─────┴──────┐     │
│  ┌──────────┐                    │ ingest.py  │     │
│  │ Plaid API │                   │            │     │
│  │ (remote) │                    └─────┬──────┘     │
│  └──────────┘                          ▲            │
│                                        │            │
│                                  ┌─────┴──────┐    │
│                                  │ CSV files  │    │
│                                  │ (manual)   │    │
│                                  └────────────┘    │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │        Claude Code / Hermes Agent           │    │
│  │  ┌────────────────────────────────────┐    │    │
│  │  │         Agent Skills               │    │    │
│  │  │  /sync-data  /health-check         │    │    │
│  │  │  /next-dollar /spending-audit      │    │    │
│  │  │  /weekly-report /finance-query     │    │    │
│  │  │  /tactics  /onboard                │    │    │
│  │  └─────────────────┬──────────────────┘    │    │
│  │                    │ sqlite3 queries        │    │
│  │                    ▼                        │    │
│  │              data/finance.db                │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌──────────────────────────────────────────┐      │
│  │          User Files on Disk               │      │
│  │  data/snapshots/*.json (Plaid raw)        │      │
│  │  data/statements/*.csv (bank exports)     │      │
│  │  data/latest/*.json (current state)       │      │
│  │  reports/*.md (generated reports)         │      │
│  │  CLAUDE.md (advisory config + client ctx) │      │
│  │  .claude/memory/ (persistent profile)     │      │
│  └──────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

## 3. Components

### 3.1 Plaid CLI (Third-party Binary)

- **What:** Official Plaid command-line tool (`brew install plaid/plaid-cli/plaid`)
- **Auth:** OAuth token stored by Plaid CLI in its own config (`~/.plaid/`)
- **Data:** Calls Plaid API for transactions, balances, liabilities, investments
- **Trust boundary:** User's machine → Plaid API (HTTPS, OAuth 2.0)

### 3.2 sync.sh (Shell Script)

- **What:** Orchestrates Plaid CLI calls and triggers database rebuild
- **Permissions:** Sets `umask 077` and `chmod 700` on data directories
- **Output:** JSON files in `data/snapshots/` and `data/latest/`
- **Calls:** `plaid balance`, `plaid transactions list`, `plaid liabilities`, `plaid investments holdings`

### 3.3 ingest.py (Python Script)

- **What:** Reads JSON snapshots + CSV statements, normalizes, deduplicates, inserts into SQLite
- **Dedup:** SHA-256 hash of (date, description, amount, account_mask), truncated to 16 chars
- **CSV parsers:** Auto-detects Amex, Chase, Capital One, generic formats
- **No network calls:** Purely local file I/O → SQLite

### 3.4 SQLite Database (data/finance.db)

- **What:** Unified ledger of all transactions and account balances
- **Schema:** Two tables — `transactions` (deduped, indexed) and `accounts` (balance snapshots)
- **Access:** Read by Claude Code skills via `sqlite3` CLI commands
- **Protection:** Gitignored, chmod 700 on parent directory, WAL mode

### 3.5 Claude Code Skills (Agent Interface)

- **What:** Markdown skill files in `.claude/skills/` that instruct the LLM agent
- **Execution:** Skills generate `sqlite3` queries, run `bash scripts/sync.sh`, write reports
- **Data flow:** Skills read from `data/finance.db` and write to `reports/` and `.claude/memory/`
- **Trust model:** The LLM agent runs with the user's shell permissions (full filesystem access within the project)

### 3.6 CLAUDE.md + Memory Files

- **What:** Persistent configuration and personalized context
- **Contents:** Advisory frameworks, client financial profile, goals, behavioral patterns
- **Sensitivity:** Contains PII (income, debt balances, goals, household structure)
- **Protection:** Memory files are in `.claude/` (typically gitignored by user config); CLAUDE.md is tracked in git (users warned about PII)

### 3.7 CSV Statements (Manual Import)

- **What:** Downloaded bank statement files placed in `data/statements/`
- **Format:** CSV files from Amex, Chase, Capital One
- **Protection:** Gitignored via `data/` rule

## 4. Data Classification

| Data Type | Sensitivity | Storage Location | Protection |
|-----------|-------------|-----------------|------------|
| Bank transactions | HIGH (PII + financial) | data/finance.db | gitignore, chmod 700 |
| Account balances | HIGH (financial) | data/finance.db | gitignore, chmod 700 |
| Plaid access tokens | CRITICAL (credential) | ~/.plaid/ (managed by Plaid CLI) | Plaid CLI's own security |
| Plaid JSON snapshots | HIGH (raw financial) | data/snapshots/*.json | gitignore, chmod 700 |
| CSV statements | HIGH (raw financial) | data/statements/*.csv | gitignore |
| Client profile | MEDIUM (PII) | CLAUDE.md, .claude/memory/ | git-tracked (WARNING), user responsible |
| Advisory frameworks | LOW (public) | CLAUDE.md | git-tracked (intended) |
| Generated reports | MEDIUM (financial summary) | reports/ | gitignore |

## 5. Trust Boundaries

| Boundary | From | To | Protocol | Auth |
|----------|------|----|----------|------|
| TB-1 | User's machine | Plaid API | HTTPS | OAuth 2.0 (managed by Plaid CLI) |
| TB-2 | Plaid CLI | Local filesystem | File I/O | Unix permissions (umask 077) |
| TB-3 | Claude Code agent | Local filesystem | Shell exec | User's shell permissions |
| TB-4 | Claude Code agent | Anthropic API | HTTPS | API key (managed by Claude Code) |
| TB-5 | Git repository | GitHub (remote) | HTTPS/SSH | Git credentials |

## 6. Key Security Properties

### 6.1 Local-first Architecture

- No server component. No user accounts. No cloud storage of financial data.
- All financial data stays on the user's machine (enforced by architecture, not policy).
- The only external calls are: Plaid API (for sync) and Anthropic API (for LLM inference).

### 6.2 Credential Management

- Plaid tokens managed by Plaid CLI (`~/.plaid/` directory)
- Claude Code API key managed by Claude Code (`~/.claude/` or env var)
- No credentials stored in this project's files

### 6.3 Data Protection

- `sync.sh` sets `umask 077` and `chmod 700` on data directories
- `.gitignore` excludes `data/`, `reports/`, `.env`, `*.db`
- SQLite WAL mode for crash safety

### 6.4 Open Source Distribution

- Repository is public on GitHub
- Users clone and run locally
- No telemetry, analytics, or phone-home behavior
- MIT licensed

## 7. Threat Context (for Threat Modeling)

As an open-source local tool handling highly sensitive financial data, the primary concerns are:

1. **Accidental secret/PII exposure via git** — user commits financial data or credentials
2. **Credential theft** — malware or unauthorized access to Plaid tokens
3. **Data at rest** — unencrypted SQLite database on disk
4. **Supply chain** — compromised dependencies (Plaid CLI, Python packages)
5. **LLM data leakage** — financial data sent to Anthropic API for inference
6. **Fork/contribution safety** — contributors accidentally including their own financial data in PRs
7. **Misconfigured permissions** — data directory permissions relaxed

## 8. Non-Goals

- Multi-user support
- Remote/server deployment
- Encryption at rest (tradeoff: simplicity for a local-only tool)
- Authentication/authorization (single-user, local machine)
- Real-time streaming (batch sync only)
