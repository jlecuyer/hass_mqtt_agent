# Building the Distribution Packages

This document explains how to build distribution packages for the HASS MQTT Agent.

## Build Outputs

The build process creates three types of distributable packages:

1. **Python Wheel** (`.whl`) - Cross-platform, requires Python
2. **Windows Executable** (`.exe`) - Standalone Windows application
3. **Linux Binary** - Standalone Linux application

All artifacts are organized in version-specific folders: `build/<version>/`

Example:
```
build/
└── 0.1.0/
    ├── hass_mqtt_agent-0.1.0-py3-none-any.whl
    ├── hass_mqtt_agent_0.1.0.exe
    ├── hass_mqtt_agent_0.1.0
    └── checksums.txt
```

## Prerequisites

### All Platforms

- Python 3.10 or higher
- pip package manager

### Install Build Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `build` - For building wheels
- `pyinstaller` - For creating executables
- All project dependencies

## Quick Build

### Using the Build Script

The easiest way to build is using the included build script:

```bash
# On any platform
python scripts/build.py
```

**What it does:**
1. ✅ Cleans previous build artifacts
2. ✅ Builds Python wheel
3. ✅ Builds platform-specific executable (Windows .exe or Linux binary)
4. ✅ Organizes all artifacts into `build/<version>/`
5. ✅ Creates SHA256 checksums

**Output:**
```
build/0.1.0/
├── hass_mqtt_agent-0.1.0-py3-none-any.whl    # Wheel (all platforms)
├── hass_mqtt_agent_0.1.0.exe                  # Windows (if on Windows)
├── hass_mqtt_agent_0.1.0                      # Linux (if on Linux)
└── checksums.txt                              # SHA256 hashes
```

### Building on Different Platforms

**To get all three artifacts**, you need to run the build script on both platforms:

1. **On Windows:**
   ```powershell
   python scripts/build.py
   # Creates: wheel + Windows .exe
   ```

2. **On Linux:**
   ```bash
   python scripts/build.py
   # Creates: wheel + Linux binary
   ```

## Manual Build Steps

If you prefer to build manually:

## Manual Build Steps

If you prefer to build manually:

### 1. Build Python Wheel

```bash
python -m build --wheel
```

Output: `dist/hass_mqtt_agent-<version>-py3-none-any.whl`

### 2. Build Windows Executable

On Windows:

```powershell
pyinstaller --onefile `
  --name hass_mqtt_agent `
  --add-data "config.yaml.example;." `
  --add-data "scripts;scripts" `
  --hidden-import paho.mqtt.client `
  --hidden-import yaml `
  --hidden-import psutil `
  --collect-all paho `
  --collect-all pywin32 `
  main.py
```

Output: `dist/hass_mqtt_agent.exe`

### 3. Build Linux Binary

On Linux:

```bash
pyinstaller --onefile \
  --name hass_mqtt_agent \
  --add-data "config.yaml.example:." \
  --add-data "scripts:scripts" \
  --hidden-import paho.mqtt.client \
  --hidden-import yaml \
  --hidden-import psutil \
  --collect-all paho \
  main.py
```

Output: `dist/hass_mqtt_agent`

### 4. Organize Artifacts

Manually move files to versioned folder:

```bash
# Get version from pyproject.toml
VERSION="0.1.0"  # Replace with actual version

# Create directory
mkdir -p build/$VERSION

