#!/usr/bin/env python3
"""
Terminal-based configuration setup for HASS MQTT Agent
Interactive CLI wizard to create config.yaml
"""

import os
import sys
import yaml
from pathlib import Path


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def get_input(prompt, default=None, required=True):
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]"

    prompt += ": "

    while True:
        value = input(prompt).strip()

        if not value and default:
            return default

        if not value and required:
            print("  ⚠️  This field is required. Please enter a value.")
            continue

        return value


def get_yes_no(prompt, default=True):
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()

        if not response:
            return default

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("  ⚠️  Please enter 'y' or 'n'")


def get_game_folders():
    """Get game folder paths from user"""
    print("\n📁 Game Folder Configuration")
    print("   Enter folders where games are installed (one per line)")
    print("   Press Enter on empty line when done\n")

    # Suggest default folders based on platform
    suggestions = []
    if sys.platform == "win32":
        suggestions = [
            "C:\\Program Files (x86)\\Steam\\steamapps\\common",
            "C:\\Program Files\\Epic Games",
            "C:\\XboxGames"
        ]
    elif sys.platform.startswith("linux"):
        home = os.path.expanduser("~")
        suggestions = [
            f"{home}/.steam/steam/steamapps/common",
            f"{home}/.local/share/Steam/steamapps/common",
            f"{home}/Games"
        ]

    if suggestions:
        print("   Common locations:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        print()

    folders = []
    folder_num = 1

    while True:
        folder = input(f"   Folder {folder_num}: ").strip()

        if not folder:
            break

        # Expand paths
        folder = os.path.expanduser(folder)
        folder = os.path.expandvars(folder)

        if os.path.exists(folder):
            folders.append(folder)
            print(f"   ✓ Added: {folder}")
            folder_num += 1
        else:
            print(f"   ⚠️  Warning: Folder not found, but will add anyway: {folder}")
            if get_yes_no("   Add this folder anyway?", default=True):
                folders.append(folder)
                folder_num += 1

    return folders


def get_custom_commands():
    """Get custom commands from user"""
    print("\n⚙️  Custom Commands Configuration (optional)")
    print("   Define custom commands that can be executed remotely")
    print("   Format: command_name = shell command")
    print("   Press Enter on empty name when done\n")

    commands = {}

    while True:
        name = input("   Command name: ").strip()

        if not name:
            break

        command = input(f"   Command for '{name}': ").strip()

        if command:
            commands[name] = command
            print(f"   ✓ Added command: {name}")
        else:
            print("   ⚠️  Skipped (empty command)")

    return commands


def main():
    """Main setup wizard"""
    clear_screen()

    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        Home Assistant MQTT Agent - Setup Wizard           ║
║                                                            ║
║    This wizard will help you create your config.yaml      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)

    input("Press Enter to begin...")

    config = {}

    # MQTT Configuration
    clear_screen()
    print_header("MQTT Broker Configuration")

    config['mqtt'] = {}
    config['mqtt']['broker'] = get_input("MQTT Broker IP address", default="192.168.1.100")
    config['mqtt']['port'] = int(get_input("MQTT Broker port", default="1883"))

    if get_yes_no("Does your MQTT broker require authentication?", default=True):
        config['mqtt']['username'] = get_input("MQTT Username")
        config['mqtt']['password'] = get_input("MQTT Password")
    else:
        config['mqtt']['username'] = ""
        config['mqtt']['password'] = ""

    config['mqtt']['client_id'] = get_input("MQTT Client ID", default="hass_pc_agent")

    # Home Assistant Configuration
    clear_screen()
    print_header("Home Assistant Configuration")

    config['homeassistant'] = {}
    config['homeassistant']['discovery_prefix'] = get_input(
        "Discovery prefix",
        default="homeassistant"
    )

    # Suggest hostname as device name
    import socket
    default_name = socket.gethostname()

    config['homeassistant']['device_name'] = get_input(
        "Device name (shown in Home Assistant)",
        default=default_name
    )

    # Generate device_id from device name
    default_id = config['homeassistant']['device_name'].lower().replace(" ", "_").replace("-", "_")
    config['homeassistant']['device_id'] = get_input(
        "Device ID (unique identifier)",
        default=default_id
    )

    # Agent Configuration
    clear_screen()
    print_header("Agent Configuration")

    config['agent'] = {}
    config['agent']['status_update_interval'] = int(get_input(
        "Status update interval (seconds)",
        default="30"
    ))

    # Game Folders
    clear_screen()
    if get_yes_no("Do you want to configure game detection?", default=True):
        config['agent']['game_folders'] = get_game_folders()
    else:
        config['agent']['game_folders'] = []

    # Custom Commands
    clear_screen()
    if get_yes_no("Do you want to add custom commands?", default=False):
        config['agent']['custom_commands'] = get_custom_commands()
    else:
        config['agent']['custom_commands'] = {}

    # Save configuration
    clear_screen()
    print_header("Configuration Summary")

    print(f"""
MQTT Broker:        {config['mqtt']['broker']}:{config['mqtt']['port']}
Authentication:     {'Yes' if config['mqtt']['username'] else 'No'}
Device Name:        {config['homeassistant']['device_name']}
Device ID:          {config['homeassistant']['device_id']}
Update Interval:    {config['agent']['status_update_interval']}s
Game Folders:       {len(config['agent']['game_folders'])} configured
Custom Commands:    {len(config['agent']['custom_commands'])} configured
    """)

    if not get_yes_no("Save this configuration?", default=True):
        print("\n❌ Configuration cancelled.")
        return 1

    # Determine config file path
    script_dir = Path(__file__).parent.parent
    config_path = script_dir / "config.yaml"

    # Backup existing config if it exists
    if config_path.exists():
        backup_path = script_dir / "config.yaml.backup"
        print(f"\n📦 Backing up existing config to: {backup_path}")
        import shutil
        shutil.copy(config_path, backup_path)

    # Write configuration
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"\n✅ Configuration saved to: {config_path}")
        print("\n🚀 You can now start the agent with:")
        print("   python main.py")

        if sys.platform == "win32":
            print("\n   Or install as a service:")
            print("   python main.py install")
        elif sys.platform.startswith("linux"):
            print("\n   Or install as a systemd service:")
            print("   sudo python scripts/install_systemd.py")

        return 0

    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

