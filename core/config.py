import os
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

def get_openai_client_params():
    openai_cfg = CONFIG.get("openai", {})
    api_key = openai_cfg.get("api_key", "env")
    if api_key == "env":
        api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    
    base_url = openai_cfg.get("base_url")
    return {
        "api_key": api_key,
        "base_url": base_url
    }

def get_model():
    return CONFIG.get("openai", {}).get("model", "gpt-5.4")

def get_codex_model():
    return CONFIG.get("openai", {}).get("codex_model", "gpt-5.3-codex-spark")

def get_optimization_config():
    return CONFIG.get("optimization", {})
