# Load necessary assemblies
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create a new form
$form = New-Object System.Windows.Forms.Form
$form.Text = "QR Code Generator"
$form.Size = New-Object System.Drawing.Size(400, 500)
$form.StartPosition = "CenterScreen"

# Create URL label and text box
$urlLabel = New-Object System.Windows.Forms.Label
$urlLabel.Text = "Enter URL:"
$urlLabel.Location = New-Object System.Drawing.Point(20, 20)
$urlLabel.Size = New-Object System.Drawing.Size(80, 30)
$form.Controls.Add($urlLabel)

$urlTextbox = New-Object System.Windows.Forms.TextBox
$urlTextbox.Location = New-Object System.Drawing.Point(100, 20)
$urlTextbox.Size = New-Object System.Drawing.Size(250, 30)
$urlTextbox.Text = "Enter URL here"
$form.Controls.Add($urlTextbox)

# Create Background Color label and combobox
$colorLabel = New-Object System.Windows.Forms.Label
$colorLabel.Text = "Select Background Color:"
$colorLabel.Location = New-Object System.Drawing.Point(20, 60)
$colorLabel.Size = New-Object System.Drawing.Size(140, 30)
$form.Controls.Add($colorLabel)

$colorCombobox = New-Object System.Windows.Forms.ComboBox
$colorCombobox.Items.AddRange(@("red", "blue", "green", "yellow", "white"))
$colorCombobox.Location = New-Object System.Drawing.Point(180, 60)
$colorCombobox.Size = New-Object System.Drawing.Size(100, 30)
$colorCombobox.SelectedIndex = 0
$form.Controls.Add($colorCombobox)

# Create PictureBox to display the QR Code
$pictureBox = New-Object System.Windows.Forms.PictureBox
$pictureBox.Location = New-Object System.Drawing.Point(50, 150)
$pictureBox.Size = New-Object System.Drawing.Size(300, 300)
$form.Controls.Add($pictureBox)

# Function to generate the QR Code using an online API
function Generate-QRCode {
    param (
        [string]$url,
        [string]$backColor
    )

    if (-not $url) {
        [System.Windows.Forms.MessageBox]::Show("Please enter a valid URL.", "Input Error", "OK", "Error")
        return
    }

    # Create the URL for the QR code
    $apiUrl = "https://api.qrserver.com/v1/create-qr-code/?data=$($url)&size=300x300&bgcolor=$($backColor)&color=000000"

    # Download the QR code image
    $bitmap = [System.Drawing.Image]::FromStream((New-Object System.Net.WebClient).OpenRead($apiUrl))

    # Display the image in the PictureBox
    $pictureBox.Image = $bitmap
}

# Create Generate QR Code button
$generateButton = New-Object System.Windows.Forms.Button
$generateButton.Text = "Generate QR Code"
$generateButton.Location = New-Object System.Drawing.Point(50, 100)
$generateButton.Size = New-Object System.Drawing.Size(120, 30)
$generateButton.Add_Click({
    $bgColorHex = switch ($colorCombobox.SelectedItem.ToString()) {
        "red" { "FF0000" }
        "blue" { "0000FF" }
        "green" { "00FF00" }
        "yellow" { "FFFF00" }
        "white" { "FFFFFF" }
    }
    Generate-QRCode -url $urlTextbox.Text -backColor $bgColorHex
})
$form.Controls.Add($generateButton)

# Function to save the QR code
function Save-QRCode {
    if ($pictureBox.Image) {
        $saveFileDialog = New-Object System.Windows.Forms.SaveFileDialog
        $saveFileDialog.Filter = "PNG Image|*.png"
        $saveFileDialog.Title = "Save QR Code Image"
        $saveFileDialog.ShowDialog()

        if ($saveFileDialog.FileName -ne "") {
            $pictureBox.Image.Save($saveFileDialog.FileName, [System.Drawing.Imaging.ImageFormat]::Png)
            [System.Windows.Forms.MessageBox]::Show("QR Code saved successfully.", "Success", "OK", "Information")
        }
    } else {
        [System.Windows.Forms.MessageBox]::Show("No QR Code to save. Please generate one first.", "Save Error", "OK", "Error")
    }
}

# Create Save QR Code button
$saveButton = New-Object System.Windows.Forms.Button
$saveButton.Text = "Save QR Code"
$saveButton.Location = New-Object System.Drawing.Point(200, 100)
$saveButton.Size = New-Object System.Drawing.Size(120, 30)
$saveButton.Add_Click({
    Save-QRCode
})
$form.Controls.Add($saveButton)

# Run the form
[void] $form.ShowDialog()
