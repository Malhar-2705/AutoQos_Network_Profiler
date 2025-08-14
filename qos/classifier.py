# qos/classifier.py
CATEGORY_PRIORITY = {
    "Critical": 5, "Gaming": 4, "Work/Communication": 3,
    "Browse/Streaming": 2, "Background": 1, "Unclassified": 5
}
CRITICAL_APPS = {"svchost.exe", "lsass.exe", "wininit.exe", "services.exe", "System"}
GAMING_APPS = {"steam.exe", "valorant.exe", "FortniteClient-Win64-Shipping.exe"}
WORK_APPS = {"ms-teams.exe", "Zoom.exe", "slack.exe", "Discord.exe", "pycharm64.exe"}
Browse_STREAMING_APPS = {"chrome.exe", "msedge.exe", "firefox.exe", "Spotify.exe"}
BACKGROUND_APPS = {"OneDrive.exe", "Dropbox.exe"}

def classify_process(process_name):
    if process_name in CRITICAL_APPS: category = "Critical"
    elif process_name in GAMING_APPS: category = "Gaming"
    elif process_name in WORK_APPS: category = "Work/Communication"
    elif process_name in Browse_STREAMING_APPS: category = "Browse/Streaming"
    elif process_name in BACKGROUND_APPS: category = "Background"
    else: category = "Unclassified"
    priority = CATEGORY_PRIORITY.get(category, 5)
    return priority, category