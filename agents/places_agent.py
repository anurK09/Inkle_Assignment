# agents/places_agent.py

import httpx
import urllib.parse
from utils.geocode import geocode_place

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Wikipedia API – thumbnail + summary
WIKI_SEARCH_URL = (
    "https://en.wikipedia.org/w/api.php?"
    "action=query&prop=pageimages|extracts&exintro&explaintext&format=json"
    "&pithumbsize=500&titles={}"
)


async def fetch_wikipedia_details(place_name: str):
    """
    Fetch thumbnail + summary for a place from Wikipedia.
    Returns dict or None.
    """
    title = urllib.parse.quote(place_name)
    url = WIKI_SEARCH_URL.format(title)

    headers = {"User-Agent": "inkel-tourism-ai/1.0"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

    page = next(iter(pages.values()))

    thumbnail = None
    if "thumbnail" in page and "source" in page["thumbnail"]:
        thumbnail = page["thumbnail"]["source"]

    summary = page.get("extract", "") or ""
    wiki_title = page.get("title", place_name)
    description = page.get("description", "") or ""

    # Popularity score heuristic
    score = 0.0
    if thumbnail:
        score += 2.0
    if summary:
        score += min(len(summary) / 200, 3.0)
    if any(
        k in description.lower()
        for k in ["tourist", "temple", "beach", "fort", "museum", "park", "palace"]
    ):
        score += 1.5

    return {
        "wiki_title": wiki_title,
        "thumbnail": thumbnail,
        "summary": summary,
        "description": description,
        "popularity_score": score,
    }


async def get_places_for_place(place_name: str, max_places: int = 5):
    """
    Returns:
    {
      "success": bool,
      "message": str,
      "places": [
        {
          "name": str,
          "wiki_title": str,
          "thumbnail": str | None,
          "summary": str,
          "description": str,
          "popularity_score": float
        }, ...
      ]
    }
    """

    lat, lon, display = await geocode_place(place_name)

    if lat is None or lon is None:
        return {
            "success": False,
            "message": "I don’t know if this place exists.",
            "places": [],
        }

    # Overpass query – 10km radius
    query = f"""
[out:json][timeout:30];
(
  node["tourism"~"attraction|museum|gallery|zoo|viewpoint|artwork|park|castle|ruins|monument"](around:10000,{lat},{lon});
  way["tourism"~"attraction|museum|gallery|zoo|viewpoint|artwork|park|castle|ruins|monument"](around:10000,{lat},{lon});
  relation["tourism"~"attraction|museum|gallery|zoo|viewpoint|artwork|park|castle|ruins|monument"](around:10000,{lat},{lon});
);
out center;
"""

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(OVERPASS_URL, data={"data": query})
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return {
            "success": False,
            "message": "Unable to fetch tourist places right now.",
            "places": [],
        }

    raw_places = []
    banned = [
        "hotel",
        "guest",
        "lodge",
        "residence",
        "apartment",
        "home",
        "hostel",
        "inn",
        "residency",
        "pg",
        "bank",
    ]

    for el in data.get("elements", []):
        name = el.get("tags", {}).get("name")
        if not name:
            continue

        lower = name.lower()
        if any(b in lower for b in banned):
            continue

        raw_places.append(name)

    # de-duplicate
    unique = []
    for p in raw_places:
        if p not in unique:
            unique.append(p)

    unique = unique[:10]

    if not unique:
        return {
            "success": True,
            "message": f"No major tourist attractions found near {place_name}.",
            "places": [],
        }

    detailed = []
    for name in unique:
        wiki = await fetch_wikipedia_details(name)

        if not wiki:
            detailed.append(
                {
                    "name": name,
                    "wiki_title": name,
                    "thumbnail": None,
                    "summary": "",
                    "description": "",
                    "popularity_score": 0.0,
                }
            )
        else:
            detailed.append(
                {
                    "name": name,
                    "wiki_title": wiki["wiki_title"],
                    "thumbnail": wiki["thumbnail"],
                    "summary": wiki["summary"],
                    "description": wiki["description"],
                    "popularity_score": wiki["popularity_score"],
                }
            )

    detailed.sort(key=lambda x: x["popularity_score"], reverse=True)

    return {
        "success": True,
        "message": f"Here are some popular places you can visit in or near {place_name}:",
        "places": detailed[:max_places],
    }
