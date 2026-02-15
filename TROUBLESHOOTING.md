# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### 1. pywin32 Installation Fails

**Problem:** `pip install pywin32` fails or service doesn't register

**Solutions:**
```bash
# Try installing with admin privileges
pip install --user pywin32

# Run post-install script
python Scripts/pywin32_postinstall.py -install

# Or use pre-built wheel
pip install --upgrade pywin32
```

#### 2. "No module named 'yaml'" Error

**Problem:** PyYAML not installed

**Solution:**
```bash
pip install pyyaml
# or
pip install -r requirements.txt
```

### Configuration Issues

#### 3. "config.yaml not found"

**Problem:** Config file doesn't exist

**Solution:**
```bash
copy config.yaml.example config.yaml
# Then edit config.yaml with your settings
```

#### 4. MQTT Connection Refused

**Problem:** Cannot connect to MQTT broker

**Check:**
- MQTT broker is running
- IP address is correct
- Port is correct (default: 1883)
- Firewall allows connection
- Username/password are correct

**Test MQTT Connection:**
```bash
# Install mosquitto clients
# Windows: download from mosquitto.org
# Test connection
mosquitto_sub -h 192.168.1.100 -t test/topic -u username -P password
```

### Service Issues

#### 5. Service Won't Install

**Problem:** `python main.py install` fails

**Check:**
- Running as Administrator
- Python in system PATH
- pywin32 is properly installed

**Solution:**
```bash
# Run as Administrator
python main.py install

# If still failing, reinstall pywin32
pip uninstall pywin32
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

#### 6. Service Installed but Won't Start

**Problem:** Service starts then immediately stops

**Check the log:**
```bash
# Open hass_mqtt_agent.log in the installation directory
notepad hass_mqtt_agent.log
```

**Common causes:**
- config.yaml is missing or invalid
- MQTT broker unreachable
- Permission issues

**Solution:**
```bash
# Test in console mode first
python main.py

# If it works in console, check service permissions
# Service should run as Local System or Network Service
```

#### 7. Service Shows "Error 1053: The service did not respond"

**Problem:** Service timeout during startup

**Solutions:**
1. Check that config.yaml exists in the same directory as main.py
2. Verify MQTT broker is accessible
3. Check Windows Event Viewer for details:
   - Open Event Viewer
   - Windows Logs > Application
   - Look for HASSMQTTAgent errors

### Runtime Issues

#### 8. Commands Not Executing

**Problem:** Buttons in Home Assistant don't work

**Check:**
1. Service is running (check availability sensor)
2. MQTT messages are being received:
   ```bash
   # Monitor MQTT topic
   mosquitto_sub -h 192.168.1.100 -t "hass_agent/#" -v
   ```
3. Check the log for errors

**Test manually:**
```bash
# Send test command
mosquitto_pub -h 192.168.1.100 -t "hass_agent/gaming_pc_01/command" -m "sleep"
```

#### 9. Game Detection Not Working

**Problem:** binary_sensor.gaming_pc_game_running always shows "off"

**Debug:**
1. Find exact process name in Task Manager
2. Add to config.yaml:
   ```yaml
   agent:
     game_processes:
       - "exactprocessname.exe"
   ```
3. Check log for detected processes (enable DEBUG logging)

**Enable debug logging:**
Edit main.py and change:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    ...
)
```

#### 10. Status Not Updating in Home Assistant

**Problem:** Sensors show "unavailable" or don't update

**Check:**
1. Agent is connected to MQTT (check log)
2. MQTT integration is working in Home Assistant
3. Topics match:
   ```bash
   # Listen for state updates
   mosquitto_sub -h 192.168.1.100 -t "hass_agent/+/state" -v
   ```

**Refresh discovery:**
1. Restart the agent
2. Wait 30 seconds
3. Check MQTT discovery topic:
   ```bash
   mosquitto_sub -h 192.168.1.100 -t "homeassistant/#" -v
   ```

### Wake-on-LAN Issues

#### 11. PC Won't Wake Up

**Problem:** WoL magic packet doesn't wake PC

**BIOS Settings:**
1. Enable "Wake on LAN" or "Resume by PCI-E Device"
2. Enable "Power On by PCIE/PCI"
3. Disable "Deep Sleep" or "ErP Ready"

