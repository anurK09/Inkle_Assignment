#  agents/weather_agent.py

import os
import httpx
from dotenv import load_dotenv
import streamlit as st

# Load .env for local runs
load_dotenv()

# ---------------------------------------------------------
# API KEY HANDLING (WORKS LOCALLY + STREAMLIT CLOUD)
# ---------------------------------------------------------

API_KEY = None

# 1) Try to load from Streamlit Cloud secrets
try:
    if "WEATHER_API_KEY" in st.secrets:
        API_KEY = st.secrets["WEATHER_API_KEY"]
except Exception:
    API_KEY = None  # No secrets available locally

# 2) Fallback to local .env file
if not API_KEY:
    API_KEY = os.getenv("WEATHER_API_KEY")

# ---------------------------------------------------------

BASE_URL = "http://api.weatherapi.com/v1/current.json"


async def get_weather_for_place(place: str) -> dict:
    """Fetch real weather data using WeatherAPI."""

    if not place:
        return {
            "success": False,
            "message": "No place provided for weather lookup.",
        }

    if not API_KEY:
        return {
            "success": False,
            "message": (
                "Weather API key missing! Add WEATHER_API_KEY in "
                "Streamlit Secrets (deployment) or in your .env file (local)."
            ),
        }

    params = {
        "key": API_KEY,
        "q": place,
        "aqi": "no",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Unable to fetch weather: {str(e)}",
        }

    if "error" in data:
        return {
            "success": False,
            "message": f"Couldn't fetch weather for {place}.",
        }

    current = data.get("current", {})
    temp_c = current.get("temp_c")
    cloud = current.get("cloud", 0)  # cloud used as basic rain chance

    if temp_c is None:
        return {
            "success": False,
            "message": f"Couldn't fetch weather for {place}.",
        }

    message = (
        f"In {place} it's currently {temp_c}°C "
        f"with a {cloud}% chance of rain."
    )

    return {
        "success": True,
        "message": message,
        "raw": data,
    }
