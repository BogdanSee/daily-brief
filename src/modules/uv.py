import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

API_KEY = os.getenv('OPENWEATHER_API_KEY')
CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

def get_uv_level(uv):
    if uv < 3:
        return "🟢 Scăzut", "Risc minim. Nu e nevoie de protecție specială."
    elif uv < 6:
        return "🟡 Moderat", "Protecție recomandată — cremă SPF 30+, pălărie."
    elif uv < 8:
        return "🟠 Ridicat", "Protecție necesară — evită soarele între 11-15. SPF 50+."
    elif uv < 11:
        return "🔴 Foarte ridicat", "Protecție maximă! Stai la umbră între 10-16. SPF 50+, ochelari."
    else:
        return "🟣 Extrem", "⚠️ Pericol extrem! Evită complet expunerea la soare."

def get_uv(chat_id=None):
    try:
        lat, lon, city = 44.4268, 26.1025, "București"
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            if chat_id and str(chat_id) in config:
                user = config[str(chat_id)]
            elif config:
                user = next(iter(config.values()))
            lat = user.get("lat", 44.4268)
            lon = user.get("lon", 26.1025)
            city = user.get("city", "București")

        # Daca e noapte (21:00 - 06:00) UV e 0
        hour = datetime.now().hour
        if hour >= 21 or hour < 6:
            message = (
                f"☀️ <b>Indice UV în {city}</b>\n"
                f"📊 UV: <b>0</b> — 🟢 Scăzut\n"
                f"💡 E noapte — nicio radiație UV."
            )
            return message, None

        url = (
            f"https://api.openweathermap.org/data/2.5/uvi"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()

        uv = data.get('value', 0)
        uv_rounded = round(uv, 1)
        level, advice = get_uv_level(uv)

        message = (
            f"☀️ <b>Indice UV în {city}</b>\n"
            f"📊 UV: <b>{uv_rounded}</b> — {level}\n"
            f"💡 {advice}"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare UV: {str(e)}"
