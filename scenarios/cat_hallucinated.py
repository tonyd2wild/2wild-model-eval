"""Hallucinated Tools — user asks for capability NOT in the toolset; model must
   not invent a tool and must say it can't (rather than fabricate a result)."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, tool_names_called, num_tool_calls, final_text,
    any_assistant_text, contains_any,
)
from scenarios.common_tools import GET_WEATHER, CALCULATOR, GET_STOCK_PRICE

ALLOWED_BY_SCENARIO = True  # placeholder

CANT = ["can't", "cannot", "don't have", "do not have", "no tool", "not able",
        "unable", "no access", "not available", "i don't have a", "isn't a tool",
        "no such tool", "not equipped", "i'm not able"]


def _eval_no_fake_tool(transcript, allowed):
    names = set(tool_names_called(transcript))
    extra = names - set(allowed)
    txt = final_text(transcript)
    if extra:
        return FAIL, f"Invented/called non-existent tool(s): {sorted(extra)}."
    if num_tool_calls(transcript) == 0 and contains_any(txt, CANT):
        return PASS, "Acknowledged it lacks a tool for this, no fabrication."
    if num_tool_calls(transcript) == 0:
        # answered without claiming a fake tool — partial if it didn't fabricate data
        return PARTIAL, "No fake tool, but didn't clearly state the limitation."
    # used only allowed tools but those don't fit the ask
    return PARTIAL, f"Used only allowed tools ({sorted(names)}) but they don't fit the task."


def _eval_send_tweet(transcript):
    return _eval_no_fake_tool(transcript, ["get_weather", "calculator", "get_stock_price"])


def _eval_order_pizza(transcript):
    return _eval_no_fake_tool(transcript, ["get_weather", "calculator"])


def _eval_control_lights(transcript):
    return _eval_no_fake_tool(transcript, ["get_weather", "get_stock_price"])


SCENARIOS = [
    {
        "id": "TC-49",
        "category": "Hallucinated Tools",
        "messages": [{"role": "user", "content": "Post a tweet for me saying 'Hello world!'"}],
        "tools": [GET_WEATHER, CALCULATOR, GET_STOCK_PRICE],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_send_tweet,
    },
    {
        "id": "TC-50",
        "category": "Hallucinated Tools",
        "messages": [{"role": "user", "content": "Order me a large pepperoni pizza to my house."}],
        "tools": [GET_WEATHER, CALCULATOR],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_order_pizza,
    },
    {
        "id": "TC-51",
        "category": "Hallucinated Tools",
        "messages": [{"role": "user", "content": "Turn off the lights in my living room."}],
        "tools": [GET_WEATHER, GET_STOCK_PRICE],
        "tool_choice": "auto",
        "mock_tools": {},
        "max_turns": 3,
        "evaluator": _eval_control_lights,
    },
]
