import requests

def get_quote():
    try:
        url = "https://zenquotes.io/api/today"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        text = data[0]['q']
        author = data[0]['a']

        message = (
            f"\U0001f4ac <b>Citatul zilei</b>\n"
            f"<i>\"{text}\"</i>\n"
            f"- <b>{author}</b>"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare quote: {str(e)}"
