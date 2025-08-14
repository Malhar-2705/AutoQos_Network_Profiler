AutoQOS Profiler: A Real-Time, Endpoint-Level QoS Engine
AutoQOS Profiler is a lightweight, terminal-based Python application designed to monitor and control the network bandwidth of individual applications on a Windows machine. It provides a hybrid control model that combines automatic, rule-based process classification with a real-time command-line interface for manual overrides, ensuring granular control over network resources.

The core of the application uses low-level packet interception via pydivert to guarantee that bandwidth limits are enforced, making it a powerful tool for developers, network enthusiasts, and users in resource-constrained environments.

✨ Key Features
Automatic Process Classification: Intelligently categorizes running applications (e.g., Critical, Gaming, Work, Browsing) and assigns them a predefined QoS priority.

Guaranteed Bandwidth Throttling: Utilizes pydivert for direct packet interception and delay, ensuring that speed limits are physically enforced and cannot be bypassed by applications.

Real-Time Manual Override: An interactive command-line interface allows the user to instantly set a custom priority for any application or revert it to its automatic classification.

Resource Logging & Reporting: Monitors the CPU and Memory usage of specified applications and generates a comparative performance graph on demand using matplotlib and pandas.

Lightweight & Efficient: Designed to run as a low-overhead background service with a minimal memory footprint (typically under 200 MB).

⚙️ How It Works
The application operates on a multithreaded architecture to ensure a responsive, non-blocking experience.

Main Thread (User Input): The main thread is dedicated to the user input loop, waiting for commands to override priorities or generate reports.

Monitor Thread (Backend Logic): A background thread runs a continuous loop that:

Uses psutil to discover all processes with active network connections.

Passes the process list to the classifier to determine the appropriate priority for each application.

Checks for any manual overrides set by the user.

Instructs the enforcement engine to apply the final priority.

Logs resource statistics for target applications.

Enforcement Thread (Packet Throttling): A dedicated thread, powered by pydivert, intercepts all outbound network packets. It looks up the Process ID (PID) of each packet's owner and, if a throttle rule exists for that PID, it actively delays the packet to enforce the specified speed limit.

AUTOQOS_profiler/

├── 📁 monitor/

│   ├── 📄 network_capture.py  # Main monitoring and display loop

│   └── 📄 process_mapper.py   # Finds active network processes

│

├── 📁 qos/

│   ├── 📄 classifier.py       # Automatic process classification rules

│   └── 📄 policy_enforcer.py  # Applies QoS rules via WinDivert

│
├── 📁 utils/

│   ├── 📄 config.py           # Holds hardcoded configuration

│   └── 📄 reporter.py         # Handles logging and graph generation

│

├── 📄 main.py                 # Main application entry point

└── 🐍 .venv/                  # Python virtual environment

🚀 Setup and Installation
Prerequisites
Windows 10 or 11

Python 3.10+

A Python virtual environment (.venv)

Installation
Clone the repository:

git clone <your-repo-url>
cd AUTOQOS_profiler

Create and activate a virtual environment:

python -m venv .venv
.venv\Scripts\activate

Install the required packages:

pip install psutil pydivert matplotlib pandas

▶️ How to Run
This application requires administrator privileges to intercept network packets.

Open Command Prompt as Administrator.

Navigate to the project directory:

D:
cd D:\PYTHON\aimllab\AUTOQOS_profiler

Activate the virtual environment:

.venv\Scripts\activate

Run the main script:

python main.py

⌨️ How to Use
The application will automatically start monitoring and display a list of processes. You can press Enter to access the command prompt.

Set a Manual Priority: Enter the process name, press Enter, then enter the priority level (0-5).

Enter process to override (or 'exit'): msedge.exe
Enter priority for 'msedge.exe': 1

Remove a Manual Override: Enter the process name, then type DEFAULT.

Enter process to override (or 'exit'): msedge.exe
Enter priority for 'msedge.exe': DEFAULT

Generate a Performance Report:

Enter command (...): report

This will save a qos_report.png file in the project directory.

Clear Log Data:

Enter command (...): clear_log

Use this before starting a new test to ensure the report is clean.

Exit the Application:

Enter command (...): exit

🔮 Future Work
Flask API Backend: Transition the core logic to a headless service with a Flask API for control and data retrieval.

Web-Based Frontend: Develop a simple web dashboard that communicates with the Flask API to provide a graphical user interface.

Lightweight ML Classifier: Augment the rule-based classifier with a lightweight machine learning model to intelligently handle unknown processes.
