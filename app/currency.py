import json
import requests
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = "exchange_rates.json"
RATES_FILE = os.path.join(BASE_DIR, "..", "data", DATA_PATH)

SUPPORTED_CURRENCIES = [
    "PLN", "EUR", "USD", "GBP", "CHF",
    "SEK", "NOK", "DKK", "CZK"
]

def load_rates():
    with open(RATES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rates(data):
    with open(RATES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def fetch_rates_from_nbp():
    url = "https://api.nbp.pl/api/exchangerates/tables/A?format=json"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("NBP API down")

    data = response.json()[0]["rates"]

    rates = {"PLN": 1.0}

    for entry in data:
        code = entry["code"]
        mid = entry["mid"]

        if code in SUPPORTED_CURRENCIES:
            rates[code] = float(mid)

    return rates

def update_rates_if_needed():
    data = load_rates()
    today = datetime.now().strftime("%Y-%m-%d")

    if data["last_update"] == today:
        return data["rates"]

    new_rates = fetch_rates_from_nbp()

    data["last_update"] = today
    data["rates"] = new_rates
    save_rates(data)

    return new_rates

def convert(amount, from_currency, to_currency):
    rates = update_rates_if_needed()

    if from_currency not in rates or to_currency not in rates:
        raise Exception("Unsupported currency")

    amount_in_pln = amount * rates[from_currency]

    result = amount_in_pln / rates[to_currency]

    return round(result, 2)
