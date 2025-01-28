import subprocess
import paramiko
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
from plyer import notification


def ssh_connect(host, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)
        return client
    except paramiko.AuthenticationException:
        messagebox.showerror("Authentication Error", "Invalid username or password.")
        return None
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect: {e}")
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


class SSHApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote System Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFFFFF")

        self.machines = []
        self.thresholds = {"cpu": 10, "memory": 10, "disk": 90}  # Alert thresholds

        self.load_machines()
        self.create_widgets()

    def create_widgets(self):
        """Create UI elements."""
        tk.Label(
            self.root, text="Remote System Monitor", font=("Helvetica", 18, "bold"), bg="#A41034", fg="white", padx=10, pady=10
        ).pack(fill="x")

        self.info_frame = tk.Frame(self.root, bg="#F5F5F5", padx=20, pady=20)
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.output_label = tk.Label(
            self.info_frame,
            text="No machines added. Click 'Add' to monitor a machine.",
            font=("Helvetica", 14),
            bg="#F5F5F5",
            fg="black",
        )
        self.output_label.pack(anchor="w", pady=10)

        self.button_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.button_frame.pack(pady=10)

        self.add_button = tk.Button(
            self.button_frame,
            text="Add Machine",
            command=self.add_machine,
            font=("Helvetica", 14, "bold"),
            bg="#A41034",
            fg="white",
            padx=20,
            pady=10,
        )
        self.add_button.grid(row=0, column=0, padx=10)

        self.refresh_button = tk.Button(
            self.button_frame,
            text="Refresh",
            command=self.refresh_info,
            font=("Helvetica", 14, "bold"),
            bg="#A41034",
            fg="white",
            padx=20,
            pady=10,
        )
        self.refresh_button.grid(row=0, column=1, padx=10)

    def add_machine(self):
        """Add a new machine."""
        host = simpledialog.askstring("Add Machine", "Enter the IP address or hostname:")
        username = simpledialog.askstring("Add Machine", "Enter the username:")
        password = simpledialog.askstring("Add Machine", "Enter the password:", show="*")
        if not (host and username and password):
            return

        self.machines.append({"host": host, "username": username, "password": password})
        self.save_machines()
        self.update_output()

    def save_machines(self):
        """Save machine configurations to a JSON file."""
        with open("../DSPM/src/DSPM/resources/machines.json", "w") as file:
            json.dump(self.machines, file)

    def load_machines(self):
        """Load machine configurations from a JSON file."""
        try:
            with open("../DSPM/src/DSPM/resources/machines.json", "r") as file:
                self.machines = json.load(file)
        except FileNotFoundError:
            self.machines = []

    def send_notification(self, machine, metric, value):
        """Send a macOS notification using SwiftDialog."""
        notification_title = f"High {metric} Usage on {machine['host']}"
        notification_message = f"The {metric} usage on {machine['host']} is at {value}%."
        try:
            subprocess.run([
                "/usr/local/bin/dialog",
                "--title", notification_title,
                "--message", notification_message,
                "--icon", "warning",
                "--button1text", "OK"
            ], check=True)
            print(f"Notification sent for {metric} on {machine['host']}")
        except Exception as e:
            print(f"Failed to send notification: {e}")

    def refresh_info(self):
        """Refresh system information."""
        if not self.machines:
            messagebox.showinfo("No Machines", "No machines to monitor. Add a machine first.")
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

            print(f"Raw CPU output for {host}: {cpu_usage}")
            print(f"Raw Memory output for {host}: {memory_usage}")
            print(f"Raw Disk output for {host}: {disk_usage}")

            # Validate and parse metrics
            try:
                cpu_usage = float(cpu_usage) if cpu_usage else 0.0
                memory_usage = float(memory_usage) if memory_usage else 0.0
                disk_usage = float(disk_usage) if disk_usage else 0.0
            except ValueError:
                print(f"Failed to parse metrics for {host}. Skipping machine.")
                cpu_usage, memory_usage, disk_usage = 0.0, 0.0, 0.0

            # Check thresholds and send notifications
            if cpu_usage > self.thresholds["cpu"]:
                print(
                    f"Triggering notification for {host}. CPU Usage: {cpu_usage}%, Threshold: {self.thresholds['cpu']}%")
                self.send_notification(machine, "CPU", cpu_usage)
            if memory_usage > self.thresholds["memory"]:
                self.send_notification(machine, "Memory", memory_usage)
            if disk_usage > self.thresholds["disk"]:
                self.send_notification(machine, "Disk", disk_usage)

            # Update output text
            output_text += f"  CPU Usage: {cpu_usage:.2f}%\n"
            output_text += f"  Memory Usage: {memory_usage:.2f}%\n"
            output_text += f"  Disk Usage: {disk_usage:.2f}%\n\n"

            ssh_disconnect(ssh_client)

        # Update the output label
        self.output_label.config(text=output_text)

    def update_output(self):
        """Update the output display."""
        text = f"Monitoring {len(self.machines)} machine(s)."
        self.output_label.config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    app = SSHApp(root)
    root.mainloop()
