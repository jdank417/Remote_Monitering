# **DSPM (Dank's Squash Pie Monitor) Documentation**

## **Table of Contents**

1. Overview  
2. Features  
3. Prerequisites  
4. Installation  
5. Configuration  
6. Usage  
7. Application Structure  
8. Functions and Classes  
9. Error Handling  
10. Customization  
11. Troubleshooting  
12. License and Author

---

## **Overview**

**DSPM (Dank's Squash Pie Monitor)** is a Python-based application that monitors multiple Linux systems from a macOS environment. Leveraging SSH connections, the application periodically retrieves critical system metrics such as CPU usage, memory consumption, disk usage, and system uptime. The user-friendly graphical interface, built with PyQt5, allows administrators to add, edit, and monitor multiple machines seamlessly.

---

## **Features**

* **SSH Connectivity:** Securely connect to Linux machines using SSH to fetch system metrics.  
* **Real-time Monitoring:** Automatically refreshes system information at set intervals.  
* **Customizable Thresholds:** Users can set CPU, memory, and disk usage thresholds to receive alerts.  
* **Machine Management:** Add, edit, and manage multiple machines through the GUI.  
* **User-Friendly Interface:** Intuitive layout with real-time updates and easy navigation.  
* **Persistence:** Machine configurations are saved in a JSON file for persistence across sessions.  
* **Cross-Platform Deployment:** Designed for macOS but can be adapted for other operating systems.

---

## **Prerequisites**

Before installing and running DSPM, ensure the following prerequisites are met:

1. **Operating System:**  
   * macOS (tested on versions from Bigsur onwards).  
2. **Hardware:**  
   * Must be equipped with an M series CPU (arm).  
3. **Python:**  
   * Python 3.7 or higher is required (the app has been deployed to .pkg / .app, so this is only for further development or changes).  
4. **Python Libraries:**  
   * `paramiko` for SSH connections.  
   * `PyQt5` for the graphical user interface.  
5. **Permissions:**  
   * SSH access to the target Linux machines with valid credentials (dlsadmin VPN tunnel for ATHL Squash \- INC05756030).

---

## **Installation (for development)**

### **1\. Clone the Repository**

`git clone https://github.com/jdank417/Remote_Monitering.git`  
`cd dspm`

### **2\. Set Up a Virtual Environment (Optional but Recommended)**

`python3 -m venv venv`  
`source venv/bin/activate`

### **3\. Install Dependencies**

Ensure you have `pip` installed. Then, install the required Python packages:

`pip install paramiko PyQt5`

### **4\. Directory Structure**

Ensure the following directory structure is maintained:

`dspm/`  
`│`  
`├── dspm.py`  
`├── resources/`  
`│   └── machines.json`  
`└── README.md`

* **dspm.py:** The main application script.  
* **resources/machines.json:** Stores the list of machines to monitor. This file is created automatically if it doesn't exist.

---

## **Configuration**

### **1\. machines.json**

The `machines.json` file, located in the `resources` directory, holds the list of machines to be monitored. Each machine entry includes:

* **host:** IP address or hostname of the Linux machine.  
* **username:** SSH username.  
* **password:** SSH password.

**Example `machines.json`:**

`[`  
    `{`  
        `"host": "192.168.1.10",`  
        `"username": "admin",`  
        `"password": "password123"`  
    `},`  
    `{`  
        `"host": "192.168.1.11",`  
        `"username": "root",`  
        `"password": "securepass"`  
    `}`  
`]`

**Note:** The application provides a GUI to add and manage machines, automatically updating this file.

### **2\. Thresholds**

Thresholds for CPU, memory, and disk usage are set via sliders in the application. Default thresholds are:

* **CPU:** 50%  
* **Memory:** 50%  
* **Disk:** 95%

These can be adjusted in the application interface to suit monitoring needs.

---

## **Usage**

### **1\. Launching the Application**

Navigate to the project directory and run:

`python dspm.py`

The GUI window titled "DSPM" will appear, displaying the monitoring dashboard.

### **2\. Adding a Machine**

1. Click the **"Add Machine"** button.  
2. Enter the **IP address or hostname** of the Linux machine.  
3. Provide the **username** and **password** for SSH access.  
4. Click **"OK"** to add the machine. The machine will appear in the grid layout.

### **3\. Refreshing Information**

* **Automatic Refresh:** The application automatically refreshes machine information every 3 seconds.  
* **Manual Refresh:** Click the **"Refresh Now"** button to manually trigger an update.  
* **Play/Pause Refresh:** Use the **"Play Refresh"** and **"Pause Refresh"** buttons to control automatic updates.

### **4\. Editing Machines**

* Click the **"Edit Machines"** button to open the `machines.json` file in the default editor.  
* Modify the machine entries as needed and save the file.

### **5\. Setting Thresholds**

* Adjust the **CPU**, **Memory**, and **Disk** sliders to set custom thresholds.  
* The numerical value next to each slider displays the current threshold percentage.

### **6\. Monitoring Dashboard**

Each machine is represented by a label in the grid layout, displaying:

* **Host:** IP or hostname.  
* **CPU Usage:** Current CPU usage percentage.  
* **Memory Usage:** Current memory usage percentage.  
* **Disk Usage:** Current disk usage percentage.  
* **Uptime:** System uptime.  
* **Last Updated:** Timestamp of the last refresh.

---

## **Application Structure**

### **1\. File Overview**

* **dspm.py:** Main application script containing all functionalities.  
* **resources/machines.json:** JSON file storing machine configurations.

### **2\. Libraries Used**

* **subprocess:** To interact with system-level commands.  
* **paramiko:** For establishing SSH connections and executing commands on remote machines.  
* **json:** For reading and writing machine configurations.  
* **Os:** For file and directory operations.  
* **datetime:** For timestamping updates.  
* **PyQt5:** For building the graphical user interface.

---

## **Functions and Classes**

### **1\. Functions**

#### **`ssh_connect(host, username, password)`**

* **Description:** Establishes an SSH connection to the specified host using the provided credentials.  
* **Parameters:**  
  * `host` (str): IP address or hostname.  
  * `username` (str): SSH username.  
  * `password` (str): SSH password.  
* **Returns:** `paramiko.SSHClient` object if successful, `None` otherwise.  
* **Error Handling:** Displays a critical message box if authentication fails or connection issues occur.

#### **`ssh_run_command(client, command)`**

* **Description:** Executes a shell command over an established SSH connection.  
* **Parameters:**  
  * `client` (`paramiko.SSHClient`): Active SSH client.  
  * `command` (str): Command to execute.  
* **Returns:** Standard output as a string if successful; error message prefixed with "Error:" otherwise.

#### **`ssh_disconnect(client)`**

* **Description:** Closes the SSH connection.  
* **Parameters:**  
  * `client` (`paramiko.SSHClient`): Active SSH client.

#### **`safe_parse_float(value)`**

* **Description:** Safely parses a string to a float. Returns `None` if parsing fails or the value starts with "Error".  
* **Parameters:**  
  * `value` (str): The string to parse.  
* **Returns:** `float` or `None`.

### **2\. Classes**

#### **`SSHApp(QMainWindow)`**

* **Description:** Main application class inheriting from `QMainWindow`. Manages the GUI and monitoring functionalities.  
* **Attributes:**  
  * `thresholds` (dict): Stores threshold values for CPU, memory, and disk.  
  * `machines` (list): List of machine dictionaries loaded from `machines.json`.  
  * `silenced_hosts` (set): Set of hosts for which notifications are silenced.  
  * `current_machine_index` (int): Index of the machine currently being updated.  
  * `machine_labels` (dict): Maps hostnames to their respective `QLabel` widgets.  
  * `timer` (`QTimer`): Timer object for periodic updates.  
* **Methods:**  
  * `__init__()`: Initializes the application, loads machines, sets up the UI, and starts the timer.  
  * `init_ui()`: Constructs the GUI layout, including labels, buttons, sliders, and grid layout for machine info.  
  * `load_machines()`: Loads machine configurations from `machines.json`. Creates the file if it doesn't exist.  
  * `save_machines()`: Saves the current list of machines to `machines.json`.  
  * `update_threshold(metric, value)`: Updates threshold values and corresponding labels when sliders are adjusted.  
  * `add_machine()`: Prompts the user to input machine details and adds it to the monitoring list.  
  * `refresh_info()`: Retrieves system metrics for the current machine and updates the GUI.  
  * `advance_to_next_machine()`: Moves to the next machine in the list for sequential updates.  
  * `update_grid()`: Updates the grid layout with the current list of machines.  
  * `update_machine_label(host, info)`: Updates the `QLabel` for a specific host with new information.  
  * `pause_refresh()`: Stops the automatic refresh timer.  
  * `play_refresh()`: Starts the automatic refresh timer.  
  * `edit_machines_file()`: Opens the `machines.json` file in the default editor for manual editing.

#### **`main()`**

* **Description:** Entry point of the application. Initializes the `QApplication`, creates an instance of `SSHApp`, and starts the event loop.

---

## **Error Handling**

The application includes comprehensive error handling to ensure smooth operation and provide informative feedback to the user.

### **1\. SSH Connection Errors**

* **Authentication Failure:** If the provided SSH credentials are incorrect, a critical message box is displayed: "Invalid username or password."  
* **Connection Issues:** For other SSH connection failures (e.g., network issues, host unreachable), a critical message box displays the specific error.

### **2\. JSON Parsing Errors**

* If `machines.json` contains invalid JSON, a critical message box alerts the user: "Error parsing machines.json: \[error details\]."

### **3\. File Operation Errors**

* **Saving Machines:** If saving to `machines.json` fails, a critical message box notifies the user: "Could not save machines to file: \[error details\]."  
* **Editing Machines File:** If the application fails to open `machines.json` for editing, a critical message box displays: "Could not open file: \[error details\]."

### **4\. Command Execution Errors**

* If executing a command over SSH fails, the application displays "Error: \[error details\]" in the machine's label.

---

## **Customization**

### **1\. Adjusting Refresh Interval**

By default, the application refreshes machine information every 3 seconds. To change this:

Locate the following line in `dspm.py`:

`self.timer.start(3000)  # 3000 milliseconds = 3 seconds`

1. 

Modify the value `3000` to the desired interval in milliseconds. For example, for a 5-second interval:

`self.timer.start(5000)`

2. 

### **2\. Changing the GUI Appearance**

The GUI's appearance can be customized by modifying the PyQt5 widgets' properties, such as stylesheets, fonts, and layouts. For example, to change the title label's color or font size:

`self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #A41034;")`

Adjust the CSS properties as desired.

### **3\. Extending Monitored Metrics**

To monitor additional system metrics:

1. **Modify SSH Commands:**  
   Add new SSH commands in the `refresh_info` method to retrieve desired metrics.  
2. **Update `machine_info` String:**  
   Incorporate the new metrics into the `machine_info` string to display them in the GUI.  
3. **Update Thresholds (If Applicable):**  
   If the new metric requires threshold settings, add corresponding sliders and update the `thresholds` dictionary.

### **4\. Supporting Different Operating Systems**

While the application is designed for macOS, adjustments can be made to support other operating systems:

**Editing Machines File:**  
Modify the `edit_machines_file` method to use the appropriate command for opening files on the target OS.

`subprocess.call(["open", MACHINES_FILE])  # macOS`  
`# For Windows:`  
`subprocess.call(["start", MACHINES_FILE], shell=True)`  
`# For Linux:`  
`subprocess.call(["xdg-open", MACHINES_FILE])`

*   
* **File Paths:**  
  Ensure that file paths are compatible with the target OS, using `os.path` methods for cross-platform compatibility.

---

## **Troubleshooting**

### **1\. Unable to Connect to SSH**

* **Incorrect Credentials:** Verify that the username and password are correct.  
* **Network Issues:** Ensure that the target machine is reachable over the network.  
* **SSH Service:** Confirm that the SSH service is running on the target machine.  
* **Firewall Settings:** Check if firewalls are blocking SSH connections.

### **2\. machines.json Not Loading Correctly**

* **Invalid JSON Format:** Ensure that `machines.json` contains valid JSON. Use a JSON validator to check syntax.  
* **File Permissions:** Verify that the application has read/write permissions for `machines.json`.

### **3\. Application Crashes or Freezes**

* **Dependency Issues:** Ensure all required Python libraries are installed and up to date.  
* **Python Version:** Confirm that you are using a compatible Python version (3.7+).  
* **Resource Limitations:** Monitor system resources to ensure the application isn't consuming excessive memory or CPU.

### **4\. Sliders Not Updating Thresholds**

* **Signal Connections:** Ensure that the slider `valueChanged` signals are correctly connected to the `update_threshold` method.  
* **GUI Refresh:** If changes aren't reflected, try restarting the application.

### **5\. machines.json Not Opening in Editor**

* **Default Application:** Ensure that the system has a default application set for opening `.json` files.  
* **Command Errors:** Check if the `open` command is correctly specified for your operating system.

---

## **License and Author**

* **Author:** Jason Dank  
* **Creation Date:** January 27, 2025

---

## **Contact and Support**

For issues, feature requests, or contributions, please contact:

* **Email:** jason\_dank@harvard.edu  
  
