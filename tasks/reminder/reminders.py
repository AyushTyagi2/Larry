import time
import threading

def set_reminder(minutes, message):
    def remind():
        print(f"Reminder set for {minutes} minute(s). I'll remind you soon!")
        time.sleep(minutes * 60)
        print(f"🔔 REMINDER: {message}")

    thread = threading.Thread(target=remind)
    thread.start()
