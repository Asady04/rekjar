# traffic_detector.py

import time

LOG_FILE = "/var/log/nginx/access.log"

def monitor_log():
    print("Monitoring traffic on NGINX access log...")
    with open(LOG_FILE, "r") as file:
        file.seek(0, 2)  # Go to end of file
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.2)
                continue
            print(f"[NGINX LOG] {line.strip()}")

if __name__ == "__main__":
    monitor_log()
