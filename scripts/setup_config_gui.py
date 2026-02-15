#!/usr/bin/env python3
"""
GUI-based configuration setup for HASS MQTT Agent
Interactive GUI wizard to create config.yaml using tkinter
"""

import os
import sys
import yaml
import socket
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
except ImportError:
    print("Error: tkinter is not available.")
    print("On Linux, install with: sudo apt-get install python3-tk")
    sys.exit(1)


class SetupWizard:
    """GUI Setup Wizard for HASS MQTT Agent"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HASS MQTT Agent - Configuration Wizard")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Configuration data
        self.config = {
            'mqtt': {},
            'homeassistant': {},
            'agent': {
                'game_folders': [],
                'custom_commands': {}
            }
        }

        # Current page
        self.current_page = 0
        self.pages = []

        # Create UI
        self.create_widgets()
        self.show_page(0)

    def create_widgets(self):
        """Create main UI structure"""
        # Header
        header = tk.Frame(self.root, bg="#2196F3", height=80)
        header.pack(fill=tk.X)

        title_label = tk.Label(
            header,
            text="HASS MQTT Agent Setup",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=20)

        # Content area
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)

        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            command=self.previous_page,
            width=10
        )
        self.back_btn.pack(side=tk.LEFT)

        self.next_btn = tk.Button(
            nav_frame,
            text="Next →",
            command=self.next_page,
            width=10,
            bg="#4CAF50",
            fg="white"
        )
        self.next_btn.pack(side=tk.RIGHT)

        # Create all pages
        self.create_welcome_page()
        self.create_mqtt_page()
        self.create_homeassistant_page()
        self.create_agent_page()
        self.create_games_page()
        self.create_commands_page()
        self.create_summary_page()

    def create_welcome_page(self):
        """Create welcome page"""
        page = tk.Frame(self.content_frame)

        welcome_text = """
Welcome to the HASS MQTT Agent Configuration Wizard!

This wizard will guide you through setting up your
Home Assistant MQTT Agent.

You will configure:
  • MQTT Broker connection
  • Home Assistant integration
  • Game detection (optional)
  • Custom commands (optional)

