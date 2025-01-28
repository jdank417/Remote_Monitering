import subprocess
import paramiko
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QInputDialog, QWidget, QMessageBox, QTextEdit, QSlider
)
from PyQt5.QtCore import Qt, QTimer

def ssh_connect(host, username, password):
    """Connect to the SSH server and return a client object, or None on failure."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)
        return client
    except paramiko.AuthenticationException:
        QMessageBox.critical(None, "Authentication Error", "Invalid username or password.")
        return None
    except Exception as e:
        QMessageBox.critical(None, "Connection Error", f"Failed to connect: {e}")
        return None

def ssh_run_command(client, command):
    """Run a command over SSH and return stdout or an error message on failure."""
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

class SSHApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote System Monitor")
        self.setGeometry(100, 100, 800, 600)

        # Default thresholds
        self.thresholds = {"cpu": 50, "memory": 50, "disk": 95}

        # Load or initialize machine list
        self.machines = []
        self.load_machines()

        # Keep track of silenced hosts (no future notifications)
        self.silenced_hosts = set()

        self.init_ui()

        # Auto-refresh timer: set to 5000 ms (5 seconds) or 10000 ms (10 seconds).
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_info)
        self.timer.start(5000)  # 5000 ms = 5 seconds

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Dank's Squash Pie Monitor", self)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #A41034;")
        main_layout.addWidget(self.title_label)

        # Output Area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        main_layout.addWidget(self.output_area)

        # Buttons
        self.add_button = QPushButton("Add Machine", self)
        self.add_button.clicked.connect(self.add_machine)
        main_layout.addWidget(self.add_button)

        self.refresh_button = QPushButton("Refresh Now", self)
        self.refresh_button.clicked.connect(self.refresh_info)
        main_layout.addWidget(self.refresh_button)

        # Threshold Sliders
        sliders_layout = QVBoxLayout()

        # CPU Threshold row
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

        # Memory Threshold row
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

        # Disk Threshold row
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
        self.update_output()

    def load_machines(self):
        """Load machine data from JSON file."""
        try:
            with open("../DSPM/src/DSPM/resources/machines.json", "r") as file:
                self.machines = json.load(file)
        except FileNotFoundError:
            self.machines = []
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Error", f"Error parsing machines.json: {e}")
            self.machines = []

    def save_machines(self):
        """Save machine data to JSON file."""
        try:
            with open("../DSPM/src/DSPM/resources/machines.json", "w") as file:
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
        self.update_output()

    def send_notification(self, machine, metric, value):
        """
        Show a warning dialog if usage is high.
        If the user chooses to silence notifications for this host,
        add the host to `silenced_hosts`.
        """
        host = machine["host"]
        notification_title = f"High {metric} Usage on {host}"
        notification_message = f"The {metric} usage on {host} is at {value:.2f}%.\n\nStop future notifications for this device?"

        # We add extra buttons so the user can silence further warnings:
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(notification_title)
        msg_box.setText(notification_message)
        # StandardButtons: "Ok" => keep notifying; "Cancel" => stop notifying
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.button(QMessageBox.Ok).setText("Keep Notifying")
        msg_box.button(QMessageBox.Cancel).setText("Stop Notifying")

        result = msg_box.exec_()
        if result == QMessageBox.Cancel:
            # Add the host to the silenced set
            self.silenced_hosts.add(host)

    def refresh_info(self):
        """
        Connect to each machine via SSH, fetch CPU/mem/disk usage,
        and compare against thresholds. Send notifications unless
        user has silenced that host.
        """
        if not self.machines:
            QMessageBox.information(self, "No Machines", "No machines to monitor. Add a machine first.")
            return

        output_text = ""
        for machine in self.machines:
            host = machine["host"]
            username = machine["username"]
            password = machine["password"]

            output_text += f"Machine: {host}\n"

            # Connect if not silenced
            ssh_client = ssh_connect(host, username, password)
            if not ssh_client:
                output_text += "  Failed to connect.\n\n"
                continue

            # Fetch system metrics
            cpu_usage_raw = ssh_run_command(ssh_client, "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'")
            mem_usage_raw = ssh_run_command(ssh_client, "free -m | awk '/Mem:/ {print $3/$2*100}'")
            disk_usage_raw = ssh_run_command(ssh_client, "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'")

            ssh_disconnect(ssh_client)

            # Convert to floats safely
            cpu_usage = safe_parse_float(cpu_usage_raw)
            memory_usage = safe_parse_float(mem_usage_raw)
            disk_usage = safe_parse_float(disk_usage_raw)

            # For text output, handle None (parsing failed)
            cpu_usage_text = f"{cpu_usage:.2f}%" if cpu_usage is not None else "N/A"
            mem_usage_text = f"{memory_usage:.2f}%" if memory_usage is not None else "N/A"
            disk_usage_text = f"{disk_usage:.2f}%" if disk_usage is not None else "N/A"

            output_text += f"  CPU Usage: {cpu_usage_text}\n"
            output_text += f"  Memory Usage: {mem_usage_text}\n"
            output_text += f"  Disk Usage: {disk_usage_text}\n\n"

            # Skip notifications if this host is silenced
            if host in self.silenced_hosts:
                continue

            # Check thresholds and send notifications
            if cpu_usage is not None and cpu_usage > self.thresholds["cpu"]:
                self.send_notification(machine, "CPU", cpu_usage)
            if memory_usage is not None and memory_usage > self.thresholds["memory"]:
                self.send_notification(machine, "Memory", memory_usage)
            if disk_usage is not None and disk_usage > self.thresholds["disk"]:
                self.send_notification(machine, "Disk", disk_usage)

        self.output_area.setPlainText(output_text)

    def update_output(self):
        """Show how many machines we have, and list their host & username."""
        if not self.machines:
            self.output_area.setPlainText("No machines are currently monitored.")
            return

        text = f"Monitoring {len(self.machines)} machine(s):\n"
        for i, machine in enumerate(self.machines, start=1):
            text += f"{i}. Host: {machine['host']}, User: {machine['username']}\n"
        self.output_area.setPlainText(text)

if __name__ == "__main__":
    app = QApplication([])
    window = SSHApp()
    window.show()
    app.exec()
