import subprocess
import json


# Define the path to the PowerShell script
ps_script_path = "C:\\Users\\Jason Dank\\Remote_Monitering\\remote_json.ps1"


# Use subprocess to call PowerShell and run the script
try:
    # Use the 'powershell' command along with '-File' to specify the script path
    result = subprocess.run(["powershell", "-File", ps_script_path], capture_output=True, text=True, shell=True)
    
    # Print the standard output and error
    print("Output:\n", result.stdout)

    print("Errors:\n", result.stderr)
except Exception as e:
    print(f"An error occurred: {e}")











