#!/usr/bin/env python3
"""
run_eval.py — 2Wild model-eval harness driver.

Runs tool-calling / reasoning scenarios against any OpenAI-compatible
/v1/chat/completions endpoint, scores them, and writes a markdown + json
scorecard into results/.

Methodology adapted from "tool-eval-bench v2.0.1" by wolttam (credited in README).

Examples
--------
    # full suite
    python3 run_eval.py --endpoint http://100.92.77.51:8000/v1 \
        --model deepseek-v4-flash --label "DS4-Flash"

    # smoke test (a few scenario ids)
    python3 run_eval.py --endpoint http://100.113.64.18:8010/v1 \
        --model qwen3.6-27b-autoround --label "3090-27B" \
        --only TC-01,TC-16,TC-29

Only stdlib + `requests` are used.
"""

import argparse
import datetime
import json
import os
import re
import sys
import time

import requests

import eval_core
from scenarios import load_all


HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")


# ---- low-level chat call -----------------------------------------------------

def _stream_chat(endpoint, model, messages, tools, tool_choice, timeout):
    """
    Stream one /v1/chat/completions call. Returns:
        (assistant_message_dict, ttft_ms, usage_dict, latency_ms)

    assistant_message_dict has keys: role, content, tool_calls (list of
    {"id","name","arguments"(parsed dict)}).
    ttft_ms = ms to first token/chunk.
    """
    url = endpoint.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        # ask OpenAI-compatible servers to emit a final usage chunk while streaming
        "stream_options": {"include_usage": True},
        "temperature": 0.0,
        "max_tokens": 8192,
    }
    if tools:
        payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

    t0 = time.time()
    ttft_ms = None
    content_parts = []
    # tool_calls accumulate by index
    tool_acc = {}

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, stream=True, timeout=timeout)
    resp.raise_for_status()

    usage = {}
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw:
            continue
        if raw.startswith("data:"):
            raw = raw[len("data:"):].strip()
        if raw == "[DONE]":
            break
        try:
            chunk = json.loads(raw)
        except Exception:
            continue
        if ttft_ms is None:
            ttft_ms = (time.time() - t0) * 1000.0
        if chunk.get("usage"):
            usage = chunk["usage"]
        choices = chunk.get("choices") or []
        if not choices:
            continue
        delta = choices[0].get("delta") or {}
        if delta.get("content"):
            content_parts.append(delta["content"])
        for tc in delta.get("tool_calls") or []:
            idx = tc.get("index", 0)
            slot = tool_acc.setdefault(idx, {"id": None, "name": "", "arguments": ""})
            if tc.get("id"):
                slot["id"] = tc["id"]
            fn = tc.get("function") or {}
            if fn.get("name"):
                slot["name"] += fn["name"]
            if fn.get("arguments"):
                slot["arguments"] += fn["arguments"]

    latency_ms = (time.time() - t0) * 1000.0
    if ttft_ms is None:
        ttft_ms = latency_ms

    tool_calls = []
    for idx in sorted(tool_acc):
        slot = tool_acc[idx]
        if not slot["name"]:
            continue
        try:
            args = json.loads(slot["arguments"]) if slot["arguments"].strip() else {}
        except Exception:
            args = {"__raw__": slot["arguments"]}
        tool_calls.append({
            "id": slot["id"] or f"call_{idx}",
            "name": slot["name"],
            "arguments": args,
        })

    msg = {
        "role": "assistant",
        "content": "".join(content_parts),
        "tool_calls": tool_calls,
    }
    return msg, ttft_ms, usage, latency_ms


def _resolve_mock(mock_tools, name, args):
    """Return the mock tool result string for a tool call."""
    if name not in mock_tools:
        return f"ERROR: tool '{name}' is not available."
    spec = mock_tools[name]
    if callable(spec):
        try:
            out = spec(args)
        except Exception as e:  # defensive
            out = f"ERROR in mock: {e}"
        return out if isinstance(out, str) else json.dumps(out)
    return spec


# ---- scenario runner ---------------------------------------------------------

