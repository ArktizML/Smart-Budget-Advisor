import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "data"
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "data.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
            return []

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []
    except FileNotFoundError:
         return[]
    
def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
