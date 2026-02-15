#!/usr/bin/env python3
"""
Install HASS MQTT Agent as a systemd service on Linux
"""

import os
import sys
import subprocess
from pathlib import Path


SERVICE_TEMPLATE = """[Unit]
Description=Home Assistant MQTT Agent
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
ExecStart={python_path} {script_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""


def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        return False
    return True


def get_python_path():
    """Get the Python executable path"""
    return sys.executable


def get_script_path():
    """Get the main.py script path"""
    script_dir = Path(__file__).parent.parent
    return script_dir / "main.py"


def get_working_dir():
    """Get the working directory"""
    return Path(__file__).parent.parent


def get_current_user():
    """Get the user who invoked sudo"""
    return os.environ.get('SUDO_USER', os.environ.get('USER', 'root'))


def create_service_file():
    """Create systemd service file"""
    print("📝 Creating systemd service file...")

    user = get_current_user()
    python_path = get_python_path()
    script_path = get_script_path()
    working_dir = get_working_dir()

    service_content = SERVICE_TEMPLATE.format(
        user=user,
        python_path=python_path,
        script_path=script_path,
        working_dir=working_dir
    )

    service_path = Path("/etc/systemd/system/hass-mqtt-agent.service")

    try:
        with open(service_path, 'w') as f:
            f.write(service_content)

        print(f"✅ Service file created: {service_path}")
        return True

    except Exception as e:
        print(f"❌ Failed to create service file: {e}")
        return False


def reload_systemd():
    """Reload systemd daemon"""
    print("🔄 Reloading systemd daemon...")
    try:
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print("✅ Systemd daemon reloaded")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to reload systemd: {e}")
        return False


def enable_service():
    """Enable service to start on boot"""
    print("⚙️  Enabling service...")
    try:
        subprocess.run(["systemctl", "enable", "hass-mqtt-agent"], check=True)
        print("✅ Service enabled (will start on boot)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to enable service: {e}")
        return False


def start_service():
    """Start the service"""
    print("🚀 Starting service...")
    try:
        subprocess.run(["systemctl", "start", "hass-mqtt-agent"], check=True)
        print("✅ Service started")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start service: {e}")
        return False


def check_status():
    """Check service status"""
    print("\n" + "="*60)
    print("Service Status:")
    print("="*60)
    subprocess.run(["systemctl", "status", "hass-mqtt-agent", "--no-pager"])


def main():
    """Main installation process"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║    HASS MQTT Agent - Linux Systemd Service Installer      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Check if running as root
    if not check_root():
        return 1

    # Check if config exists
    config_path = get_working_dir() / "config.yaml"
    if not config_path.exists():
        print("⚠️  Warning: config.yaml not found!")
        print(f"   Expected at: {config_path}")
        print("\n   Please create a config file first:")
        print("   python scripts/setup_config.py")

        response = input("\n   Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Installation cancelled.")
            return 1

    # Install steps
    steps = [
        ("Creating service file", create_service_file),
        ("Reloading systemd", reload_systemd),
        ("Enabling service", enable_service),
        ("Starting service", start_service),
    ]

    print("\nInstallation Steps:")
    print("-" * 60)

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Installation failed at: {step_name}")
            return 1

    # Show status
    check_status()

    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                   Installation Complete!                   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

Service Management Commands:
  sudo systemctl start hass-mqtt-agent       # Start service
  sudo systemctl stop hass-mqtt-agent        # Stop service
  sudo systemctl restart hass-mqtt-agent     # Restart service
  sudo systemctl status hass-mqtt-agent      # Check status
  sudo systemctl disable hass-mqtt-agent     # Disable auto-start
  
  sudo journalctl -u hass-mqtt-agent -f      # View logs (follow)
  sudo journalctl -u hass-mqtt-agent -n 50   # View last 50 log lines

Log file location:
  {working_dir}/hass_mqtt_agent.log

To uninstall:
  sudo systemctl stop hass-mqtt-agent
  sudo systemctl disable hass-mqtt-agent
  sudo rm /etc/systemd/system/hass-mqtt-agent.service
  sudo systemctl daemon-reload
    """.format(working_dir=get_working_dir()))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

