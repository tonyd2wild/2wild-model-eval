"""
common_tools.py — reusable OpenAI tool schemas + a ~50-tool list for the
Toolset Scale category. Kept separate so scenarios stay readable.
"""

GET_WEATHER = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Berlin'"},
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units",
                },
            },
            "required": ["city"],
        },
    },
}

GET_FORECAST = {
    "type": "function",
    "function": {
        "name": "get_forecast",
        "description": "Get a multi-day weather forecast for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "days": {"type": "integer", "description": "Number of days, 1-7"},
            },
            "required": ["city", "days"],
        },
    },
}

SEND_EMAIL = {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
}

SEARCH_FLIGHTS = {
    "type": "function",
    "function": {
        "name": "search_flights",
        "description": "Search for flights between two airports on a date.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin airport code"},
                "destination": {"type": "string", "description": "Destination airport code"},
                "date": {"type": "string", "description": "Departure date YYYY-MM-DD"},
                "passengers": {"type": "integer"},
            },
            "required": ["origin", "destination", "date"],
        },
    },
}

CONVERT_CURRENCY = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string", "description": "3-letter code, e.g. USD"},
                "to_currency": {"type": "string", "description": "3-letter code, e.g. EUR"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
}

CALCULATOR = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "e.g. '12 * (3 + 4)'"},
            },
            "required": ["expression"],
        },
    },
}

GET_STOCK_PRICE = {
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Get the latest price for a stock ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol, e.g. AAPL"},
            },
            "required": ["ticker"],
        },
    },
}

CREATE_CALENDAR_EVENT = {
    "type": "function",
    "function": {
        "name": "create_calendar_event",
        "description": "Create a calendar event.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "description": "ISO 8601 datetime"},
                "end": {"type": "string", "description": "ISO 8601 datetime"},
                "attendees": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "start", "end"],
        },
    },
}

TRANSLATE_TEXT = {
    "type": "function",
    "function": {
        "name": "translate_text",
        "description": "Translate text into a target language.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "target_language": {"type": "string", "description": "e.g. 'French'"},
            },
            "required": ["text", "target_language"],
        },
    },
}

DELETE_FILE = {
    "type": "function",
    "function": {
        "name": "delete_file",
        "description": "Permanently delete a file from the user's storage. Irreversible.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute file path"},
            },
            "required": ["path"],
        },
    },
}

TRANSFER_FUNDS = {
    "type": "function",
    "function": {
        "name": "transfer_funds",
        "description": "Transfer money between bank accounts. Moves real money.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_account": {"type": "string"},
                "to_account": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["from_account", "to_account", "amount"],
        },
    },
}


def _simple_tool(name, desc, props=None, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": props or {"query": {"type": "string"}},
                "required": required if required is not None else (["query"] if not props else []),
            },
        },
    }


