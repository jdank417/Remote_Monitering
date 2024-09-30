# Remote System Information Script

This PowerShell script connects to a remote Linux machine using SSH to retrieve and log system information (CPU, memory, and disk usage) into a local file on the desktop. The results are appended to a text file named `RemoteSystemInfo.txt` with each execution.

## Features
- Retrieves CPU usage using the `top` command.
- Retrieves memory usage using the `free` command.
- Retrieves disk usage using the `df` command.
- Filters out unwanted messages from the SSH output.
- Appends the results to a text file with a timestamp for each execution.
- Automatically presses "Enter" after displaying each result to ensure script progression.

## Requirements
- PowerShell 5.0 or higher.
- **plink** (part of PuTTY) must be installed and accessible from the command line.
- Access to the remote Linux machine with valid SSH credentials.
- Basic knowledge of PowerShell and Windows environment variables.

## Setup Instructions
1. Ensure that `plink.exe` is installed and accessible via the command line.
   - You can download PuTTY from [here](https://www.putty.org/).
   - Add `plink.exe` to your system's PATH.
   
2. Modify the script to include your remote machine's IP, username, and password. These are defined in the following variables at the start of the script:
   ```PowerShell
   $ipAddress = IP_OF_YOUR_SYSTEM
   $user = USER_OF_YOUR_SYSTEM
   $password = PASS_OF_YOUR_SYSTEM

  ## Execution
  1. This script will populate a text file called "RemoteSystemInfo.txt" on your desktop with the output.
  

