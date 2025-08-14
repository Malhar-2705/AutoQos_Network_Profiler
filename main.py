# main.py
import threading
import time
from utils.config import PRIORITY_SPEED_MAP
from qos.policy_enforcer import start_enforcement_thread, clear_all_app_policies, is_admin
from monitor.network_capture import automate_and_display
from utils.reporter import generate_report, clear_log_data  # Re-import reporter functions

manual_overrides = {}


def user_input_loop():
    """Handles user input for overrides and report commands."""
    global manual_overrides
    while True:
        try:
            command = input("Enter command ('process_name priority', 'report', 'clear_log', 'exit'): ").strip()

            if command.lower() == 'exit':
                break
            elif command.lower() == 'report':
                generate_report()
            elif command.lower() == 'clear_log':
                clear_log_data()
            else:
                parts = command.split()
                if len(parts) == 2:
                    process_name, priority_str = parts
                    try:
                        priority_int = int(priority_str)
                        if priority_int in PRIORITY_SPEED_MAP:
                            manual_overrides[process_name] = priority_int
                            print(f"Manual override for '{process_name}' set.")
                        else:
                            print("Invalid priority.")
                    except ValueError:
                        print("Priority must be a number.")
                elif command:
                    print("Invalid command format.")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    if not is_admin():
        print("ERROR: This script must be run as an Administrator.")
        input("Press Enter to exit.")
    else:
        print("Starting AUTOQOS Profiler...")
        start_enforcement_thread()

        stop_monitor = threading.Event()


        def monitor_thread_func():
            while not stop_monitor.is_set():
                automate_and_display(manual_overrides)
                time.sleep(15)


        monitor_thread = threading.Thread(target=monitor_thread_func, daemon=True)
        monitor_thread.start()

        try:
            user_input_loop()
        finally:
            print("\nShutting down...")
            stop_monitor.set()
            # Generate a final report on exit
            generate_report()
            clear_all_app_policies()
            print("Application stopped.")