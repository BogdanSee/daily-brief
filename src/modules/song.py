import requests

def get_song():
    try:
        resp = requests.get(
            "https://itunes.apple.com/ro/rss/topsongs/limit=5/json",
            timeout=10
        )
        data = resp.json()
        entry = data['feed']['entry']

        # entry poate fi dict (1 rezultat) sau lista
        if isinstance(entry, dict):
            entry = [entry]

        song = entry[0]
        title = song['im:name']['label']
        artist = song['im:artist']['label']
        link = song['id']['label']

        message = (
            f"🎵 <b>Melodia zilei</b>\n"
            f"🎤 <b>{title}</b> — {artist}\n"
            f"🎧 <a href='{link}'>Ascultă pe Apple Music</a>"
        )
        return message, None

    except Exception as e:
        return None, f"Eroare song: {str(e)}"
