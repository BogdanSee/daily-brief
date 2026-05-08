import sys
import os
from datetime import datetime

sys.path.insert(0, 'src/modules')

from notifier import send_brief, send_alert
from weather import get_weather
from news import get_news

def build_header():
    now = datetime.now()
    zile = ['Luni','Marți','Miercuri','Joi','Vineri','Sâmbătă','Duminică']
    zi = zile[now.weekday()]
    data = now.strftime('%d %B %Y')
    ora = now.strftime('%H:%M')
    return f"🌅 <b>Bună dimineața, Bogdan!</b>\n📅 {zi}, {data} | ⏰ {ora}\n"

def run():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Pornesc Daily Brief...")

    errors = []
    message_parts = []

    # Header
    header = build_header()
    message_parts.append(header)

    # Vreme
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Preiau vremea...")
    weather_msg, weather_err = get_weather()
    if weather_msg:
        message_parts.append(weather_msg)
    else:
        errors.append(f"Weather: {weather_err}")
        message_parts.append("🌤 <i>Vremea indisponibilă momentan.</i>")

    message_parts.append("─────────────────────")

    # Stiri
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Preiau stirile...")
    news_msg, news_err = get_news()
    if news_msg:
        message_parts.append(news_msg)
    else:
        errors.append(f"News: {news_err}")
        message_parts.append("📰 <i>Știrile indisponibile momentan.</i>")

    # Asambleaza mesajul final
    final_message = "\n".join(message_parts)

    # Trimite pe Telegram
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Trimit pe Telegram...")
    result = send_brief(final_message)

    if result.get('ok'):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Mesaj trimis cu succes!")
    else:
        errors.append(f"Telegram send failed: {result}")

    # Trimite alerte daca au fost erori
    if errors:
        error_text = "\n".join(errors)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Trimit alerte erori...")
        send_alert(f"Erori în Daily Brief:\n{error_text}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Done.")

if __name__ == '__main__':
    run()
