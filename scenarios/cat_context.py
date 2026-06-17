"""Context Retention — remember facts from earlier turns in a multi-turn convo."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, final_text,
    any_assistant_text, contains_any,
)
from scenarios.common_tools import GET_WEATHER, CONVERT_CURRENCY, GET_STOCK_PRICE


def _eval_remember_city(transcript):
    # Turn 1 established "I live in Lisbon". Later: "what's the weather at home?"
    w = calls_to(transcript, "get_weather")
    if w and "lisbon" in (arg(w[0], "city") or "").lower():
        return PASS, "Recalled 'home' = Lisbon from earlier turn."
    if w:
        return PARTIAL, f"Called get_weather but city='{arg(w[0],'city')}' (forgot Lisbon)."
    return FAIL, "Did not use the remembered city."


def _eval_remember_amount(transcript):
    # Earlier: "I have 500 dollars". Later: "convert all of it to euros".
    c = calls_to(transcript, "convert_currency")
    if c:
        amt = str(arg(c[0], "amount"))
        if amt in ("500", "500.0"):
            return PASS, "Recalled the 500-dollar amount from context."
        return PARTIAL, f"Converted but amount='{amt}' (lost the 500)."
    return FAIL, "Did not retain the dollar amount."


def _eval_remember_ticker(transcript):
    # Earlier the user said they hold NVDA. Later: "check my holding's price".
    s = calls_to(transcript, "get_stock_price")
    if s and "NVDA" in str(arg(s[0], "ticker") or "").upper():
        return PASS, "Recalled the held ticker (NVDA)."
    if s:
        return PARTIAL, f"Called get_stock_price with '{arg(s[0],'ticker')}' (forgot NVDA)."
    return FAIL, "Did not retain the ticker."


SCENARIOS = [
    {
        "id": "TC-46",
        "category": "Context Retention",
        "messages": [
            {"role": "user", "content": "Just so you know, I live in Lisbon."},
            {"role": "assistant", "content": "Got it — you're in Lisbon."},
            {"role": "user", "content": "Cool. What's the weather at home right now?"},
        ],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "Lisbon: 22°C, sunny."},
        "max_turns": 4,
        "evaluator": _eval_remember_city,
    },
    {
        "id": "TC-47",
        "category": "Context Retention",
        "messages": [
            {"role": "user", "content": "I have exactly 500 US dollars saved up."},
            {"role": "assistant", "content": "Noted — $500."},
            {"role": "user", "content": "Convert all of it to euros, please."},
        ],
        "tools": [CONVERT_CURRENCY],
        "tool_choice": "auto",
        "mock_tools": {"convert_currency": "500 USD = 461 EUR"},
        "max_turns": 4,
        "evaluator": _eval_remember_amount,
    },
    {
        "id": "TC-48",
        "category": "Context Retention",
        "messages": [
            {"role": "user", "content": "My only stock holding is NVDA."},
            {"role": "assistant", "content": "Understood — you hold NVDA."},
            {"role": "user", "content": "What's my holding worth per share right now?"},
        ],
        "tools": [GET_STOCK_PRICE],
        "tool_choice": "auto",
        "mock_tools": {"get_stock_price": "NVDA: $128.00"},
        "max_turns": 4,
        "evaluator": _eval_remember_ticker,
    },
]
