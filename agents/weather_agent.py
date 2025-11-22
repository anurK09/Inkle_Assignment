# agents/weather_agent.py

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"


async def get_weather_for_place(place: str) -> dict:
    """
    Fetch real weather data using WeatherAPI.com.
    Requires WEATHER_API_KEY in .env.
    """

    if not place:
        return {
            "success": False,
            "message": "No place provided for weather lookup.",
        }

    if not API_KEY:
        return {
            "success": False,
            "message": "Weather API key missing. Please add WEATHER_API_KEY in .env file.",
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
    cloud = current.get("cloud", 0)  # rough rain chance

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
