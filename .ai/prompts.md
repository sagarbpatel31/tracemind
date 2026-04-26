# AI Prompts

All LLM prompts used in TraceMind — location, design rationale, token counts.

---

## 1. Incident Analysis Summary

**File:** `apps/api/app/services/analysis.py` → `generate_llm_summary()`  
**Model:** `claude-haiku-4-5`  
**Trigger:** `POST /api/v1/incidents/{id}/analyze`

### Prompt template

```
Incident: {incident_title}
Top cause: {top_cause['cause']} (confidence: {top_cause['confidence']:.0%})
Evidence: {evidence_str}   ← capped at 4 signals joined by "; "
Remediation hint: {top_cause['description']}

Write 2 sentences: what failed and what to do. Terse. No preamble.
```

### Token budget

| | Tokens |
|-|--------|
| Input | ~120 |
| Output ceiling | 80 (`max_tokens=80`) |
| Expected output | 40–60 (2 sentences) |
| Cost per 1000 calls | ~$0.03 |

### Design principles applied (caveman-style)

- **Instruction is the last line:** model reads forward, instruction at end reduces preamble generation
- **"Terse. No preamble."** — explicit constraint kills filler phrases ("Certainly!", "Based on the analysis...")
- **Structured input, not narrative input** — rules output is already structured; prompt feeds keys not paragraphs
- **Hard output cap** — `max_tokens=80` enforces 2-sentence ceiling even if model tries to elaborate

### Example output

> Thermal throttling on the TX2 caused inference latency to spike 3× above baseline, triggering a mission abort. Check cooling fan clearance and reduce model inference frequency to below 10 Hz.

### Fallback behavior

If `settings.anthropic_api_key == ""`:
```python
return top_cause.get("description", top_cause.get("cause", "Analysis unavailable."))
```
Returns the rules-generated description string. No API call, no cost, no error.

---

## Prompt design guidelines for future LLM features

When adding new LLM calls to TraceMind:

1. **Always set `max_tokens`** — never let the model run unbounded
2. **Use Haiku** unless the task requires multi-step reasoning or code generation
3. **Feed structured data, not prose** — extract key fields before prompting
4. **End with constraint** — last line should be the output format instruction
5. **Add fallback** — every LLM call must have a non-LLM fallback path
6. **Log `message.usage`** in dev to measure actual token consumption before deploying

### Template for new LLM calls

```python
async def generate_X(inputs: dict) -> str:
    if not settings.anthropic_api_key:
        return fallback_string(inputs)      # ← always required

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    prompt = build_terse_prompt(inputs)     # structured fields, not prose

    message = await client.messages.create(
        model="claude-haiku-4-5",           # upgrade to sonnet only if needed
        max_tokens=N,                        # explicit ceiling
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
```
