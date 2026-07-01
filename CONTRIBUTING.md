# Contributing to Fiduciary

Thanks for wanting to contribute. This project is a local-first personal finance
toolkit — every contribution should maintain that principle.

## Quick Start

1. Fork and clone
2. Install prerequisites: Python 3.8+, Plaid CLI, Claude Code
3. Run `bash scripts/sync.sh` (or use sample data if you don't have Plaid set up)
4. Make your change
5. Test it works with real or sample data
6. Open a PR

## What We're Looking For

**Great contributions:**
- CSV parsers for new banks/institutions (see `scripts/ingest.py` for the pattern)
- New skills for financial planning tasks (debt payoff calculator, tax estimation, etc.)
- Improvements to category detection and merchant matching
- New advisory frameworks grounded in evidence-based financial planning
- Bug fixes and documentation improvements

**Less likely to merge:**
- Features that require internet-connected services (we're local-first)
- Changes that break the privacy model (no data should leave the machine)
- Opinionated advice without evidence backing (cite your sources)
- Dependencies on commercial APIs beyond Plaid

## Security: Skills Are Executable Code

**Skill files (`.claude/skills/`) are not documentation — they are executable
instructions** that LLM agents follow with full filesystem access. A modified
skill can instruct the agent to read sensitive files, modify scripts, or alter
financial advice.

Treat skill modifications with the same scrutiny as code changes:
- Never add instructions that read files outside the project scope
- Never add instructions that make network requests to third-party URLs
- Never embed encoded/obfuscated content in skill files
- Always have a human review skill file changes before merge

This applies across all agent runtimes (Claude Code, Hermes, Gemini CLI, Cursor,
etc.) — they all read and execute the same skill files.

**Active supply chain campaigns** (TrapDoor, Hades Worm — 2026) specifically target
agent config files. If you see a PR modifying skills from an unknown contributor,
review it carefully.

## Data Separation

This project handles sensitive financial data. Contributors must understand the boundary:

| File/Directory | Contains | Git-tracked? |
|----------------|----------|-------------|
| `CLAUDE.md` | Advisory frameworks ONLY (no PII) | Yes |
| `.claude/skills/` | Skill instructions (no PII) | Yes |
| `data/` | Financial transactions, balances | **NO** (gitignored) |
| `reports/` | Generated analysis | **NO** (gitignored) |
| `~/.claude/projects/` | User's financial profile | **NO** (outside repo) |
| `~/.hermes/memories/` | User's financial profile | **NO** (outside repo) |

**Never commit:**
- Dollar amounts tied to real financial situations
- Account numbers (even last-4 masks like ***1234)
- Transaction data or merchant lists
- Personal financial goals, income, or debt information

The CI pipeline scans for these patterns and will block your PR if detected.

## Writing Skills

Skills follow the [Agent Skills open standard](https://agentskills.io):

```
.claude/skills/your-skill/
  SKILL.md          ← YAML frontmatter (name, description) + markdown instructions
  references/       ← Optional supporting docs loaded on demand
  scripts/          ← Optional helper scripts
```

Guidelines:
- Keep SKILL.md under 500 lines / 5000 tokens
- Write the `description` field aggressively — list trigger phrases so the skill activates reliably
- Use `data/finance.db` as the primary data source (see schema in CLAUDE.md)
- Don't hardcode user-specific values — read from Client Context or memory files
- Query patterns should work for any user, not just one person's bank

## Adding Bank Parsers

To add support for a new bank's CSV format:

1. Add a detection function in `scripts/ingest.py` (check headers or filename patterns)
2. Map columns to the standard schema: `date, description, amount, account_mask`
3. Handle the bank's sign convention (some use negative for debits, others for credits)
4. Normalize to our convention: POSITIVE = money spent, NEGATIVE = money received
5. Test with a real export from that bank

## Advisory Frameworks

If you're adding financial planning frameworks to CLAUDE.md:

- Cite your source (CFP Board standards, academic research, established methodology)
- No product recommendations or affiliate-driven advice
- Frameworks must be general enough to apply regardless of income level or geography
- Follow the fiduciary standard: would a prudent advisor give this guidance?

## Pull Request Process

1. One concern per PR — don't bundle unrelated changes
2. Describe what you changed and why
3. If adding a skill, include example prompts that trigger it
4. If changing the DB schema, update both `scripts/ingest.py` and `CLAUDE.md`

## Response Times

I review PRs within a week. If it's been longer, ping me — I probably missed it.

## Code of Conduct

Be decent. This is a personal finance tool — people's money is involved. Treat
contributions and discussions with the same care you'd want from someone advising
you on your finances.
