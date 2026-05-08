import requests
from bs4 import BeautifulSoup
from datetime import datetime

MONTHS_RO = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie",
    5: "mai", 6: "iunie", 7: "iulie", 8: "august",
    9: "septembrie", 10: "octombrie", 11: "noiembrie", 12: "decembrie"
}

def get_orthodox():
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        year = today.year
        month_name = MONTHS_RO[month]

        url = f"https://www.crestinortodox.ro/calendar-ortodox/{year}-{month_name}/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table", class_="calendar-listing")
        if not table:
            return None, "Tabel calendar negasit"

        for row in table.find_all("tr"):
            ths = row.find_all("th")
            if ths and ths[0].get_text(strip=True) == str(day):
                link = row.find("a")
                if link:
                    saint = link.get("title", link.get_text(strip=True))
                    # Curatam textul de eventuale sufixe (Ap., Ev., glas)
                    saint = saint.split(" - Ap.")[0].split(" - Ev.")[0].strip()
                    message = (
                        f"✝️ <b>Calendar Ortodox</b>\n"
                        f"👼 <b>{saint}</b>"
                    )
                    return message, None

        return f"✝️ <b>Calendar Ortodox</b>\n👼 <b>Zi fără sfânt marcat</b>", None

    except Exception as e:
        return None, f"Eroare orthodox: {str(e)}"
