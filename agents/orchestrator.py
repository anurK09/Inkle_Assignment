# agents/orchestrator.py

import re
from typing import Literal, Tuple

from agents.weather_agent import get_weather_for_place
from agents.places_agent import get_places_for_place

IntentType = Literal["weather", "places", "both", "unknown"]


# -----------------------------------------------------
# PLACE DETECTION – reliable for desktop + mobile
# -----------------------------------------------------
async def detect_place(user_input: str) -> str:
    """
    Extract city/place name from any user query.
    Works on mobile + desktop + autocorrect text.
    """

    if not user_input:
        return ""

    original = user_input.strip()
    lower = original.lower()

    STOPWORDS = {
        "what", "we", "i", "you", "there", "next", "week", "trip", "plan",
        "planning", "temperature", "weather", "maybe", "thinking", "should",
        "pack", "my", "to", "in", "visit", "go", "going", "lets", "let",
        "and", "or", "is", "the", "it", "im", "for", "about", "please",
        "places", "place", "city", "want"
    }

    def normalize(candidate: str) -> str:
        """Turn extracted text into a valid city name."""
        candidate = re.sub(r"[^\w\s]", " ", candidate.lower())
        tokens = [t for t in candidate.split() if t and t not in STOPWORDS]
        if not tokens:
            return ""
        tokens = tokens[:3]
        return " ".join(tokens).title()

    # -----------------------------------------------
    # 1) Pattern-based extraction
    # -----------------------------------------------
    patterns = [
        r"going to\s+([a-z\s]+)",
        r"go to\s+([a-z\s]+)",
        r"travel to\s+([a-z\s]+)",
        r"plan my trip to\s+([a-z\s]+)",
        r"plan trip to\s+([a-z\s]+)",
        r"thinking to go to\s+([a-z\s]+)",
        r"thinking of visiting\s+([a-z\s]+)",
        r"visit\s+([a-z\s]+)",
        r"places in\s+([a-z\s]+)",
        r"in\s+([a-z\s]+)",
    ]

    for pattern in patterns:
        m = re.search(pattern, lower)
        if m:
            cand = normalize(m.group(1))
            if cand:
                return cand

    # -----------------------------------------------
    # 2) Capitalized words (e.g., Delhi, New Delhi, Goa)
    # -----------------------------------------------
    caps = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b", original)
    for phrase in caps:
        cand = normalize(phrase)
        if cand:
            return cand

    # -----------------------------------------------
    # 3) Single-word city fallback
    # -----------------------------------------------
    words = [
        w for w in re.sub(r"[^\w\s]", " ", lower).split()
        if w not in STOPWORDS
    ]
    if words:
        return words[-1].title()

    return ""


# -----------------------------------------------------
# INTENT DETECTION
# -----------------------------------------------------
def detect_intent(user_input: str) -> IntentType:
    text = user_input.lower()

    ask_weather = any(k in text for k in ["weather", "temperature", "hot", "cold"])
    ask_places = any(k in text for k in ["places", "place", "visit", "tourist", "attractions"])

    if ask_weather and ask_places:
        return "both"
    if ask_weather:
        return "weather"
    if ask_places:
        return "places"
    if "plan my trip" in text or "plan trip" in text:
        return "both"

    return "unknown"


# -----------------------------------------------------
# MAIN ORCHESTRATOR
# -----------------------------------------------------
async def handle_user_query(user_input: str) -> Tuple[str, dict]:
    place = await detect_place(user_input)
    intent = detect_intent(user_input)

    debug = {
        "detected_place": place,
        "intent": intent,
    }

    if not place:
        return ("I couldn't detect the place you want to visit. Please mention a valid city name.", debug)

    responses = []

    # WEATHER
    if intent in ("weather", "both"):
        weather = await get_weather_for_place(place)
        debug["weather_result"] = weather

        if not weather.get("success"):
            return (weather.get("message", "Couldn't fetch weather."), debug)

        responses.append(weather["message"])

    # PLACES
    if intent in ("places", "both"):
        places = await get_places_for_place(place)
        debug["places_result"] = places

        if not places.get("success"):
            return (places.get("message", "Couldn't fetch tourist places."), debug)

        if places.get("places"):
            formatted = "\n".join(f"- {p}" for p in places["places"])
            responses.append(places["message"] + "\n" + formatted)
        else:
            responses.append(places["message"])

    # UNKNOWN → return both
    if intent == "unknown":
        weather = await get_weather_for_place(place)
        places = await get_places_for_place(place)

        debug["weather_result"] = weather
        debug["places_result"] = places

        if not weather.get("success"):
            return (weather.get("message", "Couldn't fetch weather."), debug)

        resp = [weather["message"]]

        if places.get("places"):
            formatted = "\n".join(f"- {p}" for p in places["places"])
            resp.append(places["message"] + "\n" + formatted)
        else:
            resp.append(places.get("message", "Couldn't fetch tourist places."))

        return ("\n\n".join(resp), debug)

    return ("\n\n".join(responses), debug)
