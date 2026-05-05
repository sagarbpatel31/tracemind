# Prompts

Reusable prompts for working on this repo, plus the actual LLM prompts used in the product.

---

## Product prompts (in the codebase)

### Incident analysis summary

**File:** `apps/api/app/services/analysis.py:generate_llm_summary()`
**Model:** `claude-haiku-4-5`
**Trigger:** `POST /api/v1/incidents/{id}/analyze`

```
Incident: {incident_title}
Top cause: {top_cause['cause']} (confidence: {confidence:.0%})
Evidence: {evidence_str}          ← joined by "; ", capped at 4 signals
Remediation hint: {top_cause['description']}

Write 2 sentences: what failed and what to do. Terse. No preamble.
```

**Token budget:** ~120 input / 80 output ceiling / ~$0.03 per 1,000 calls

**Design notes:**
- Constraint is the last line (model reads forward — instruction at end suppresses preamble generation)
- "Terse. No preamble." kills filler phrases ("Certainly!", "Based on the analysis...")
- Structured key/value input, not prose — feeds the model pre-digested signal
- `max_tokens=80` hard ceiling enforces 2-sentence output even if model wants to elaborate
- Fallback: returns `top_cause['description']` (rules text) if `ANTHROPIC_API_KEY` is empty

---

## Template for new LLM features

```python
async def generate_X(inputs: dict) -> str:
    # 1. Always fail gracefully
    if not settings.anthropic_api_key:
        return fallback_value(inputs)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    # 2. Build terse, structured prompt
    prompt = (
        f"Key: {inputs['key']}\n"
        f"Context: {inputs['context']}\n\n"
        "Output constraint here. Terse. No preamble."  # last line = instruction
    )

    # 3. Hard output ceiling
    message = await client.messages.create(
        model="claude-haiku-4-5",   # upgrade to sonnet only if task requires reasoning
        max_tokens=80,               # set explicitly — never omit
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
```

---

## Dev prompts (for Claude Code sessions)

### Understand a module before changing it
```
Read .ai/architecture.md sections for [module name].
Then read graphify-out/GRAPH_REPORT.md for community structure.
Then show me how [specific function] connects to [other function].
Do not make any changes yet.
```

### Add a new API route
```
I need to add a new route: [METHOD] [path] that does [description].
Before writing code:
1. Read apps/api/app/routers/ to find the right router file
2. Read apps/api/app/schemas/ for existing schema patterns
3. Read apps/api/app/models/ to confirm which models to query
Follow the existing async SQLAlchemy 2.0 patterns. No new dependencies.
```

### Add a new model field
```
I need to add field [name] ([type]) to [Model] in apps/api/app/models/[file].
IMPORTANT: create_all will not add this column to an existing table.
After adding the model field, also provide the ALTER TABLE SQL to run on the live DB.
Do not use Alembic — alembic/versions/ is empty and not yet initialized.
```

### Debug a failing endpoint
```
The route [METHOD] [path] is returning [status code / error].
Read .ai/debugging.md for the [category] section first.
Then read the route handler in apps/api/app/routers/[file].py.
Show me the exact curl command to reproduce the error, then diagnose.
```

### Add a new LLM feature
```
I want to add LLM-powered [feature] to [location].
Read .ai/prompts.md for the template and token budget rules.
Read .ai/principles.md rules 2, 3, and 4.
The feature must: (1) have a non-LLM fallback, (2) use claude-haiku-4-5,
(3) have explicit max_tokens, (4) not require ANTHROPIC_API_KEY to be set.
```

### Review before merging
```
Before I merge [branch], check:
1. No passlib imports added
2. No `asChild` prop on Button in apps/web/
3. All ingest route payloads use wrapper format {metrics:[...]} not flat arrays
4. Any new LLM calls have a fallback path
5. No secrets hardcoded in any file
Report findings only — do not fix anything.
```
