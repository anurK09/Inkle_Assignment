# utils/geocode.py

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "madras": "Chennai",
    "pondicherry": "Puducherry",
    "pondy": "Puducherry",
    "puducherry": "Puducherry",
}


async def geocode_place(place_name: str):
    """
    Use Nominatim API to get coordinates (lat, lon) for a place.
    - Normalizes some common aliases.
    - Tries multiple query variants.
    Returns (lat, lon, display_name) or (None, None, None) if not found.
    """
    if not place_name:
        return None, None, None

    raw = place_name.strip()
    key = raw.lower()
    normalized = CITY_ALIASES.get(key, raw)

    headers = {
        "User-Agent": "inkel-assignment-streamlit-app",  # required by Nominatim
    }

    queries = [
        normalized,
        f"{normalized}, India",
        f"{normalized} city",
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for q in queries:
            params = {
                "q": q,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
            }
            try:
                resp = await client.get(NOMINATIM_URL, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                continue

            if not data:
                continue

            first = data[0]
            lat = first.get("lat")
            lon = first.get("lon")
            if lat is None or lon is None:
                continue

            display_name = first.get("display_name", normalized)
            try:
                return float(lat), float(lon), display_name
            except (TypeError, ValueError):
                continue

    return None, None, None
