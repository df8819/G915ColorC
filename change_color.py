import tkinter as tk
from tkinter import messagebox, ttk, colorchooser
import subprocess
import sys


# noinspection PyAttributeOutsideInit,GrazieInspection
class G915ColorChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("G915 LED Color Changer")
        self.root.geometry("850x420")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Color Changer")

        # Setup the UI
        self.setup_main_tab()

        # Check dependencies on startup
        self.root.after(100, self.check_dependencies)

    def setup_main_tab(self):
        frame = self.main_tab

        # Device selection
        ttk.Label(frame, text="Device:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.device_var = tk.StringVar(value="")  # Default value
        self.device_combo = ttk.Combobox(frame, textvariable=self.device_var, width=40)
        self.device_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame, text="Refresh", command=self.refresh_devices).grid(row=0, column=2, padx=5, pady=5)

        # LED selection
        ttk.Label(frame, text="LED:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.led_var = tk.StringVar(value="0")  # Default value
        self.led_combo = ttk.Combobox(frame, textvariable=self.led_var, width=40)
        self.led_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame, text="Refresh", command=self.refresh_leds).grid(row=1, column=2, padx=5, pady=5)

        # Color selection
        ttk.Label(frame, text="Color (hex format '2bdee6'):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.color_entry = ttk.Entry(frame, width=20)
        self.color_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.color_entry.insert(0, "")  # Default value

        # Color picker button
        ttk.Button(frame, text="Select Color", command=self.choose_color).grid(row=2, column=2, padx=5, pady=5)

        # Apply button
        ttk.Button(frame, text="Apply Color", command=self.apply_color).grid(row=3, column=1, pady=10)

        # Status label
        self.status_label = ttk.Label(frame, text="", wraplength=700)
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)

        # Refresh devices on startup
        self.root.after(500, self.refresh_devices)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose a color")
        if color_code[1]:
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, color_code[1][1:])

    def check_dependencies(self):
        try:
            subprocess.run(["ratbagctl", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.status_label.config(text="Dependencies are installed.")
            return True
        except FileNotFoundError:
            install = messagebox.askyesno("Install Dependencies",
                                          "ratbagctl is not installed. Would you like to install it?")
            if install:
                try:
                    pm = self.detect_package_manager()
                    if pm == "apt":
                        cmd = "sudo apt install -y ratbagd"
                    elif pm == "pacman":
                        cmd = "sudo pacman -S --noconfirm ratbagd"
                    elif pm == "dnf":
                        cmd = "sudo dnf install -y libratbag"
                    elif pm == "zypper":
                        cmd = "sudo zypper install -y libratbag"
                    elif pm == "flatpak":
                        cmd = "flatpak install -y org.libratbag.ratbagd"
                    else:
                        messagebox.showerror("Error", "Unsupported package manager. Please install ratbagd manually.")
                        return False

                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()

                    if process.returncode != 0:
                        messagebox.showerror("Error", f"Failed to install dependencies: {stderr.decode()}")
                        return False

                    messagebox.showinfo("Success", "Dependencies installed successfully.")
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to install dependencies: {e}")
                    return False
        except Exception as e:
            messagebox.showerror("Error", f"Error checking dependencies: {e}")
            return False

    def refresh_devices(self):
        try:
            result = subprocess.run(["ratbagctl", "list"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()

            devices = []
            for line in lines:
                if ":" in line and len(line.split()) > 1:
                    device_name = " ".join(line.split()[1:])
                    devices.append(device_name)

            if not devices:
                self.status_label.config(text="No compatible devices found.")
                return

            self.device_combo['values'] = devices

            # Select the first device
            if devices:
                self.device_combo.set(devices[0])

            # Refresh LEDs for the selected device
            self.refresh_leds()

        except Exception as e:
            self.status_label.config(text=f"Error: {e}")

    def refresh_leds(self):
        device = self.device_var.get()
        if not device:
            return

        try:
            result = subprocess.run(["ratbagctl", device, "led", "get"], check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()

            leds = []
            for line in lines:
                if line.startswith("LED:"):
                    led_id = line.split()[1][:-1]  # Remove the colon
                    leds.append(led_id)

            if not leds:
                self.status_label.config(text="No LEDs found on the device.")
                return

            self.led_combo['values'] = leds

            # Select the first LED
            if leds:
                self.led_combo.set(leds[0])

            self.status_label.config(text=f"Found {len(leds)} LEDs on {device}")

        except Exception as e:
            self.status_label.config(text=f"Error: {e}")

    def apply_color(self):
        device = self.device_var.get()
        led = self.led_var.get()
        color = self.color_entry.get()

        if not device:
            self.status_label.config(text="Error: No device selected")
            return

        if not led:
            self.status_label.config(text="Error: No LED selected")
            return

        if not color:
            self.status_label.config(text="Error: No color specified")
            return

        try:
            # Set the profile to 0 directly
            active_profile = "0"

            # Apply the color to profile 0
            command = f'ratbagctl "{device}" profile {active_profile} led {led} set color {color}'
            subprocess.run(command, shell=True, check=True)
            self.status_label.config(text=f"Color changed successfully to #{color} on profile {active_profile}")
        except Exception as e:
            self.status_label.config(text=f"Error changing color: {e}")

def main():
    # Check if tkinter is available
    try:
        root = tk.Tk()
        app = G915ColorChanger(root)
        root.mainloop()
    except ImportError:
        print("Error: Tkinter is not installed.")
        print("Please install the tk package for your distribution:")
        print("  Debian/Ubuntu: sudo apt install python3-tk")
        print("  Arch Linux: sudo pacman -S tk")
        print("  Fedora: sudo dnf install python3-tkinter")
        print("  openSUSE: sudo zypper install python3-tk")

        # Prompt for installation
        install_prompt = messagebox.askyesno("Install Tkinter", "Would you like to install Tkinter now?")
        if install_prompt:
            pm = detect_package_manager()
            if pm == "apt":
                subprocess.run(["sudo", "apt", "install", "-y", "python3-tk"])
            elif pm == "pacman":
                subprocess.run(["sudo", "pacman", "-S", "tk"])
            elif pm == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", "python3-tkinter"])
            elif pm == "zypper":
                subprocess.run(["sudo", "zypper", "install", "-y", "python3-tk"])
            else:
                print("Unsupported package manager. Please install Tkinter manually.")
        sys.exit(1)

def detect_package_manager():
    """Detect the package manager used by the system."""
    try:
        subprocess.run(["apt", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "apt"
    except FileNotFoundError:
        pass
    try:
        subprocess.run(["pacman", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "pacman"
    except FileNotFoundError:
        pass
    try:
        subprocess.run(["dnf", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "dnf"
    except FileNotFoundError:
        pass
    try:
        subprocess.run(["zypper", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "zypper"
    except FileNotFoundError:
        pass
    return None

if __name__ == "__main__":
    main()