# logger.py (inside utils)
import csv
import os
from queue import Queue
from threading import Thread
from datetime import datetime
import joblib
import numpy as np

LOG_FILE = os.path.join(r"D:\PYTHON\aimllab\AUTOQOS_profiler\monitor\reports", "net_log.csv")
CLASSIFIER_PATH = os.path.join(r"D:\PYTHON\aimllab\AUTOQOS_profiler\qos\reports", "classifier_model.pkl")

log_queue = Queue()

# Load the trained classifier once
try:
    classifier = joblib.load(CLASSIFIER_PATH)
except Exception as e:
    print(f"[Logger] Could not load classifier: {e}")
    classifier = None

def human_readable(speed_bps):
    if speed_bps < 1024:
        return f"{speed_bps:.2f} Bps"
    elif speed_bps < 1024**2:
        return f"{speed_bps/1024:.2f} KBps"
    else:
        return f"{speed_bps/1024**2:.2f} MBps"

def extract_features_for_classification(upload_speed, download_speed, active_connections, top_protocol, process_info):
    # You can adjust this logic based on the features used during training
    proto_map = {
        "TCP": 0,
        "UDP": 1,
        "ICMP": 2,
        "HTTP": 3,
        "HTTPS": 4
    }
    protocol_encoded = proto_map.get(top_protocol.upper(), -1)
    process_len = len(process_info) if process_info else 0

    # Construct feature vector (same order as in training)
    return np.array([[upload_speed, download_speed, active_connections, protocol_encoded, process_len]])

def log_worker():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Upload Speed", "Download Speed",
                "Upload Total", "Download Total",
                "Active Connections", "Top Protocol", "Process Info", "Priority"
            ])
        while True:
            data = log_queue.get()
            if data is None:
                break

            # Predict priority
            try:
                if classifier:
                    upload_speed = float(data[1].split()[0]) if "Bps" in data[1] else 0
                    download_speed = float(data[2].split()[0]) if "Bps" in data[2] else 0
                    active_connections = int(data[5])
                    top_protocol = data[6]
                    process_info = data[7]

                    features = extract_features_for_classification(
                        upload_speed, download_speed,
                        active_connections, top_protocol, process_info
                    )
                    priority = int(classifier.predict(features)[0])
                else:
                    priority = -1  # fallback
            except Exception as e:
                print(f"[Logger] Classification failed: {e}")
                priority = -1

            data.append(priority)
            writer.writerow(data)
            file.flush()
            log_queue.task_done()

def start_logger():
    thread = Thread(target=log_worker, daemon=True)
    thread.start()
    return thread

def stop_logger():
    log_queue.put(None)

def log_to_csv(upload_speed, download_speed, upload_total, download_total, active_connections, top_protocol, process_info=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_queue.put([
        timestamp,
        human_readable(upload_speed),
        human_readable(download_speed),
        f"{upload_total / (1024**2):.2f} MB",
        f"{download_total / (1024**2):.2f} MB",
        active_connections,
        top_protocol,
        process_info or "N/A"
    ])

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_line = [timestamp, "EVENT", message]

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(event_line)
