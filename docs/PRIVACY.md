# Privacy & Data Retention

This document explains exactly what data goes where when you use Fiduciary.

## What stays local

- **All financial data** (transactions, balances, account info) stays in `data/finance.db` on your machine
- **Your personal profile** (income, debts, goals) stays in agent memory files (never git-tracked)
- **Plaid credentials** stay in `~/.plaid/` (managed by Plaid CLI)
- **No telemetry, analytics, or phone-home behavior**

## What leaves your machine

When you ask questions about your finances, transaction data from your local database is
sent to your LLM provider for analysis. The amount of data sent depends on the query —
a spending summary sends aggregates, while a transaction search sends individual records.

### LLM Provider Comparison

| Configuration | Recommended? | Server retention | Training | Notes |
|---|---|---|---|---|
| **API key (Commercial)** | Yes | 7 days | Never | Best balance of capability + privacy |
| **API key + ZDR** | Best cloud option | 0 days | Never | Request from Anthropic account team |
| **Local LLM (Ollama)** | Best privacy | 0 — never leaves device | Never | Reduced capability, no tool use |
| Enterprise + ZDR | Yes (orgs) | 0 days | Never | Admin controls, SOC 2, ISO 27001 |
| Consumer Pro/Max (opt-out) | No | 30 days | No | Potential human review for safety |
| Consumer Pro/Max (opt-in) | **Do not use** | 5 years | **Yes** | Your financial data trains the model |

**Recommended:** Use a pay-as-you-go API key from an Anthropic Commercial organization
(`ANTHROPIC_API_KEY`). Under commercial terms: 7-day retention, AES-256 encryption at rest,
contractually excluded from model training.

**Zero-trust option:** Use Ollama or llama.cpp locally. Nothing leaves your machine.
The skill logic still works — only the LLM backend changes. Tradeoff: significantly
reduced analysis quality.

### Important Caveats

- Even under ZDR, sessions flagged for policy violations may be retained up to 2 years
- Certain models (Fable 5, Mythos 5) require 30-day retention and cannot use ZDR
- Claude Code is excluded from Anthropic's HIPAA BAA regardless of plan

### Multi-hop Provider Warning

If using Hermes Agent with OpenRouter (its default), your data passes through OpenRouter
AND the underlying model provider. For financial data, configure a direct provider:

```yaml
# ~/.hermes/config.yaml
model:
  provider: anthropic    # or: ollama (for local)
  default: claude-sonnet-5
```

Also ensure trajectory capture is off: `agent.save_trajectories: false`

## Local Session Logs

Every agent runtime stores conversation history (including financial query results)
in plaintext on your machine. **None encrypt at rest.**

| Runtime | Location | Default Retention | Recommended Setting |
|---------|----------|-------------------|---------------------|
| Claude Code | `~/.claude/projects/` | 30 days | `cleanupPeriodDays: 7` |
| Hermes Agent | `~/.hermes/state.db` | 90 days | `sessions.retention_days: 7` + `auto_prune: true` |
| Gemini CLI | `~/.gemini/tmp/` | Indefinite | Periodically clear manually |
| Cursor | `~/Library/Application Support/Cursor/` | Indefinite | Periodically clear manually |

### Exclude from cloud backups

```bash
# macOS: exclude from Time Machine
tmutil addexclusion ~/.claude/projects/
tmutil addexclusion ~/.hermes/state.db
```

Exclude these paths from iCloud, Dropbox, and OneDrive sync as well.

## Credential Security

| Credential | Location | Protection |
|-----------|----------|------------|
| Plaid tokens | `~/.plaid/` | Exclude from dotfile repos and cloud sync |
| LLM API keys | Environment variable | Never in project files |
| Financial data | `data/finance.db` | chmod 600, gitignored, full-disk encryption |

## Policy Links

- [Anthropic Commercial Data Retention](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)
- [API & Data Retention (Platform Docs)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- [Claude Code Data Usage](https://code.claude.com/docs/en/data-usage)
- [Zero Data Retention Docs](https://code.claude.com/docs/en/zero-data-retention)
- [Anthropic Trust Center](https://trust.anthropic.com/)

*Last verified: June 2026. Policies change — check the links above for current terms.*
