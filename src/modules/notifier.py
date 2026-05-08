import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='config/.env')

BRIEF_TOKEN = os.getenv('TELEGRAM_BRIEF_TOKEN')
BRIEF_CHAT_ID = os.getenv('TELEGRAM_BRIEF_CHAT_ID')
ALERT_TOKEN = os.getenv('TELEGRAM_ALERT_TOKEN')
ALERT_CHAT_ID = os.getenv('TELEGRAM_ALERT_CHAT_ID')

def send_brief(message):
    url = f"https://api.telegram.org/bot{BRIEF_TOKEN}/sendMessage"
    payload = {
        "chat_id": BRIEF_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.json()

def send_alert(message):
    url = f"https://api.telegram.org/bot{ALERT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ALERT_CHAT_ID,
        "text": f"🚨 ALERT:\n{message}",
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.json()
