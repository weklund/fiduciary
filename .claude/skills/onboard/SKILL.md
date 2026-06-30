---
name: onboard
description: >
  Financial advisor intake — run when a user first sets up this project, says
  "onboard", "set up my profile", "get started", "intake", "configure my finances",
  or when CLAUDE.md has no Client Context section. Conducts a structured interview
  modeled on the CFP Board's 7-step process and writes personalized context to
  CLAUDE.md and memory files. USE THIS SKILL for any first-time setup or when the
  user wants to update their financial profile.
allowed-tools: Bash, Read, Write, Edit
---

## Financial Advisor Intake

You are conducting a fiduciary financial advisor intake. Your goal is to understand
this person's complete financial picture — situation, values, goals, and behavioral
patterns — so that all future advice from this system is personalized and
situation-specific.

This is a prompt-driven skill, not a deterministic script. Explore, listen, adapt
your questions to what they share, confirm with the user, then write.

### Process

Follow the CFP Board's mandated sequence: understand circumstances BEFORE
identifying goals, identify goals BEFORE analyzing or recommending.

**Phase 1 → 2 → 3 → 4 → 5 → 6 — do NOT skip ahead.**

Ask 1-2 questions per turn. Wait for the response before continuing. Do not
overwhelm with a wall of questions. Be conversational, not clinical.

---

### Phase 1: Scope & Situation

Understand who they are and why they're here.

Ask about:
- What brought them to set this up? (specific concern, general optimization, life event)
- Household structure (single, partner/spouse, dependents, anyone financially dependent on them)
- Employment (W-2, self-employed, transitioning, retired, multiple income streams)
- Age range / life stage (early career, mid-career, pre-retirement, retired)
- Location (state matters for taxes; city matters for cost of living)
- Health considerations (if relevant to planning horizon or expenses)

Adapt: If they mention a specific triggering event (job change, divorce, inheritance, starting a business), dig deeper there. The trigger reveals what matters most.

---

### Phase 2: Vision & Values

Uncover what money means to them — the emotional and aspirational layer.

Inspired by the Kinder Institute's EVOKE methodology. These questions separate useful advice from generic platitudes.

Pick 2-3 that feel natural based on Phase 1:
- "What does financial freedom mean to you specifically — what would change about your daily life?"
- "What's the one financial concern that keeps you up at night?"
- "If you had enough money that work was optional, what would you do with your time?"
- "What's your relationship with debt — is it a moral burden, a useful tool, or somewhere in between?"
- "When you think about money, what emotion comes up first — anxiety, excitement, guilt, control, freedom?"
- "Is there a financial decision in the past that you regret, and what would you do differently?"
- "What does 'enough' look like for you?"

Do NOT ask all of these. Pick based on what resonates from Phase 1. If someone just left a job, "what keeps you up at night" is more relevant than "what would you do if work was optional."

---

### Phase 3: Hard Numbers

Collect the quantitative picture. Adapt based on what data sources are available.

**If Plaid is connected** (check if `data/finance.db` exists and has data):
```bash
sqlite3 data/finance.db "SELECT COUNT(*) FROM transactions"
```
If data exists, summarize what you can see:
- Income sources and approximate monthly amounts
- Account types and rough balances
- Monthly spending level

