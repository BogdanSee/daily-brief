import requests
from datetime import datetime, timezone, timedelta

def get_sun():
    try:
        url = "https://api.sunrise-sunset.org/json?lat=44.4268&lng=26.1025&formatted=0"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        sunrise_utc = data['results']['sunrise']
        sunset_utc = data['results']['sunset']

        # Romania e UTC+3 vara (EEST), UTC+2 iarna (EET)
        # Detectam automat daca e ora de vara sau iarna
        now = datetime.now(timezone.utc)
        # Ora de vara in Romania: ultima duminica martie - ultima duminica octombrie
        year = now.year
        # Ultima duminica din martie
        last_sunday_march = max(
            datetime(year, 3, day, tzinfo=timezone.utc)
            for day in range(25, 32)
            if datetime(year, 3, day).weekday() == 6
        )
        # Ultima duminica din octombrie
        last_sunday_october = max(
            datetime(year, 10, day, tzinfo=timezone.utc)
            for day in range(25, 32)
            if datetime(year, 10, day).weekday() == 6
        )

        if last_sunday_march <= now < last_sunday_october:
            ro_tz = timezone(timedelta(hours=3))  # EEST (vara)
        else:
            ro_tz = timezone(timedelta(hours=2))  # EET (iarna)

        sunrise = datetime.fromisoformat(sunrise_utc).astimezone(ro_tz).strftime("%H:%M")
        sunset = datetime.fromisoformat(sunset_utc).astimezone(ro_tz).strftime("%H:%M")

        message = (
            f"🌅 <b>Răsărit / Apus</b>\n"
            f"🌄 Răsărit: <b>{sunrise}</b>\n"
            f"🌇 Apus: <b>{sunset}</b>"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare sun: {str(e)}"
