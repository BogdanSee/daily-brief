import json
from datetime import datetime
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

def get_user_city(chat_id=None):
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            if chat_id and str(chat_id) in config:
                return config[str(chat_id)].get("city", "București")
            elif config:
                return next(iter(config.values())).get("city", "București")
    except Exception:
        pass
    return "București"

def get_traffic(chat_id=None):
    try:
        now = datetime.now()
        hour = now.hour
        city = get_user_city(chat_id)

        if 7 <= hour <= 9:
            level = "🔴 <b>Trafic intens</b> — ora de vârf dimineața"
            tip = "Pleacă mai devreme sau evită arterele principale!"
        elif 12 <= hour <= 14:
            level = "🟡 <b>Trafic moderat</b> — ora de prânz"
            tip = "Centrul orașului poate fi aglomerat."
        elif 17 <= hour <= 20:
            level = "🔴 <b>Trafic intens</b> — ora de vârf seara"
            tip = "Ia în calcul +20-30 minute față de normal."
        elif 22 <= hour or hour <= 5:
            level = "🟢 <b>Trafic redus</b> — noapte"
            tip = "Circulație liberă pe majoritatea arterelor."
        else:
            level = "🟢 <b>Trafic normal</b>"
            tip = "Condiții bune de circulație."

        # Coordonate pentru link-uri
        lat_lon = {"București": "44.4268,26.1025", "Iași": "47.1585,27.6014",
                   "Cluj-Napoca": "46.7712,23.6236", "Timișoara": "45.7489,21.2087",
                   "Brașov": "45.6427,25.5887", "Constanța": "44.1598,28.6348"}
        coords = lat_lon.get(city, "44.4268,26.1025")

        message = (
            f"🚗 <b>Trafic {city}</b>\n"
            f"{level}\n"
            f"💡 {tip}\n"
            f"🗺 <a href='https://www.waze.com/ro/live-map?ll={coords}&zoom=13'>Vezi live pe Waze</a> | "
            f"<a href='https://maps.google.com/?q={city}&layer=traffic'>Google Maps Trafic</a>"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare traffic: {str(e)}"
