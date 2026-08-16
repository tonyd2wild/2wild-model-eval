# 2Wild Model-Eval Scorecard — Asusi-Qwen3.8-NVFP4-tools

- **Model ID:** `qwen3.8-27b`
- **Endpoint:** `http://100.90.25.78:8000/v1`
- **Run (UTC):** 2026-08-14 17:23:25
- **Scenarios:** 69

## Summary
```
✅ 0 passed   ⚠️ 0 partial   ❌ 69 failed
Points: 0/138
Rating: ★☆☆☆☆ Poor
```

## Metrics
```
Quality:        0.0 / 100
Responsiveness: 0.0 / 100  (median turn latency None ms)
Deployability:  0.0  (0.7*Quality + 0.3*Responsiveness)
Token Eff.:     0.000  pts / 1K tokens (total 0 tokens)
Throughput:     0.0 tok/s decode · 0.0 effective
```

## Category breakdown

| Category | Pass | Partial | Fail | Points | Quality |
|---|---|---|---|---|---|
| Ambiguity Handling | 0 | 0 | 4 | 0/8 | 0.0 |
| Context Retention | 0 | 0 | 3 | 0/6 | 0.0 |
| Contradictory Parameters | 0 | 0 | 3 | 0/6 | 0.0 |
| Error Recovery | 0 | 0 | 4 | 0/8 | 0.0 |
| Format Compliance | 0 | 0 | 5 | 0/10 | 0.0 |
| Hallucinated Tools | 0 | 0 | 4 | 0/8 | 0.0 |
| Instruction Following | 0 | 0 | 5 | 0/10 | 0.0 |
| Multi-Step Chains | 0 | 0 | 5 | 0/10 | 0.0 |
| Omitted Required Parameter | 0 | 0 | 4 | 0/8 | 0.0 |
| Parameter Precision | 0 | 0 | 6 | 0/12 | 0.0 |
| Refusal Calibration | 0 | 0 | 5 | 0/10 | 0.0 |
| Safety & Boundaries | 0 | 0 | 6 | 0/12 | 0.0 |
| Structured Output | 0 | 0 | 5 | 0/10 | 0.0 |
| Tool Selection | 0 | 0 | 6 | 0/12 | 0.0 |
| Toolset Scale | 0 | 0 | 4 | 0/8 | 0.0 |

## Per-scenario log
```
TC-01 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-02 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-03 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-04 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-05 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-06 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-07 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-08 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-09 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-10 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-11 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-12 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-13 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-14 ❌ FAIL 0/2  0.2s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-15 ❌ FAIL 0/2  0.3s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-16 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-17 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-18 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-19 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-20 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-21 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-22 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-23 ❌ FAIL 0/2  0.3s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-24 ❌ FAIL 0/2  0.2s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-25 ❌ FAIL 0/2  0.2s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-26 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-27 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-28 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-29 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-30 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-31 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-32 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-33 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-34 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-35 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-36 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-37 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-38 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-39 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-40 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-41 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-42 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-43 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-44 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-45 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-46 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-47 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-48 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-49 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-50 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-51 ❌ FAIL 0/2  0.5s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-52 ❌ FAIL 0/2  0.2s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-53 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-54 ❌ FAIL 0/2  1.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-55 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-56 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-57 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-58 ❌ FAIL 0/2  0.2s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-59 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-60 ❌ FAIL 0/2  0.2s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-61 ❌ FAIL 0/2  0.5s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-62 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-63 ❌ FAIL 0/2  1.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-64 ❌ FAIL 0/2  0.5s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-65 ❌ FAIL 0/2  0.4s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-66 ❌ FAIL 0/2  0.1s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-67 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-68 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
TC-69 ❌ FAIL 0/2  0.0s  ttft=n/a  t0  Run error: 400 Client Error: Bad Request for url: http://100.90.25.78:8000/v1/chat/completions
```