# Copy artifacts
cp dist/*.whl build/$VERSION/
cp dist/hass_mqtt_agent* build/$VERSION/

# Rename to include version
mv build/$VERSION/hass_mqtt_agent.exe build/$VERSION/hass_mqtt_agent_$VERSION.exe
mv build/$VERSION/hass_mqtt_agent build/$VERSION/hass_mqtt_agent_$VERSION
```

## Automated Builds (GitHub Actions)

The project includes a GitHub Actions workflow that automatically builds on both platforms.

### On Every Push

Every push to `main` or `develop` branches triggers builds on both Windows and Linux with Python 3.10, 3.11, and 3.12 to ensure compatibility.

**Workflow runs:**
- ✅ Build wheel on both platforms
- ✅ Build Windows .exe on Windows
- ✅ Build Linux binary on Linux
- ✅ Test imports on both platforms
- ✅ Upload artifacts (kept for 30 days)

### Creating a Release

To create a release with all artifacts:

1. **Update version in `pyproject.toml`:**
   ```toml
   [project]
   version = "1.2.3"  # Update this
   ```

2. **Commit and push:**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.2.3"
   git push origin main
   ```

3. **Create and push version tag** (no 'v' prefix):
   ```bash
   git tag 1.2.3
   git push origin 1.2.3
   ```

4. **GitHub Actions automatically:**
   - Builds on Windows and Linux
   - Creates GitHub Release
   - Uploads all 3 artifacts:
     - `hass_mqtt_agent-1.2.3-py3-none-any.whl`
     - `hass_mqtt_agent_1.2.3.exe`
     - `hass_mqtt_agent_1.2.3` (Linux)
     - `checksums.txt`
   - Generates release notes

### Workflow Matrix

The workflow tests multiple configurations:

| Platform | Python Versions | Artifacts Created |
|----------|----------------|-------------------|
| Windows  | 3.10, 3.11, 3.12 | Wheel + .exe |
| Linux    | 3.10, 3.11, 3.12 | Wheel + binary |

**Note:** Wheels are platform-independent, so they're the same from all builds. The release uses the Python 3.10 build artifacts by preference.

## What's Included in Each Build Type

### Python Wheel (`.whl`)
Cross-platform, requires Python installed.

**Includes:**
- `main.py` - Main agent code
- `config.yaml.example` - Configuration template
- `scripts/` - All setup and installation scripts
- All documentation files (README, guides, etc.)
- `homeassistant_examples.yaml` - Home Assistant config examples

**Installation:**
```bash
pip install hass_mqtt_agent-<version>-py3-none-any.whl
```

### Windows Executable (`.exe`)
Standalone application, no Python required.

**Includes:**
- Bundled Python interpreter
- All dependencies (paho-mqtt, psutil, pywin32, etc.)
- `config.yaml.example`
- `scripts/` folder

**Installation:**
- Just download and run
- No installation needed
- Can install as Windows Service

### Linux Binary
Standalone application, no Python required.

**Includes:**
- Bundled Python interpreter
- All dependencies (paho-mqtt, psutil, etc.)
- `config.yaml.example`
- `scripts/` folder

**Installation:**
```bash
chmod +x hass_mqtt_agent_<version>
./hass_mqtt_agent_<version>
```
- `install.ps1` - Windows installation script
- `requirements.txt` - Dependencies list
- `LICENSE` - MIT License

## Version Management

Update the version in `pyproject.toml`:

```toml
[project]
name = "hass-mqtt-agent"
version = "0.1.0"  # Change this
```

## Testing the Build

After building, you can test the wheel in a clean environment:

```bash
# Create a virtual environment
python -m venv test_env
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# Install the wheel
pip install dist/hass_mqtt_agent-0.1.0-py3-none-any.whl

# Test the installation
hass-mqtt-agent --help
# or
python -m main
```

## Clean Build

To ensure a clean build, remove old distributions:

```bash
# Windows
rmdir /s /q dist build hass_mqtt_agent.egg-info

# Linux/Mac
rm -rf dist/ build/ *.egg-info

# Then rebuild
python -m build
```

## Distribution

### PyPI (Optional)

If you want to publish to PyPI:

1. Install twine:
   ```bash
   pip install twine
   ```

2. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

3. Or test on TestPyPI first:
   ```bash
   twine upload --repository testpypi dist/*
   ```

### GitHub Releases

The GitHub Actions workflow automatically creates releases when you push version tags:

```bash
# Create a new version tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

The workflow will:
- Build wheel and source distribution
- Create a GitHub Release with release notes
- Attach the built distributions to the release

Users can then download the wheel directly from GitHub Releases.

## Troubleshooting

### "No module named 'build'"

Install the build package:
```bash
pip install build
```

### "error: Multiple top-level packages discovered"

This is normal - the project uses `py-modules` instead of packages in `pyproject.toml`.

### Build fails on Windows

Ensure you have:
- Python 3.10+ installed
- Latest pip: `python -m pip install --upgrade pip`
- Build tools: `pip install --upgrade build setuptools wheel`

### Dependencies not included

The wheel doesn't include dependencies - they're listed in `pyproject.toml` and installed automatically when you install the wheel with pip.

## Advanced: Customizing the Build

### Adding More Files

Edit `MANIFEST.in` to include additional files:

```
include myfile.txt
recursive-include docs *.md
```

### Build Options

```bash
# Build with specific build backend
python -m build --wheel --sdist

# Show verbose output
python -m build --verbose

# Skip dependency installation
python -m build --no-isolation
```

## CI/CD Workflow Details

The `.github/workflows/build.yml` workflow:

1. **Triggers on:**
   - Version tags (v*)
   - Manual workflow dispatch
   - Pull requests to main

2. **Build job:**
   - Runs on Windows (for Windows-specific dependencies)
   - Sets up Python 3.10
   - Builds wheel and source distribution
   - Uploads artifacts

3. **Release job:**
   - Only runs on version tags
   - Downloads build artifacts
   - Creates GitHub Release
   - Attaches wheel and source distribution

## Next Steps

After building the wheel, you can:
1. Install it locally for testing
2. Distribute it to users
3. Upload to PyPI for public distribution
4. Include it in GitHub Releases

For most users, the GitHub Actions workflow handles building automatically when you create version tags.

