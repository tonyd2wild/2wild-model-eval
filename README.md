# 2Wild Model-Eval

A self-hosted **tool-calling / reasoning benchmark harness** plus a results
store for the 2Wild local model fleet (DS4-Flash, Qwen3.6-27B, Qwen3.6-35B-A3B,
and any other OpenAI-compatible endpoint).

It fires a suite of scenarios at an OpenAI-compatible `/v1/chat/completions`
server with `tools` + `tool_choice`, runs the full multi-turn tool loop (feeding
mock tool results back until the model gives a final answer or hits a turn cap),
scores each scenario, and writes a markdown + JSON scorecard.

> **Methodology credit.** This is our own implementation, but the methodology —
> the Pass/Partial/Fail (2/1/0) scoring, the Quality / Responsiveness /
> Deployability / Token-Efficiency metric set, the star rating, and the
> per-scenario log style — is adapted from **`tool-eval-bench v2.0.1` by
> wolttam**. Credit to wolttam for the original framework.

Dependencies: **Python 3 + `requests`** (everything else is stdlib).

---

## Quick start

```bash
# Run the full 69-scenario suite against any OpenAI-compatible endpoint:
python3 run_eval.py --endpoint http://HOST:PORT/v1 --model MODEL_ID --label "Name"

# Then refresh the leaderboard:
python3 update_leaderboard.py
```

See [`endpoints.md`](endpoints.md) for the known fleet endpoints and copy-paste
one-liners.

### Useful flags
- `--only TC-01,TC-16,TC-29` — run just those scenario ids (smoke testing).
- `--category "Safety & Boundaries"` — run one category.
- `--timeout 90` — per-call timeout in seconds (default 120).
- `--note "..."` — free-text note stored in the scorecard.
- `--no-write` — print to console only, don't write result files.

---

## Scoring & metrics

**Per-scenario verdict** (each scenario has a programmatic evaluator):

| Verdict | Icon | Points |
|---|---|---|
| Pass | ✅ | 2 |
| Partial | ⚠️ | 1 |
| Fail | ❌ | 0 |

**Metrics**

- **Quality (0–100)** = `(points / max_points) × 100`, where `max_points =
  scenarios × 2`.
- **Responsiveness (0–100)** — derived from the **median per-turn latency**
  across every model turn in the run. Piecewise-linear ramp:
  - `≤ 500 ms` → **100** (instant)
  - `≥ 20 000 ms` → **0** (unusable)
  - in between → `100 × (1 − (latency − 500) / (20000 − 500))`
- **Deployability** = `0.7 × Quality + 0.3 × Responsiveness`.
- **Token Efficiency** = `points per 1 000 total tokens`
  (`points / (total_tokens / 1000)`). Requires the server to emit `usage`
  in the streaming response; the harness requests it via
  `stream_options.include_usage`.
- **Per-scenario:** `ttft(ms)` (time to first streamed token), turn count,
  and wall seconds.

**Star rating** (from Quality): `90+ → ★★★★★`, `80–89 → ★★★★`,
`70–79 → ★★★`, `60–69 → ★★`, `< 60 → ★`.

### Summary style
```
✅ 60 passed   ⚠️ 5 partial   ❌ 4 failed
Points: 125/138
Rating: ★★★★★ Excellent
```

### Per-scenario log style
```
TC-01 ✅ PASS 2/2  6.4s  ttft=753ms  t2  Used get_weather with Berlin only.
```

---

## Categories (15)

The suite ships **69 scenarios** spanning every category:

1. **Tool Selection** — pick the right tool (and skip tools when none fits).
2. **Parameter Precision** — exact, correctly-typed arguments.
3. **Instruction Following** — honor explicit constraints (limits, scope, format).
4. **Safety & Boundaries** — refuse unsafe actions; resist **prompt injection**
   and **"sleeper" injection** planted in tool output.
5. **Toolset Scale** — find the right tool inside a ~50-tool catalog.
6. **Multi-Step Chains** — sequence multiple tool calls, feeding results forward.
7. **Structured Output** — return strict, parseable JSON.
8. **Error Recovery** — handle a tool error (retry / report) without hallucinating.
9. **Contradictory Parameters** — conflicting values → clarify or take the most recent.
10. **Omitted Required Parameter** — a required arg is missing → ask, don't guess.
11. **Ambiguity Handling** — vague request → ask a clarifying question.
12. **Context Retention** — recall facts from earlier turns.
13. **Hallucinated Tools** — don't invent a tool that isn't in the toolset.
14. **Format Compliance** — obey an explicit output format (table, bullets, CSV…).
15. **Refusal Calibration** — refuse genuinely-bad requests, help benign look-alikes.

---

## Layout

```
2wild-model-eval/
├── run_eval.py            # CLI driver: streaming chat, multi-turn tool loop, timing
├── eval_core.py           # scoring, metric formulas, report formatting
├── update_leaderboard.py  # rebuilds LEADERBOARD.md from results/*.json
├── endpoints.md           # fleet endpoints + one-liners (tailnet IPs, no secrets)
├── LEADERBOARD.md         # auto-generated, sorted by Deployability
├── scenarios/
│   ├── __init__.py        # auto-discovers every SCENARIOS list
│   ├── evaluators.py      # transcript-inspection + verdict helpers
│   ├── common_tools.py    # reusable tool schemas + a ~50-tool catalog
│   └── cat_*.py           # scenario data, one module per category group
└── results/
    └── <slug>__<UTCstamp>.md / .json   # one scorecard per run (committed)
```

### How a scenario is defined

Each scenario is plain data: an `id`, a `category`, the initial `messages`,
the `tools` schemas, a `mock_tools` map (static strings or `callable(args)->str`
so multi-step chains can return different results per call), a `max_turns` cap,
and an `evaluator(transcript) -> (verdict, reason)`. The runner records a
simplified transcript of assistant turns (content + tool calls) and tool
results, which the evaluator inspects to assign 2 / 1 / 0.

---

## Notes

- **Mock tools, real model.** Tool *execution* is mocked (deterministic, offline)
  so scoring is reproducible; the model under test is the real served endpoint.
- **`datetime.utcnow()`** is used for result timestamps (acceptable here).
- This is an internal 2Wild tool. Endpoints are tailnet-private; this repo
  contains **no secrets or tokens**.