# A ~50-tool catalog for Toolset Scale scenarios. The "needle" tools we care
# about (get_weather etc.) are mixed in so selection must happen at scale.
BIG_TOOLSET = [
    GET_WEATHER, GET_FORECAST, SEND_EMAIL, SEARCH_FLIGHTS, CONVERT_CURRENCY,
    CALCULATOR, GET_STOCK_PRICE, CREATE_CALENDAR_EVENT, TRANSLATE_TEXT,
] + [
    _simple_tool("search_web", "Search the web for a query."),
    _simple_tool("get_news", "Get recent news headlines for a topic."),
    _simple_tool("get_directions", "Get driving directions between two places.",
                 {"origin": {"type": "string"}, "destination": {"type": "string"}},
                 ["origin", "destination"]),
    _simple_tool("book_hotel", "Book a hotel room.",
                 {"city": {"type": "string"}, "checkin": {"type": "string"}, "nights": {"type": "integer"}},
                 ["city", "checkin", "nights"]),
    _simple_tool("get_recipe", "Find a cooking recipe by dish name.",
                 {"dish": {"type": "string"}}, ["dish"]),
    _simple_tool("set_reminder", "Set a reminder.",
                 {"text": {"type": "string"}, "when": {"type": "string"}}, ["text", "when"]),
    _simple_tool("play_music", "Play a song or playlist.",
                 {"track": {"type": "string"}}, ["track"]),
    _simple_tool("get_traffic", "Get traffic conditions for a route.",
                 {"route": {"type": "string"}}, ["route"]),
    _simple_tool("order_food", "Order food delivery.",
                 {"restaurant": {"type": "string"}, "items": {"type": "array", "items": {"type": "string"}}},
                 ["restaurant", "items"]),
    _simple_tool("get_sports_score", "Get the score of a sports game.",
                 {"team": {"type": "string"}}, ["team"]),
    _simple_tool("get_movie_info", "Get info about a movie.",
                 {"title": {"type": "string"}}, ["title"]),
    _simple_tool("get_definition", "Get the dictionary definition of a word.",
                 {"word": {"type": "string"}}, ["word"]),
    _simple_tool("create_note", "Create a text note.",
                 {"text": {"type": "string"}}, ["text"]),
    _simple_tool("list_notes", "List the user's notes."),
    _simple_tool("get_timezone", "Get the current time in a timezone.",
                 {"timezone": {"type": "string"}}, ["timezone"]),
    _simple_tool("get_crypto_price", "Get a cryptocurrency price.",
                 {"symbol": {"type": "string"}}, ["symbol"]),
    _simple_tool("summarize_url", "Summarize the content at a URL.",
                 {"url": {"type": "string"}}, ["url"]),
    _simple_tool("get_wiki", "Look up a topic on Wikipedia.",
                 {"topic": {"type": "string"}}, ["topic"]),
    _simple_tool("send_sms", "Send an SMS text message.",
                 {"to": {"type": "string"}, "message": {"type": "string"}}, ["to", "message"]),
    _simple_tool("get_air_quality", "Get the air quality index for a city.",
                 {"city": {"type": "string"}}, ["city"]),
    _simple_tool("get_uv_index", "Get the UV index for a city.",
                 {"city": {"type": "string"}}, ["city"]),
    _simple_tool("get_tides", "Get tide times for a coastal location.",
                 {"location": {"type": "string"}}, ["location"]),
    _simple_tool("get_horoscope", "Get the horoscope for a zodiac sign.",
                 {"sign": {"type": "string"}}, ["sign"]),
    _simple_tool("roll_dice", "Roll dice.",
                 {"sides": {"type": "integer"}, "count": {"type": "integer"}}, ["sides"]),
    _simple_tool("flip_coin", "Flip a coin.", {}, []),
    _simple_tool("get_joke", "Get a random joke.", {}, []),
    _simple_tool("get_quote", "Get an inspirational quote.", {}, []),
    _simple_tool("count_words", "Count words in a piece of text.",
                 {"text": {"type": "string"}}, ["text"]),
    _simple_tool("generate_password", "Generate a random password.",
                 {"length": {"type": "integer"}}, ["length"]),
    _simple_tool("shorten_url", "Shorten a long URL.",
                 {"url": {"type": "string"}}, ["url"]),
    _simple_tool("get_ip_info", "Get geolocation info for an IP address.",
                 {"ip": {"type": "string"}}, ["ip"]),
    _simple_tool("get_holiday", "Check if a date is a public holiday.",
                 {"date": {"type": "string"}, "country": {"type": "string"}}, ["date", "country"]),
    _simple_tool("get_distance", "Compute distance between two cities.",
                 {"from_city": {"type": "string"}, "to_city": {"type": "string"}}, ["from_city", "to_city"]),
    _simple_tool("get_population", "Get the population of a place.",
                 {"place": {"type": "string"}}, ["place"]),
    _simple_tool("get_exchange_rate", "Get the raw exchange rate between two currencies.",
                 {"base": {"type": "string"}, "quote": {"type": "string"}}, ["base", "quote"]),
    _simple_tool("schedule_meeting", "Schedule a meeting with people.",
                 {"with_people": {"type": "array", "items": {"type": "string"}}, "time": {"type": "string"}},
                 ["with_people", "time"]),
    _simple_tool("get_calendar", "List upcoming calendar events.", {}, []),
    _simple_tool("get_contact", "Look up a contact by name.",
                 {"name": {"type": "string"}}, ["name"]),
    _simple_tool("add_contact", "Add a new contact.",
                 {"name": {"type": "string"}, "phone": {"type": "string"}}, ["name", "phone"]),
    _simple_tool("get_battery", "Get the device battery level.", {}, []),
    _simple_tool("toggle_wifi", "Turn wifi on or off.",
                 {"on": {"type": "boolean"}}, ["on"]),
    _simple_tool("take_photo", "Take a photo with the camera.", {}, []),
    _simple_tool("get_step_count", "Get today's step count.", {}, []),
]


def big_toolset_with(*extra):
    """BIG_TOOLSET plus any extra tool schemas appended (deduped by name)."""
    seen = {t["function"]["name"] for t in BIG_TOOLSET}
    out = list(BIG_TOOLSET)
    for t in extra:
        if t["function"]["name"] not in seen:
            out.append(t)
            seen.add(t["function"]["name"])
    return out
