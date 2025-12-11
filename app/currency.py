import json, os, requests
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
CACHE_PATH = os.path.join(ROOT_DIR, "data", "exchange_rates.json")
BASE_CURRENCY = "PLN"


def load_cached_rates():
    if not os.path.exists(CACHE_PATH):
        return None

    try:
        with open(CACHE_PATH, "r") as f:
            data = json.load(f)
    except:
        return None  # invalid json

    if "timestamp" not in data or "rates" not in data:
        return None

    try:
        timestamp = datetime.fromisoformat(data["timestamp"])
    except:
        return None

    # cache expires after 24 hours
    if datetime.now() - timestamp > timedelta(hours=24):
        return None

    return data["rates"]


def save_rates(rates):
    data = {
        "timestamp": datetime.now().isoformat(),
        "rates": rates
    }
    try:
        with open(CACHE_PATH, "w") as f:
            json.dump(data, f, indent=4)
        print("Saved rates to:", CACHE_PATH)
    except Exception as e:
        print("SAVE ERROR:", e)
        raise


def fetch_rates():
    url = f"https://open.er-api.com/v6/latest/{BASE_CURRENCY}"
    r = requests.get(url)

    if r.status_code != 200:
        raise Exception("Failed to fetch currency rates")

    data = r.json()

    if data.get("result") != "success":
        raise Exception("Currency API error")

    return data["rates"]


def get_rates():
    cached = load_cached_rates()
    if cached:
        return cached

    fresh = fetch_rates()
    save_rates(fresh)
    return fresh


def convert(amount, from_currency, to_currency, rates):
    if from_currency == to_currency:
        return amount

    # only base currency → target supported for now
    # if from_currency != BASE_CURRENCY:
    #     raise ValueError("Only base currency → target supported right now")

    rate = rates.get(to_currency)
    if not rate:
        return amount

    return round(amount * rate, 2)
