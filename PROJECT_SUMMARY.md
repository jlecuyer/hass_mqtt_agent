# Home Assistant MQTT Agent - Project Summary

## Overview

A complete Windows service solution for controlling and monitoring your PC from Home Assistant via MQTT over local ethernet.

## What This Does

✅ **Remote PC Control**
- Shutdown, reboot, and sleep commands from Home Assistant
- Secure - only predefined commands can be executed
- 5-second delay on shutdown/reboot for safety

✅ **Status Monitoring**
- Online/offline availability tracking
- CPU usage monitoring
- Memory usage monitoring  
- Game detection (know when games are running)
- Sleep state detection

✅ **Home Assistant Integration**
- Automatic entity discovery (no manual configuration needed)
- Creates buttons for shutdown/reboot/sleep
- Creates sensors for status, game running, CPU, memory
- Full availability tracking

✅ **Windows Service**
- Runs as background Windows service
- Starts automatically on boot
- Reliable and persistent

## Project Structure

```
hass_mqtt_agent/
├── main.py                          # Main agent code
├── config.yaml.example              # Configuration template
├── requirements.txt                 # Python dependencies
├── install.ps1                      # Windows installation script
├── README.md                        # Main documentation
├── TROUBLESHOOTING.md              # Troubleshooting guide
└── homeassistant_examples.yaml     # Home Assistant config examples
```

## Quick Start

### On Windows PC:

1. **Install Python 3.10+** from python.org

2. **Clone/download this project** to your PC

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure:**
   ```powershell
   copy config.yaml.example config.yaml
   notepad config.yaml
   ```
   
   Update with your MQTT broker IP and settings.

5. **Test it:**
   ```powershell
   python main.py
   ```
   
   Verify it connects to MQTT and check Home Assistant for new device.

6. **Install as service (as Administrator):**
   ```powershell
   python main.py install
   python main.py start
   ```

### In Home Assistant:

The device and entities will automatically appear! Look for:
- Device: "Gaming PC" (or whatever you named it)
- Entities: Status, Game Running, CPU, Memory, Shutdown button, etc.

## Key Features

### Security
- No arbitrary command execution
- Only predefined commands in config.yaml
- MQTT authentication support
- Runs with minimal privileges

### Reliability
- Automatic reconnection to MQTT broker
- Availability tracking (shows offline if disconnected)
- Error logging and handling
- Graceful shutdown

### Flexibility
- Configurable status update interval
- Customizable game process detection
- Add your own custom commands
- Works with any MQTT broker

## Configuration Options

**MQTT Settings:**
- Broker IP address
- Port (default: 1883)
- Username/password (optional)
- Client ID

**Home Assistant:**
- Discovery prefix
- Device name
- Device ID (unique identifier)

**Agent Settings:**
- Status update interval (seconds)
- Game process list (which processes indicate gaming)
- Custom commands (predefined safe commands)

## Home Assistant Features

**Buttons Created:**
- Shutdown PC
- Reboot PC
- Sleep PC

**Sensors Created:**
- PC Status (online/offline)
- Game Running (binary sensor)
- CPU Usage (%)
- Memory Usage (%)

**All entities include:**
- Availability tracking
- Proper device association
- Appropriate icons
- Unique IDs

## Example Automations

**Auto-shutdown when leaving home:**
```yaml
automation:
  - alias: "Shutdown PC when leaving"
    trigger:
      - platform: state
        entity_id: group.all_persons
        to: 'not_home'
    condition:
      - condition: state
        entity_id: binary_sensor.gaming_pc_game_running
        state: 'off'
    action:
      - service: button.press
        target:
          entity_id: button.gaming_pc_shutdown
```

**Wake PC in the morning:**
```yaml
automation:
  - alias: "Wake PC morning"
    trigger:
      - platform: time
        at: '08:00:00'
    action:
      - service: wake_on_lan.send_magic_packet
        data:
          mac: "AA:BB:CC:DD:EE:FF"
```

## Technical Details

**Technologies:**
- Python 3.10+
- paho-mqtt (MQTT client)
- psutil (system monitoring)
- pywin32 (Windows service integration)
- PyYAML (configuration)

**MQTT Topics:**
- `hass_agent/{device_id}/availability` - Online/offline status
- `hass_agent/{device_id}/state` - JSON state with all sensor data
- `hass_agent/{device_id}/command` - Command input
- `homeassistant/...` - Auto-discovery topics

**Architecture:**
- Main agent class (HASSMQTTAgent)
- Status monitor class (PCStatusMonitor)
- Windows service wrapper (HASSMQTTService)
- Background thread for periodic status updates
- Event-driven MQTT command handling

## Maintenance

**View Logs:**
```powershell
notepad hass_mqtt_agent.log
```

**Restart Service:**
```powershell
python main.py restart
```

**Update After Code Changes:**
```powershell
python main.py update
python main.py restart
```

## Extending

**Add Custom Commands:**

Edit config.yaml:
```yaml
agent:
  custom_commands:
    launch_game: "C:\\Games\\MyGame.exe"
    run_script: "C:\\scripts\\backup.bat"
```

Send from Home Assistant:
```yaml
script:
  launch_my_game:
    sequence:
      - service: mqtt.publish
        data:
          topic: "hass_agent/gaming_pc_01/command"
          payload: "custom:launch_game"
```

**Add Game Detection:**

Edit config.yaml:
```yaml
agent:
  game_processes:
    - "steam.exe"
    - "EpicGamesLauncher.exe"
    - "GTA5.exe"
    - "csgo.exe"
    # Add any .exe you want to detect
```

## Troubleshooting

See `TROUBLESHOOTING.md` for detailed solutions.

**Common issues:**
- Service won't start → Check config.yaml exists and is valid
- MQTT won't connect → Verify broker IP and credentials
- Commands don't work → Check availability sensor is online
- Game detection fails → Add exact .exe name from Task Manager

## Files Included

| File | Purpose |
|------|---------|
| `main.py` | Complete agent implementation |
| `config.yaml.example` | Configuration template |
| `requirements.txt` | Python dependencies |
| `install.ps1` | Automated installation script |
| `README.md` | Main documentation and setup guide |
| `TROUBLESHOOTING.md` | Common issues and solutions |
| `homeassistant_examples.yaml` | Home Assistant config examples |
| `.gitignore` | Git ignore file (excludes config.yaml, logs) |

## Next Steps

1. ✅ Review the code in `main.py`
2. ✅ Read `README.md` for detailed setup instructions
3. ✅ Copy and edit `config.yaml.example` → `config.yaml`
4. ✅ Test in console mode first
5. ✅ Install as Windows service
6. ✅ Configure automations in Home Assistant
7. ✅ Refer to `TROUBLESHOOTING.md` if needed

## Support

- Check `TROUBLESHOOTING.md` for common issues
- Review logs in `hass_mqtt_agent.log`
- Verify MQTT connection with mosquitto_sub/pub tools
- Test in console mode before running as service

## License

MIT License - Free to use and modify!

---

**Enjoy controlling your PC from Home Assistant!** 🎮🏠

