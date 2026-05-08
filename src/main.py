import sys
import json
import requests
from datetime import datetime
from pathlib import Path
sys.path.insert(0, 'src/modules')

from notifier import send_brief, send_alert
from weather import get_weather, get_weather_tomorrow
from news import get_news
from news_global import get_news_global
from finance import get_finance
from sun import get_sun
from quote import get_quote
from history import get_history
from horoscope import get_horoscope
from orthodox import get_orthodox
from birthdays import get_birthdays
from traffic import get_traffic
from song import get_song
from uv import get_uv

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config/user_config.json"

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def add_module(label, func, parts, errors, *args):
    msg, err = func(*args) if args else func()
    if msg:
        parts.append(msg)
    else:
        errors.append(f"{label}: {err}")
        parts.append(f"<i>{label} indisponibil momentan.</i>")

def sep(parts):
    parts.append("─────────────────────")

def ask_city_confirmation(chat_id, city, token):
    keyboard = [[
        {"text": f"✅ Da, sunt în {city}", "callback_data": "city_confirm"},
        {"text": "🔄 Sunt în alt oraș", "callback_data": "city_change"}
    ]]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": f"📍 Ești tot în <b>{city}</b> azi?",
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": keyboard}
    }, timeout=10)

def run_morning(chat_id, user_data):
    now = datetime.now()
    zile = ['Luni','Marti','Miercuri','Joi','Vineri','Sambata','Duminica']
    zi = zile[now.weekday()]
    data = now.strftime('%d %B %Y')
    parts, errors = [], []

    name = user_data.get("name", "")
    parts.append(f"🌅 <b>Buna dimineata, {name}!</b>\n📅 {zi}, {data}\n")
    sep(parts)
    add_module("Vreme", get_weather, parts, errors)
    sep(parts)
    add_module("UV", get_uv, parts, errors)
    sep(parts)
    add_module("Calendar Ortodox", get_orthodox, parts, errors)
    sep(parts)
    add_module("Finance", get_finance, parts, errors)
    sep(parts)
    add_module("Rasarit/Apus", get_sun, parts, errors)
    sep(parts)
    add_module("Stiri Interne", get_news, parts, errors)
    sep(parts)
    add_module("Stiri Internationale", get_news_global, parts, errors)
    sep(parts)
    add_module("Istorie", get_history, parts, errors)
    sep(parts)
    add_module("Nasteri", get_birthdays, parts, errors)
    sep(parts)
    add_module("Horoscop", get_horoscope, parts, errors, chat_id)
    sep(parts)
    add_module("Melodia zilei", get_song, parts, errors)
    sep(parts)
    add_module("Citat", get_quote, parts, errors)

    return "\n".join(parts), errors

def run_noon(chat_id, user_data):
    now = datetime.now()
    parts, errors = [], []

    name = user_data.get("name", "")
    parts.append(f"☀️ <b>Buna ziua, {name}!</b>\n⏰ Briefing de pranz — {now.strftime('%H:%M')}\n")
    sep(parts)
    add_module("Vreme", get_weather, parts, errors)
    sep(parts)
    add_module("Stiri Interne", get_news, parts, errors)
    sep(parts)
    add_module("Stiri Internationale", get_news_global, parts, errors)
    sep(parts)

    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            timeout=10
        )
        btc = resp.json()['bitcoin']['usd']
        parts.append(f"₿ <b>Bitcoin acum:</b> ${btc:,}")
    except Exception as e:
        errors.append(f"BTC: {str(e)}")
        parts.append("<i>Bitcoin indisponibil momentan.</i>")

    sep(parts)
    add_module("Trafic", get_traffic, parts, errors)

    return "\n".join(parts), errors

def run_evening(chat_id, user_data):
    now = datetime.now()
    parts, errors = [], []

    name = user_data.get("name", "")
    parts.append(f"🌙 <b>Buna seara, {name}!</b>\n⏰ Briefing de seara — {now.strftime('%H:%M')}\n")
    sep(parts)
    add_module("Vreme azi", get_weather, parts, errors)
    sep(parts)
    add_module("Vreme maine", get_weather_tomorrow, parts, errors)
    sep(parts)
    add_module("Stiri Interne", get_news, parts, errors)
    sep(parts)
    add_module("Stiri Internationale", get_news_global, parts, errors)
    sep(parts)
    parts.append(
        f"📋 <b>Sumar zilei</b>\n"
        f"Ziua de azi a luat sfarsit. Reflecteaza la ce ai realizat si pregateste-te pentru maine! 💪"
    )
    sep(parts)
    parts.append("🌙 <i>Noapte buna si vise placute!</i> ✨")

    return "\n".join(parts), errors

def run(mode="morning"):
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Pornesc Daily Brief ({mode})...")

    config = load_config()
    if not config:
        print("Nu exista utilizatori in config!")
        return

    for chat_id, user_data in config.items():
        name = user_data.get("name", chat_id)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Trimit la {name}...")
        errors = []

        if mode == "morning":
            message, errors = run_morning(chat_id, user_data)
            result = send_brief(message, chat_id=chat_id)
            if TOKEN:
                ask_city_confirmation(chat_id, user_data.get("city", ""), TOKEN)
        elif mode == "noon":
            message, errors = run_noon(chat_id, user_data)
            result = send_brief(message, chat_id=chat_id)
        elif mode == "evening":
            message, errors = run_evening(chat_id, user_data)
            result = send_brief(message, chat_id=chat_id)
        else:
            print(f"Mod necunoscut: {mode}")
            return

        if result.get('ok'):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Trimis cu succes la {name}!")
        else:
            errors.append(f"Telegram send failed: {result}")

        if errors:
            send_alert(f"Erori Daily Brief ({mode}) pentru {name}:\n" + "\n".join(errors))

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Done.")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    run(mode)
