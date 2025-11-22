
# # agents/places_agent.py

# import httpx
# from utils.geocode import geocode_place

# OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# async def get_places_for_place(place_name: str, max_places: int = 6):
#     """
#     Fetch tourist attractions using ONLY Overpass (OpenStreetMap).
#     Works on Streamlit Cloud + Mobile.
#     """

#     lat, lon, display_name = await geocode_place(place_name)

#     if lat is None or lon is None:
#         return {
#             "success": False,
#             "message": "I don’t know if this place exists.",
#             "places": [],
#         }

#     # OSM Query (tourism, historic, leisure)
#     query = f"""
# [out:json][timeout:30];
# (
#   node["tourism"~"attraction|museum|zoo|gallery|viewpoint|theme_park|artwork"](around:8000,{lat},{lon});
#   way["tourism"~"attraction|museum|zoo|gallery|viewpoint|theme_park|artwork"](around:8000,{lat},{lon});
#   relation["tourism"~"attraction|museum|zoo|gallery|viewpoint|theme_park|artwork"](around:8000,{lat},{lon});

#   node["historic"~"fort|monument|ruins|castle|memorial"](around:8000,{lat},{lon});
#   way["historic"~"fort|monument|ruins|castle|memorial"](around:8000,{lat},{lon});
#   relation["historic"~"fort|monument|ruins|castle|memorial"](around:8000,{lat},{lon});

#   node["leisure"~"park|garden"](around:8000,{lat},{lon});
#   way["leisure"~"park|garden"](around:8000,{lat},{lon});
#   relation["leisure"~"park|garden"](around:8000,{lat},{lon});
# );
# out center;
# """

#     try:
#         async with httpx.AsyncClient(timeout=20) as client:
#             resp = await client.post(OVERPASS_URL, data={"data": query})
#             data = resp.json()
#     except Exception:
#         return {
#             "success": False,
#             "message": "Unable to fetch tourist places right now.",
#             "places": [],
#         }

#     elements = data.get("elements", [])
#     results = []

#     banned = ["hotel", "resort", "hostel", "inn", "lodge", "pg", "residency"]

#     for el in elements:
#         tags = el.get("tags", {})
#         name = tags.get("name")
#         if not name:
#             continue

#         if any(b in name.lower() for b in banned):
#             continue

#         results.append(name)

#     # Remove duplicates
#     clean = []
#     for r in results:
#         if r not in clean:
#             clean.append(r)

#     clean = clean[:max_places]

#     if not clean:
#         return {
#             "success": True,
#             "message": f"No attractions found near {place_name}.",
#             "places": [],
#         }

#     return {
#         "success": True,
#         "message": f"Here are some popular places you can visit in or near {place_name}:",
#         "places": clean,
#     }




























# agents/places_agent.py

import httpx
from utils.geocode import geocode_place

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

async def get_places_for_place(place_name: str, max_places: int = 5):
    """
    Returns tourist places using ONLY Overpass API (stable for mobile + Streamlit).
    """

    lat, lon, display = await geocode_place(place_name)

    if lat is None:
        return {
            "success": False,
            "message": "I don’t know if this place exists.",
            "places": [],
        }

    # REQUIRED HEADER → Overpass blocks Streamlit without this
    headers = {
        "User-Agent": "Inkle-Tourism-AI/1.0 (student project contact: test@example.com)"
    }

    query = f"""
[out:json][timeout:30];
(
  node["tourism"~"attraction|museum|gallery|zoo|viewpoint|park|castle|monument|theme_park"](around:15000,{lat},{lon});
  way["tourism"~"attraction|museum|gallery|zoo|viewpoint|park|castle|monument|theme_park"](around:15000,{lat},{lon});
  relation["tourism"~"attraction|museum|gallery|zoo|viewpoint|park|castle|monument|theme_park"](around:15000,{lat},{lon});
);
out center;
"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                OVERPASS_URL,
                data={"data": query},
                headers=headers  # required
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print("OVERPASS ERROR:", e)
        return {
            "success": False,
            "message": "Unable to fetch tourist places right now.",
            "places": [],
        }

    raw_names = []
    banned = ["hotel", "lodge", "guest", "inn", "residency", "home"]

    for el in data.get("elements", []):
        name = el.get("tags", {}).get("name")
        if not name:
            continue

        # skip hotels, hostels
        if any(b in name.lower() for b in banned):
            continue

        raw_names.append(name)

    # de-duplicate
    result = []
    for n in raw_names:
        if n not in result:
            result.append(n)

    result = result[:max_places]

    if not result:
        return {
            "success": True,
            "message": f"No major tourist attractions found near {place_name}.",
            "places": [],
        }

    return {
        "success": True,
        "message": f"Here are some popular places you can visit in or near {place_name}:",
        "places": result,
    }
