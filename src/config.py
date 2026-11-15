import json
import os
from paths import config_file_path, persistent_core

DEFAULT_CONFIG = {
    "idioma": "EN",
    "bth_day": "",
    "bth_month": "",
    "topmost": False
}


def load_config() -> dict:
    if not os.path.exists(config_file_path):
        return DEFAULT_CONFIG.copy()
    try:
        with open(config_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config_data: dict) -> bool:
    try:
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def update_config_value(key: str, value) -> bool:
    config = load_config()
    config[key] = value
    return save_config(config)


def get_config_value(key: str, default=None):
    config = load_config()
    return config.get(key, default)
