import paramiko
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


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
        self.root.configure(bg="#FFFFFF")  # White background

        # Machines to monitor
        self.machines = []  # List of dictionaries with keys: host, username, password

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        """Create UI elements."""
        # Title
        tk.Label(
            self.root, text="Remote System Monitor", font=("Helvetica", 18, "bold"), bg="#A41034", fg="white", padx=10, pady=10
        ).pack(fill="x")

        # Command Output Section
        self.info_frame = tk.Frame(self.root, bg="#F5F5F5", padx=20, pady=20)
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.output_label = tk.Label(
            self.info_frame,
            text="No machines added. Click 'Add' to monitor a machine.",
            font=("Helvetica", 14),
            bg="#F5F5F5",
            fg="black",  # Ensures text color is black
        )
        self.output_label.pack(anchor="w", pady=10)

        # Buttons Section
        self.button_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.button_frame.pack(pady=10)

        self.add_button = tk.Button(
            self.button_frame,
            text="Add Machine",
            command=self.add_machine,
            font=("Helvetica", 14, "bold"),
            bg="#A41034",
            fg="white",
            activebackground="#7A0D29",
            activeforeground="white",
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
            activebackground="#7A0D29",
            activeforeground="white",
            padx=20,
            pady=10,
            state="disabled",  # Initially disabled
        )
        self.refresh_button.grid(row=0, column=1, padx=10)

    def add_machine(self):
        """Prompt user to add a new machine to monitor."""
        host = simpledialog.askstring("Add Machine", "Enter the IP address or hostname:")
        if not host:
            return

        username = simpledialog.askstring("Add Machine", "Enter the username:")
        if not username:
            return

        password = simpledialog.askstring("Add Machine", "Enter the password:", show="*")
        if not password:
            return

        # Add the machine details to the list
        self.machines.append({"host": host, "username": username, "password": password})
        self.output_label.config(
            text=f"Monitoring {len(self.machines)} machine(s). Click 'Refresh' to update.",
            fg="black",  # Ensures text color is black
        )
        self.refresh_button.config(state="normal")  # Enable refresh button

    def refresh_info(self):
        """Refresh system information for all machines."""
        if not self.machines:
            messagebox.showinfo("No Machines", "No machines to monitor. Add a machine first.")
            return

        output_text = ""
        for i, machine in enumerate(self.machines, start=1):
            host = machine["host"]
            username = machine["username"]
            password = machine["password"]

            output_text += f"Machine {i}: {host}\n"

            # Connect to SSH
            ssh_client = ssh_connect(host, username, password)
            if not ssh_client:
                output_text += "  Failed to connect.\n\n"
                continue

            # Commands to run
            cpu_command = "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'"
            memory_command = "free -m | awk '/Mem:/ {print $3 \"/\" $2 \" MB\"}'"
            disk_command = "df -h / | awk 'NR==2 {print $3 \"/\" $2 \" used\"}'"
            network_command = "cat /proc/net/dev | grep -w eth0 | awk '{print $2 \" KB RX, \" $10 \" KB TX\"}'"

            # Fetch and append info
            output_text += f"  CPU Usage: {ssh_run_command(ssh_client, cpu_command)}% utilized\n"
            output_text += f"  Memory Usage: {ssh_run_command(ssh_client, memory_command)}\n"
            output_text += f"  Disk Usage: {ssh_run_command(ssh_client, disk_command)}\n"
            output_text += f"  Network Traffic: {ssh_run_command(ssh_client, network_command)}\n\n"

            # Disconnect SSH
            ssh_disconnect(ssh_client)

        # Update output
        self.output_label.config(text=output_text, fg="black")  # Ensures all text is black


if __name__ == "__main__":
    root = tk.Tk()
    app = SSHApp(root)
    root.mainloop()
