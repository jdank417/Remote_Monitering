import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import qrcode

def generate_qr():
    # Get the user inputs
    url = url_entry.get()
    back_color = back_color_combobox.get()

    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color=back_color)  # fill color is set to 'black'

    # Convert the QR code image to PhotoImage format and display it
    photo = ImageTk.PhotoImage(img)
    label.config(image=photo)
    label.image = photo  # Keep a reference to prevent garbage collection

    # Save the original image for saving to file
    root.img = img

def save_qr():
    # Ask the user where to save the file
    file_path = filedialog.asksaveasfilename(defaultextension=".png")

    # Save the image to the specified file
    root.img.save(file_path)

# Create the Tkinter window
root = tk.Tk()
root.title("QR Code Generator")
root.geometry("400x400")

# Create the input fields
url_entry = tk.Entry(root)
url_entry.pack()
url_entry.insert(0, 'Enter URL here')

# Approved colors
approved_colors = ['red', 'blue', 'green', 'yellow', 'white']

# Create the combobox for background color selection
back_color_combobox = ttk.Combobox(root, values=approved_colors)
back_color_combobox.pack()
back_color_combobox.set('Select background color')

# Create the buttons
generate_button = tk.Button(root, text='Generate QR Code', command=generate_qr)
generate_button.pack()

save_button = tk.Button(root, text='Save QR Code', command=save_qr)
save_button.pack()

# Create the label for displaying the QR code
label = tk.Label(root)
label.pack()

# Start the Tkinter event loop
root.mainloop()