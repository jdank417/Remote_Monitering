import subprocess
import paramiko
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, QInputDialog, QWidget, QMessageBox, QTextEdit)


def ssh_connect(host, username, password):
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
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if error:
            return f"Error: {error}"
        return output.strip()
    except Exception as e:
        return f"Failed to execute command: {e}"


def ssh_disconnect(client):
    client.close()


class SSHApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote System Monitor")
        self.setGeometry(100, 100, 800, 600)

        self.machines = []
        self.thresholds = {"cpu": 10, "memory": 10, "disk": 90}  # Alert thresholds

        self.load_machines()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Remote System Monitor", self)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #A41034;")
        layout.addWidget(self.title_label)

        # Output Area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Buttons
        self.add_button = QPushButton("Add Machine", self)
        self.add_button.clicked.connect(self.add_machine)
        layout.addWidget(self.add_button)

        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_info)
        layout.addWidget(self.refresh_button)

        # Main Widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_machine(self):
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

    def save_machines(self):
        with open("../DSPM/src/DSPM/resources/machines.json", "w") as file:
            json.dump(self.machines, file)

    def load_machines(self):
        try:
            with open("../DSPM/src/DSPM/resources/machines.json", "r") as file:
                self.machines = json.load(file)
        except FileNotFoundError:
            self.machines = []

    def send_notification(self, machine, metric, value):
        notification_title = f"High {metric} Usage on {machine['host']}"
        notification_message = f"The {metric} usage on {machine['host']} is at {value}%"
        QMessageBox.warning(self, notification_title, notification_message)

    def refresh_info(self):
        if not self.machines:
            QMessageBox.information(self, "No Machines", "No machines to monitor. Add a machine first.")
            return

        output_text = ""
        for machine in self.machines:
            host = machine["host"]
            username = machine["username"]
            password = machine["password"]

            output_text += f"Machine: {host}\n"

            ssh_client = ssh_connect(host, username, password)
            if not ssh_client:
                output_text += "  Failed to connect.\n\n"
                continue

            # Fetch system metrics
            cpu_usage = ssh_run_command(ssh_client, "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'").strip()
            memory_usage = ssh_run_command(ssh_client, "free -m | awk '/Mem:/ {print $3/$2*100}'").strip()
            disk_usage = ssh_run_command(ssh_client, "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'").strip()

            try:
                cpu_usage = float(cpu_usage) if cpu_usage else 0.0
                memory_usage = float(memory_usage) if memory_usage else 0.0
                disk_usage = float(disk_usage) if disk_usage else 0.0
            except ValueError:
                cpu_usage, memory_usage, disk_usage = 0.0, 0.0, 0.0

            # Check thresholds and send notifications
            if cpu_usage > self.thresholds["cpu"]:
                self.send_notification(machine, "CPU", cpu_usage)
            if memory_usage > self.thresholds["memory"]:
                self.send_notification(machine, "Memory", memory_usage)
            if disk_usage > self.thresholds["disk"]:
                self.send_notification(machine, "Disk", disk_usage)

            output_text += f"  CPU Usage: {cpu_usage:.2f}%\n"
            output_text += f"  Memory Usage: {memory_usage:.2f}%\n"
            output_text += f"  Disk Usage: {disk_usage:.2f}%\n\n"

            ssh_disconnect(ssh_client)

        self.output_area.setPlainText(output_text)

    def update_output(self):
        self.output_area.setPlainText(f"Monitoring {len(self.machines)} machine(s).")


if __name__ == "__main__":
    app = QApplication([])
    window = SSHApp()
    window.show()
    app.exec()
