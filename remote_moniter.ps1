# Define the remote machine's IP, username, and password
$ipAddress = "10.17.60.35"
$user = "jason"
$password = "W!t2024"

# Define the file path to save the results on the desktop
$desktopPath = [System.Environment]::GetFolderPath("Desktop")
$resultsFile = Join-Path $desktopPath "RemoteSystemInfo.txt"

# Load the required assembly for keystroke entry
Add-Type -AssemblyName System.Windows.Forms

# Write a separator line before appending new results
"______________________________________________________________" | Out-File -Append -FilePath $resultsFile

# Write the timestamp and IP address to the file
"Results for $ipAddress at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -Append -FilePath $resultsFile

# Press enter to show results 
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

# Get CPU information, filter out unwanted messages, and append to file
plink -ssh "$user@$ipAddress" -pw "$password" "top -b -n1 | grep 'Cpu(s)'" | Select-String -NotMatch "Access granted. Press Return to begin session." | Out-File -Append -FilePath $resultsFile

# Press enter to show results
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

# Get memory information, filter out unwanted messages, and append to file
plink -ssh "$user@$ipAddress" -pw "$password" "free -m" | Select-String -NotMatch "Access granted. Press Return to begin session." | Out-File -Append -FilePath $resultsFile

# Press enter to show results
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

# Get disk information, filter out unwanted messages, and append to file
plink -ssh "$user@$ipAddress" -pw "$password" "df -h" | Select-String -NotMatch "Access granted. Press Return to begin session." | Out-File -Append -FilePath $resultsFile

# Press enter to show results
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
