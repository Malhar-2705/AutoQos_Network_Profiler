# monitor/process_mapper.py
import psutil

def get_running_processes():
    process_map = {}
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.pid and conn.status == psutil.CONN_ESTABLISHED:
                try:
                    proc = psutil.Process(conn.pid)
                    if conn.pid not in process_map:
                        process_map[conn.pid] = proc.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
    except psutil.AccessDenied:
        print("Warning: Access denied to network connections.")
    return process_map