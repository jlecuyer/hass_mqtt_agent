# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOME ASSISTANT                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Buttons    │  │   Sensors    │  │  Automations │          │
│  │              │  │              │  │              │          │
│  │  Shutdown    │  │  Status      │  │  Auto-wake   │          │
│  │  Reboot      │  │  CPU         │  │  Auto-sleep  │          │
│  │  Sleep       │  │  Memory      │  │  Gaming mode │          │
│  │              │  │  Game Running│  │              │          │
│  └──────┬───────┘  └──────▲───────┘  └──────────────┘          │
│         │                 │                                      │
└─────────┼─────────────────┼──────────────────────────────────────┘
          │                 │
          │    MQTT         │
          │  (Local         │
          │  Ethernet)      │
          │                 │
┌─────────▼─────────────────┴──────────────────────────────────────┐
│                    MQTT BROKER                                    │
│              (Mosquitto on Home Assistant)                        │
│                                                                   │
│  Topics:                                                          │
│    • hass_agent/{device_id}/command    (commands in)            │
│    • hass_agent/{device_id}/state      (status out)             │
│    • hass_agent/{device_id}/availability (online/offline)       │
│    • homeassistant/...                  (auto-discovery)         │
└─────────┬─────────────────▲──────────────────────────────────────┘
          │                 │
          │   MQTT          │
          │  (Local         │
          │  Ethernet)      │
          │                 │
┌─────────▼─────────────────┴──────────────────────────────────────┐
│                    WINDOWS PC                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         HASS MQTT Agent (Windows Service)                  │ │
│  │                                                             │ │
│  │  ┌──────────────────┐         ┌─────────────────────┐     │ │
│  │  │  MQTT Client     │         │  Status Monitor     │     │ │
│  │  │                  │         │                     │     │ │
│  │  │  • Subscribe     │         │  • CPU Usage        │     │ │
│  │  │  • Publish       │         │  • Memory Usage     │     │ │
│  │  │  • Auto-reconnect│         │  • Process List     │     │ │
│  │  └────────┬─────────┘         │  • Game Detection   │     │ │
│  │           │                   └──────────┬──────────┘     │ │
│  │           │                              │                │ │
│  │  ┌────────▼──────────────────────────────▼──────────┐    │ │
│  │  │         Command Executor                          │    │ │
│  │  │                                                   │    │ │
│  │  │  • Shutdown PC                                    │    │ │
│  │  │  • Reboot PC                                      │    │ │
│  │  │  • Sleep PC                                       │    │ │
│  │  │  • Custom Commands (from config.yaml)            │    │ │
│  │  └───────────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Files:                                                          │
│    • main.py              (agent code)                          │
│    • config.yaml          (configuration)                       │
│    • hass_mqtt_agent.log  (log file)                           │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Startup Sequence

```
1. Windows Service Starts
   ↓
2. Load config.yaml
   ↓
3. Connect to MQTT Broker
   ↓
4. Publish "online" to availability topic
   ↓
5. Publish Home Assistant discovery messages
   ↓
6. Subscribe to command topic
   ↓
7. Start status monitoring thread
   ↓
8. Publish initial state
```

### 2. Command Flow (e.g., Shutdown)

```
User presses "Shutdown" button in Home Assistant
   ↓
Home Assistant → MQTT Publish
   Topic: hass_agent/gaming_pc_01/command
   Payload: "shutdown"
   ↓
MQTT Broker → forwards message
   ↓
Windows PC Agent receives message
   ↓
Parse command: "shutdown"
   ↓
Execute: subprocess.run(["shutdown", "/s", "/t", "5"])
   ↓
Log: "Executing shutdown command"
   ↓
PC shuts down after 5 seconds
```

### 3. Status Update Flow

```
Every 30 seconds (configurable):
   ↓
1. Check CPU usage (psutil)
   ↓
2. Check memory usage (psutil)
   ↓
3. Check running processes
   ↓
4. Match against game_processes list
   ↓
5. Build JSON state:
   {
     "status": "online",
     "game_running": true/false,
     "cpu_percent": 45.2,
     "memory_percent": 62.1,
     "sleeping": false
   }
   ↓
6. Publish to state topic
   ↓
Home Assistant updates sensors
```

### 4. Auto-Discovery Flow

