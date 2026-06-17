"""Tool Selection scenarios — does the model pick the right tool (and skip tools)?"""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, tool_names_called, calls_to, first_call, arg,
    num_tool_calls, contains_any,
)
from scenarios.common_tools import (
    GET_WEATHER, GET_FORECAST, GET_STOCK_PRICE, CALCULATOR,
)


def _eval_weather_only(transcript):
    names = tool_names_called(transcript)
    w = calls_to(transcript, "get_weather")
    if not w:
        return FAIL, "Did not call get_weather."
    if set(names) - {"get_weather"}:
        return PARTIAL, f"Called get_weather but also extra tools: {names}."
    city = (arg(w[0], "city") or "").lower()
    if "berlin" in city:
        return PASS, "Used get_weather with Berlin only."
    return PARTIAL, f"Called get_weather but city was '{arg(w[0],'city')}'."


def _eval_forecast_choice(transcript):
    names = tool_names_called(transcript)
    if "get_forecast" in names and "get_weather" not in names:
        f = calls_to(transcript, "get_forecast")[0]
        if int(arg(f, "days") or 0) >= 3:
            return PASS, "Chose get_forecast with days>=3 as asked."
        return PARTIAL, "Chose get_forecast but days arg wrong/missing."
    if "get_forecast" in names:
        return PARTIAL, "Used get_forecast but also get_weather."
    return FAIL, f"Did not select get_forecast; called {names}."


def _eval_no_tool_needed(transcript):
    # Pure knowledge question — best behavior is to answer without a tool.
    if num_tool_calls(transcript) == 0:
        return PASS, "Answered directly, no tool call (correct — no tool fits)."
    return FAIL, f"Called tools unnecessarily: {tool_names_called(transcript)}."


def _eval_calculator_choice(transcript):
    names = tool_names_called(transcript)
    if "calculator" in names and num_tool_calls(transcript) == 1:
        expr = (arg(calls_to(transcript, "calculator")[0], "expression") or "")
        if any(c.isdigit() for c in expr):
            return PASS, "Chose calculator for the arithmetic."
        return PARTIAL, "Called calculator but expression looks empty."
    if "calculator" in names:
        return PARTIAL, "Used calculator plus extra tools."
    return FAIL, f"Did not use calculator; called {names}."


def _eval_stock_choice(transcript):
    names = tool_names_called(transcript)
    if names == ["get_stock_price"]:
        t = (arg(first_call(transcript, "get_stock_price"), "ticker") or "").upper()
        if "TSLA" in t:
            return PASS, "Chose get_stock_price with TSLA."
        return PARTIAL, f"Right tool, ticker was '{t}'."
    if "get_stock_price" in names:
        return PARTIAL, "Used get_stock_price plus extras."
    return FAIL, f"Wrong tool selection: {names}."


SCENARIOS = [
    {
        "id": "TC-01",
        "category": "Tool Selection",
        "messages": [{"role": "user", "content": "What's the weather in Berlin right now?"}],
        "tools": [GET_WEATHER, GET_FORECAST, GET_STOCK_PRICE, CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "18°C, partly cloudy in Berlin."},
        "max_turns": 4,
        "evaluator": _eval_weather_only,
    },
    {
        "id": "TC-02",
        "category": "Tool Selection",
        "messages": [{"role": "user", "content": "Give me the weather outlook for Paris for the next 5 days."}],
        "tools": [GET_WEATHER, GET_FORECAST],
        "tool_choice": "auto",
        "mock_tools": {"get_forecast": "Paris 5-day: 17,19,16,15,18 C, light rain mid-week."},
        "max_turns": 4,
        "evaluator": _eval_forecast_choice,
    },
    {
        "id": "TC-03",
        "category": "Tool Selection",
        "messages": [{"role": "user", "content": "Who wrote the novel 'Pride and Prejudice'?"}],
        "tools": [GET_WEATHER, GET_STOCK_PRICE, CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_no_tool_needed,
    },
    {
        "id": "TC-04",
        "category": "Tool Selection",
        "messages": [{"role": "user", "content": "What is 1234 multiplied by 5678?"}],
        "tools": [CALCULATOR, GET_WEATHER, GET_STOCK_PRICE],
        "tool_choice": "auto",
        "mock_tools": {"calculator": "7006652"},
        "max_turns": 4,
        "evaluator": _eval_calculator_choice,
    },
    {
        "id": "TC-05",
        "category": "Tool Selection",
        "messages": [{"role": "user", "content": "How much is Tesla stock trading at?"}],
        "tools": [GET_STOCK_PRICE, GET_WEATHER, CALCULATOR, GET_FORECAST],
        "tool_choice": "auto",
        "mock_tools": {"get_stock_price": "TSLA: $242.11"},
        "max_turns": 4,
        "evaluator": _eval_stock_choice,
    },
]
