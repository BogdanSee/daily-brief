import sys
sys.path.insert(0, 'src/modules')

from notifier import send_brief, send_alert

print("Testez Bot 1 - Brief...")
result1 = send_brief("✅ <b>Test reușit!</b>\nBot 1 funcționează corect.")
print(f"Răspuns Bot 1: {result1}")

print("\nTestez Bot 2 - Alert...")
result2 = send_alert("Test alert - totul e ok!")
print(f"Răspuns Bot 2: {result2}")
