import os
from typing import Any

from dotenv import load_dotenv
import requests

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or ""
AQICN_API_KEY = os.getenv("AQICN_API_KEY") or ""


def check_weather_trigger(pincode: str) -> dict | None:
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": f"{pincode},IN", "appid": OPENWEATHER_API_KEY, "units": "metric"}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return None
        data: dict[str, Any] = resp.json()

        rain_1h = None
        if isinstance(data.get("rain"), dict):
            rain_1h = data["rain"].get("1h")

        temp = None
        if isinstance(data.get("main"), dict):
            temp = data["main"].get("temp")

        if rain_1h is not None and float(rain_1h) > 25.0:
            return {
                "event_type": "rain",
                "severity_value": float(rain_1h),
                "zone_pincode": pincode,
                "api_source": "openweathermap",
            }

        if temp is not None and float(temp) > 42.0:
            return {
                "event_type": "heat",
                "severity_value": float(temp),
                "zone_pincode": pincode,
                "api_source": "openweathermap",
            }

        return None
    except Exception:
        return None


def check_aqi_trigger(pincode: str) -> dict | None:
    try:
        url = f"https://api.waqi.info/feed/{pincode}/?token={AQICN_API_KEY}"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        data: dict[str, Any] = resp.json()
        aqi = None
        if isinstance(data.get("data"), dict):
            aqi = data["data"].get("aqi")
        if aqi is not None and float(aqi) > 300:
            return {
                "event_type": "aqi",
                "severity_value": float(aqi),
                "zone_pincode": pincode,
                "api_source": "aqicn",
            }
        return None
    except Exception:
        return None


def check_mock_curfew_trigger(pincode: str) -> dict | None:
    mock_curfew_zones = []
    if pincode in mock_curfew_zones:
        return {
            "event_type": "curfew",
            "severity_value": 1.0,
            "zone_pincode": pincode,
            "api_source": "mock_civic_api",
        }
    return None


def check_mock_app_outage_trigger(pincode: str) -> dict | None:
    app_outage_active = False
    if app_outage_active is True:
        return {
            "event_type": "app_outage",
            "severity_value": 1.0,
            "zone_pincode": pincode,
            "api_source": "mock_platform_api",
        }
    return None


def run_all_triggers_for_pincode(pincode: str) -> list:
    triggers: list[dict] = []
    for fn in (
        check_weather_trigger,
        check_aqi_trigger,
        check_mock_curfew_trigger,
        check_mock_app_outage_trigger,
    ):
        result = fn(pincode)
        if result is not None:
            triggers.append(result)
    return triggers

