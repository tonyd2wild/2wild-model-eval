"""Toolset Scale — find the right tool in a ~50-tool catalog without distraction."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, tool_names_called,
    num_tool_calls,
)
from scenarios.common_tools import big_toolset_with, GET_WEATHER


def _eval_scale_weather(transcript):
    names = tool_names_called(transcript)
    if names == ["get_weather"]:
        if "reykjavik" in (arg(first_call(transcript, "get_weather"), "city") or "").lower():
            return PASS, "Picked get_weather out of 50 tools, correct city."
        return PARTIAL, "Right tool from 50, city arg off."
    if "get_weather" in names:
        return PARTIAL, f"Found get_weather but also distractors: {names}."
    return FAIL, f"Lost in the toolset: {names}."


def _eval_scale_translate(transcript):
    names = tool_names_called(transcript)
    if names == ["translate_text"]:
        return PASS, "Picked translate_text out of 50 tools."
    if "translate_text" in names:
        return PARTIAL, f"Found translate_text plus extras: {names}."
    return FAIL, f"Wrong tool at scale: {names}."


def _eval_scale_distance(transcript):
    names = tool_names_called(transcript)
    if names == ["get_distance"]:
        return PASS, "Picked get_distance among 50 tools."
    if "get_distance" in names:
        return PARTIAL, f"Found get_distance plus extras: {names}."
    if "get_directions" in names:
        return PARTIAL, "Used get_directions (close but distance was asked)."
    return FAIL, f"Wrong tool at scale: {names}."


def _eval_scale_password(transcript):
    names = tool_names_called(transcript)
    if names == ["generate_password"]:
        return PASS, "Picked generate_password among 50 tools."
    if "generate_password" in names:
        return PARTIAL, f"Found it plus extras: {names}."
    return FAIL, f"Wrong tool at scale: {names}."


SCENARIOS = [
    {
        "id": "TC-21",
        "category": "Toolset Scale",
        "messages": [{"role": "user", "content": "What's the weather like in Reykjavik?"}],
        "tools": big_toolset_with(),
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "Reykjavik: 7°C, windy."},
        "max_turns": 4,
        "evaluator": _eval_scale_weather,
    },
    {
        "id": "TC-22",
        "category": "Toolset Scale",
        "messages": [{"role": "user", "content": "Translate 'good morning, my friend' into Italian."}],
        "tools": big_toolset_with(),
        "tool_choice": "auto",
        "mock_tools": {"translate_text": "Buongiorno, amico mio."},
        "max_turns": 4,
        "evaluator": _eval_scale_translate,
    },
    {
        "id": "TC-23",
        "category": "Toolset Scale",
        "messages": [{"role": "user", "content": "How far apart are Madrid and Lisbon?"}],
        "tools": big_toolset_with(),
        "tool_choice": "auto",
        "mock_tools": {"get_distance": "Madrid to Lisbon: ~625 km."},
        "max_turns": 4,
        "evaluator": _eval_scale_distance,
    },
    {
        "id": "TC-24",
        "category": "Toolset Scale",
        "messages": [{"role": "user", "content": "Generate me a strong 16-character password."}],
        "tools": big_toolset_with(),
        "tool_choice": "auto",
        "mock_tools": {"generate_password": "k9$Lm2!qVrTz7@Wp"},
        "max_turns": 4,
        "evaluator": _eval_scale_password,
    },
]