**Windows Settings:**
1. Open Device Manager
2. Network Adapters > Right-click your adapter > Properties
3. Power Management tab:
   - ✓ Allow this device to wake the computer
   - ✓ Only allow a magic packet to wake the computer
4. Advanced tab:
   - Wake on Magic Packet: Enabled
   - Wake on Pattern Match: Enabled

**Network:**
- Use broadcast address (e.g., 192.168.1.255)
- Some routers block WoL packets
- May need to configure router to allow directed broadcasts

#### 12. WoL Works Locally but Not Remotely

**Problem:** Can wake PC from same network but not remotely

**Solutions:**
- Configure port forwarding on router (UDP port 9)
- Use VPN to access local network
- Use dynamic DNS service
- Some cloud services offer WoL relay

### Home Assistant Integration Issues

#### 13. Entities Not Appearing in Home Assistant

**Problem:** No devices/entities created

**Check:**
1. MQTT integration is configured
2. Discovery prefix matches (default: `homeassistant`)
3. Check MQTT discovery topics:
   ```bash
   mosquitto_sub -h 192.168.1.100 -t "homeassistant/#" -v
   ```

**Force rediscovery:**
```bash
# Stop service
python main.py stop

# Clear retained messages (if needed)
mosquitto_pub -h 192.168.1.100 -t "homeassistant/sensor/gaming_pc_01/status/config" -n -r

# Start service
python main.py start
```

#### 14. Entities Show "Unavailable"

**Problem:** Entities exist but show unavailable

**Check:**
1. Availability topic is publishing:
   ```bash
   mosquitto_sub -h 192.168.1.100 -t "hass_agent/+/availability" -v
   ```
   Should show "online"

2. State topic is publishing:
   ```bash
   mosquitto_sub -h 192.168.1.100 -t "hass_agent/+/state" -v
   ```

### Performance Issues

#### 15. High CPU Usage

**Problem:** Agent uses too much CPU

**Solutions:**
1. Increase status_update_interval in config.yaml:
   ```yaml
   agent:
     status_update_interval: 60  # Increase from 30
   ```

2. Reduce number of game_processes to monitor

3. Check for errors in log that might cause retry loops

#### 16. Memory Usage Increasing Over Time

**Problem:** Memory leak

**Solutions:**
1. Restart service periodically
2. Check for MQTT disconnect/reconnect loops in log
3. Update to latest version of dependencies:
   ```bash
   pip install --upgrade paho-mqtt psutil pywin32
   ```

## Debugging Tips

### Enable Verbose Logging

Edit main.py:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hass_mqtt_agent.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor MQTT Traffic

```bash
# Watch all agent topics
mosquitto_sub -h 192.168.1.100 -t "hass_agent/#" -v

# Watch Home Assistant discovery
mosquitto_sub -h 192.168.1.100 -t "homeassistant/#" -v

# Watch everything (verbose!)
mosquitto_sub -h 192.168.1.100 -t "#" -v
```

### Test Without Service

Always test in console mode first:
```bash
python main.py
```

This allows you to see errors immediately.

### Check Windows Event Viewer

For service-specific errors:
1. Win + R > `eventvwr.msc`
2. Windows Logs > Application
3. Look for "HASSMQTTAgent" source

### Verify Python Environment

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify all dependencies
pip install -r requirements.txt --dry-run
```

## Getting Help

If you're still stuck:

1. Check the log file: `hass_mqtt_agent.log`
2. Test MQTT connection separately
3. Verify Home Assistant MQTT integration is working
4. Test the agent in console mode
5. Check Windows Event Viewer for service errors

## Useful Commands Reference

```bash
# Service Management
python main.py install    # Install service
python main.py start      # Start service
python main.py stop       # Stop service
python main.py restart    # Restart service
python main.py remove     # Uninstall service
python main.py update     # Update service after code changes

# Console Mode (for testing)
python main.py            # Run in foreground

# MQTT Testing
mosquitto_sub -h <broker> -t "hass_agent/#" -v
mosquitto_pub -h <broker> -t "hass_agent/device_id/command" -m "shutdown"

# Windows Services
services.msc              # Open Services Manager
eventvwr.msc              # Open Event Viewer
```

## Security Checklist

- [ ] Use MQTT authentication (username/password)
- [ ] Consider MQTT over TLS
- [ ] Restrict network access to MQTT broker
- [ ] Use strong passwords
- [ ] Keep custom commands list minimal
- [ ] Run service with minimal privileges
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity

