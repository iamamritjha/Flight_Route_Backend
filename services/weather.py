"""Live weather + wind from Open-Meteo (no API key)."""

from __future__ import annotations

import httpx

# WMO Weather interpretation codes (subset)
_WMO_LABEL: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def _label(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return _WMO_LABEL.get(int(code), f"Code {code}")


def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "kmh",
    }
    with httpx.Client(timeout=20.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        payload = r.json()

    cur = payload.get("current") or {}
    code = cur.get("weather_code")
    return {
        "latitude": lat,
        "longitude": lon,
        "temperature_c": cur.get("temperature_2m"),
        "relative_humidity_pct": cur.get("relative_humidity_2m"),
        "weather_code": code,
        "conditions": _label(code),
        "wind_speed_kmh": cur.get("wind_speed_10m"),
        "wind_direction_deg": cur.get("wind_direction_10m"),
        "source": "Open-Meteo",
    }
