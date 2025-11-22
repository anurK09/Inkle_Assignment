# agents/orchestrator.py

import re
from typing import Literal, Tuple

from agents.weather_agent import get_weather_for_place
from agents.places_agent import get_places_for_place

IntentType = Literal["weather", "places", "both", "unknown"]


# -----------------------------------------------------
# PLACE DETECTION – robust + case-insensitive
# -----------------------------------------------------
async def detect_place(user_input: str) -> str:
    """
    Detect a place name from the user input.

    Handles:
    - "I'm going to go to bangalore, let's plan my trip."
    - "what is the temperature in pune?"
    - "places to visit in pondicherry"
    - "weather and tourist places in hyderabad"
    """

    if not user_input:
        return ""

    original = user_input.strip()
    text = original.lower()

    STOPWORDS = {
        "what", "we", "i", "you", "there", "next", "week", "trip",
        "plan", "planning", "temperature", "weather", "maybe", "thinking",
        "should", "pack", "my", "to", "in", "visit", "go", "going",
        "lets", "let", "and", "or", "is", "the", "it", "im", "for",
        "about", "please", "places", "place", "city"
    }

    def normalize_candidate(candidate: str) -> str:
        # remove punctuation, split, remove stopwords
        candidate = re.sub(r"[?,.!]", " ", candidate.strip().lower())
        tokens = [t for t in candidate.split() if t and t not in STOPWORDS]
        if not tokens:
            return ""
        # multi-word cities like "new delhi", "south goa"
        tokens = tokens[:3]
        # Title() so geocoder gets capitalized city name
        return " ".join(tokens).title()

    # -----------------------------------------------
    # 1) Pattern-based extraction (lowercase text)
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
        r"in\s+([a-z\s]+)",
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            cand = normalize_candidate(m.group(1))
            if cand:
                return cand

    # -----------------------------------------------
    # 2) Capitalized phrase fallback
    #    e.g. "Bangalore", "New Delhi", "Pondicherry"
    # -----------------------------------------------
    caps = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b", original)
    for phrase in caps:
        cand = normalize_candidate(phrase)
        if cand:
            return cand

    # -----------------------------------------------
    # 3) Last non-stopword as final fallback
    # -----------------------------------------------
    words = [w for w in re.sub(r"[?,.!]", " ", text).split() if w and w not in STOPWORDS]
    if words:
        return words[-1].title()

    return ""


# -----------------------------------------------------
# INTENT DETECTION
# -----------------------------------------------------
def detect_intent(user_input: str) -> IntentType:
    text = user_input.lower()

    ask_weather = any(word in text for word in ["weather", "temperature", "hot", "cold"])
    ask_places = any(word in text for word in ["place", "places", "visit", "attractions", "tourist"])

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

    debug_info = {
        "detected_place": place,
        "intent": intent,
    }

    if not place:
        return (
            "I couldn't detect the place you want to visit. Please mention a valid city name.",
            debug_info,
        )

    responses = []

    # WEATHER
    if intent in ("weather", "both"):
        weather_result = await get_weather_for_place(place)
        debug_info["weather_result"] = weather_result

        if not weather_result.get("success"):
            return weather_result.get("message", "Couldn't fetch weather."), debug_info

        responses.append(weather_result["message"])

    # PLACES
    if intent in ("places", "both"):
        places_result = await get_places_for_place(place)
        debug_info["places_result"] = places_result

        if not places_result.get("success"):
            return places_result.get("message", "Couldn't fetch tourist places."), debug_info

        if places_result.get("places"):
            names = []
            for p in places_result["places"]:
                if isinstance(p, dict):
                    names.append(p.get("name") or p.get("wiki_title") or "")
                else:
                    names.append(str(p))
            names = [n for n in names if n]
            places_list = "\n".join(f"- {n}" for n in names)
            responses.append(places_result["message"] + "\n" + places_list)
        else:
            responses.append(places_result["message"])

    # UNKNOWN → return both
    if intent == "unknown":
        weather_result = await get_weather_for_place(place)
        places_result = await get_places_for_place(place)

        debug_info["weather_result"] = weather_result
        debug_info["places_result"] = places_result

        if not weather_result.get("success"):
            return weather_result.get("message", "Couldn't fetch weather."), debug_info

        resp = [weather_result["message"]]

        if places_result.get("success") and places_result.get("places"):
            names = []
            for p in places_result["places"]:
                if isinstance(p, dict):
                    names.append(p.get("name") or p.get("wiki_title") or "")
                else:
                    names.append(str(p))
            names = [n for n in names if n]
            places_list = "\n".join(f"- {n}" for n in names)
            resp.append(places_result["message"] + "\n" + places_list)
        else:
            resp.append(places_result.get("message", "Couldn't fetch tourist places."))

        return "\n\n".join(resp), debug_info

    if not responses:
        return (
            "I’m not sure what you are asking. You can ask about weather, places, or both.",
            debug_info,
        )

    final_response = "\n\n".join(responses)
    return final_response, debug_info
