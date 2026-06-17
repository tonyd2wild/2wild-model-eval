"""
evaluators.py — helpers for inspecting a runner transcript and building verdicts.

A transcript is a list of step dicts:
    {"role": "assistant", "content": str, "tool_calls": [ {"name", "arguments"} ]}
    {"role": "tool", "name": str, "content": str}

Evaluator functions return (verdict, reason) where verdict is one of the
eval_core constants PASS / PARTIAL / FAIL.
"""

import json
import re

from eval_core import PASS, PARTIAL, FAIL  # noqa: F401  (re-exported for scenarios)


# ---- transcript inspection ---------------------------------------------------

def all_tool_calls(transcript):
    """Flat list of every tool call across the transcript, in order."""
    calls = []
    for step in transcript:
        if step.get("role") == "assistant":
            for tc in step.get("tool_calls") or []:
                calls.append(tc)
    return calls


def tool_names_called(transcript):
    return [tc["name"] for tc in all_tool_calls(transcript)]


def calls_to(transcript, name):
    return [tc for tc in all_tool_calls(transcript) if tc["name"] == name]


def first_call(transcript, name=None):
    for tc in all_tool_calls(transcript):
        if name is None or tc["name"] == name:
            return tc
    return None


def final_text(transcript):
    """The last assistant message that carried natural-language content."""
    for step in reversed(transcript):
        if step.get("role") == "assistant":
            txt = (step.get("content") or "").strip()
            if txt:
                return txt
    return ""


def any_assistant_text(transcript):
    """Concatenated assistant natural-language content (lowercased)."""
    parts = []
    for step in transcript:
        if step.get("role") == "assistant" and step.get("content"):
            parts.append(step["content"])
    return "\n".join(parts).lower()


def num_tool_calls(transcript):
    return len(all_tool_calls(transcript))


# ---- argument helpers --------------------------------------------------------

def arg(tc, key, default=None):
    args = tc.get("arguments") or {}
    return args.get(key, default)


def args_of(tc):
    return tc.get("arguments") or {}


# ---- text matching -----------------------------------------------------------

def contains_any(text, needles):
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


def contains_all(text, needles):
    t = (text or "").lower()
    return all(n.lower() in t for n in needles)


# ---- JSON extraction (for Structured Output scenarios) -----------------------

def extract_json(text):
    """
    Pull the first JSON object/array out of a final text answer. Handles the
    case where the model wraps it in a ```json fence. Returns parsed obj or None.
    """
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    candidate = fence.group(1) if fence else None
    if candidate is None:
        m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        candidate = m.group(1) if m else None
    if candidate is None:
        return None
    try:
        return json.loads(candidate)
    except Exception:
        return None


def is_pure_json(text):
    """True if the final answer is JSON with no extra prose around it."""
    if not text:
        return False
    stripped = text.strip()
    # allow a single ```json fence
    fence = re.fullmatch(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", stripped, re.DOTALL)
    if fence:
        try:
            json.loads(fence.group(1))
            return True
        except Exception:
            return False
    try:
        json.loads(stripped)
        return True
    except Exception:
        return False
