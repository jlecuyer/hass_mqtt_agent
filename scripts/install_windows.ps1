# Home Assistant MQTT Agent - Installation Script
# Run this as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Home Assistant MQTT Agent Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from https://www.python.org/" -ForegroundColor Yellow
    pause
    exit 1
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Dependencies installed successfully!" -ForegroundColor Green

# Check if config exists
Write-Host ""
if (-not (Test-Path "config.yaml")) {
    Write-Host "Config file not found. Creating from example..." -ForegroundColor Yellow

    if (Test-Path "config.yaml.example") {
        Copy-Item "config.yaml.example" "config.yaml"
        Write-Host "Created config.yaml from example" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Please edit config.yaml with your MQTT broker settings before continuing!" -ForegroundColor Yellow
        Write-Host "Press any key when you've finished editing config.yaml..." -ForegroundColor Yellow
        pause
    } else {
        Write-Host "ERROR: config.yaml.example not found!" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host "Found existing config.yaml" -ForegroundColor Green
}

# Test the agent
Write-Host ""
Write-Host "Would you like to test the agent before installing as a service? (Y/N)" -ForegroundColor Yellow
$test = Read-Host
if ($test -eq "Y" -or $test -eq "y") {
    Write-Host "Starting agent in test mode... (Press Ctrl+C to stop)" -ForegroundColor Cyan
    python main.py
}

# Install as service
Write-Host ""
Write-Host "Would you like to install as a Windows service? (Y/N)" -ForegroundColor Yellow
$install = Read-Host
if ($install -eq "Y" -or $install -eq "y") {
    Write-Host "Installing Windows service..." -ForegroundColor Yellow
    python main.py install

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service installed successfully!" -ForegroundColor Green

        Write-Host ""
        Write-Host "Would you like to start the service now? (Y/N)" -ForegroundColor Yellow
        $start = Read-Host
        if ($start -eq "Y" -or $start -eq "y") {
            python main.py start
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Service started successfully!" -ForegroundColor Green
            } else {
                Write-Host "ERROR: Failed to start service" -ForegroundColor Red
                Write-Host "Check hass_mqtt_agent.log for details" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "ERROR: Failed to install service" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service Management Commands:" -ForegroundColor Yellow
Write-Host "  Start:   python main.py start" -ForegroundColor White
Write-Host "  Stop:    python main.py stop" -ForegroundColor White
Write-Host "  Restart: python main.py restart" -ForegroundColor White
Write-Host "  Remove:  python main.py remove" -ForegroundColor White
Write-Host ""
Write-Host "Check hass_mqtt_agent.log for runtime information" -ForegroundColor Cyan
Write-Host ""
pause

