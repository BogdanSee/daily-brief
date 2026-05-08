import requests
from datetime import datetime
from deep_translator import GoogleTranslator

def get_history():
    try:
        today = datetime.now()
        month = today.month
        day = today.day

        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        headers = {"User-Agent": "DailyBriefBot/1.0 (personal project; bogdan@example.com)"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()

        events = data['events'][:3]

        lines = ["📅 <b>Ce s-a întâmplat azi în istorie</b>"]
        for event in events:
            year = event['year']
            text_en = event['text']
            text_ro = GoogleTranslator(source='en', target='ro').translate(text_en)
            lines.append(f"• <b>{year}</b> — {text_ro}")

        return "\n".join(lines), None

    except Exception as e:
        return None, f"Eroare history: {str(e)}"
