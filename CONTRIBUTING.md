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
