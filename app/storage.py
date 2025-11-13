import json, os

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "data.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
