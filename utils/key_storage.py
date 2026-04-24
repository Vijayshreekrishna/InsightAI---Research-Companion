import json
import os

KEYS_FILE = ".user_keys.json"

def save_user_keys(keys_dict):
    """Save user API keys to a local hidden JSON file."""
    try:
        with open(KEYS_FILE, "w", encoding="utf-8") as f:
            json.dump(keys_dict, f)
        return True
    except Exception:
        return False

def load_user_keys():
    """Load user API keys from the local hidden JSON file."""
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}
