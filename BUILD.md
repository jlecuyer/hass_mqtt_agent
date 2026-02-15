# Building the Wheel

This document explains how to build the Python wheel distribution for the Home Assistant MQTT Agent.

## Prerequisites

- Python 3.10 or higher
- `build` package installed

## Quick Build

### Install Build Tools

```bash
pip install build
```

### Build the Wheel

```bash
# Build both wheel and source distribution
python -m build

# Or build only the wheel
python -m build --wheel

# Or build only source distribution
python -m build --sdist
```

The built files will be in the `dist/` directory:
- `hass_mqtt_agent-0.1.0-py3-none-any.whl` - Wheel distribution
- `hass_mqtt_agent-0.1.0.tar.gz` - Source distribution

## Installing from Wheel

Once built, you can install the wheel:

```bash
pip install dist/hass_mqtt_agent-0.1.0-py3-none-any.whl
```

## Automated Builds (GitHub Actions)

The project includes a GitHub Actions workflow that automatically builds wheels:

### On Tag Push

Create and push a version tag to trigger a release build:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This will:
1. Build the wheel and source distribution
2. Create a GitHub Release
3. Upload the built artifacts to the release

### Manual Trigger

You can also manually trigger the build workflow from the GitHub Actions tab.

### On Pull Request

The workflow runs on pull requests to `main` to verify the package builds correctly.

## What's Included in the Wheel

The wheel includes:
- `main.py` - Main agent code
- `config.yaml.example` - Configuration template
- `README.md` - Documentation
- `QUICKSTART.md` - Quick start guide
- `TROUBLESHOOTING.md` - Troubleshooting guide
- `ARCHITECTURE.md` - Architecture documentation
- `PROJECT_SUMMARY.md` - Project summary
- `homeassistant_examples.yaml` - Home Assistant examples
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