Click 'Next' to begin.
        """

        label = tk.Label(
            page,
            text=welcome_text,
            font=("Arial", 12),
            justify=tk.LEFT
        )
        label.pack(pady=50)

        self.pages.append(page)

    def create_mqtt_page(self):
        """Create MQTT configuration page"""
        page = tk.Frame(self.content_frame)

        tk.Label(page, text="MQTT Broker Configuration", font=("Arial", 14, "bold")).pack(pady=10)

        # Broker IP
        tk.Label(page, text="Broker IP Address:").pack(anchor=tk.W, pady=(10, 0))
        self.mqtt_broker = tk.Entry(page, width=40)
        self.mqtt_broker.insert(0, "192.168.1.100")
        self.mqtt_broker.pack(pady=5)

        # Port
        tk.Label(page, text="Port:").pack(anchor=tk.W, pady=(10, 0))
        self.mqtt_port = tk.Entry(page, width=40)
        self.mqtt_port.insert(0, "1883")
        self.mqtt_port.pack(pady=5)

        # Authentication
        self.mqtt_auth = tk.BooleanVar(value=True)
        tk.Checkbutton(
            page,
            text="Require Authentication",
            variable=self.mqtt_auth,
            command=self.toggle_mqtt_auth
        ).pack(anchor=tk.W, pady=10)

        # Username
        self.mqtt_username_label = tk.Label(page, text="Username:")
        self.mqtt_username_label.pack(anchor=tk.W, pady=(10, 0))
        self.mqtt_username = tk.Entry(page, width=40)
        self.mqtt_username.pack(pady=5)

        # Password
        self.mqtt_password_label = tk.Label(page, text="Password:")
        self.mqtt_password_label.pack(anchor=tk.W, pady=(10, 0))
        self.mqtt_password = tk.Entry(page, width=40, show="*")
        self.mqtt_password.pack(pady=5)

        # Client ID
        tk.Label(page, text="Client ID:").pack(anchor=tk.W, pady=(10, 0))
        self.mqtt_client_id = tk.Entry(page, width=40)
        self.mqtt_client_id.insert(0, "hass_pc_agent")
        self.mqtt_client_id.pack(pady=5)

        self.pages.append(page)

    def toggle_mqtt_auth(self):
        """Toggle MQTT authentication fields"""
        state = tk.NORMAL if self.mqtt_auth.get() else tk.DISABLED
        self.mqtt_username.config(state=state)
        self.mqtt_password.config(state=state)

    def create_homeassistant_page(self):
        """Create Home Assistant configuration page"""
        page = tk.Frame(self.content_frame)

        tk.Label(page, text="Home Assistant Configuration", font=("Arial", 14, "bold")).pack(pady=10)

        # Discovery prefix
        tk.Label(page, text="Discovery Prefix:").pack(anchor=tk.W, pady=(10, 0))
        self.ha_discovery = tk.Entry(page, width=40)
        self.ha_discovery.insert(0, "homeassistant")
        self.ha_discovery.pack(pady=5)

        # Device name
        tk.Label(page, text="Device Name:").pack(anchor=tk.W, pady=(10, 0))
        tk.Label(page, text="(How this PC appears in Home Assistant)", font=("Arial", 9), fg="gray").pack(anchor=tk.W)
        self.ha_device_name = tk.Entry(page, width=40)
        self.ha_device_name.insert(0, socket.gethostname())
        self.ha_device_name.pack(pady=5)

        # Device ID
        tk.Label(page, text="Device ID:").pack(anchor=tk.W, pady=(10, 0))
        tk.Label(page, text="(Unique identifier - use lowercase, underscores)", font=("Arial", 9), fg="gray").pack(anchor=tk.W)
        self.ha_device_id = tk.Entry(page, width=40)
        default_id = socket.gethostname().lower().replace(" ", "_").replace("-", "_")
        self.ha_device_id.insert(0, default_id)
        self.ha_device_id.pack(pady=5)

        self.pages.append(page)

    def create_agent_page(self):
        """Create agent configuration page"""
        page = tk.Frame(self.content_frame)

        tk.Label(page, text="Agent Configuration", font=("Arial", 14, "bold")).pack(pady=10)

        # Update interval
        tk.Label(page, text="Status Update Interval (seconds):").pack(anchor=tk.W, pady=(10, 0))
        tk.Label(page, text="(How often to report PC status to Home Assistant)", font=("Arial", 9), fg="gray").pack(anchor=tk.W)
        self.agent_interval = tk.Entry(page, width=40)
        self.agent_interval.insert(0, "30")
        self.agent_interval.pack(pady=5)

        self.pages.append(page)

    def create_games_page(self):
        """Create game folders configuration page"""
        page = tk.Frame(self.content_frame)

        tk.Label(page, text="Game Folder Configuration", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(
            page,
            text="Add folders where games are installed for automatic game detection",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=5)

        # Listbox with scrollbar
        list_frame = tk.Frame(page)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.game_folders_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.game_folders_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.game_folders_list.yview)

        # Buttons
        btn_frame = tk.Frame(page)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add Folder", command=self.add_game_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_game_folder).pack(side=tk.LEFT, padx=5)

        # Add default suggestions
        self.suggest_game_folders()

        self.pages.append(page)

    def suggest_game_folders(self):
        """Suggest default game folders based on platform"""
        suggestions = []

        if sys.platform == "win32":
            suggestions = [
                "C:\\Program Files (x86)\\Steam\\steamapps\\common",
                "C:\\Program Files\\Epic Games",
            ]
        elif sys.platform.startswith("linux"):
            home = os.path.expanduser("~")
            suggestions = [
                f"{home}/.steam/steam/steamapps/common",
                f"{home}/.local/share/Steam/steamapps/common",
            ]

        for folder in suggestions:
            if os.path.exists(folder):
                self.game_folders_list.insert(tk.END, folder)

    def add_game_folder(self):
        """Add a game folder"""
        folder = filedialog.askdirectory(title="Select Game Folder")
        if folder:
            self.game_folders_list.insert(tk.END, folder)

    def remove_game_folder(self):
        """Remove selected game folder"""
        selection = self.game_folders_list.curselection()
        if selection:
            self.game_folders_list.delete(selection[0])

    def create_commands_page(self):
        """Create custom commands configuration page"""
        page = tk.Frame(self.content_frame)

        tk.Label(page, text="Custom Commands (Optional)", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(
            page,
            text="Define custom commands that can be executed remotely",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=5)

        # Commands list
        self.commands_text = scrolledtext.ScrolledText(page, height=10, width=60)
        self.commands_text.pack(pady=10, fill=tk.BOTH, expand=True)

        help_text = """# Enter custom commands in the format:
