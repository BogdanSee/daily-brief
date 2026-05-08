import requests
import json
from pathlib import Path
from deep_translator import GoogleTranslator

CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

ZODIAC_RO = {
    "aries": "Berbec", "taurus": "Taur", "gemini": "Gemeni",
    "cancer": "Rac", "leo": "Leu", "virgo": "Fecioară",
    "libra": "Balanță", "scorpio": "Scorpion", "sagittarius": "Săgetător",
    "capricorn": "Capricorn", "aquarius": "Vărsător", "pisces": "Pești"
}

def get_horoscope(chat_id=None):
    try:
        sign = "scorpio"
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            if chat_id and str(chat_id) in config:
                sign = config[str(chat_id)].get("zodiac", "scorpio")
            elif config:
                first_user = next(iter(config.values()))
                sign = first_user.get("zodiac", "scorpio")

        url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=TODAY"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        horoscope_en = data['data']['horoscope']
        horoscope_ro = GoogleTranslator(source='en', target='ro').translate(horoscope_en)
        sign_ro = ZODIAC_RO.get(sign, sign.capitalize())

        message = (
            f"⭐ <b>Horoscop {sign_ro}</b>\n"
            f"{horoscope_ro}"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare horoscope: {str(e)}"
