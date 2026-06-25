# Endpoints

Internal tailnet IPs only — **no secrets or tokens here**. These are
OpenAI-compatible `/v1` servers reachable on the 2Wild tailnet.

| Label | Base URL | Model ID | Notes |
|---|---|---|---|
| DS4-Flash | `http://100.92.77.51:8000/v1` | `deepseek-v4-flash` | DeepSeek-V4-Flash on the 3-Spark cluster. LIVE again. |
| 3090 27B | `http://100.113.64.18:8010/v1` | `qwen3.6-27b-autoround` | Dual-3090 prod supervisor brain. Used for the smoke test. |
| 3090 35B | `http://100.113.64.18:8059/v1` | `qwen3.6-35b-a3b-autoround` | 35B-A3B on the 3rd 3090 (ik_llama / vLLM). Now reused for Ornith. |
| Ornith 35B | `http://100.113.64.18:8059/v1` | `ornith-1.0-35b` | Ornith-1.0-35B GGUF Q5_K_M, thinking-OFF, single-stream llama.cpp/ik-llama slot on the 3090 box. |

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

# Full suite against Ornith-1.0-35B (GGUF, thinking-OFF, single-stream)
python3 run_eval.py --endpoint http://100.113.64.18:8059/v1 \
    --model ornith-1.0-35b --label "ornith-1.0-35b-gguf-thinkoff" \
    --quant Q5_K_M --cluster "3090 dual (ik-llama)" --ctx 32768

# Smoke test (a few scenarios)
python3 run_eval.py --endpoint http://100.113.64.18:8010/v1 \
    --model qwen3.6-27b-autoround --label "3090-27B smoke" \
    --only TC-01,TC-16,TC-29
```

After any run, refresh the table:

```bash
python3 update_leaderboard.py
```
