import os
import shutil
import subprocess
import paramiko
import json
import socket
from datetime import datetime


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QInputDialog, QWidget, QMessageBox, QSlider, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal


# Determine base directories and paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPDATA_DIR = os.environ.get("APPDATA")
DSPM_DIR = os.path.join(APPDATA_DIR, "DSPM")
MACHINES_FILE = os.path.join(DSPM_DIR, "machines.json")


# Check if the DSPM directory exists. If not, create it and copy the built-in file.
if not os.path.exists(DSPM_DIR):
    os.makedirs(DSPM_DIR)
    source_machines_file = os.path.join(BASE_DIR, "resources", "machines.json")
    if os.path.exists(source_machines_file):
        shutil.copy(source_machines_file, MACHINES_FILE)
    else:
        # If the built-in file is missing, create an empty JSON file
        with open(MACHINES_FILE, "w") as file:
            json.dump([], file)


# No-op notification function (notifications removed)
def show_notification(title, message):
    pass


def ssh_connect(host, username, password, timeout=10):
    """
    Connect to the SSH server and return a client object.
    If a socket timeout occurs, return the string "timeout".
    Other errors return None.
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password, timeout=timeout)
        return client
    except socket.timeout:
        return "timeout"
    except paramiko.AuthenticationException:
        return None
    except Exception as e:
        return None


def ssh_run_command(client, command):
    """
    Run a command over SSH and return stdout or an error message on failure.
    """
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()


        if error:
            return f"Error: {error}"
        return output
    except Exception as e:
        return f"Error: Failed to execute command: {e}"


def ssh_disconnect(client):
    """Close the SSH connection."""
    client.close()


def safe_parse_float(value):
    """
    Safely parse a string to float. If it starts with 'Error' or fails to convert,
    returns None to indicate an error/unavailable metric.
    """
    if not value or value.startswith("Error"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


class SSHWorker(QThread):
    # Signal emits the host and the gathered machine info
    result_ready = pyqtSignal(str, str)


    def __init__(self, machine):
        super().__init__()
        self.machine = machine


    def run(self):
        host = self.machine["host"]
        username = self.machine["username"]
        password = self.machine["password"]


        ssh_client = ssh_connect(host, username, password, timeout=10)


        # If a timeout occurred, simply emit a result without notification.
        if ssh_client == "timeout":
            self.result_ready.emit(host, "Connection timeout")
            return
        elif not ssh_client:
            self.result_ready.emit(host, "Connection failed")
            return


        # Run commands to gather metrics
        cpu_usage_raw = ssh_run_command(ssh_client, "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'")
        mem_usage_raw = ssh_run_command(ssh_client, "free -m | awk '/Mem:/ {print $3/$2*100}'")
        disk_usage_raw = ssh_run_command(ssh_client, "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'")
        uptime_raw = ssh_run_command(ssh_client, "uptime -p")


        ssh_disconnect(ssh_client)


        cpu_usage = safe_parse_float(cpu_usage_raw)
        memory_usage = safe_parse_float(mem_usage_raw)
        disk_usage = safe_parse_float(disk_usage_raw)


        cpu_usage_text = f"CPU: {cpu_usage:.2f}%" if cpu_usage is not None else "CPU: N/A"
        memory_usage_text = f"Memory: {memory_usage:.2f}%" if memory_usage is not None else "Memory: N/A"
        disk_usage_text = f"Disk: {disk_usage:.2f}%" if disk_usage is not None else "Disk: N/A"
        uptime_text = uptime_raw if uptime_raw and not uptime_raw.startswith("Error") else "Uptime: N/A"


        # Add a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        machine_info = (
            f"{cpu_usage_text}\n"
            f"{memory_usage_text}\n"
            f"{disk_usage_text}\n"
            f"Uptime: {uptime_text}\n"
            f"Last Updated: {timestamp}"
        )
        self.result_ready.emit(host, machine_info)


class SSHApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSPM")
        self.setGeometry(100, 100, 800, 500)


        # Default thresholds
        self.thresholds = {"cpu": 50, "memory": 50, "disk": 95}


        # Load or initialize machine list
        self.machines = []
        self.load_machines()


        # Keep track of which machine is currently being updated
        self.current_machine_index = 0


        # Grid layout for machine info (store QLabel widgets)
        self.machine_labels = {}


        # Maintain a list of active worker threads
        self.workers = []


        self.init_ui()


        # Timer for sequential machine updates (auto-starts now)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_info)
        self.timer.start(3000)  # Refresh every 3 seconds


    def init_ui(self):
        main_layout = QVBoxLayout()


        # Title Label
        self.title_label = QLabel("Dank's Squash Pie Monitor", self)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #A41034;")
        main_layout.addWidget(self.title_label)


        # Grid Layout for Machine Info
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        main_layout.addLayout(self.grid_layout)


        # Buttons (Add Machine, Refresh Now)
        self.add_button = QPushButton("Add Machine", self)
        self.add_button.clicked.connect(self.add_machine)
        main_layout.addWidget(self.add_button)


        self.refresh_button = QPushButton("Refresh Now", self)
        self.refresh_button.clicked.connect(self.refresh_info)
        main_layout.addWidget(self.refresh_button)


        # Play/Pause Buttons
        play_pause_layout = QHBoxLayout()
        self.play_button = QPushButton("Play Refresh")
        self.play_button.clicked.connect(self.play_refresh)
        play_pause_layout.addWidget(self.play_button)


        self.pause_button = QPushButton("Pause Refresh")
        self.pause_button.clicked.connect(self.pause_refresh)
        play_pause_layout.addWidget(self.pause_button)


        # Edit Machines Button
        self.edit_button = QPushButton("Edit Machines")
        self.edit_button.clicked.connect(self.edit_machines_file)
        play_pause_layout.addWidget(self.edit_button)


        main_layout.addLayout(play_pause_layout)


        # Threshold Sliders
        sliders_layout = QVBoxLayout()


        # CPU Threshold
        cpu_row = QHBoxLayout()
        cpu_label = QLabel("CPU Threshold:")
        cpu_row.addWidget(cpu_label)


        self.cpu_slider = QSlider(Qt.Horizontal)
        self.cpu_slider.setRange(0, 100)
        self.cpu_slider.setValue(self.thresholds["cpu"])
        self.cpu_slider.valueChanged.connect(lambda val: self.update_threshold("cpu", val))
        cpu_row.addWidget(self.cpu_slider)


        self.cpu_value_label = QLabel(str(self.thresholds["cpu"]))
        cpu_row.addWidget(self.cpu_value_label)
        sliders_layout.addLayout(cpu_row)


        # Memory Threshold
        mem_row = QHBoxLayout()
        mem_label = QLabel("Memory Threshold:")
        mem_row.addWidget(mem_label)


        self.memory_slider = QSlider(Qt.Horizontal)
        self.memory_slider.setRange(0, 100)
        self.memory_slider.setValue(self.thresholds["memory"])
        self.memory_slider.valueChanged.connect(lambda val: self.update_threshold("memory", val))
        mem_row.addWidget(self.memory_slider)


        self.memory_value_label = QLabel(str(self.thresholds["memory"]))
        mem_row.addWidget(self.memory_value_label)
        sliders_layout.addLayout(mem_row)


        # Disk Threshold
        disk_row = QHBoxLayout()
        disk_label = QLabel("Disk Threshold:")
        disk_row.addWidget(disk_label)


        self.disk_slider = QSlider(Qt.Horizontal)
        self.disk_slider.setRange(0, 100)
        self.disk_slider.setValue(self.thresholds["disk"])
        self.disk_slider.valueChanged.connect(lambda val: self.update_threshold("disk", val))
        disk_row.addWidget(self.disk_slider)


        self.disk_value_label = QLabel(str(self.thresholds["disk"]))
        disk_row.addWidget(self.disk_value_label)
        sliders_layout.addLayout(disk_row)


        main_layout.addLayout(sliders_layout)


        # Main Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


        # Show initial machine count and list
        self.update_grid()


    def load_machines(self):
        """Load machine data from the machines.json file."""
        try:
            with open(MACHINES_FILE, "r") as file:
                self.machines = json.load(file)
        except FileNotFoundError:
            self.machines = []
            with open(MACHINES_FILE, "w") as file:
                json.dump(self.machines, file)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Error", f"Error parsing machines.json: {e}")
            self.machines = []


    def save_machines(self):
        """Save machine data to the machines.json file."""
        try:
            with open(MACHINES_FILE, "w") as file:
                json.dump(self.machines, file)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save machines to file: {e}")


    def update_threshold(self, metric, value):
        """Update the threshold dictionary when a slider changes, and update the label."""
        self.thresholds[metric] = value
        if metric == "cpu":
            self.cpu_value_label.setText(str(value))
        elif metric == "memory":
            self.memory_value_label.setText(str(value))
        elif metric == "disk":
            self.disk_value_label.setText(str(value))


    def add_machine(self):
        """Add a new machine to monitor (prompting the user for host/username/password)."""
        host, ok = QInputDialog.getText(self, "Add Machine", "Enter the IP address or hostname:")
        if not ok or not host:
            return


        username, ok = QInputDialog.getText(self, "Add Machine", "Enter the username:")
        if not ok or not username:
            return


        password, ok = QInputDialog.getText(self, "Add Machine", "Enter the password:", echo=QLineEdit.Password)
        if not ok or not password:
            return


        self.machines.append({"host": host, "username": username, "password": password})
        self.save_machines()
        self.update_grid()


    def refresh_info(self):
        """Update one machine at a time, cycling through the list using a worker thread."""
        if not self.machines:
            return


        # Get the current machine to update
        machine = self.machines[self.current_machine_index]
        host = machine["host"]


        # Create the worker thread for SSH operations
        worker = SSHWorker(machine)
        worker.result_ready.connect(self.handle_result)


        # Ensure the worker stays referenced until it is finished.
        self.workers.append(worker)
        worker.finished.connect(lambda: self.cleanup_worker(worker))
        worker.start()


        # Advance to the next machine for the next refresh cycle
        self.advance_to_next_machine()


    def cleanup_worker(self, worker):
        """Remove the worker from the list once finished."""
        if worker in self.workers:
            self.workers.remove(worker)


    def handle_result(self, host, machine_info):
        """Slot to handle the result from the SSHWorker."""
        self.update_machine_label(host, machine_info)


    def advance_to_next_machine(self):
        """Advance the current machine index and wrap around if needed."""
        self.current_machine_index = (self.current_machine_index + 1) % len(self.machines)


    def update_grid(self):
        """Update the grid layout with the current machines."""
        # Clear the grid layout first
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)


        self.machine_labels = {}
        for i in range(len(self.machines)):
            row = i // 5
            col = i % 5


            machine = self.machines[i]
            host = machine["host"]


            label = QLabel(f"Host: {host}\nStatus: Waiting...")
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label.setLineWidth(2)
            label.setAlignment(Qt.AlignTop)
            self.grid_layout.addWidget(label, row, col)
            self.machine_labels[host] = label


    def update_machine_label(self, host, info):
        """Update the QLabel for a specific machine with new information."""
        if host in self.machine_labels:
            self.machine_labels[host].setText(f"Host: {host}\n{info}")


    def pause_refresh(self):
        if self.timer.isActive():
            self.timer.stop()


    def play_refresh(self):
        if not self.timer.isActive():
            self.timer.start(3000)


    def edit_machines_file(self):
        """Open the machines.json file for editing and refresh the machine list if changes were made."""
        try:
            os.startfile(MACHINES_FILE)  # Windows: open with the default associated program
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")
            return


        # Ask the user if they changed the machine list
        response = QMessageBox.question(
            self,
            "Refresh Machine List",
            "Did you change the machine list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if response == QMessageBox.Yes:
            self.load_machines()
            self.update_grid()


def main():
    app = QApplication([])
    window = SSHApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()





