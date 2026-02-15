# Home Assistant MQTT Agent for Windows

A Windows service that connects to Home Assistant via MQTT to control your PC remotely. Features include shutdown, reboot, sleep commands, system monitoring, and game detection.

## Features

- **Remote PC Control**: Shutdown, reboot, and sleep your PC from Home Assistant
- **Status Monitoring**: 
  - PC availability (online/offline)
  - CPU and memory usage
  - Game detection (know when games are running)
  - Sleep state monitoring
- **Custom Commands**: Execute predefined commands securely
- **Auto-discovery**: Automatically creates entities in Home Assistant
- **Windows Service**: Runs as a background Windows service

## Requirements

- Windows 10/11
- Python 3.10 or higher
- MQTT broker (Mosquitto recommended)
- Home Assistant instance
- Local ethernet connection

## Installation

### 1. Install Python Dependencies

```bash
# Using pip (if not using uv)
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -e .
```

### 2. Configure the Agent

Copy the example configuration file and edit it:

```bash
copy config.yaml.example config.yaml
```

Edit `config.yaml` with your settings:

```yaml
mqtt:
  broker: "192.168.1.100"  # Your MQTT broker IP
  port: 1883
  username: "your_username"  # Optional
  password: "your_password"  # Optional
  
homeassistant:
  device_name: "Gaming PC"
  device_id: "gaming_pc_01"
  
agent:
  status_update_interval: 30
  
  # Add folders where your games are installed
  # The agent will scan these at startup to find all game executables
  game_folders:
    - "C:\\Program Files (x86)\\Steam\\steamapps\\common"
    - "C:\\Program Files\\Epic Games"
    - "D:\\SteamLibrary\\steamapps\\common"  # Add all your game library folders
```

### 3. Test the Agent

Run the agent in console mode first to verify everything works:

```bash
python main.py
```

You should see:
- Connection to MQTT broker
- Auto-discovery messages sent to Home Assistant
- Status updates being published

Check Home Assistant - you should see a new device with buttons and sensors.

### 4. Install as Windows Service

Once tested, install as a Windows service (run as Administrator):

```bash
# Install the service
python main.py install

# Start the service
python main.py start

# Check service status in Windows Services (services.msc)
```

## Usage

### In Home Assistant

After the agent connects, you'll find a new device with:

**Buttons:**
- Shutdown - Shuts down the PC (5 second delay)
- Reboot - Reboots the PC (5 second delay)
- Sleep - Puts the PC to sleep

**Sensors:**
- Status - Shows if the PC is online/offline
- Game Running - Binary sensor showing if a game is detected
- CPU - Current CPU usage percentage
- Memory - Current memory usage percentage

### Manual MQTT Commands

You can also send commands directly via MQTT:

```bash
# Shutdown
mosquitto_pub -h 192.168.1.100 -t "hass_agent/gaming_pc_01/command" -m "shutdown"

# Reboot
mosquitto_pub -h 192.168.1.100 -t "hass_agent/gaming_pc_01/command" -m "reboot"

# Sleep
mosquitto_pub -h 192.168.1.100 -t "hass_agent/gaming_pc_01/command" -m "sleep"

# Custom command
mosquitto_pub -h 192.168.1.100 -t "hass_agent/gaming_pc_01/command" -m "custom:open_steam"
```

## Home Assistant Automation Examples

### Shutdown PC when leaving home

```yaml
automation:
  - alias: "Shutdown PC when leaving"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: 'not_home'
        for: '00:10:00'
    condition:
      - condition: state
        entity_id: binary_sensor.gaming_pc_game_running
        state: 'off'
    action:
      - service: button.press
        target:
          entity_id: button.gaming_pc_shutdown
```

### Wake and turn on PC

```yaml
automation:
  - alias: "Wake PC in the morning"
    trigger:
      - platform: time
        at: '08:00:00'
    action:
      - service: wake_on_lan.send_magic_packet
        data:
          mac: "AA:BB:CC:DD:EE:FF"  # Your PC's MAC address
```

### Notification when PC is available

```yaml
automation:
  - alias: "Notify when PC is ready"
    trigger:
      - platform: state
        entity_id: sensor.gaming_pc_status
        to: 'online'
    action:
      - service: notify.mobile_app
        data:
          message: "Gaming PC is now online and ready!"
```

## Service Management

```bash
# Start service
python main.py start

# Stop service
python main.py stop

# Restart service
python main.py restart

# Remove service
python main.py remove

# Update service after code changes
python main.py update
```

## Troubleshooting

### Service won't start
1. Check the log file `hass_mqtt_agent.log` in the installation directory
2. Verify `config.yaml` exists and is valid
3. Ensure MQTT broker is accessible from the PC

### Game detection not working
1. Add specific game executable names to `game_processes` in config.yaml
2. Use Task Manager to find exact process names
3. Check the log for detected processes (set log level to DEBUG)

### PC doesn't wake up
1. Verify Wake-on-LAN is enabled in BIOS
2. Check network adapter power management settings in Windows
3. Ensure the MAC address in Home Assistant is correct

### Commands not executing
1. Verify the agent is running (check availability sensor in HA)
2. Check MQTT broker logs
3. Review `hass_mqtt_agent.log` for errors

## Security Notes

- **No arbitrary commands**: Only predefined commands can be executed
- Commands must be defined in `config.yaml`
- Uses MQTT authentication (configure username/password)
- Consider using MQTT over TLS for production
- Run the service with least privileges needed

## Advanced Configuration

### Adding Custom Commands

Edit `config.yaml`:

```yaml
agent:
  custom_commands:
    open_steam: "C:\\Program Files (x86)\\Steam\\steam.exe"
    backup_data: "C:\\scripts\\backup.bat"
    close_browsers: "taskkill /F /IM chrome.exe /IM firefox.exe"
```

Send command via MQTT:
```bash
mosquitto_pub -t "hass_agent/gaming_pc_01/command" -m "custom:open_steam"
```

### Detecting Games

The agent scans your game installation folders at startup to automatically detect all installed games:

```yaml
agent:
  game_folders:
    - "C:\\Program Files (x86)\\Steam\\steamapps\\common"
    - "D:\\SteamLibrary\\steamapps\\common"  # Additional Steam library
    - "C:\\Program Files\\Epic Games"
    - "C:\\XboxGames"
    - "%PROGRAMFILES(X86)%\\GOG Galaxy\\Games"  # Can use env variables
```

When any executable from these folders runs, the agent detects it as gaming activity.
The scan happens once at startup - restart the service after installing new games.

## License

MIT License - Feel free to modify and use as needed.

## Contributing

Issues and pull requests welcome!

