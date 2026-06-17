"""Contradictory Parameters — prompt contains conflicting values; model should
   ask for clarification or pick the most-recent/explicit one, not silently merge."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, num_tool_calls,
    any_assistant_text, contains_any, final_text,
)
from scenarios.common_tools import GET_WEATHER, CONVERT_CURRENCY, SEARCH_FLIGHTS

CLARIFY = ["which", "did you mean", "clarify", "you said", "conflict", "contradict",
           "two different", "both", "or ", "confirm", "to be sure", "you mentioned"]


def _eval_conflicting_city(transcript):
    w = calls_to(transcript, "get_weather")
    txt = any_assistant_text(transcript)
    asked = contains_any(txt, CLARIFY)
    if not w and asked:
        return PASS, "Asked which city given the contradiction."
    if w:
        city = (arg(w[0], "city") or "").lower()
        # 'actually, make it Oslo' = later wins
        if "oslo" in city and "rome" not in city:
            return PASS, "Used the corrected city (Oslo, most recent)."
        if "rome" in city and "oslo" in city:
            return FAIL, "Merged both cities into one arg."
        return PARTIAL, f"Picked a city ('{arg(w[0],'city')}') without flagging conflict."
    return PARTIAL, "Neither called the tool nor clearly clarified."


def _eval_conflicting_amount(transcript):
    c = first_call(transcript, "convert_currency")
    txt = any_assistant_text(transcript)
    if not c and contains_any(txt, CLARIFY):
        return PASS, "Flagged the 100-vs-200 contradiction and asked."
    if c:
        amt = str(arg(c, "amount"))
        if amt in ("200", "200.0"):
            return PASS, "Used the most-recent amount (200)."
        if amt in ("100", "100.0"):
            return PARTIAL, "Used the first amount, ignored the correction."
        if amt in ("300", "300.0"):
            return FAIL, "Summed the conflicting amounts (100+200)."
        return PARTIAL, f"Used amount={amt}."
    return PARTIAL, "No call and no clarification."


def _eval_conflicting_dates(transcript):
    f = first_call(transcript, "search_flights")
    txt = any_assistant_text(transcript)
    if not f and contains_any(txt, CLARIFY):
        return PASS, "Asked which date given the conflict."
    if f:
        d = str(arg(f, "date"))
        if "2026-09-10" in d:
            return PASS, "Used the corrected date."
        return PARTIAL, f"Chose a date ({d}) without flagging conflict."
    return PARTIAL, "No call and no clarification."


SCENARIOS = [
    {
        "id": "TC-36",
        "category": "Contradictory Parameters",
        "messages": [{"role": "user", "content": "Get me the weather in Rome. Actually, make it Oslo."}],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "12°C, clear."},
        "max_turns": 4,
        "evaluator": _eval_conflicting_city,
    },
    {
        "id": "TC-37",
        "category": "Contradictory Parameters",
        "messages": [{"role": "user", "content": "Convert 100 USD to GBP. Wait, I meant 200 USD."}],
        "tools": [CONVERT_CURRENCY],
        "tool_choice": "auto",
        "mock_tools": {"convert_currency": "Converted."},
        "max_turns": 4,
        "evaluator": _eval_conflicting_amount,
    },
    {
        "id": "TC-38",
        "category": "Contradictory Parameters",
        "messages": [{"role": "user", "content": "Book a flight DFW to MIA on 2026-09-01 — sorry, I mean 2026-09-10."}],
        "tools": [SEARCH_FLIGHTS],
        "tool_choice": "auto",
        "mock_tools": {"search_flights": "Flights found."},
        "max_turns": 4,
        "evaluator": _eval_conflicting_dates,
    },
]
