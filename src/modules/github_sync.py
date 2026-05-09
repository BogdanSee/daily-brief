import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
from base64 import b64encode
from nacl import encoding, public

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN_SYNC")
GITHUB_REPO = "BogdanSee/daily-brief"
CONFIG_FILE = Path(__file__).resolve().parents[2] / "config/user_config.json"

def encrypt_secret(public_key_str, secret_value):
    public_key = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def get_public_key():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.json()

def update_github_secret(config):
    try:
        # Obtinem cheia publica
        key_data = get_public_key()
        key_id = key_data["key_id"]
        public_key = key_data["key"]

        # Encryptam secretul
        secret_value = json.dumps(config, ensure_ascii=False)
        encrypted = encrypt_secret(public_key, secret_value)

        # Actualizam secretul
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/USER_CONFIG"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "encrypted_value": encrypted,
            "key_id": key_id
        }
        resp = requests.put(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in [201, 204]:
            print(f"[GitHub] Secret USER_CONFIG actualizat cu succes!")
            return True
        else:
            print(f"[GitHub] Eroare: {resp.status_code} - {resp.text}")
            return False

    except Exception as e:
        print(f"[GitHub] Exceptie: {str(e)}")
        return False

def sync_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return update_github_secret(config)
    return False
