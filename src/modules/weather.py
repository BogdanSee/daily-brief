import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

API_KEY = os.getenv('OPENWEATHER_API_KEY')
CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

def get_user_location(chat_id=None):
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            if chat_id and str(chat_id) in config:
                user = config[str(chat_id)]
            elif config:
                user = next(iter(config.values()))
            return (
                user.get("lat", 44.4268),
                user.get("lon", 26.1025),
                user.get("city", "București")
            )
    except Exception:
        pass
    return 44.4268, 26.1025, "București"

def get_clothing_recommendation(temp, description):
    desc = description.lower()
    if temp < 5:
        clothes = "🧥 Geacă groasă, fular și mănuși — e foarte frig!"
    elif temp < 12:
        clothes = "🧥 Geacă caldă recomandată."
    elif temp < 18:
        clothes = "🧣 Un hanorac sau o jachetă ușoară e suficientă."
    elif temp < 24:
        clothes = "👕 Vreme plăcută — tricou și un strat subțire."
    else:
        clothes = "☀️ Vreme caldă — îmbracă-te ușor!"

    if "ploaie" in desc or "rain" in desc or "drizzle" in desc:
        clothes += "\n☂️ Ia umbrela cu tine!"
    elif "furtuna" in desc or "storm" in desc or "thunderstorm" in desc:
        clothes += "\n⛈️ Furtună posibilă — evită deplasările inutile!"

    return clothes

def get_weather(chat_id=None):
    try:
        lat, lon, city = get_user_location(chat_id)

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
            f"&units=metric&lang=ro"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if resp.status_code != 200:
            return None, f"Eroare API meteo: {data.get('message', 'unknown')}"

        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        clouds = data['clouds']['all']
        rain = data.get('rain', {}).get('1h', 0)

        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
            f"&units=metric&lang=ro&cnt=8"
        )
        forecast_resp = requests.get(forecast_url, timeout=10)
        forecast_data = forecast_resp.json()

        temps_today = [item['main']['temp'] for item in forecast_data['list']]
        temp_min = round(min(temps_today), 1)
        temp_max = round(max(temps_today), 1)

        clothes = get_clothing_recommendation(temp, description)

        message = (
            f"🌤 <b>Vremea în {city}</b>\n"
            f"🌡 Acum: <b>{temp}°C</b> (se simte {feels_like}°C)\n"
            f"📊 Azi: min <b>{temp_min}°C</b> / max <b>{temp_max}°C</b>\n"
            f"☁️ Condiții: {description.capitalize()}\n"
            f"💧 Umiditate: {humidity}% | 💨 Vânt: {wind_speed} m/s | ☁️ Nori: {clouds}%\n"
        )
        if rain > 0:
            message += f"🌧 Precipitații ultima oră: {rain} mm\n"
        message += f"\n👗 <b>Recomandare:</b>\n{clothes}"

        return message, None

    except Exception as e:
        return None, f"Exceptie weather: {str(e)}"

def get_weather_tomorrow(chat_id=None):
    try:
        lat, lon, city = get_user_location(chat_id)

        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
            f"&units=metric&lang=ro&cnt=16"
        )
        resp = requests.get(forecast_url, timeout=10)
        data = resp.json()

        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow_items = [
            item for item in data['list']
            if item['dt_txt'].startswith(tomorrow)
        ]

        if not tomorrow_items:
            return None, "Nu sunt date pentru maine"

        temps = [item['main']['temp'] for item in tomorrow_items]
        temp_min = round(min(temps), 1)
        temp_max = round(max(temps), 1)
        descriptions = list(set([item['weather'][0]['description'] for item in tomorrow_items]))
        desc_text = ", ".join(descriptions[:2])

        rain_chance = any(
            "ploaie" in item['weather'][0]['description'].lower() or
            "rain" in item['weather'][0]['description'].lower()
            for item in tomorrow_items
        )

        message = (
            f"🌅 <b>Vremea de mâine în {city}</b>\n"
            f"🌡 Min: <b>{temp_min}°C</b> / Max: <b>{temp_max}°C</b>\n"
            f"☁️ Condiții: {desc_text.capitalize()}\n"
        )
        if rain_chance:
            message += "☂️ <b>Posibile precipitații mâine — ia umbrela!</b>"

        return message, None

    except Exception as e:
        return None, f"Exceptie weather tomorrow: {str(e)}"
