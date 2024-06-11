import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import stat

def check_dependencies():
    try:
        subprocess.run(["ratbagctl", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        install = messagebox.askyesno("Install Dependencies", "ratbagctl is not installed. Would you like to install it?")
        if install:
            try:
                subprocess.run(["sudo", "apt-get", "install", "-y", "ratbagd"], check=True)
                messagebox.showinfo("Success", "Dependencies installed successfully. Please restart the application.")
                root.destroy()
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to install dependencies: {e}")
                root.destroy()
        else:
            root.destroy()

def check_script_permissions(script_path):
    if not os.path.isfile(script_path):
        messagebox.showerror("Error", f"{script_path} not found.")
        root.destroy()
        return

    st = os.stat(script_path)
    if not st.st_mode & stat.S_IEXEC:
        change_permissions = messagebox.askyesno("Change Permissions", f"{script_path} is not executable. Would you like to make it executable?")
        if change_permissions:
            try:
                subprocess.run(["chmod", "+x", script_path], check=True)
                messagebox.showinfo("Success", f"{script_path} is now executable.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to change permissions: {e}")
                root.destroy()
        else:
            root.destroy()

def get_device_name():
    try:
        result = subprocess.run(["ratbagctl", "list"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if "G915" in line:
                return " ".join(line.split()[1:])
        messagebox.showerror("Error", "Logitech G915 keyboard not found.")
        root.destroy()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to list devices: {e}")
        root.destroy()

def get_leds():
    try:
        result = subprocess.run(["ratbagctl", device_name, "led", "get"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()
        leds = [line for line in lines if line.startswith("LED:")]
        return leds
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to get LEDs: {e}")
        root.destroy()

def change_color():
    color_code = color_entry.get()
    led_index = led_var.get()
    command = f'ratbagctl "{device_name}" led {led_index} set color {color_code}'
    try:
        subprocess.run(command, shell=True, check=True)
        result_label.config(text="Color changed successfully!", fg="green")
        color_entry.delete(0, tk.END)  # Clear the color entry field
    except subprocess.CalledProcessError as e:
        result_label.config(text=f"Failed to change color: {e}", fg="red")

def insert_color_code(color_code):
    color_entry.delete(0, tk.END)
    color_entry.insert(0, color_code)

# Initialize the main window
root = tk.Tk()
root.title("Change G915 LED Color")
root.geometry("380x180")  # Set the initial window size

# Check if dependencies are installed
check_dependencies()

# Check if the script has the correct permissions
check_script_permissions("G915.sh")

# Get the device name
device_name = get_device_name()

# Get the list of LEDs
leds = get_leds()

# Create and place the LED selection dropdown
tk.Label(root, text="Select LED (Usually 0 for G-Logo and 1 for the rest):").pack(pady=5)
led_var = tk.StringVar(root)
led_var.set(leds[0].split()[1][:-1])  # Default value
led_dropdown = tk.OptionMenu(root, led_var, *[led.split()[1][:-1] for led in leds])
led_dropdown.pack(pady=5)

# Create and place the color entry field and color dropdown
color_frame = tk.Frame(root)
color_frame.pack(pady=5)

color_entry = tk.Entry(color_frame)
color_entry.pack(side=tk.LEFT, padx=5)

# Predefined color choices
colors = {
    "Off-White": "F0F0F0",
    "Black (OFF)": "000000",
    "Grey": "808080",
    "Red": "FF0000",
    "Green": "00FF00",
    "Blue": "0000FF",
    "Yellow": "FFFF00",
    "Cyan": "00FFFF",
    "Magenta": "FF00FF",
    "Orange": "FFA500",
    "Purple": "800080",
    "Dark Red": "8B0000",
    "Dark Green": "006400",
    "Dark Blue": "00008B",
    "Dark Yellow": "9B870C",
    "Dark Cyan": "008B8B",
    "Dark Magenta": "8B008B",
    "Dark Orange": "FF8C00",
    "Dark Purple": "4B0082",
    "Dark Slate Grey": "2F4F4F",
    "Olive": "808000",
    "Light Red": "FF6961",
    "Light Green": "77DD77",
    "Light Blue": "AEC6CF",
    "Light Yellow": "FDFD96",
    "Light Cyan": "A0E7E5",
    "Light Magenta": "FFB7C5",
    "Light Orange": "FFB347",
    "Light Purple": "CBAACB",
    "Light Pink": "FFD1DC",
    "Light Peach": "FFDAB9"
}

color_var = tk.StringVar(root)
color_var.set("Color")  # Default value
color_dropdown = tk.OptionMenu(color_frame, color_var, *colors.keys(), command=lambda choice: insert_color_code(colors[choice]))
color_dropdown.pack(side=tk.RIGHT, padx=5)

# Create and place the Change Color button
change_button = tk.Button(root, text="Change Color", command=change_color)
change_button.pack(pady=10)

# Create and place the result label
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# Run the application
root.mainloop()

