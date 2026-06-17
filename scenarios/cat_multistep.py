"""Multi-Step Chains — sequence multiple tool calls, feeding results forward."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, tool_names_called, calls_to, first_call, arg,
    final_text, contains_any, num_tool_calls,
)
from scenarios.common_tools import (
    GET_STOCK_PRICE, CONVERT_CURRENCY, GET_WEATHER, GET_FORECAST,
    CREATE_CALENDAR_EVENT, CALCULATOR, SEARCH_FLIGHTS, SEND_EMAIL,
)


def _eval_stock_then_convert(transcript):
    names = tool_names_called(transcript)
    got_stock = "get_stock_price" in names
    got_conv = "convert_currency" in names
    if got_stock and got_conv:
        # convert should reference the price (~242) — feed-forward check is loose
        return PASS, "Chained get_stock_price -> convert_currency."
    if got_stock or got_conv:
        return PARTIAL, f"Only half the chain: {names}."
    return FAIL, f"No chain performed: {names}."


def _eval_weather_then_calc(transcript):
    names = tool_names_called(transcript)
    got_w = "get_weather" in names
    got_c = "calculator" in names
    if got_w and got_c:
        return PASS, "Chained get_weather -> calculator on the result."
    if got_w:
        return PARTIAL, "Got weather but never did the conversion math."
    return FAIL, f"Chain not attempted: {names}."


def _eval_flight_then_calendar(transcript):
    names = tool_names_called(transcript)
    got_f = "search_flights" in names
    got_cal = "create_calendar_event" in names
    if got_f and got_cal:
        return PASS, "Chained search_flights -> create_calendar_event."
    if got_f or got_cal:
        return PARTIAL, f"Partial chain: {names}."
    return FAIL, f"No chain: {names}."


def _eval_three_step(transcript):
    names = tool_names_called(transcript)
    want = {"get_stock_price", "calculator"}
    have = want & set(names)
    if "get_stock_price" in names and "calculator" in names and len(calls_to(transcript, "get_stock_price")) >= 2:
        return PASS, "Pulled both tickers and computed the difference."
    if "get_stock_price" in names and "calculator" in names:
        return PARTIAL, "Computed but may have pulled only one ticker."
    if "get_stock_price" in names:
        return PARTIAL, "Got price(s) but no comparison math."
    return FAIL, f"Chain not performed: {names}."


SCENARIOS = [
    {
        "id": "TC-25",
        "category": "Multi-Step Chains",
        "messages": [{"role": "user", "content": "Get Apple's stock price, then tell me what that is in euros."}],
        "tools": [GET_STOCK_PRICE, CONVERT_CURRENCY],
        "tool_choice": "auto",
        "mock_tools": {
            "get_stock_price": "AAPL: $242.00",
            "convert_currency": "242 USD = 223.50 EUR",
        },
        "max_turns": 6,
        "evaluator": _eval_stock_then_convert,
    },
    {
        "id": "TC-26",
        "category": "Multi-Step Chains",
        "messages": [{"role": "user", "content": "Get the temperature in Cairo in celsius, then convert that number to fahrenheit using the calculator."}],
        "tools": [GET_WEATHER, CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {
            "get_weather": "Cairo: 35°C, sunny.",
            "calculator": "95",
        },
        "max_turns": 6,
        "evaluator": _eval_weather_then_calc,
    },
    {
        "id": "TC-27",
        "category": "Multi-Step Chains",
        "messages": [{"role": "user", "content": "Find a flight from BOS to ORD on 2026-08-01, then put the departure on my calendar."}],
        "tools": [SEARCH_FLIGHTS, CREATE_CALENDAR_EVENT],
        "tool_choice": "auto",
        "mock_tools": {
            "search_flights": "UA123 departs 2026-08-01 09:15, arrives 11:00, $140.",
            "create_calendar_event": "Event created.",
        },
        "max_turns": 6,
        "evaluator": _eval_flight_then_calendar,
    },
    {
        "id": "TC-28",
        "category": "Multi-Step Chains",
        "messages": [{"role": "user", "content": "Compare the prices of MSFT and NVDA stock, and tell me the dollar difference."}],
        "tools": [GET_STOCK_PRICE, CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {
            "get_stock_price": lambda a: {"MSFT": "MSFT: $410.00", "NVDA": "NVDA: $128.00"}.get(
                str(a.get("ticker", "")).upper(), "Unknown ticker."
            ),
            "calculator": "282",
        },
        "max_turns": 8,
        "evaluator": _eval_three_step,
    },
]
