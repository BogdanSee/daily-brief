import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='config/.env')

API_KEY = os.getenv('OPENWEATHER_API_KEY')
LAT = os.getenv('DEFAULT_LAT', '44.4268')
LON = os.getenv('DEFAULT_LON', '26.1025')
CITY = os.getenv('DEFAULT_CITY', 'Bucharest')

def get_weather():
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={LAT}&lon={LON}&appid={API_KEY}"
            f"&units=metric&lang=ro"
        )

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return None, f"Eroare API meteo: {data.get('message', 'unknown')}"

        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']

        message = (
            f"🌤 <b>Vremea în {CITY}</b>\n"
            f"🌡 Temperatură: <b>{temp}°C</b> (se simte {feels_like}°C)\n"
            f"💧 Umiditate: {humidity}%\n"
            f"💨 Vânt: {wind_speed} m/s\n"
            f"☁️ {description.capitalize()}"
        )

        return message, None

    except Exception as e:
        return None, f"Excepție weather: {str(e)}"
