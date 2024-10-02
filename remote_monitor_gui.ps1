# Check if plink is installed
if (-not (Get-Command plink -ErrorAction SilentlyContinue)) {
    Write-Host "Error: 'plink' is not installed or not in the system PATH."
    exit
}

# Load the required assemblies for Windows Forms
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Define the remote machine's IP, username, and password
$ipAddress = "10.17.60.35"
$user = "jason"
$password = "W!t2024"

# Function to get system info from the remote host
function Get-RemoteData {
    param (
        [string]$command
    )

    # Execute the command using plink
    try {
        # Add the command directly to plink
        $result = plink -batch -ssh "$user@$ipAddress" -pw "$password" "$command"

        # If the command is 'free -m', parse the output
        if ($command -eq "free -m") {
            $lines = $result -split "`n"
            $memLine = $lines[1] -split '\s+', 0, 'Regex'
            $result = "Total: $($memLine[1]) MB, Used: $($memLine[2]) MB, Free: $($memLine[3]) MB"
        }

        # If the command is 'df -h', parse the output
        if ($command -eq "df -h") {
            $lines = $result -split "`n"
            foreach ($line in $lines) {
                if ($line -match '^/dev') {
                    $diskLine = $line -split '\s+', 0, 'Regex'
                    $result = "Size: $($diskLine[1]), Used: $($diskLine[2]), Available: $($diskLine[3])"
                    break
                }
            }
        }

        # Return the result, cleaned up if needed
        return $result -replace "Access granted. Press Return to begin session.", ""
    }
    catch {
        Write-Host "Error: Unable to connect to the remote server."
        return "N/A"
    }
}

# Get CPU information
$cpuInfo = Get-RemoteData "top -b -n1 | grep 'Cpu(s)'"
Write-Host "CPU Info: $cpuInfo"

# Get memory information
$memoryInfo = Get-RemoteData "free -m"
Write-Host "Memory Info: $memoryInfo"

# Get disk information
$diskInfo = Get-RemoteData "df -h"
Write-Host "Disk Info: $diskInfo"

# Initialize a hashtable to store the system information
$systemInfo = @{
    IPAddress = $ipAddress
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    CPU = $cpuInfo
    Memory = $memoryInfo
    Disk = $diskInfo
}

# Create a new form
Write-Host "Creating the form..."
$form = New-Object System.Windows.Forms.Form
$form.Text = "System Information"
$form.Size = New-Object System.Drawing.Size(800, 600)

# Use FlowLayoutPanel for proper alignment of labels
$panel = New-Object System.Windows.Forms.FlowLayoutPanel
$panel.Dock = [System.Windows.Forms.DockStyle]::Fill
$panel.AutoScroll = $true

# Create a list to store the labels
$labels = New-Object System.Collections.Generic.List[System.Windows.Forms.Label]

# Create a new label for each piece of system information and add it to the panel
foreach ($entry in $systemInfo.GetEnumerator()) {
    $key = $entry.Key
    $value = $entry.Value

    $label = New-Object System.Windows.Forms.Label
    $label.Text = "${key}:`n${value}"
    $label.Size = New-Object System.Drawing.Size(750, 50)
    $label.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
    $label.Padding = New-Object System.Windows.Forms.Padding(10)
    $panel.Controls.Add($label)

    # Add the label to the list
    $labels.Add($label)
}

# Create a new button for refreshing the data
$refreshButton = New-Object System.Windows.Forms.Button
$refreshButton.Text = "Refresh"
$refreshButton.Width = 100
$refreshButton.Height = 30
$refreshButton.Location = New-Object System.Drawing.Point(350, 520)

$refreshButton.Add_Click({
    # Get fresh data
    Write-Host "Getting new data..."
    $cpuInfo = Get-RemoteData "top -b -n1 | grep 'Cpu(s)'"
    Write-Host "CPU Info: $cpuInfo"
    $memoryInfo = Get-RemoteData "free -m"
    Write-Host "Memory Info: $memoryInfo"
    $diskInfo = Get-RemoteData "df -h"
    Write-Host "Disk Info: $diskInfo"

    # Update the hashtable
    $systemInfo.CPU = $cpuInfo
    $systemInfo.Memory = $memoryInfo
    $systemInfo.Disk = $diskInfo
    $systemInfo.Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'  # Update the timestamp
    Write-Host "Updated System Info: $($systemInfo | Out-String)"

    # Update the labels on the form
    foreach ($label in $labels) {
        $key = $label.Text.Split(":")[0]
        $label.Text = "${key}:`n" + $systemInfo[$key]
    }
})

# Add the button to the form
$form.Controls.Add($refreshButton)

# Add panel to the form
$form.Controls.Add($panel)

# Show the form and print to console for debugging
Write-Host "Displaying the form..."
$form.ShowDialog()  # This blocks the script until the form is closed