def run_scenario(endpoint, model, scenario, timeout=120):
    """
    Execute the multi-turn tool loop for one scenario.
    Returns a result dict ready for eval_core.summarize().
    """
    sid = scenario["id"]
    messages = [dict(m) for m in scenario["messages"]]
    tools = scenario.get("tools") or []
    tool_choice = scenario.get("tool_choice", "auto")
    mock_tools = scenario.get("mock_tools") or {}
    max_turns = scenario.get("max_turns", 4)

    transcript = []          # evaluator-facing simplified view
    turn_latencies = []
    first_ttft = None
    total_prompt = 0
    total_completion = 0
    turns = 0
    error = None

    t_start = time.time()
    try:
        for _ in range(max_turns):
            msg, ttft, usage, latency = _stream_chat(
                endpoint, model, messages, tools, tool_choice, timeout
            )
            turns += 1
            turn_latencies.append(latency)
            if first_ttft is None:
                first_ttft = ttft
            total_prompt += int(usage.get("prompt_tokens", 0) or 0)
            total_completion += int(usage.get("completion_tokens", 0) or 0)

            # record into evaluator transcript
            transcript.append({
                "role": "assistant",
                "content": msg["content"],
                "tool_calls": [{"name": tc["name"], "arguments": tc["arguments"]}
                               for tc in msg["tool_calls"]],
            })

            # append the assistant message to the running conversation (OpenAI shape)
            assistant_api_msg = {"role": "assistant", "content": msg["content"] or None}
            if msg["tool_calls"]:
                assistant_api_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]),
                        },
                    }
                    for tc in msg["tool_calls"]
                ]
            messages.append(assistant_api_msg)

            if not msg["tool_calls"]:
                break  # final natural-language answer reached

            # execute each tool call against the mocks and feed results back
            for tc in msg["tool_calls"]:
                result = _resolve_mock(mock_tools, tc["name"], tc["arguments"])
                transcript.append({
                    "role": "tool", "name": tc["name"], "content": result,
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["name"],
                    "content": result,
                })
    except Exception as e:
        error = str(e)

    wall_s = time.time() - t_start

    # evaluate
    if error and not transcript:
        verdict, reason = eval_core.FAIL, f"Run error: {error[:120]}"
    else:
        try:
            verdict, reason = scenario["evaluator"](transcript)
        except Exception as e:
            verdict, reason = eval_core.FAIL, f"Evaluator error: {e}"
        if error:
            reason = f"{reason} (note: turn error: {error[:80]})"

    points = eval_core.VERDICT_POINTS[verdict]
    total_tokens = total_prompt + total_completion

    return {
        "id": sid,
        "category": scenario["category"],
        "verdict": verdict,
        "points": points,
        "reason": reason,
        "ttft_ms": first_ttft,
        "turns": turns,
        "wall_s": wall_s,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
        "turn_latencies_ms": turn_latencies,
    }


# ---- output ------------------------------------------------------------------

def _slugify(label):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", label.strip().lower()).strip("-")
    return s or "model"


def write_results(meta, scenario_results, agg):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    slug = _slugify(meta["label"])
    stamp = meta["utc"].replace(":", "").replace("-", "").replace(" ", "T")
    base = f"{slug}__{stamp}"
    md_path = os.path.join(RESULTS_DIR, base + ".md")
    json_path = os.path.join(RESULTS_DIR, base + ".json")

    with open(md_path, "w") as f:
        f.write(eval_core.format_markdown_report(meta, scenario_results, agg))

    with open(json_path, "w") as f:
        json.dump({
            "meta": meta,
            "aggregate": agg,
            "scenarios": scenario_results,
        }, f, indent=2)

    return md_path, json_path


# ---- CLI ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="2Wild model-eval harness")
    ap.add_argument("--endpoint", required=True,
                    help="OpenAI-compatible base, e.g. http://HOST:PORT/v1")
    ap.add_argument("--model", required=True, help="model id served at the endpoint")
    ap.add_argument("--label", required=True, help="display name for the run")
    ap.add_argument("--only", default=None,
                    help="comma-separated scenario ids to run (e.g. TC-01,TC-16)")
    ap.add_argument("--category", default=None,
                    help="only run scenarios in this category")
    ap.add_argument("--timeout", type=int, default=120, help="per-call timeout (s)")
    ap.add_argument("--note", default=None, help="free-text note stored in the report")
    ap.add_argument("--quant", default=None,
                    help="quantization, e.g. AWQ-INT4, NVFP4, FP8, Q2_K_XL")
    ap.add_argument("--cluster", default=None,
                    help="hardware/topology, e.g. '4x DGX Spark TP=4'")
    ap.add_argument("--ctx", default=None,
                    help="served context length, e.g. 230K, 1M")
    ap.add_argument("--no-write", action="store_true",
                    help="print only, don't write result files")
    args = ap.parse_args()

    scenarios = load_all()
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        scenarios = [s for s in scenarios if s["id"] in want]
    if args.category:
        scenarios = [s for s in scenarios
                     if s["category"].lower() == args.category.lower()]

    if not scenarios:
        print("No scenarios matched the filter.", file=sys.stderr)
        sys.exit(2)

    cats = sorted({s["category"] for s in scenarios})
    print(f"Running {len(scenarios)} scenarios across {len(cats)} categories "
          f"vs {args.label} ({args.model}) @ {args.endpoint}\n")

    results = []
    for s in scenarios:
        r = run_scenario(args.endpoint, args.model, s, timeout=args.timeout)
        results.append(r)
        print(eval_core.format_scenario_log(r))

    agg = eval_core.summarize(results)
    print()
    print(eval_core.format_summary_block(agg))
    print()
    print(eval_core.format_metrics_block(agg))

    meta = {
        "label": args.label,
        "model": args.model,
        "endpoint": args.endpoint,
        "utc": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "note": args.note,
        "quant": args.quant,
        "cluster": args.cluster,
        "ctx": args.ctx,
    }

    if not args.no_write:
        md_path, json_path = write_results(meta, results, agg)
        print(f"\nWrote {md_path}")
        print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
