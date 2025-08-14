# monitor/network_capture.py
import os
from monitor.process_mapper import get_running_processes
from qos.policy_enforcer import apply_qos_policy
from qos.classifier import classify_process
from utils.config import PRIORITY_SPEED_MAP
from utils.reporter import log_stats  # Import the new logging function


def automate_and_display(overrides):
    os.system('cls' if os.name == 'nt' else 'clear')
    process_map = get_running_processes()  # Gets {pid: name}

    # --- THIS IS THE NEW LINE ---
    log_stats(process_map)  # Log stats for target processes
    # --- END OF NEW LINE ---

    print("--- AUTOQOS PROFILER (Terminal Mode) ---")
    print(f"{'Process Name':<30} | {'Priority':<10} | {'Category':<25} | {'Speed Limit'}")
    print("-" * 90)

    if not process_map:
        print("No running processes with network activity found.")
        return

    for pid, process_name in sorted(process_map.items(), key=lambda item: item[1]):
        category_str = ""
        if process_name in overrides:
            priority = overrides[process_name]
            category_str = "Manual Override"
        else:
            priority, category_str = classify_process(process_name)

        apply_qos_policy(pid, priority, PRIORITY_SPEED_MAP)

        speed_limit = PRIORITY_SPEED_MAP.get(priority)
        limit_str = f"{speed_limit} Mbps" if speed_limit is not None else "Unlimited"
        print(f"{process_name:<30} | {priority:<10} | {category_str:<25} | {limit_str}")

    print("\nPress Enter to access command prompt to set an override...")