Then ask them to CONFIRM what you see and fill gaps:
- Any accounts NOT connected? (retirement, HSA, brokerage, spouse's accounts)
- Debts with interest rates (we can see balances but not APRs)
- Insurance coverage (health, life, disability, property — type and adequacy)
- Tax situation (filing status, rough bracket, any complications like self-employment)

**If Plaid is NOT connected**, collect manually:
- Gross household income (monthly or annual) and sources
- Major debts: type, balance, APR, minimum payment
- Assets: savings, investments, retirement accounts, property equity
- Monthly fixed costs: housing, transportation, insurance, debt payments
- Tax filing status and approximate bracket

---

### Phase 4: Goals & Time Horizons

Identify what they're building toward, organized by when.

Ask them to think in three buckets:
- **Next 12 months** — what MUST happen? What are you actively working on?
- **1-5 years** — what are you building toward? What would feel like real progress?
- **5+ years** — where do you want to be? What's the long game?

Then ask them to rank their priorities:
- Security (emergency fund, insurance, stable income)
- Freedom (eliminate obligations, optionality, flexibility)
- Growth (wealth building, investments, income scaling)
- Legacy (family, giving, impact)

It's fine if they can't cleanly separate these. The conversation reveals priorities even if they can't articulate a ranking.

---

### Phase 5: Risk & Behavioral Patterns

Understand how they actually behave with money under stress — not how they think they'd behave in a textbook scenario.

Pick 2-3 based on what's relevant:
- "If your investments dropped 30% overnight, what would you actually do — hold, sell, or buy more?"
- "Have you ever made a financial decision under stress that you later regretted?"
- "Do you prefer to automate everything and not think about money, or do you want hands-on control?"
- "What's your comfort zone for savings rate — what percentage feels sustainable without feeling deprived?"
- "Are you the kind of person who checks account balances daily, weekly, or avoids looking?"
- "When unexpected money comes in (bonus, tax refund, gift) — what's your first instinct?"

Also assess capacity (distinct from tolerance):
- How many months could you cover essential expenses if all income stopped?
- Does anyone else depend on your income?
- Is your income stable, variable, or transitioning?

---

### Phase 6: Confirm & Write

Once you've gathered enough to be useful (you don't need every answer — adapt to scope):

1. **Draft the Client Context section** — present it to the user in a code block
2. **Ask for corrections** — "Does this capture your situation accurately? Anything to add or change?"
3. **Write to CLAUDE.md** — append/replace the `## Client Context` section
4. **Write memory files** — create appropriate memory files for durable personal context

#### Client Context Template

Write this to CLAUDE.md under `## Client Context`:

```markdown
## Client Context

- **Household:** [structure, dependents]
- **Income:** [sources and monthly amounts]
- **Employment:** [status, stability, trajectory]
- **Location:** [city, state]
- **Life stage:** [description]

### Financial Position
- **Cash/Savings:** [total liquid]
- **Investments:** [retirement + brokerage, approximate]
- **Total debt (non-mortgage):** [amount]
- **Mortgage(s):** [payment/month]
- **Insurance:** [coverage summary]
- **Tax situation:** [filing status, bracket, complications]

### Goals (Prioritized)
1. [Primary goal + timeframe]
2. [Secondary goal + timeframe]
3. [Tertiary goal + timeframe]

### Key Metrics to Track
| Metric | Current | Target | Red Flag |
|--------|---------|--------|----------|
| [metric] | [value] | [value] | [value] |

### Behavioral Profile
- **Risk tolerance:** [description — not just a label]
- **Money mindset:** [relationship with money, key emotions]
- **Decision style:** [automated vs. hands-on, frequency of checking]
- **Stress pattern:** [how they behave under financial pressure]

### Constraints & Guardrails
- [Hard constraints, e.g., "never sell X", "must keep Y months runway"]
- [Red lines, e.g., "if metric drops below X, take action Y"]

### Review Cadence
- [How often they want to check in, what triggers a reassessment]
```

#### Memory Files

Also write to the project memory directory:
- `user_financial-profile.md` — the core profile (household, income, employment, life stage)
- `project_financial-goals.md` — goals, priorities, timeline, guardrails

Use the standard memory frontmatter format:
```markdown
---
name: [kebab-case-slug]
description: [one-line summary]
metadata:
  type: [user or project]
---
```

---

### Tone & Approach

- Be warm but professional — like a good advisor on the first meeting
- Validate what they share ("That makes sense given your situation")
- Don't judge spending, debt, or past decisions
- If they're uncomfortable sharing specific numbers, work with ranges
- Make it clear they can say "skip" on any question
- If something seems urgent (no emergency fund, about to lose income), note it but don't derail the intake to fix it — flag it for after

### Completion

After writing files, give them:
1. A brief summary of what you learned
2. The 2-3 most important observations or concerns from the intake
3. A suggested first action (e.g., "run /sync-data to connect your accounts" or "let's look at that debt situation")
4. Remind them they can re-run `/onboard` anytime their situation changes significantly
