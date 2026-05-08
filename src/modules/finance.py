import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

def get_finance():
    try:
        eur_url = "https://api.exchangerate-api.com/v4/latest/RON"
        eur_resp = requests.get(eur_url, timeout=10)
        eur_data = eur_resp.json()

        eur = round(1 / eur_data['rates']['EUR'], 4)
        usd = round(1 / eur_data['rates']['USD'], 4)

        crypto_url = (
            "https://api.coingecko.com/api/v3/simple/price"
            "?ids=bitcoin&vs_currencies=usd"
        )
        crypto_resp = requests.get(crypto_url, timeout=10)
        btc = crypto_resp.json()['bitcoin']['usd']

        message = (
            f"💱 <b>Curs valutar</b>\n"
            f"🇪🇺 EUR: <b>{eur} RON</b>\n"
            f"🇺🇸 USD: <b>{usd} RON</b>\n\n"
            f"₿ <b>Bitcoin: ${btc:,}</b>"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare finance: {str(e)}"
