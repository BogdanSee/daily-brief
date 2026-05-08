import requests
from datetime import datetime

def get_birthdays():
    try:
        today = datetime.now()
        month = today.month
        day = today.day

        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/births/{month}/{day}"
        headers = {"User-Agent": "DailyBriefBot/1.0 (personal project; bogdan@example.com)"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()

        births = data.get("births", [])[:4]

        lines = ["🎂 <b>Personalități născute azi</b>"]
        for person in births:
            year = person.get("year", "?")
            text = person.get("text", "")
            lines.append(f"• <b>{year}</b> — {text}")

        message = "\n".join(lines)
        return message, None

    except Exception as e:
        return None, f"Eroare birthdays: {str(e)}"
