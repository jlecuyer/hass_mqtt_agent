"""
Home Assistant MQTT Agent for Windows PC Control
Provides remote control and status monitoring for Windows PCs via MQTT
"""

import json
import logging
import os
import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Optional, List
import yaml

import paho.mqtt.client as mqtt
import psutil

# Windows-specific imports
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import win32api
    import win32con
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False
    print("Warning: pywin32 not available. Service mode will not work.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hass_mqtt_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PCStatusMonitor:
    """Monitor PC status including sleep state and running games"""

    def __init__(self, game_folders: List[str]):
        self.game_folders = game_folders or []
        self.game_executables: set = set()
        self._scan_game_folders()

    def _scan_game_folders(self):
        """Scan game folders for executables"""
        if not self.game_folders:
            logger.info("No game folders configured for monitoring")
            return

        logger.info(f"Scanning {len(self.game_folders)} game folder(s) for executables...")

        for folder_path in self.game_folders:
            try:
                # Expand environment variables and resolve path
                expanded_path = os.path.expandvars(folder_path)
                if not os.path.exists(expanded_path):
                    logger.warning(f"Game folder not found: {expanded_path}")
                    continue

                # Scan for .exe files
                exe_count = 0
                for root, dirs, files in os.walk(expanded_path):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            # Store just the executable name (lowercase for comparison)
                            self.game_executables.add(file.lower())
                            exe_count += 1

                logger.info(f"Found {exe_count} executable(s) in: {expanded_path}")

            except Exception as e:
                logger.error(f"Error scanning game folder {folder_path}: {e}")

        logger.info(f"Total game executables tracked: {len(self.game_executables)}")

    def rescan_game_folders(self):
        """Rescan game folders (useful if games are installed/uninstalled)"""
        self.game_executables.clear()
        self._scan_game_folders()

    def is_game_running(self) -> bool:
        """Check if any game process is running"""
        if not self.game_executables:
            return False

        try:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and proc_name.lower() in self.game_executables:
                        # Additional validation: check if the process path is in a game folder
                        try:
                            proc_exe = proc.info.get('exe', '')
                            if proc_exe:
                                for game_folder in self.game_folders:
                                    expanded_folder = os.path.expandvars(game_folder)
                                    if expanded_folder.lower() in proc_exe.lower():
                                        logger.info(f"Detected game running: {proc_name} from {proc_exe}")
                                        return True
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            # If we can't get the full path, just trust the name match
                            logger.info(f"Detected game running: {proc_name}")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error checking game processes: {e}")
        return False

    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "memory_available_gb": round(memory.available / (1024**3), 2)
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}

    @staticmethod
    def is_system_sleeping() -> bool:
        """Check if system is in sleep mode (this is tricky on Windows)"""
        # This is a simplified check - if the service is running, the PC is not sleeping
        # A more sophisticated approach would involve monitoring power events
        return False


