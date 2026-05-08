import requests

def get_sun():
    try:
        # Coordonate Bucuresti
        url = "https://api.sunrise-sunset.org/json?lat=44.4268&lng=26.1025&formatted=0"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        sunrise_utc = data['results']['sunrise']
        sunset_utc = data['results']['sunset']

        # Convertim din UTC+0 in UTC+3 (Romania vara) / UTC+2 (iarna)
        from datetime import datetime, timezone, timedelta
        import time

        # Detectam automat offset-ul local
        offset_sec = -time.timezone if time.daylight == 0 else -time.altzone
        local_tz = timezone(timedelta(seconds=offset_sec))

        sunrise = datetime.fromisoformat(sunrise_utc).astimezone(local_tz).strftime("%H:%M")
        sunset = datetime.fromisoformat(sunset_utc).astimezone(local_tz).strftime("%H:%M")

        message = (
            f"🌅 <b>Răsărit / Apus</b>\n"
            f"🌄 Răsărit: <b>{sunrise}</b>\n"
            f"🌇 Apus: <b>{sunset}</b>"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare sun: {str(e)}"
