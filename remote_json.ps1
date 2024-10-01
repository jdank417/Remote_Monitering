# Define the remote machine's IP, username, and password
$ipAddress = "10.17.60.35"
$user = "jason"
$password = "W!t2024"

# Define the file path to save the results as JSON
$resultsFile = Join-Path $PSScriptRoot "RemoteSystemInfo.json"

# Load the required assembly for keystroke entry
Add-Type -AssemblyName System.Windows.Forms

# Initialize a hashtable to store the system information
$systemInfo = @{
    IPAddress = $ipAddress
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    CPU = ""
    Memory = ""
    Disk = ""
}


# Get CPU information, filter out unwanted messages
$cpuInfo = plink -ssh "$user@$ipAddress" -pw "$password" "top -b -n1 | grep 'Cpu(s)'" | Select-String -NotMatch "Access granted. Press Return to begin session."
$systemInfo.CPU = $cpuInfo -join "`n"



# Get memory information, filter out unwanted messages
$memoryInfo = plink -ssh "$user@$ipAddress" -pw "$password" "free -m" | Select-String -NotMatch "Access granted. Press Return to begin session."
$systemInfo.Memory = $memoryInfo -join "`n"


# Get disk information, filter out unwanted messages
$diskInfo = plink -ssh "$user@$ipAddress" -pw "$password" "df -h" | Select-String -NotMatch "Access granted. Press Return to begin session."
$systemInfo.Disk = $diskInfo -join "`n"


# Convert the hashtable to JSON and write it to the file
$systemInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath $resultsFile
