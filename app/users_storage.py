import json
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "data"
USERS_PATH = os.path.join(BASE_DIR, "..", "data", "users.json")

def load_users():
    if not os.path.exists(USERS_PATH):
        return []    # pusta lista jeśli brak pliku
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_users(users_list):
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users_list, f, indent=2, ensure_ascii=False)