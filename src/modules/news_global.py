import requests
from bs4 import BeautifulSoup

RSS_FEEDS_GLOBAL = [
    ("Digi24", "https://www.digi24.ro/rss/externe"),
]

SPORT_KEYWORDS = [
    "fotbal", "sport", "meci", "gol", "campionat", "liga", "tenis", "rugby",
    "handbal", "baschet", "atletism", "natatie", "formula 1", "motogp"
]

def get_news_global():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        all_articles = []
        seen = set()

        for source, url in RSS_FEEDS_GLOBAL:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")[:10]
                for item in items:
                    title = item.find("title")
                    if title:
                        text = title.get_text(strip=True)
                        # Sarim sport
                        if any(kw in text.lower() for kw in SPORT_KEYWORDS):
                            continue
                        # Deduplicare
                        key = text[:50].lower()
                        if key in seen:
                            continue
                        seen.add(key)
                        all_articles.append(f"[{source}] {text}")
            except Exception:
                continue

        if not all_articles:
            return None, "Nicio stire disponibila"

        lines = ["🌍 <b>Știri Internaționale</b>"]
        for article in all_articles[:5]:
            lines.append(f"• {article}")

        return "\n".join(lines), None

    except Exception as e:
        return None, f"Eroare news_global: {str(e)}"