# command_name: shell command
#
# Example (Windows):
# open_steam: C:\\Program Files (x86)\\Steam\\steam.exe
#
# Example (Linux):
# open_firefox: firefox
"""
        self.commands_text.insert("1.0", help_text)

        self.pages.append(page)

    def create_summary_page(self):
        """Create summary/confirmation page"""
        page = tk.Frame(self.content_frame)

        tk.Label(page, text="Configuration Summary", font=("Arial", 14, "bold")).pack(pady=10)

        self.summary_text = scrolledtext.ScrolledText(page, height=20, width=60, state=tk.DISABLED)
        self.summary_text.pack(pady=10, fill=tk.BOTH, expand=True)

        self.pages.append(page)

    def show_page(self, index):
        """Show a specific page"""
        # Hide all pages
        for page in self.pages:
            page.pack_forget()

        # Show current page
        if 0 <= index < len(self.pages):
            self.current_page = index
            self.pages[index].pack(fill=tk.BOTH, expand=True)

            # Update buttons
            self.back_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)

            if index == len(self.pages) - 1:
                # Last page - show Save button
                self.next_btn.config(text="Save & Finish", bg="#4CAF50")
            else:
                self.next_btn.config(text="Next →", bg="#2196F3")

            # Update summary on last page
            if index == len(self.pages) - 1:
                self.update_summary()

    def next_page(self):
        """Go to next page"""
        if self.current_page == len(self.pages) - 1:
            # Last page - save configuration
            self.save_configuration()
        else:
            # Collect data from current page
            self.collect_page_data()
            self.show_page(self.current_page + 1)

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def collect_page_data(self):
        """Collect data from current page"""
        if self.current_page == 1:  # MQTT page
            self.config['mqtt']['broker'] = self.mqtt_broker.get()
            self.config['mqtt']['port'] = int(self.mqtt_port.get())
            self.config['mqtt']['client_id'] = self.mqtt_client_id.get()

            if self.mqtt_auth.get():
                self.config['mqtt']['username'] = self.mqtt_username.get()
                self.config['mqtt']['password'] = self.mqtt_password.get()
            else:
                self.config['mqtt']['username'] = ""
                self.config['mqtt']['password'] = ""

        elif self.current_page == 2:  # Home Assistant page
            self.config['homeassistant']['discovery_prefix'] = self.ha_discovery.get()
            self.config['homeassistant']['device_name'] = self.ha_device_name.get()
            self.config['homeassistant']['device_id'] = self.ha_device_id.get()

        elif self.current_page == 3:  # Agent page
            self.config['agent']['status_update_interval'] = int(self.agent_interval.get())

        elif self.current_page == 4:  # Games page
            folders = []
            for i in range(self.game_folders_list.size()):
                folders.append(self.game_folders_list.get(i))
            self.config['agent']['game_folders'] = folders

        elif self.current_page == 5:  # Commands page
            commands = {}
            text = self.commands_text.get("1.0", tk.END)
            for line in text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        name, cmd = line.split(':', 1)
                        commands[name.strip()] = cmd.strip()
            self.config['agent']['custom_commands'] = commands

    def update_summary(self):
        """Update the summary text"""
        self.collect_page_data()

        summary = f"""
MQTT Configuration:
  Broker:          {self.config['mqtt']['broker']}:{self.config['mqtt']['port']}
  Client ID:       {self.config['mqtt']['client_id']}
  Authentication:  {'Yes' if self.config['mqtt'].get('username') else 'No'}

Home Assistant Configuration:
  Discovery Prefix: {self.config['homeassistant']['discovery_prefix']}
  Device Name:      {self.config['homeassistant']['device_name']}
  Device ID:        {self.config['homeassistant']['device_id']}

Agent Configuration:
  Update Interval:  {self.config['agent']['status_update_interval']} seconds
  Game Folders:     {len(self.config['agent']['game_folders'])} configured
  Custom Commands:  {len(self.config['agent']['custom_commands'])} configured

Game Folders:
"""

        for folder in self.config['agent']['game_folders']:
            summary += f"  • {folder}\n"

        if self.config['agent']['custom_commands']:
            summary += "\nCustom Commands:\n"
            for name in self.config['agent']['custom_commands']:
                summary += f"  • {name}\n"

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", summary)
        self.summary_text.config(state=tk.DISABLED)

    def save_configuration(self):
        """Save configuration to file"""
        # Get script directory
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config.yaml"

        # Check if config exists
        if config_path.exists():
            if not messagebox.askyesno(
                "Overwrite Configuration",
                "Configuration file already exists. Overwrite?"
            ):
                return

            # Backup existing
            backup_path = script_dir / "config.yaml.backup"
            import shutil
            shutil.copy(config_path, backup_path)

        # Save
        try:
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

            messagebox.showinfo(
                "Success",
                f"Configuration saved to:\n{config_path}\n\n"
                "You can now start the agent with:\npython main.py"
            )

            self.root.quit()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def run(self):
        """Run the wizard"""
        self.root.mainloop()


def main():
    """Main entry point"""
    wizard = SetupWizard()
    wizard.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

