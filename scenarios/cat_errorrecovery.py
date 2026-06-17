"""Error Recovery — handle a tool error gracefully (retry/fallback/report), not crash."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, tool_names_called, final_text,
    any_assistant_text, contains_any, num_tool_calls,
)
from scenarios.common_tools import GET_WEATHER, GET_STOCK_PRICE, SEARCH_FLIGHTS, CALCULATOR


def _make_fail_then_ok(good_response):
    state = {"n": 0}

    def fn(_args):
        state["n"] += 1
        if state["n"] == 1:
            return "ERROR 503: service temporarily unavailable. Please retry."
        return good_response
    return fn


def _eval_retry_then_success(transcript):
    calls = calls_to(transcript, "get_weather")
    txt = final_text(transcript)
    if len(calls) >= 2 and contains_any(txt, ["20", "celsius", "sunny", "madrid"]):
        return PASS, "Retried after 503 and reported the recovered result."
    if len(calls) >= 2:
        return PARTIAL, "Retried but final answer didn't surface the data."
    if contains_any(any_assistant_text(transcript), ["error", "try again", "unavailable", "failed"]):
        return PARTIAL, "Surfaced the error but did not retry."
    return FAIL, "Did not retry or acknowledge the tool error."


def _eval_report_hard_error(transcript):
    # Tool always returns a permanent error; model should report, not hallucinate.
    txt = final_text(transcript).lower()
    fabricated_price = any(c.isdigit() for c in txt) and "$" in txt
    acknowledged = contains_any(
        txt, ["error", "couldn't", "could not", "unable", "failed", "not available",
               "unavailable", "try again", "sorry"]
    )
    if acknowledged and not fabricated_price:
        return PASS, "Reported the persistent error instead of inventing a price."
    if acknowledged:
        return PARTIAL, "Acknowledged error but also stated a suspicious price."
    return FAIL, "Did not report the error (possibly hallucinated a result)."


def _eval_fallback_tool(transcript):
    names = tool_names_called(transcript)
    # primary search_flights errors; acceptable to report inability clearly.
    txt = final_text(transcript).lower()
    if contains_any(txt, ["error", "couldn't", "could not", "unable", "no flights", "failed", "try"]):
        return PASS, "Handled flight-search failure with a clear report."
    if "search_flights" in names and len(calls_to(transcript, "search_flights")) >= 2:
        return PARTIAL, "Retried but didn't clearly report outcome."
    return FAIL, "Ignored the flight-search error."


SCENARIOS = [
    {
        "id": "TC-33",
        "category": "Error Recovery",
        "messages": [{"role": "user", "content": "What's the weather in Madrid?"}],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": _make_fail_then_ok("Madrid: 20°C, sunny.")},
        "max_turns": 6,
        "evaluator": _eval_retry_then_success,
    },
    {
        "id": "TC-34",
        "category": "Error Recovery",
        "messages": [{"role": "user", "content": "Get me the current price of GOOG."}],
        "tools": [GET_STOCK_PRICE],
        "tool_choice": "auto",
        "mock_tools": {"get_stock_price": "ERROR 500: market data feed down."},
        "max_turns": 5,
        "evaluator": _eval_report_hard_error,
    },
    {
        "id": "TC-35",
        "category": "Error Recovery",
        "messages": [{"role": "user", "content": "Search for flights from LHR to CDG tomorrow."}],
        "tools": [SEARCH_FLIGHTS],
        "tool_choice": "auto",
        "mock_tools": {"search_flights": "ERROR: upstream provider returned 502."},
        "max_turns": 5,
        "evaluator": _eval_fallback_tool,
    },
]
