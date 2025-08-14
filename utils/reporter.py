# utils/reporter.py
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time

log_data = []
last_net_io = {}


def log_stats(process_map, targets=('msedge.exe', 'Speedtest.exe')):
    """
    Finds target processes, gets their stats, and logs them.
    """
    global last_net_io
    timestamp = datetime.now()

    # --- NETWORK USAGE FIX ---
    # Calculate system-wide network usage first
    net_io = psutil.net_io_counters()
    total_bytes = net_io.bytes_sent + net_io.bytes_recv
    network_usage_mbps = 0
    if 'system' in last_net_io:
        last_bytes, last_time = last_net_io['system']
        interval = (timestamp - last_time).total_seconds()
        if interval > 0:
            bytes_per_second = (total_bytes - last_bytes) / interval
            network_usage_mbps = (bytes_per_second * 8) / (1024 * 1024)
    last_net_io['system'] = (total_bytes, timestamp)
    # --- END OF NETWORK FIX ---

    active_targets = {name for pid, name in process_map.items() if name in targets}

    for pid, name in process_map.items():
        if name in targets:
            try:
                p = psutil.Process(pid)
                cpu_usage = p.cpu_percent(interval=0.1) / psutil.cpu_count()
                memory_usage = p.memory_info().rss / (1024 * 1024)

                log_data.append({
                    "timestamp": timestamp,
                    "process_name": name,
                    # Assign the system-wide network usage to whichever target is active
                    "network_mbps": network_usage_mbps if name in active_targets else 0,
                    "cpu_usage": cpu_usage,
                    "memory_mb": memory_usage
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue


# The generate_report function remains the same.
def generate_report(targets=('msedge.exe', 'Speedtest.exe')):
    if not log_data:
        print("No data logged. Skipping report generation.")
        return

    df = pd.DataFrame(log_data)
    if df.empty:
        print("Logged data is empty. Skipping report generation.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 20), sharex=True)
    fig.suptitle('AUTOQOS Resource Usage Report', fontsize=20)

    metrics = {
        'network_mbps': ('Network Usage (Mbps)', axes[0]),
        'cpu_usage': ('CPU Usage (%)', axes[1]),
        'memory_mb': ('Memory Usage (MB)', axes[2])
    }

    for metric, (title, ax) in metrics.items():
        ax.set_title(title, fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.6)
        for app in targets:
            if app in df['process_name'].values:
                app_df = df[df['process_name'] == app]
                if not app_df.empty:
                    app_df[metric].plot(ax=ax, label=app, marker='o', linestyle='-')
        ax.legend()

    last_ax = axes[-1]
    last_ax.set_xlabel('Time', fontsize=12)
    last_ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(last_ax.get_xticklabels(), rotation=30, ha="right")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    report_filename = 'qos_report.png'
    plt.savefig(report_filename, dpi=100)
    print(f"\nReport generated and saved as '{report_filename}'")


def clear_log_data():
    global log_data, last_net_io
    log_data = []
    last_net_io = {}
    print("Log data cleared.")