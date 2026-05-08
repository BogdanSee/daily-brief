import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

BRIEF_TOKEN = os.getenv('TELEGRAM_BRIEF_TOKEN')
ALERT_TOKEN = os.getenv('TELEGRAM_ALERT_TOKEN')
ALERT_CHAT_ID = os.getenv('TELEGRAM_ALERT_CHAT_ID')

CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

def get_all_users():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config
    except Exception:
        pass
    return {}

def send_brief(message, chat_id=None):
    """Trimite mesajul la un user specific sau la toti utilizatorii."""
    url = f"https://api.telegram.org/bot{BRIEF_TOKEN}/sendMessage"
    
    if chat_id:
        # Trimite la un singur user
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    else:
        # Trimite la toti utilizatorii din config
        users = get_all_users()
        results = []
        for uid, user_data in users.items():
            try:
                payload = {
                    "chat_id": uid,
                    "text": message,
                    "parse_mode": "HTML"
                }
                resp = requests.post(url, json=payload, timeout=10)
                results.append(resp.json())
            except Exception as e:
                results.append({"ok": False, "error": str(e)})
        
        # Returnam primul rezultat pentru compatibilitate
        return results[0] if results else {"ok": False, "error": "No users"}

def send_alert(message):
    url = f"https://api.telegram.org/bot{ALERT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ALERT_CHAT_ID,
        "text": f"🚨 ALERT:\n{message}",
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload, timeout=10)
    return response.json()