```
Agent connects to MQTT
   ↓
For each entity (sensors, buttons):
   ↓
   Build discovery config JSON
   ↓
   Publish to: homeassistant/{component}/{device_id}/{entity}/config
   ↓
   Example: homeassistant/button/gaming_pc_01/shutdown/config
   {
     "name": "Gaming PC Shutdown",
     "command_topic": "hass_agent/gaming_pc_01/command",
     "payload_press": "shutdown",
     ...
   }
   ↓
Home Assistant receives and auto-creates entities
```

## Component Breakdown

### HASSMQTTAgent Class
- **Purpose**: Main coordinator
- **Responsibilities**:
  - MQTT connection management
  - Configuration loading
  - Command execution
  - State publishing
  - Discovery publishing

### PCStatusMonitor Class
- **Purpose**: System monitoring
- **Responsibilities**:
  - CPU/Memory monitoring (psutil)
  - Process enumeration
  - Game detection
  - Sleep state detection

### HASSMQTTService Class (Windows only)
- **Purpose**: Windows service wrapper
- **Responsibilities**:
  - Service lifecycle management
  - Integration with Windows Service Manager
  - Working directory setup
  - Error reporting to Event Log

## Network Communication

### MQTT Topics Used

```
Subscribed (PC listens):
  hass_agent/{device_id}/command

Published by PC:
  hass_agent/{device_id}/availability  (retain=true)
  hass_agent/{device_id}/state         (retain=true)
  homeassistant/sensor/{device_id}/status/config
  homeassistant/sensor/{device_id}/cpu/config
  homeassistant/sensor/{device_id}/memory/config
  homeassistant/binary_sensor/{device_id}/game_running/config
  homeassistant/button/{device_id}/shutdown/config
  homeassistant/button/{device_id}/reboot/config
  homeassistant/button/{device_id}/sleep/config
```

### Message Examples

**Command (Home Assistant → PC):**
```
Topic: hass_agent/gaming_pc_01/command
Payload: "shutdown"
```

**State (PC → Home Assistant):**
```
Topic: hass_agent/gaming_pc_01/state
Payload: {
  "status": "online",
  "game_running": false,
  "sleeping": false,
  "cpu_percent": 23.4,
  "memory_percent": 54.2,
  "memory_available_gb": 7.82
}
```

**Availability (PC → Home Assistant):**
```
Topic: hass_agent/gaming_pc_01/availability
Payload: "online"  (or "offline" via Last Will)
```

## Security Model

```
┌─────────────────────────────────────────┐
│         Security Layers                  │
├─────────────────────────────────────────┤
│ 1. Network Level                        │
│    • Local network only                 │
│    • No internet exposure               │
│    • Optional: MQTT over TLS            │
├─────────────────────────────────────────┤
│ 2. MQTT Authentication                  │
│    • Username/password                  │
│    • Client ID verification             │
├─────────────────────────────────────────┤
│ 3. Command Whitelist                    │
│    • Only predefined commands           │
│    • No arbitrary execution             │
│    • Validated against config.yaml     │
├─────────────────────────────────────────┤
│ 4. Service Permissions                  │
│    • Runs as LocalSystem/Network Service│
│    • Limited to configured actions      │
└─────────────────────────────────────────┘
```

## Threading Model

```
Main Thread
  │
  ├─► MQTT Network Loop Thread (paho-mqtt)
  │   └─► Handles network I/O, callbacks
  │
  └─► Status Update Thread
      └─► Every N seconds:
          • Gather system info
          • Check game processes
          • Publish state update
```

## Error Handling

```
Connection Lost?
  ↓
MQTT client automatically reconnects
  ↓
On reconnect:
  • Re-subscribe to command topic
  • Re-publish availability (online)
  • Publish current state

Service Stop?
  ↓
Graceful shutdown:
  1. Stop status update thread
  2. Publish "offline" availability
  3. Disconnect MQTT
  4. Exit

Exception in command execution?
  ↓
  • Log error
  • Continue running
  • Don't crash service
```

## Wake-on-LAN Integration

```
PC is off/sleeping
  ↓
Home Assistant automation triggers
  ↓
Send Wake-on-LAN magic packet
  (wake_on_lan.send_magic_packet)
  ↓
Network card receives packet
  ↓
BIOS wakes PC
  ↓
Windows boots
  ↓
Service starts automatically
  ↓
Agent connects to MQTT
  ↓
Publishes "online" status
  ↓
Home Assistant sees PC is available
```

