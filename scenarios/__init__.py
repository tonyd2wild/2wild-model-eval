"""
scenarios package — auto-discovers every scenario defined in the modules here.

Each scenario is a dict with this shape:

    {
      "id": "TC-01",
      "category": "Tool Selection",
      "messages": [ {"role": "user", "content": "..."} ],   # initial conversation
      "tools": [ <OpenAI tool schema>, ... ],
      "tool_choice": "auto",                  # or "required" / {"type":"function",...}
      "mock_tools": { "tool_name": <callable(args)->result_str> OR <static str> },
      "max_turns": 4,
      "evaluator": <callable(transcript)-> (verdict, reason)>,
    }

`transcript` passed to the evaluator is a list of recorded steps produced by the
runner, each like:
    {"role": "assistant", "content": "...", "tool_calls": [
        {"name": "...", "arguments": {...}} , ...]}
    {"role": "tool", "name": "...", "content": "..."}

Evaluator helpers (verdict builders + transcript inspection) live in evaluators.py.
"""

import importlib
import pkgutil


def load_all():
    """Import every sibling module that exposes SCENARIOS and concatenate them."""
    scenarios = []
    pkg = importlib.import_module(__name__)
    for mod_info in pkgutil.iter_modules(pkg.__path__):
        name = mod_info.name
        if name in ("evaluators",):
            continue
        mod = importlib.import_module(f"{__name__}.{name}")
        if hasattr(mod, "SCENARIOS"):
            scenarios.extend(mod.SCENARIOS)
    # stable order by id
    scenarios.sort(key=lambda s: s["id"])
    return scenarios