class HASSMQTTAgent:
    """Main agent class for HASS MQTT communication"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.mqtt_client: Optional[mqtt.Client] = None
        self.status_monitor: Optional[PCStatusMonitor] = None
        self.running = False
        self.status_thread: Optional[threading.Thread] = None

        # MQTT topics
        device_id = self.config['homeassistant']['device_id']
        self.base_topic = f"hass_agent/{device_id}"
        self.availability_topic = f"{self.base_topic}/availability"
        self.state_topic = f"{self.base_topic}/state"
        self.command_topic = f"{self.base_topic}/command"

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            logger.info("Please copy config.yaml.example to config.yaml and update it")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)

    def _setup_mqtt(self):
        """Setup MQTT client and callbacks"""
        mqtt_config = self.config['mqtt']

        self.mqtt_client = mqtt.Client(
            client_id=mqtt_config.get('client_id', 'hass_pc_agent'),
            protocol=mqtt.MQTTv311
        )

        # Set username/password if provided
        if mqtt_config.get('username') and mqtt_config.get('password'):
            self.mqtt_client.username_pw_set(
                mqtt_config['username'],
                mqtt_config['password']
            )

        # Set will message (offline status)
        self.mqtt_client.will_set(
            self.availability_topic,
            payload="offline",
            qos=1,
            retain=True
        )

        # Set callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect

        # Connect to broker
        try:
            logger.info(f"Connecting to MQTT broker at {mqtt_config['broker']}:{mqtt_config['port']}")
            self.mqtt_client.connect(
                mqtt_config['broker'],
                mqtt_config.get('port', 1883),
                60
            )
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker")

            # Subscribe to command topic
            client.subscribe(self.command_topic, qos=1)
            logger.info(f"Subscribed to {self.command_topic}")

            # Publish availability
            client.publish(self.availability_topic, "online", qos=1, retain=True)

            # Publish Home Assistant discovery messages
            self._publish_discovery()

            # Publish initial state
            self._publish_state()
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")

    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received command: {payload}")

            # Execute command
            self._execute_command(payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _execute_command(self, command: str):
        """Execute a command based on the payload"""
        try:
            if command == "shutdown":
                logger.info("Executing shutdown command")
                self._shutdown_pc()
            elif command == "reboot":
                logger.info("Executing reboot command")
                self._reboot_pc()
            elif command == "sleep":
                logger.info("Executing sleep command")
                self._sleep_pc()
            elif command.startswith("custom:"):
                # Execute custom predefined command
                custom_cmd = command.replace("custom:", "")
                self._execute_custom_command(custom_cmd)
            else:
                logger.warning(f"Unknown command: {command}")

        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")

    def _shutdown_pc(self):
        """Shutdown the PC"""
        try:
            if sys.platform == "win32":
                subprocess.run(["shutdown", "/s", "/t", "5", "/c", "Shutdown requested via Home Assistant"])
            else:
                logger.warning("Shutdown command only supported on Windows")
        except Exception as e:
            logger.error(f"Error shutting down PC: {e}")

    def _reboot_pc(self):
        """Reboot the PC"""
        try:
            if sys.platform == "win32":
                subprocess.run(["shutdown", "/r", "/t", "5", "/c", "Reboot requested via Home Assistant"])
            else:
                logger.warning("Reboot command only supported on Windows")
        except Exception as e:
            logger.error(f"Error rebooting PC: {e}")

    def _sleep_pc(self):
        """Put PC to sleep"""
        try:
            if sys.platform == "win32":
                # Use rundll32 to call the sleep function
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            else:
                logger.warning("Sleep command only supported on Windows")
        except Exception as e:
            logger.error(f"Error putting PC to sleep: {e}")

    def _execute_custom_command(self, command_name: str):
        """Execute a predefined custom command"""
        custom_commands = self.config.get('agent', {}).get('custom_commands', {})

        if command_name in custom_commands:
            cmd = custom_commands[command_name]
            logger.info(f"Executing custom command '{command_name}': {cmd}")
            try:
                subprocess.Popen(cmd, shell=True)
            except Exception as e:
                logger.error(f"Error executing custom command: {e}")
        else:
            logger.warning(f"Custom command not found: {command_name}")

    def _publish_discovery(self):
        """Publish Home Assistant MQTT discovery messages"""
        device_config = self.config['homeassistant']
        device_name = device_config['device_name']
        device_id = device_config['device_id']
        discovery_prefix = device_config.get('discovery_prefix', 'homeassistant')

        # Device information
        device_info = {
            "identifiers": [device_id],
            "name": device_name,
            "manufacturer": "Custom",
            "model": "HASS MQTT Agent",
            "sw_version": "0.1.0"
        }

        # Sensor: PC Status
        status_sensor_config = {
            "name": f"{device_name} Status",
            "unique_id": f"{device_id}_status",
            "state_topic": self.state_topic,
            "value_template": "{{ value_json.status }}",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:desktop-tower"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/sensor/{device_id}/status/config",
            json.dumps(status_sensor_config),
            qos=1,
            retain=True
        )

        # Binary Sensor: Game Running
        game_sensor_config = {
            "name": f"{device_name} Game Running",
            "unique_id": f"{device_id}_game_running",
            "state_topic": self.state_topic,
            "value_template": "{{ value_json.game_running }}",
            "payload_on": True,
            "payload_off": False,
            "availability_topic": self.availability_topic,
            "device": device_info,
            "device_class": "running",
            "icon": "mdi:gamepad-variant"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/binary_sensor/{device_id}/game_running/config",
            json.dumps(game_sensor_config),
            qos=1,
            retain=True
        )

        # Sensor: CPU Usage
        cpu_sensor_config = {
            "name": f"{device_name} CPU",
            "unique_id": f"{device_id}_cpu",
            "state_topic": self.state_topic,
            "value_template": "{{ value_json.cpu_percent }}",
            "unit_of_measurement": "%",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:chip"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/sensor/{device_id}/cpu/config",
            json.dumps(cpu_sensor_config),
            qos=1,
            retain=True
        )

        # Sensor: Memory Usage
        memory_sensor_config = {
            "name": f"{device_name} Memory",
            "unique_id": f"{device_id}_memory",
            "state_topic": self.state_topic,
            "value_template": "{{ value_json.memory_percent }}",
            "unit_of_measurement": "%",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:memory"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/sensor/{device_id}/memory/config",
            json.dumps(memory_sensor_config),
            qos=1,
            retain=True
        )

        # Button: Shutdown
        shutdown_button_config = {
            "name": f"{device_name} Shutdown",
            "unique_id": f"{device_id}_shutdown",
            "command_topic": self.command_topic,
            "payload_press": "shutdown",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:power"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/button/{device_id}/shutdown/config",
            json.dumps(shutdown_button_config),
            qos=1,
            retain=True
        )

        # Button: Reboot
        reboot_button_config = {
            "name": f"{device_name} Reboot",
            "unique_id": f"{device_id}_reboot",
            "command_topic": self.command_topic,
            "payload_press": "reboot",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:restart"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/button/{device_id}/reboot/config",
            json.dumps(reboot_button_config),
            qos=1,
            retain=True
        )

        # Button: Sleep
        sleep_button_config = {
            "name": f"{device_name} Sleep",
            "unique_id": f"{device_id}_sleep",
            "command_topic": self.command_topic,
            "payload_press": "sleep",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:sleep"
        }
        self.mqtt_client.publish(
            f"{discovery_prefix}/button/{device_id}/sleep/config",
            json.dumps(sleep_button_config),
            qos=1,
            retain=True
        )

        logger.info("Published Home Assistant discovery messages")

    def _publish_state(self):
        """Publish current state"""
        try:
            game_running = self.status_monitor.is_game_running()
            system_info = self.status_monitor.get_system_info()
            sleeping = self.status_monitor.is_system_sleeping()

            state = {
                "status": "online",
                "game_running": game_running,
                "sleeping": sleeping,
                **system_info
            }

            self.mqtt_client.publish(
                self.state_topic,
                json.dumps(state),
                qos=1,
                retain=True
            )

            logger.debug(f"Published state: {state}")

        except Exception as e:
            logger.error(f"Error publishing state: {e}")

    def _status_update_loop(self):
        """Background thread for periodic status updates"""
        update_interval = self.config.get('agent', {}).get('status_update_interval', 30)

        while self.running:
            try:
                self._publish_state()
                time.sleep(update_interval)
            except Exception as e:
                logger.error(f"Error in status update loop: {e}")
                time.sleep(5)

    def start(self):
        """Start the agent"""
        logger.info("Starting HASS MQTT Agent")

        # Initialize status monitor
        game_folders = self.config.get('agent', {}).get('game_folders', [])
        self.status_monitor = PCStatusMonitor(game_folders)

        # Setup and start MQTT
        self._setup_mqtt()
        self.mqtt_client.loop_start()

        # Start status update thread
        self.running = True
        self.status_thread = threading.Thread(target=self._status_update_loop, daemon=True)
        self.status_thread.start()

        logger.info("HASS MQTT Agent started successfully")

    def stop(self):
        """Stop the agent"""
        logger.info("Stopping HASS MQTT Agent")

        # Stop status updates
        self.running = False
        if self.status_thread:
            self.status_thread.join(timeout=5)

        # Publish offline status
        if self.mqtt_client:
            self.mqtt_client.publish(self.availability_topic, "offline", qos=1, retain=True)
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        logger.info("HASS MQTT Agent stopped")


# Windows Service wrapper
if WINDOWS_SERVICE_AVAILABLE:
    class HASSMQTTService(win32serviceutil.ServiceFramework):
        _svc_name_ = "HASSMQTTAgent"
        _svc_display_name_ = "Home Assistant MQTT Agent"
        _svc_description_ = "Windows service for Home Assistant PC control via MQTT"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self.agent: Optional[HASSMQTTAgent] = None

        def SvcStop(self):
            """Stop the service"""
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)
            if self.agent:
                self.agent.stop()

        def SvcDoRun(self):
            """Run the service"""
            try:
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STARTED,
                    (self._svc_name_, '')
                )

                # Change to script directory to find config file
                script_dir = os.path.dirname(os.path.abspath(__file__))
                os.chdir(script_dir)

                # Start the agent
                self.agent = HASSMQTTAgent()
                self.agent.start()

                # Wait for stop signal
                win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

            except Exception as e:
                logger.error(f"Service error: {e}")
                servicemanager.LogErrorMsg(f"Service error: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Handle Windows service commands
        if WINDOWS_SERVICE_AVAILABLE:
            if sys.argv[1] in ['install', 'update', 'remove', 'start', 'stop', 'restart']:
                win32serviceutil.HandleCommandLine(HASSMQTTService)
                return

    # Run as console application
    print("Home Assistant MQTT Agent")
    print("=" * 50)

    # Check if config exists
    if not os.path.exists('config.yaml'):
        print("Error: config.yaml not found!")
        print("Please copy config.yaml.example to config.yaml and update it with your settings.")
        return

    try:
        agent = HASSMQTTAgent()
        agent.start()

        print("\nAgent is running. Press Ctrl+C to stop.")

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping agent...")
        if 'agent' in locals():
            agent.stop()
        print("Agent stopped.")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        if 'agent' in locals():
            agent.stop()


if __name__ == '__main__':
    main()

