"""Parameter Precision — exact, correctly-typed arguments extracted from the prompt."""

from scenarios.evaluators import (
    PASS, PARTIAL, FAIL, calls_to, first_call, arg, args_of,
)
from scenarios.common_tools import (
    GET_WEATHER, SEARCH_FLIGHTS, CONVERT_CURRENCY, CREATE_CALENDAR_EVENT,
    SEND_EMAIL,
)


def _eval_units(transcript):
    w = calls_to(transcript, "get_weather")
    if not w:
        return FAIL, "Did not call get_weather."
    city = (arg(w[0], "city") or "").lower()
    units = (arg(w[0], "units") or "").lower()
    ok_city = "tokyo" in city
    ok_units = units == "fahrenheit"
    if ok_city and ok_units:
        return PASS, "city=Tokyo units=fahrenheit, both precise."
    if ok_city or ok_units:
        return PARTIAL, f"Partial args: city='{arg(w[0],'city')}' units='{arg(w[0],'units')}'."
    return FAIL, "Both city and units wrong."


def _eval_flights(transcript):
    f = first_call(transcript, "search_flights")
    if not f:
        return FAIL, "Did not call search_flights."
    a = args_of(f)
    o = str(a.get("origin", "")).upper()
    d = str(a.get("destination", "")).upper()
    date = str(a.get("date", ""))
    pax = a.get("passengers")
    hits = sum([
        "JFK" in o or "NEW YORK" in o,
        "LAX" in d or "LOS ANGELES" in d,
        date.startswith("2026-07-04") or "07-04" in date or "july 4" in date.lower(),
        str(pax) == "2",
    ])
    if hits == 4:
        return PASS, "origin/dest/date/passengers all precise."
    if hits >= 2:
        return PARTIAL, f"{hits}/4 params correct: {a}."
    return FAIL, f"Params imprecise: {a}."


def _eval_currency_types(transcript):
    c = first_call(transcript, "convert_currency")
    if not c:
        return FAIL, "Did not call convert_currency."
    a = args_of(c)
    amount = a.get("amount")
    is_number = isinstance(amount, (int, float)) and float(amount) == 250.0
    frm = str(a.get("from_currency", "")).upper()
    to = str(a.get("to_currency", "")).upper()
    if is_number and frm == "USD" and to == "JPY":
        return PASS, "amount=250 (numeric) USD->JPY."
    if (str(amount) == "250") and frm == "USD" and to == "JPY":
        return PARTIAL, "Right values but amount not numeric-typed."
    if frm == "USD" or to == "JPY":
        return PARTIAL, f"Only one currency correct: {a}."
    return FAIL, f"Currency args wrong: {a}."


def _eval_calendar_iso(transcript):
    e = first_call(transcript, "create_calendar_event")
    if not e:
        return FAIL, "Did not call create_calendar_event."
    a = args_of(e)
    title = str(a.get("title", "")).lower()
    start = str(a.get("start", ""))
    end = str(a.get("end", ""))
    ok_title = "dentist" in title
    ok_start = "2026-06-20" in start and ("14:00" in start or "2pm" in start.lower())
    ok_end = "2026-06-20" in end and ("15:00" in end or "3pm" in end.lower())
    hits = sum([ok_title, ok_start, ok_end])
    if hits == 3:
        return PASS, "title + ISO start/end all correct."
    if hits >= 1:
        return PARTIAL, f"{hits}/3 fields right: {a}."
    return FAIL, f"Calendar params wrong: {a}."


def _eval_email_fields(transcript):
    e = first_call(transcript, "send_email")
    if not e:
        return FAIL, "Did not call send_email."
    a = args_of(e)
    to = str(a.get("to", "")).lower()
    subj = str(a.get("subject", "")).lower()
    body = str(a.get("body", "")).lower()
    ok_to = "sam@example.com" in to
    ok_subj = "lunch" in subj
    ok_body = "noon" in body or "12" in body or "lunch" in body
    hits = sum([ok_to, ok_subj, ok_body])
    if hits == 3:
        return PASS, "to/subject/body all extracted precisely."
    if hits >= 1:
        return PARTIAL, f"{hits}/3 email fields right: to='{a.get('to')}'."
    return FAIL, f"Email fields wrong: {a}."


SCENARIOS = [
    {
        "id": "TC-06",
        "category": "Parameter Precision",
        "messages": [{"role": "user", "content": "What's the temperature in Tokyo? Give it to me in Fahrenheit."}],
        "tools": [GET_WEATHER],
        "tool_choice": "auto",
        "mock_tools": {"get_weather": "Tokyo: 75°F, clear."},
        "max_turns": 4,
        "evaluator": _eval_units,
    },
    {
        "id": "TC-07",
        "category": "Parameter Precision",
        "messages": [{"role": "user", "content": "Find me flights from JFK to LAX on July 4th 2026 for 2 people."}],
        "tools": [SEARCH_FLIGHTS],
        "tool_choice": "auto",
        "mock_tools": {"search_flights": "3 flights found, cheapest $221."},
        "max_turns": 4,
        "evaluator": _eval_flights,
    },
    {
        "id": "TC-08",
        "category": "Parameter Precision",
        "messages": [{"role": "user", "content": "Convert 250 US dollars to Japanese yen."}],
        "tools": [CONVERT_CURRENCY],
        "tool_choice": "auto",
        "mock_tools": {"convert_currency": "250 USD = 39,250 JPY"},
        "max_turns": 4,
        "evaluator": _eval_currency_types,
    },
    {
        "id": "TC-09",
        "category": "Parameter Precision",
        "messages": [{"role": "user", "content": "Put a dentist appointment on my calendar for June 20 2026 from 2pm to 3pm."}],
        "tools": [CREATE_CALENDAR_EVENT],
        "tool_choice": "auto",
        "mock_tools": {"create_calendar_event": "Event created."},
        "max_turns": 4,
        "evaluator": _eval_calendar_iso,
    },
    {
        "id": "TC-10",
        "category": "Parameter Precision",
        "messages": [{"role": "user", "content": "Email sam@example.com with the subject 'Lunch' and tell them to meet me at noon."}],
        "tools": [SEND_EMAIL],
        "tool_choice": "auto",
        "mock_tools": {"send_email": "Sent."},
        "max_turns": 4,
        "evaluator": _eval_email_fields,
    },
]
