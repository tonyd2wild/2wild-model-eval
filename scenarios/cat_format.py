"""Format Compliance — obey an explicit output format (markdown table, bullets,
   uppercase, CSV, code fence) in the natural-language answer."""

import re

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, final_text,
)
from scenarios.common_tools import CALCULATOR


def _eval_markdown_table(transcript):
    txt = final_text(transcript)
    rows = [l for l in txt.splitlines() if l.strip().startswith("|")]
    has_sep = any(re.match(r"\s*\|?[\s:-]*\|[\s:|-]*", l) and "-" in l for l in rows)
    if len(rows) >= 3 and has_sep:
        return PASS, "Produced a markdown table with header separator."
    if len(rows) >= 2:
        return PARTIAL, "Table-ish but missing proper separator/rows."
    return FAIL, "No markdown table."


def _eval_bullets(transcript):
    txt = final_text(transcript)
    bullets = [l for l in txt.splitlines() if re.match(r"\s*[-*•]\s+", l)]
    if len(bullets) >= 3:
        return PASS, f"Returned {len(bullets)} bullet points as asked."
    if len(bullets) >= 1:
        return PARTIAL, f"Only {len(bullets)} bullet(s)."
    return FAIL, "No bullet list."


def _eval_uppercase(transcript):
    txt = final_text(transcript).strip()
    letters = [c for c in txt if c.isalpha()]
    if not letters:
        return FAIL, "No answer."
    upper_ratio = sum(c.isupper() for c in letters) / len(letters)
    if upper_ratio >= 0.95:
        return PASS, "Answer fully uppercase as required."
    if upper_ratio >= 0.6:
        return PARTIAL, f"Mostly uppercase ({upper_ratio:.0%})."
    return FAIL, "Did not uppercase the answer."


def _eval_csv(transcript):
    txt = final_text(transcript)
    line = next((l for l in txt.splitlines() if "," in l), "")
    parts = [p.strip() for p in line.split(",") if p.strip()]
    if len(parts) >= 3:
        return PASS, "Returned comma-separated values."
    if "," in txt:
        return PARTIAL, "Some commas but not a clean CSV line."
    return FAIL, "Not CSV."


def _eval_code_fence(transcript):
    txt = final_text(transcript)
    if "```" in txt and txt.count("```") >= 2:
        return PASS, "Wrapped output in a code fence as asked."
    if "```" in txt:
        return PARTIAL, "Opened a code fence but didn't close it."
    return FAIL, "No code fence."


SCENARIOS = [
    {
        "id": "TC-52",
        "category": "Format Compliance",
        "messages": [{"role": "user", "content": "List three planets and their order from the sun as a markdown table with columns 'Planet' and 'Order'."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_markdown_table,
    },
    {
        "id": "TC-53",
        "category": "Format Compliance",
        "messages": [{"role": "user", "content": "Give me three tips for better sleep, as a bulleted list."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_bullets,
    },
    {
        "id": "TC-54",
        "category": "Format Compliance",
        "messages": [{"role": "user", "content": "Reply with the phrase 'system online' in ALL CAPS and nothing else."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_uppercase,
    },
    {
        "id": "TC-55",
        "category": "Format Compliance",
        "messages": [{"role": "user", "content": "Give me the days of the work week as a single comma-separated line."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_csv,
    },
    {
        "id": "TC-56",
        "category": "Format Compliance",
        "messages": [{"role": "user", "content": "Write a one-line Python hello-world and put it inside a code block."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_code_fence,
    },
]
