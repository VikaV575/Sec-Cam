import json
import os
from .config import DB_FILE
from .state import devices

def load_devices() -> dict:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_devices() -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=4)