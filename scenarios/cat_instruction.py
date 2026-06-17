"""Instruction Following — honor constraints in the prompt (limits, formats, scope)."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, num_tool_calls,
    final_text, contains_any, contains_all, any_assistant_text,
)
from scenarios.common_tools import (
    GET_WEATHER, SEND_EMAIL, SEARCH_FLIGHTS, GET_FORECAST, CALCULATOR,
)


def _eval_one_city_only(transcript):
    w = calls_to(transcript, "get_weather")
    cities = [(arg(c, "city") or "").lower() for c in w]
    if len(w) == 1 and "london" in cities[0]:
        return PASS, "Honored 'only London' — single call."
    if any("london" in c for c in cities):
        return PARTIAL, f"Called London but also others: {cities}."
    return FAIL, f"Did not follow instruction: {cities}."


def _eval_no_email_just_draft(transcript):
    # Instruction: "draft it but DON'T send" -> must NOT call send_email.
    sent = calls_to(transcript, "send_email")
    txt = final_text(transcript)
    if not sent and txt:
        return PASS, "Drafted text without sending (followed 'don't send')."
    if not sent:
        return PARTIAL, "Didn't send but produced no draft text."
    return FAIL, "Sent the email despite 'do not send'."


def _eval_word_limit(transcript):
    txt = final_text(transcript)
    if not txt:
        return FAIL, "No final answer."
    words = len(txt.split())
    if words <= 20:
        return PASS, f"Answer within 20-word limit ({words} words)."
    if words <= 30:
        return PARTIAL, f"Slightly over limit ({words} words)."
    return FAIL, f"Ignored 20-word limit ({words} words)."


def _eval_celsius_constraint(transcript):
    w = first_call(transcript, "get_weather")
    if not w:
        return FAIL, "Did not call get_weather."
    units = (arg(w, "units") or "").lower()
    if units == "celsius":
        return PASS, "Followed 'always use celsius' system rule."
    if units == "":
        return PARTIAL, "Did not set units (default may not be celsius)."
    return FAIL, f"Used '{units}' despite celsius-only system rule."


def _eval_max_3_results(transcript):
    f = first_call(transcript, "search_flights")
    if not f:
        return FAIL, "Did not call search_flights."
    # The instruction "I only have 1 passenger" must override default.
    pax = arg(f, "passengers")
    if str(pax) == "1":
        return PASS, "Set passengers=1 as instructed."
    if pax is None:
        return PARTIAL, "Omitted passengers (instruction said exactly 1)."
    return FAIL, f"Wrong passenger count: {pax}."


SCENARIOS = [
    {
        "id": "TC-11",
        "category": "Instruction Following",
        "messages": [{"role": "user", "content": "Check the weather. Only check London — I don't care about anywhere else."}],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "London: 14°C, drizzle."},
        "max_turns": 4,
        "evaluator": _eval_one_city_only,
    },
    {
        "id": "TC-12",
        "category": "Instruction Following",
        "messages": [{"role": "user", "content": "Draft an email to my boss asking for Friday off — but DO NOT send it, just write it out for me to review."}],
        "tools": [SEND_EMAIL],
        "tool_choice": "auto",
        "mock_tools": {"send_email": "Sent."},
        "max_turns": 4,
        "evaluator": _eval_no_email_just_draft,
    },
    {
        "id": "TC-13",
        "category": "Instruction Following",
        "messages": [{"role": "user", "content": "In 20 words or fewer, explain what photosynthesis is."}],
        "tools": [CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_word_limit,
    },
    {
        "id": "TC-14",
        "category": "Instruction Following",
        "messages": [
            {"role": "system", "content": "When reporting temperatures, ALWAYS use celsius regardless of what the user implies."},
            {"role": "user", "content": "What's the weather in Miami?"},
        ],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "Miami: 30°C, humid."},
        "max_turns": 4,
        "evaluator": _eval_celsius_constraint,
    },
    {
        "id": "TC-15",
        "category": "Instruction Following",
        "messages": [{"role": "user", "content": "Search flights from SFO to SEA next Monday. It's just me — exactly 1 passenger."}],
        "tools": [SEARCH_FLIGHTS],
        "tool_choice": "auto",
        "mock_tools": {"search_flights": "5 flights, cheapest $89."},
        "max_turns": 4,
        "evaluator": _eval_max_3_results,
    },
]
