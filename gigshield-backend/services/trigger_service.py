import os

import requests
from dotenv import load_dotenv

load_dotenv("config.env", override=True)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")
AQICN_KEY = os.getenv("AQICN_API_KEY", "")


def check_rain_heat(pincode: str) -> dict | None:
    """Check OpenWeatherMap for rain or heat triggers."""
    if not OPENWEATHER_KEY or OPENWEATHER_KEY == "your-openweather-key":
        return None
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": f"{pincode},IN", "appid": OPENWEATHER_KEY, "units": "metric"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        rain = data.get("rain", {}).get("1h", 0)
        temp = data.get("main", {}).get("temp", 0)
        if rain > 25:
            return {
                "event_type": "rain",
                "severity_value": rain,
                "api_source": "openweathermap",
                "zone_pincode": pincode,
            }
        if temp > 42:
            return {
                "event_type": "heat",
                "severity_value": temp,
                "api_source": "openweathermap",
                "zone_pincode": pincode,
            }
        return None
    except Exception as e:
        print(f"[TRIGGER] OpenWeather error: {e}")
        return None


def check_aqi(pincode: str) -> dict | None:
    """Check AQICN for air quality triggers."""
    if not AQICN_KEY or AQICN_KEY == "your-aqicn-key":
        return None
    try:
        url = f"https://api.waqi.info/feed/{pincode}/?token={AQICN_KEY}"
        r = requests.get(url, timeout=5)
        data = r.json()
        aqi = data.get("data", {}).get("aqi", 0)
        try:
            aqi_val = float(aqi)
        except (TypeError, ValueError):
            aqi_val = 0.0
        if aqi_val > 300:
            return {
                "event_type": "aqi",
                "severity_value": aqi_val,
                "api_source": "aqicn",
                "zone_pincode": pincode,
            }
        return None
    except Exception as e:
        print(f"[TRIGGER] AQICN error: {e}")
        return None


MOCK_CURFEW_ZONES = []
MOCK_OUTAGE_ACTIVE = False


def check_mock_curfew(pincode: str) -> dict | None:
    """Mock curfew trigger for testing."""
    if pincode in MOCK_CURFEW_ZONES:
        return {
            "event_type": "curfew",
            "severity_value": 1.0,
            "api_source": "mock_civic",
            "zone_pincode": pincode,
        }
    return None


def check_mock_outage(pincode: str) -> dict | None:
    """Mock platform outage trigger for testing."""
    if MOCK_OUTAGE_ACTIVE:
        return {
            "event_type": "app_outage",
            "severity_value": 1.0,
            "api_source": "mock_platform",
            "zone_pincode": pincode,
        }
    return None


def run_all_triggers(pincode: str) -> list:
    """Run all trigger checks for a pincode."""
    results = []
    for check in [check_rain_heat, check_aqi, check_mock_curfew, check_mock_outage]:
        result = check(pincode)
        if result:
            results.append(result)
    return results
