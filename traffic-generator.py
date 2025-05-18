# traffic_generator_with_qos.py

import requests
import time
import random
import string

TARGET_URL = "http://<IP-atau-domain-server>"  # Ganti dengan alamat server
NUM_REQUESTS = 50
PAYLOAD_SIZE_KB = 50  # Ukuran data yang dikirim (POST)
USE_POST = False  # Ganti True jika ingin POST dengan payload

def generate_payload(size_kb):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size_kb * 1024))

latencies = []
total_data_received = 0
success = 0
failed = 0

for i in range(NUM_REQUESTS):
    try:
        start = time.time()

        if USE_POST:
            payload = generate_payload(PAYLOAD_SIZE_KB)
            response = requests.post(TARGET_URL, data=payload)
        else:
            response = requests.get(TARGET_URL)

        end = time.time()

        latency = end - start
        latencies.append(latency)
        success += 1

        response_size = len(response.content)
        total_data_received += response_size

        print(f"[{i+1}] Status: {response.status_code}, Latency: {latency:.4f}s, Response size: {response_size} bytes")

    except Exception as e:
        print(f"[{i+1}] Request failed: {e}")
        failed += 1

    time.sleep(random.uniform(0.05, 0.2))  # Jeda antar request

# Perhitungan QoS
avg_latency = sum(latencies) / len(latencies) if latencies else 0
jitter = max(latencies) - min(latencies) if latencies else 0
throughput_kbps = (total_data_received / 1024) / sum(latencies) if latencies else 0

print("\n--- QoS Metrics ---")
print(f"Total Requests      : {NUM_REQUESTS}")
print(f"Successful Requests : {success}")
print(f"Failed Requests     : {failed}")
print(f"Average Latency     : {avg_latency:.4f} s")
print(f"Jitter              : {jitter:.4f} s")
print(f"Total Data Received : {total_data_received / 1024:.2f} KB")
print(f"Throughput          : {throughput_kbps:.2f} KB/s")
