# qos/policy_enforcer.py
import pydivert
import time
import psutil
from threading import Thread
import ctypes

def is_admin():
    """Checks for administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

THROTTLE_RULES = {}
connection_pid_map = {}

def update_connection_map():
    """Periodically updates the connection-to-PID map."""
    global connection_pid_map
    while True:
        temp_map = {}
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.pid and conn.status == psutil.CONN_ESTABLISHED and conn.raddr and conn.laddr:
                    # --- THIS IS THE FIX ---
                    # Create keys for both directions of the connection to ensure matches
                    key_outgoing = (conn.laddr.ip, conn.laddr.port, conn.raddr.ip, conn.raddr.port)
                    key_incoming = (conn.raddr.ip, conn.raddr.port, conn.laddr.ip, conn.laddr.port)
                    temp_map[key_outgoing] = conn.pid
                    temp_map[key_incoming] = conn.pid
                    # --- END OF FIX ---
            connection_pid_map = temp_map
        except psutil.AccessDenied:
            pass
        time.sleep(5)

def packet_throttler():
    """Captures and delays packets by looking up their PID from the connection map."""
    with pydivert.WinDivert("tcp or udp") as w:
        for packet in w:
            key = (packet.src_addr, packet.src_port, packet.dst_addr, packet.dst_port)
            packet_pid = connection_pid_map.get(key)

            if packet_pid in THROTTLE_RULES:
                limit = THROTTLE_RULES[packet_pid]
                if limit is not None:
                    delay = (len(packet.payload) * 8) / (limit * 8)
                    time.sleep(delay)
            w.send(packet)

def apply_qos_policy(pid, priority, priority_map):
    """Updates the throttle rules for a given PID."""
    global THROTTLE_RULES
    speed_mbps = priority_map.get(priority)
    if speed_mbps is None:
        if pid in THROTTLE_RULES:
            del THROTTLE_RULES[pid]
    else:
        speed_bytes_per_sec = (speed_mbps * 1024 * 1024) / 8
        THROTTLE_RULES[pid] = speed_bytes_per_sec

def start_enforcement_thread():
    """Starts the background threads for throttling and mapping."""
    if not is_admin():
        print("WARNING: Not running as admin. WinDivert may fail.")
    print("INFO: Starting connection mapper and WinDivert packet throttler...")
    map_updater_thread = Thread(target=update_connection_map, daemon=True)
    map_updater_thread.start()
    throttler_thread = Thread(target=packet_throttler, daemon=True)
    throttler_thread.start()

def clear_all_app_policies():
    """Clears all active throttling rules."""
    global THROTTLE_RULES
    THROTTLE_RULES.clear()
    print("INFO: All throttling rules cleared.")