import subprocess
import json
import os
import time
import stat

# Define the path to the PowerShell script
ps_script_path = "C:\\Users\\Jason Dank\\Remote_Monitering\\remote_json.ps1"

# Define the path to the JSON results file
json_results_path = "C:\\Users\\Jason Dank\\Remote_Monitering\\RemoteSystemInfo.json"

# Use subprocess to call PowerShell and run the script
try:
    print(f"Attempting to run PowerShell script: {ps_script_path}")
    # Use the 'powershell' command along with '-File' to specify the script path
    result = subprocess.run(["powershell", "-File", ps_script_path], capture_output=True, text=True, shell=True)

    # Print the standard output and error
    print("PowerShell Output:\n", result.stdout)
    print("PowerShell Errors:\n", result.stderr)

    # Wait until the file is no longer being written to
    print(f"Waiting for file to be written: {json_results_path}")
    last_mod_time = None
    wait_count = 0
    while True:
        if os.path.exists(json_results_path):
            current_mod_time = os.path.getmtime(json_results_path)
            if last_mod_time and current_mod_time == last_mod_time:
                break
            last_mod_time = current_mod_time
        time.sleep(1)
        wait_count += 1
        if wait_count % 10 == 0:
            print(f"Still waiting... ({wait_count} seconds)")

    # Check the file permissions
    permissions = stat.S_IMODE(os.lstat(json_results_path).st_mode)
    print("File permissions:", oct(permissions))

    # Check if the file is not empty
    file_size = os.path.getsize(json_results_path)
    print(f"File size: {file_size} bytes")

    if file_size > 0:
        # Open the JSON results file and load the data
        with open(json_results_path, 'rb') as f:
            content = f.read()
            print("Raw file contents (first 100 bytes):")
            print(content[:100])

            # Detect and remove BOM if present
            if content.startswith(b'\xff\xfe'):
                content = content[2:]

            # Decode as UTF-16
            content = content.decode('utf-16')

            print("Decoded content:")
            print(content)

            data = json.loads(content)

        # Print the JSON data
        print("Parsed JSON Data:\n", json.dumps(data, indent=4))
    else:
        print("The JSON file is empty.")

except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    print("Raw file contents:")
    with open(json_results_path, 'rb') as f:
        print(f.read())
except FileNotFoundError:
    print(f"File not found: {json_results_path}")
except PermissionError:
    print(f"Permission denied when trying to read: {json_results_path}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")