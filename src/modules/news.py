import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='config/.env')

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"

def get_news():
    if not NEWS_API_KEY:
        return None, "NEWS_API_KEY lipsă din .env"

    try:
        # --- Stiri Romania ---
        ro_params = {
            "country": "ro",
            "pageSize": 3,
            "apiKey": NEWS_API_KEY
        }
        ro_resp = requests.get(BASE_URL, params=ro_params, timeout=10)
        ro_data = ro_resp.json()

        # --- Stiri Internationale ---
        intl_params = {
            "language": "en",
            "pageSize": 3,
            "apiKey": NEWS_API_KEY
        }
        intl_resp = requests.get(BASE_URL, params=intl_params, timeout=10)
        intl_data = intl_resp.json()

        # --- Construieste mesajul ---
        message_lines = ["📰 <b>ȘTIRI</b>"]

        # Romania
        message_lines.append("\n🇷🇴 <b>România:</b>")
        if ro_data.get("status") == "ok" and ro_data.get("articles"):
            for article in ro_data["articles"][:3]:
                title = article.get("title", "Fără titlu")
                url = article.get("url", "")
                message_lines.append(f"• <a href='{url}'>{title}</a>")
        else:
            message_lines.append("• <i>Indisponibil momentan</i>")

        # Internationale
        message_lines.append("\n🌍 <b>Internațional:</b>")
        if intl_data.get("status") == "ok" and intl_data.get("articles"):
            for article in intl_data["articles"][:3]:
                title = article.get("title", "Fără titlu")
                url = article.get("url", "")
                message_lines.append(f"• <a href='{url}'>{title}</a>")
        else:
            message_lines.append("• <i>Indisponibil momentan</i>")

        return "\n".join(message_lines), None

    except Exception as e:
        return None, str(e)
