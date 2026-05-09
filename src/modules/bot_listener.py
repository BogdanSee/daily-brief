import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from github_sync import sync_config

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

ZODIAC_RO = {
    "aries": "Berbec", "taurus": "Taur", "gemini": "Gemeni",
    "cancer": "Rac", "leo": "Leu", "virgo": "Fecioară",
    "libra": "Balanță", "scorpio": "Scorpion", "sagittarius": "Săgetător",
    "capricorn": "Capricorn", "aquarius": "Vărsător", "pisces": "Pești"
}

# State temporar pentru utilizatorii in proces de setup
pending_setup = {}

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    sync_config()

def send_message(chat_id, text, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }, timeout=10)

def send_keyboard(chat_id, text, keyboard):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": keyboard}
    }, timeout=10)

def send_zodiac_keyboard(chat_id):
    keyboard = []
    signs = list(ZODIAC_RO.items())
    for i in range(0, len(signs), 3):
        row = [{"text": v, "callback_data": f"zodiac_{k}"} for k, v in signs[i:i+3]]
        keyboard.append(row)
    send_keyboard(chat_id, "⭐ Acum alege zodia ta:", keyboard)

def geocode_city(city):
    try:
        # Cautam in Romania intai
        url = f"https://nominatim.openstreetmap.org/search?q={city},Romania&format=json&limit=1"
        headers = {"User-Agent": "DailyBriefBot/1.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data and data[0].get('type') in ['city', 'town', 'village', 'municipality', 'administrative']:
            return float(data[0]['lat']), float(data[0]['lon']), data[0]['display_name'].split(',')[0]
        
        # Cautam global
        url2 = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        resp2 = requests.get(url2, headers=headers, timeout=10)
        data2 = resp2.json()
        if data2 and data2[0].get('type') in ['city', 'town', 'village', 'municipality', 'administrative']:
            return float(data2[0]['lat']), float(data2[0]['lon']), data2[0]['display_name'].split(',')[0]
        
        return None, None, None
    except Exception:
        return None, None, None

def answer_callback(callback_id):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_id}, timeout=10)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    resp = requests.get(url, params=params, timeout=35)
    return resp.json().get("result", [])

def run_bot():
    print("[BotListener] Pornit. Ascult comenzi...")
    config = load_config()
    offset = None

    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1

            # Mesaje text
            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                text = msg.get("text", "")

                # Comenzi
                if text == "/start":
                    if chat_id in config and "name" in config[chat_id] and "zodiac" in config[chat_id] and "city" in config[chat_id]:
                        name = config[chat_id]["name"]
                        zodiac = ZODIAC_RO[config[chat_id]["zodiac"]]
                        city = config[chat_id]["city"]
                        send_message(chat_id,
                            f"👋 Bun venit înapoi, <b>{name}</b>!\n"
                            f"⭐ Zodia: <b>{zodiac}</b>\n"
                            f"📍 Oraș: <b>{city}</b>\n\n"
                            f"Folosește /setzodiac sau /setoras să modifici setările."
                        )
                    else:
                        pending_setup[chat_id] = {"step": "name"}
                        send_message(chat_id,
                            "👋 Bun venit la <b>DailyBrief</b>!\n\n"
                            "Hai să te configurez rapid.\n"
                            "✏️ <b>Cum te numești?</b>"
                        )

                elif text == "/setzodiac":
                    send_zodiac_keyboard(chat_id)

                elif text == "/setoras":
                    pending_setup[chat_id] = {"step": "change_city"}
                    send_message(chat_id, "📍 Scrie orașul în care te afli acum:")

                elif text == "/status":
                    if chat_id in config and "name" in config[chat_id]:
                        name = config[chat_id]["name"]
                        zodiac = ZODIAC_RO.get(config[chat_id].get("zodiac", ""), "Nesetat")
                        city = config[chat_id].get("city", "Nesetat")
                        send_message(chat_id,
                            f"⚙️ <b>Setările tale</b>\n"
                            f"👤 Nume: <b>{name}</b>\n"
                            f"⭐ Zodie: <b>{zodiac}</b>\n"
                            f"📍 Oraș: <b>{city}</b>"
                        )
                    else:
                        send_message(chat_id, "⚠️ Nu ești configurat. Folosește /start")

                # Raspunsuri la setup
                elif chat_id in pending_setup:
                    step = pending_setup[chat_id].get("step")

                    if step == "name":
                        pending_setup[chat_id]["name"] = text.strip()
                        pending_setup[chat_id]["step"] = "city"
                        send_message(chat_id, f"Super, <b>{text.strip()}</b>! 👋\n\n📍 În ce oraș te afli?")

                    elif step == "city" or step == "change_city":
                        lat, lon, city_name = geocode_city(text.strip())
                        if lat:
                            if chat_id not in config:
                                config[chat_id] = {}
                            config[chat_id]["city"] = city_name
                            config[chat_id]["lat"] = lat
                            config[chat_id]["lon"] = lon

                            if step == "city":
                                config[chat_id]["name"] = pending_setup[chat_id].get("name", text)
                                pending_setup[chat_id]["step"] = "zodiac"
                                save_config(config)
                                sync_config()
                                send_zodiac_keyboard(chat_id)
                            else:
                                save_config(config)
                                sync_config()
                                del pending_setup[chat_id]
                                send_message(chat_id, f"✅ Oraș actualizat: <b>{city_name}</b>")
                        else:
                            send_message(chat_id, "❌ Nu am găsit orașul. Încearcă din nou:")

            # Callback butoane
            elif "callback_query" in update:
                cb = update["callback_query"]
                chat_id = str(cb["message"]["chat"]["id"])
                data = cb["data"]
                answer_callback(cb["id"])

                # Zodiac ales
                if data.startswith("zodiac_"):
                    sign = data.replace("zodiac_", "")
                    if sign in ZODIAC_SIGNS:
                        if chat_id not in config:
                            config[chat_id] = {}
                        config[chat_id]["zodiac"] = sign
                        save_config(config)
                        sync_config()

                        if chat_id in pending_setup:
                            del pending_setup[chat_id]

                        name = config[chat_id].get("name", "")
                        city = config[chat_id].get("city", "")
                        send_message(chat_id,
                            f"✅ <b>Configurare completă!</b>\n\n"
                            f"👤 Nume: <b>{name}</b>\n"
                            f"⭐ Zodie: <b>{ZODIAC_RO[sign]}</b>\n"
                            f"📍 Oraș: <b>{city}</b>\n\n"
                            f"Vei primi briefing-ul zilnic automat! 🎉"
                        )

                # Confirmare oras dimineata
                elif data == "city_confirm":
                    send_message(chat_id, "✅ Perfect! Briefing-ul va folosi același oraș.")

                elif data == "city_change":
                    pending_setup[chat_id] = {"step": "change_city"}
                    send_message(chat_id, "📍 Scrie noul oraș:")

if __name__ == "__main__":
    run_bot()
