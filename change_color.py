# G915ColorChanger.py - Cross-distribution compatible version
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import shutil
import json
import sys

class G915ColorChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("G915 LED Color Changer")
        self.root.geometry("750x420")

        # Configuration
        self.config_file = os.path.expanduser("~/.g915colorchanger.json")
        self.config = self.load_config()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Color Changer")

        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")

        # Setup the UI
        self.setup_main_tab()
        self.setup_settings_tab()

        # Check dependencies on startup
        if not self.config.get("skip_dependency_check", False):
            self.root.after(100, self.check_dependencies)

    def load_config(self):
        default_config = {
            "package_manager": self.detect_package_manager(),
            "install_command": self.get_default_install_command(),
            "package_name": self.get_default_package_name(),
            "has_systemd": self.has_systemd(),
            "skip_dependency_check": False,
            "last_device": "",
            "last_led": "0",
            "last_color": ""
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Update default with saved, but keep default values for any missing keys
                    for key, value in saved_config.items():
                        default_config[key] = value
        except Exception as e:
            messagebox.showwarning("Config Warning", f"Could not load config: {e}")

        return default_config

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            messagebox.showwarning("Config Warning", f"Could not save config: {e}")

    def detect_package_manager(self):
        if shutil.which("apt"):
            return "apt"
        elif shutil.which("pacman"):
            return "pacman"
        elif shutil.which("dnf"):
            return "dnf"
        elif shutil.which("zypper"):
            return "zypper"
        elif shutil.which("flatpak"):
            return "flatpak"
        else:
            return "unknown"

    def get_default_install_command(self):
        pm = self.detect_package_manager()
        if pm == "apt":
            return "sudo apt install -y"
        elif pm == "pacman":
            return "sudo pacman -S --noconfirm"
        elif pm == "dnf":
            return "sudo dnf install -y"
        elif pm == "zypper":
            return "sudo zypper install -y"
        elif pm == "flatpak":
            return "flatpak install -y"
        else:
            return "echo 'Package manager not detected. Please install manually:'"

    def get_default_package_name(self):
        pm = self.detect_package_manager()
        if pm == "apt":
            return "ratbagd"
        elif pm == "pacman":
            return "ratbagd"
        elif pm == "dnf":
            return "libratbag"
        elif pm == "zypper":
            return "libratbag"
        elif pm == "flatpak":
            return "org.libratbag.ratbagd"
        else:
            return "ratbagd"

    def has_systemd(self):
        return shutil.which("systemctl") is not None

    def setup_main_tab(self):
        frame = self.main_tab

        # Device selection
        ttk.Label(frame, text="Device:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.device_var = tk.StringVar(value=self.config.get("last_device", ""))
        self.device_combo = ttk.Combobox(frame, textvariable=self.device_var, width=30)
        self.device_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame, text="Refresh", command=self.refresh_devices).grid(row=0, column=2, padx=5, pady=5)

        # LED selection
        ttk.Label(frame, text="LED:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.led_var = tk.StringVar(value=self.config.get("last_led", "0"))
        self.led_combo = ttk.Combobox(frame, textvariable=self.led_var, width=30)
        self.led_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame, text="Refresh", command=self.refresh_leds).grid(row=1, column=2, padx=5, pady=5)

        # Color selection
        ttk.Label(frame, text="Color:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        color_frame = ttk.Frame(frame)
        color_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.color_entry = ttk.Entry(color_frame, width=10)
        self.color_entry.pack(side=tk.LEFT, fill="x", expand=True)
        self.color_entry.insert(0, self.config.get("last_color", ""))

        # Predefined colors
        self.colors = {
            "White": "F0F0F0",
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

        self.color_var = tk.StringVar(value="Select Color")
        color_dropdown = ttk.OptionMenu(
            color_frame,
            self.color_var,
            "Select Color",
            *self.colors.keys(),
            command=self.select_predefined_color
        )
        color_dropdown.pack(side=tk.RIGHT, padx=5)

        # Apply button
        ttk.Button(frame, text="Apply Color", command=self.apply_color).grid(row=3, column=1, pady=10)

        # Status label
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)

        # Refresh devices on startup
        self.root.after(500, self.refresh_devices)

    def setup_settings_tab(self):
        frame = self.settings_tab

        # Package manager settings
        ttk.Label(frame, text="Package Manager:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pm_var = tk.StringVar(value=self.config.get("package_manager", "unknown"))
        pm_combo = ttk.Combobox(frame, textvariable=self.pm_var, values=["apt", "pacman", "dnf", "zypper", "flatpak", "unknown"])
        pm_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Install command
        ttk.Label(frame, text="Install Command:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.install_cmd_var = tk.StringVar(value=self.config.get("install_command", ""))
        ttk.Entry(frame, textvariable=self.install_cmd_var, width=30).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Package name
        ttk.Label(frame, text="Package Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.package_name_var = tk.StringVar(value=self.config.get("package_name", ""))
        ttk.Entry(frame, textvariable=self.package_name_var, width=30).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Systemd checkbox
        self.systemd_var = tk.BooleanVar(value=self.config.get("has_systemd", False))
        ttk.Checkbutton(frame, text="System uses systemd", variable=self.systemd_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Skip dependency check
        self.skip_check_var = tk.BooleanVar(value=self.config.get("skip_dependency_check", False))
        ttk.Checkbutton(frame, text="Skip dependency check on startup", variable=self.skip_check_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Save button
        ttk.Button(frame, text="Save Settings", command=self.save_settings).grid(row=5, column=0, columnspan=2, pady=10)

        # Reset button
        ttk.Button(frame, text="Reset to Defaults", command=self.reset_settings).grid(row=6, column=0, columnspan=2, pady=5)

    def save_settings(self):
        self.config["package_manager"] = self.pm_var.get()
        self.config["install_command"] = self.install_cmd_var.get()
        self.config["package_name"] = self.package_name_var.get()
        self.config["has_systemd"] = self.systemd_var.get()
        self.config["skip_dependency_check"] = self.skip_check_var.get()
        self.save_config()
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def reset_settings(self):
        self.pm_var.set(self.detect_package_manager())
        self.install_cmd_var.set(self.get_default_install_command())
        self.package_name_var.set(self.get_default_package_name())
        self.systemd_var.set(self.has_systemd())
        self.skip_check_var.set(False)

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
                    cmd = f"{self.config['install_command']} {self.config['package_name']}"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()

                    if process.returncode != 0:
                        messagebox.showerror("Error", f"Failed to install dependencies: {stderr.decode()}")
                        return False

                    if self.config.get("has_systemd", False):
                        subprocess.run(["sudo", "systemctl", "start", "ratbagd"], check=True)
                        subprocess.run(["sudo", "systemctl", "enable", "ratbagd"], check=True)

                    messagebox.showinfo("Success", "Dependencies installed successfully.")
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to install dependencies: {e}")
                    return False
            else:
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

            # Select the last used device or the first G915 if found
            last_device = self.config.get("last_device", "")
            if last_device and last_device in devices:
                self.device_combo.set(last_device)
            else:
                # Try to find a G915
                for device in devices:
                    if "G915" in device:
                        self.device_combo.set(device)
                        break
                else:
                    # Otherwise select the first device
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

            # Select the last used LED or the first one
            last_led = self.config.get("last_led", "")
            if last_led and last_led in leds:
                self.led_combo.set(last_led)
            else:
                self.led_combo.set(leds[0])

            self.status_label.config(text=f"Found {len(leds)} LEDs on {device}")

        except Exception as e:
            self.status_label.config(text=f"Error: {e}")

    def select_predefined_color(self, choice):
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, self.colors[choice])

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

        # Save the current selections to config
        self.config["last_device"] = device
        self.config["last_led"] = led
        self.config["last_color"] = color
        self.save_config()

        try:
            command = f'ratbagctl "{device}" led {led} set color {color}'
            subprocess.run(command, shell=True, check=True)
            self.status_label.config(text=f"Color changed successfully to #{color}")
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
        sys.exit(1)

if __name__ == "__main__":
    main()