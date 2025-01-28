import paramiko
import tkinter as tk
from tkinter import ttk, messagebox


def ssh_connect(host, username, password):
    """
    Establishes an SSH connection to the specified host.
    """
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
    """
    Runs a command on the connected SSH server.
    """
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
    """
    Closes the SSH connection.
    """
    client.close()


class SSHApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote System Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFFFFF")  # White background

        # Configuration variables
        self.host = "128.103.125.144"
        self.username = "jason"
        self.password = ""
        self.ssh_client = None

        # UI Elements
        self.create_widgets()

        # Automatically refresh on startup
        self.refresh_info()

    def create_widgets(self):
        """Create UI elements."""
        # Title
        tk.Label(
            self.root, text="Remote System Monitor", font=("Helvetica", 18, "bold"), bg="#A41034", fg="white", padx=10, pady=10
        ).pack(fill="x")

        # Command Output Section
        self.info_frame = tk.Frame(self.root, bg="#F5F5F5", padx=20, pady=20)
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.cpu_label = tk.Label(self.info_frame, text="CPU Usage: Loading...", font=("Helvetica", 14), bg="#F5F5F5", fg="black")
        self.cpu_label.pack(anchor="w", pady=10)

        self.memory_label = tk.Label(self.info_frame, text="Memory Usage: Loading...", font=("Helvetica", 14), bg="#F5F5F5", fg="black")
        self.memory_label.pack(anchor="w", pady=10)

        self.disk_label = tk.Label(self.info_frame, text="Disk Usage: Loading...", font=("Helvetica", 14), bg="#F5F5F5", fg="black")
        self.disk_label.pack(anchor="w", pady=10)

        self.network_label = tk.Label(self.info_frame, text="Network Traffic: Loading...", font=("Helvetica", 14), bg="#F5F5F5", fg="black")
        self.network_label.pack(anchor="w", pady=10)

        # Button Section
        self.refresh_button = tk.Button(
            self.root,
            text="Refresh",
            command=self.refresh_info,
            font=("Helvetica", 14, "bold"),
            bg="#A41034",
            fg="white",
            activebackground="#7A0D29",
            activeforeground="white",
            padx=20,
            pady=10,
        )
        self.refresh_button.pack(pady=10)

    def refresh_info(self):
        """Refresh system information by running commands on the SSH server."""
        self.cpu_label.config(text="CPU Usage: Loading...")
        self.memory_label.config(text="Memory Usage: Loading...")
        self.disk_label.config(text="Disk Usage: Loading...")
        self.network_label.config(text="Network Traffic: Loading...")

        # Connect to SSH
        self.ssh_client = ssh_connect(self.host, self.username, self.password)
        if not self.ssh_client:
            return

        # Commands to run
        cpu_command = "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'"
        memory_command = "free -m | awk '/Mem:/ {print $3 \"/\" $2 \" MB\"}'"
        disk_command = "df -h / | awk 'NR==2 {print $3 \"/\" $2 \" used\"}'"
        network_command = "cat /proc/net/dev | grep -w eth0 | awk '{print $2 \" KB RX, \" $10 \" KB TX\"}'"

        # Fetch and update info
        self.cpu_label.config(
            text=f"CPU Usage: {ssh_run_command(self.ssh_client, cpu_command)}% utilized"
        )
        self.memory_label.config(
            text=f"Memory Usage: {ssh_run_command(self.ssh_client, memory_command)}"
        )
        self.disk_label.config(
            text=f"Disk Usage: {ssh_run_command(self.ssh_client, disk_command)}"
        )
        self.network_label.config(
            text=f"Network Traffic: {ssh_run_command(self.ssh_client, network_command)}"
        )

        # Disconnect SSH
        ssh_disconnect(self.ssh_client)


if __name__ == "__main__":
    root = tk.Tk()
    app = SSHApp(root)
    root.mainloop()
