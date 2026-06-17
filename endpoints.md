# Endpoints

Internal tailnet IPs only — **no secrets or tokens here**. These are
OpenAI-compatible `/v1` servers reachable on the 2Wild tailnet.

| Label | Base URL | Model ID | Notes |
|---|---|---|---|
| DS4-Flash | `http://100.92.77.51:8000/v1` | `deepseek-v4-flash` | DeepSeek-V4-Flash on the 3-Spark cluster. LIVE again. |
| 3090 27B | `http://100.113.64.18:8010/v1` | `qwen3.6-27b-autoround` | Dual-3090 prod supervisor brain. Used for the smoke test. |
| 3090 35B | `http://100.113.64.18:8059/v1` | `qwen3.6-35b-a3b-autoround` | 35B-A3B on the 3rd 3090 (ik_llama / vLLM). |

## One-liners

```bash
# Full suite against DS4-Flash
python3 run_eval.py --endpoint http://100.92.77.51:8000/v1 \
    --model deepseek-v4-flash --label "DS4-Flash"

# Full suite against the 3090 27B
python3 run_eval.py --endpoint http://100.113.64.18:8010/v1 \
    --model qwen3.6-27b-autoround --label "3090-27B"

# Full suite against the 3090 35B
python3 run_eval.py --endpoint http://100.113.64.18:8059/v1 \
    --model qwen3.6-35b-a3b-autoround --label "3090-35B"

# Smoke test (a few scenarios)
python3 run_eval.py --endpoint http://100.113.64.18:8010/v1 \
    --model qwen3.6-27b-autoround --label "3090-27B smoke" \
    --only TC-01,TC-16,TC-29
```

After any run, refresh the table:

```bash
python3 update_leaderboard.py
```
