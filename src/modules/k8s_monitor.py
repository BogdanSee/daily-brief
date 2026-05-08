import os
import subprocess
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[2] / "config/.env")

TOKEN = os.getenv("TELEGRAM_ALERT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID")

def send_alert(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }, timeout=10)

def check_pods():
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "--all-namespaces", "-o", "wide"],
            capture_output=True, text=True, timeout=30
        )
        lines = result.stdout.strip().split("\n")
        problems = []

        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) < 4:
                continue
            namespace = parts[0]
            name = parts[1]
            ready = parts[2]
            status = parts[3]
            restarts = parts[4] if len(parts) > 4 else "0"

            # Detectam probleme
            if status in ["CrashLoopBackOff", "Error", "OOMKilled", "Evicted"]:
                problems.append(f"❌ <b>{name}</b> — Status: {status} (restarts: {restarts})")
            elif status == "Pending" :
                problems.append(f"⏳ <b>{name}</b> — Status: Pending")
            elif "/" in ready:
                current, total = ready.split("/")
                if current != total and status == "Running":
                    problems.append(f"⚠️ <b>{name}</b> — Ready: {ready}")

        if problems:
            msg = "🚨 <b>Alertă Kubernetes!</b>\n\n" + "\n".join(problems)
            send_alert(msg)
            print(f"Alerte trimise: {len(problems)}")
        else:
            print("✅ Toți podii sunt sănătoși.")

    except Exception as e:
        send_alert(f"❌ <b>Eroare monitor K8s:</b> {str(e)}")

if __name__ == "__main__":
    check_pods()
