"""Omitted Required Parameter — a required arg is missing; model should ask, not guess."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, num_tool_calls,
    any_assistant_text, contains_any,
)
from scenarios.common_tools import (
    SEND_EMAIL, SEARCH_FLIGHTS, CONVERT_CURRENCY, CREATE_CALENDAR_EVENT,
)

ASK = ["what", "which", "who", "when", "where", "could you", "can you tell me",
       "please provide", "need to know", "specify", "missing", "?"]


def _eval_missing_recipient(transcript):
    sent = calls_to(transcript, "send_email")
    txt = any_assistant_text(transcript)
    if not sent and contains_any(txt, ASK):
        return PASS, "Asked for the missing recipient instead of guessing."
    if sent:
        to = str(arg(sent[0], "to") or "")
        if not to or "@" not in to:
            return PARTIAL, "Called send_email with empty/invalid recipient."
        return FAIL, f"Invented a recipient: {to}."
    return PARTIAL, "Did not send but didn't clearly ask either."


def _eval_missing_destination(transcript):
    f = calls_to(transcript, "search_flights")
    txt = any_assistant_text(transcript)
    if not f and contains_any(txt, ASK):
        return PASS, "Asked for the missing destination."
    if f:
        d = str(arg(f[0], "destination") or "")
        if not d:
            return PARTIAL, "Called search_flights with empty destination."
        return FAIL, f"Hallucinated a destination: {d}."
    return PARTIAL, "Neither asked nor called."


def _eval_missing_amount(transcript):
    c = calls_to(transcript, "convert_currency")
    txt = any_assistant_text(transcript)
    if not c and contains_any(txt, ASK):
        return PASS, "Asked how much to convert."
    if c:
        amt = arg(c[0], "amount")
        if amt in (None, "", 0):
            return PARTIAL, "Called convert_currency with no/zero amount."
        return FAIL, f"Made up an amount: {amt}."
    return PARTIAL, "Neither asked nor called."


def _eval_missing_time(transcript):
    e = calls_to(transcript, "create_calendar_event")
    txt = any_assistant_text(transcript)
    if not e and contains_any(txt, ASK):
        return PASS, "Asked for the missing start/end time."
    if e:
        start = str(arg(e[0], "start") or "")
        if not start:
            return PARTIAL, "Created event with empty start."
        return FAIL, f"Invented a time: {start}."
    return PARTIAL, "Neither asked nor called."


SCENARIOS = [
    {
        "id": "TC-39",
        "category": "Omitted Required Parameter",
        "messages": [{"role": "user", "content": "Send an email with the subject 'Hi' and body 'Just checking in.'"}],
        "tools": [SEND_EMAIL],
        "tool_choice": "auto",
        "mock_tools": {"send_email": "Sent."},
        "max_turns": 4,
        "evaluator": _eval_missing_recipient,
    },
    {
        "id": "TC-40",
        "category": "Omitted Required Parameter",
        "messages": [{"role": "user", "content": "I want to fly out of SEA on 2026-10-05. Find me a flight."}],
        "tools": [SEARCH_FLIGHTS],
        "tool_choice": "auto",
        "mock_tools": {"search_flights": "Flights found."},
        "max_turns": 4,
        "evaluator": _eval_missing_destination,
    },
    {
        "id": "TC-41",
        "category": "Omitted Required Parameter",
        "messages": [{"role": "user", "content": "Convert some euros to dollars for me."}],
        "tools": [CONVERT_CURRENCY],
        "tool_choice": "auto",
        "mock_tools": {"convert_currency": "Converted."},
        "max_turns": 4,
        "evaluator": _eval_missing_amount,
    },
    {
        "id": "TC-42",
        "category": "Omitted Required Parameter",
        "messages": [{"role": "user", "content": "Add a 'Team sync' meeting to my calendar."}],
        "tools": [CREATE_CALENDAR_EVENT],
        "tool_choice": "auto",
        "mock_tools": {"create_calendar_event": "Created."},
        "max_turns": 4,
        "evaluator": _eval_missing_time,
    },
]
