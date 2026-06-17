"""Structured Output — return strict, parseable JSON matching a requested shape."""

import json

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, final_text, extract_json, is_pure_json,
)
from scenarios.common_tools import CALCULATOR


def _eval_json_object(transcript):
    txt = final_text(transcript)
    obj = extract_json(txt)
    if obj is None:
        return FAIL, "No valid JSON found in answer."
    needed = {"name", "age", "city"}
    if isinstance(obj, dict) and needed.issubset(obj.keys()):
        if is_pure_json(txt):
            return PASS, "Strict JSON object with name/age/city, no prose."
        return PARTIAL, "Correct JSON but wrapped in extra prose."
    return PARTIAL, f"JSON parsed but missing keys: {sorted(set(obj) if isinstance(obj, dict) else [])}."


def _eval_json_array(transcript):
    txt = final_text(transcript)
    obj = extract_json(txt)
    if obj is None:
        return FAIL, "No valid JSON array found."
    if isinstance(obj, list) and len(obj) == 3 and all(isinstance(x, str) for x in obj):
        return PASS, "JSON array of exactly 3 strings."
    if isinstance(obj, list):
        return PARTIAL, f"Array but wrong length/types: {obj}."
    return FAIL, "Output was not a JSON array."


def _eval_typed_json(transcript):
    txt = final_text(transcript)
    obj = extract_json(txt)
    if not isinstance(obj, dict):
        return FAIL, "No JSON object found."
    ok_total = isinstance(obj.get("total"), (int, float))
    ok_items = isinstance(obj.get("items"), list)
    ok_paid = isinstance(obj.get("paid"), bool)
    hits = sum([ok_total, ok_items, ok_paid])
    if hits == 3:
        return PASS, "Correct types: total=number, items=array, paid=bool."
    if hits >= 1:
        return PARTIAL, f"{hits}/3 fields correctly typed: {obj}."
    return FAIL, f"Types all wrong: {obj}."


def _eval_nested_json(transcript):
    txt = final_text(transcript)
    obj = extract_json(txt)
    if not isinstance(obj, dict):
        return FAIL, "No JSON object."
    user = obj.get("user")
    if isinstance(user, dict) and "id" in user and isinstance(obj.get("roles"), list):
        return PASS, "Nested object with user.id and roles array."
    if isinstance(user, dict) or isinstance(obj.get("roles"), list):
        return PARTIAL, f"Partial structure: {obj}."
    return FAIL, f"Wrong shape: {obj}."


SCENARIOS = [
    {
        "id": "TC-29",
        "category": "Structured Output",
        "messages": [{"role": "user", "content": "Return ONLY a JSON object with keys name, age, city for: Maria, 34, who lives in Madrid. No prose, no markdown."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_json_object,
    },
    {
        "id": "TC-30",
        "category": "Structured Output",
        "messages": [{"role": "user", "content": "Give me exactly three primary colors as a JSON array of strings. Nothing else."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_json_array,
    },
    {
        "id": "TC-31",
        "category": "Structured Output",
        "messages": [{"role": "user", "content": "Return a JSON object describing an order: a numeric 'total' of 42.50, an 'items' array containing 'pen' and 'pad', and a boolean 'paid' set to true. JSON only."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_typed_json,
    },
    {
        "id": "TC-32",
        "category": "Structured Output",
        "messages": [{"role": "user", "content": "Output JSON with a nested 'user' object that has an 'id' of 7, and a top-level 'roles' array of 'admin' and 'editor'. JSON only, no commentary."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_nested_json,
    },
]
