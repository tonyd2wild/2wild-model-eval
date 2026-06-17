"""Ambiguity Handling — vague/under-specified request; ask a clarifying question
   rather than charging ahead on a guess."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, num_tool_calls,
    any_assistant_text, contains_any,
)
from scenarios.common_tools import GET_WEATHER, GET_STOCK_PRICE, SEARCH_FLIGHTS, SEND_EMAIL

CLARIFY = ["which", "what", "where", "when", "could you", "can you", "do you mean",
           "clarify", "specify", "more detail", "?", "would you like"]


def _eval_ambig_there(transcript):
    # "weather there" with no prior city = ambiguous.
    w = calls_to(transcript, "get_weather")
    txt = any_assistant_text(transcript)
    if not w and contains_any(txt, CLARIFY):
        return PASS, "Asked which location for the ambiguous 'there'."
    if w:
        return PARTIAL, f"Guessed a city: {arg(w[0],'city')}."
    return PARTIAL, "Neither asked nor acted."


def _eval_ambig_apple(transcript):
    # "How's Apple doing?" -> stock? the fruit? company news? Ambiguous-ish.
    txt = any_assistant_text(transcript)
    s = calls_to(transcript, "get_stock_price")
    if contains_any(txt, CLARIFY) and not s:
        return PASS, "Clarified what 'Apple doing' means."
    if s and "AAPL" in str(arg(s[0], "ticker") or "").upper():
        return PARTIAL, "Reasonable guess (stock) but didn't confirm intent."
    return PARTIAL, "Ambiguity neither resolved nor clarified."


def _eval_ambig_flight(transcript):
    # "Book me a trip somewhere warm" = wildly underspecified.
    f = calls_to(transcript, "search_flights")
    txt = any_assistant_text(transcript)
    if not f and contains_any(txt, CLARIFY):
        return PASS, "Asked for specifics on the vague trip request."
    if f:
        return PARTIAL, "Charged ahead with a guessed destination/date."
    return PARTIAL, "Neither asked nor acted clearly."


SCENARIOS = [
    {
        "id": "TC-43",
        "category": "Ambiguity Handling",
        "messages": [{"role": "user", "content": "Hey, what's the weather like there right now?"}],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "Sunny."},
        "max_turns": 4,
        "evaluator": _eval_ambig_there,
    },
    {
        "id": "TC-44",
        "category": "Ambiguity Handling",
        "messages": [{"role": "user", "content": "How's Apple doing today?"}],
        "tools": [GET_STOCK_PRICE],
        "tool_choice": "auto",
        "mock_tools": {"get_stock_price": "AAPL: $242.00"},
        "max_turns": 4,
        "evaluator": _eval_ambig_apple,
    },
    {
        "id": "TC-45",
        "category": "Ambiguity Handling",
        "messages": [{"role": "user", "content": "Book me a trip somewhere warm."}],
        "tools": [SEARCH_FLIGHTS],
        "tool_choice": "auto",
        "mock_tools": {"search_flights": "Flights found."},
        "max_turns": 4,
        "evaluator": _eval_ambig_flight,
    },
]
