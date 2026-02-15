#!/usr/bin/env python3
"""
Build script for HASS MQTT Agent
Creates distributable packages for all platforms
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import re

# Fix encoding on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def get_version():
    """Get version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, 'r') as f:
        content = f.read()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)

    raise ValueError("Could not find version in pyproject.toml")


def clean_build_dirs():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")

    dirs_to_clean = ['dist', 'build', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed: {path}")
            elif path.is_file():
                path.unlink()
                print(f"   Removed: {path}")


def build_wheel():
    """Build Python wheel"""
    print("\n[*] Building Python wheel...")

    try:
        subprocess.run([
            sys.executable, "-m", "build", "--wheel"
        ], check=True)
        print("   [OK] Wheel built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Failed to build wheel: {e}")
        return False


def build_windows_executable():
    """Build Windows executable using PyInstaller"""
    print("\n[*] Building Windows executable...")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("   [WARN] PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    version = get_version()
    exe_name = f"hass_mqtt_agent_{version}.exe"

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", exe_name.replace('.exe', ''),
        "--add-data", "config:config",
        "--add-data", "scripts:scripts",
        "--hidden-import", "paho.mqtt.client",
        "--hidden-import", "yaml",
        "--hidden-import", "psutil",
        "--collect-all", "paho",
        "main.py"
    ]

    # Add Windows-specific options
    if sys.platform == "win32":
        cmd.extend([
            "--hidden-import", "win32serviceutil",
            "--hidden-import", "win32service",
            "--hidden-import", "win32event",
            "--hidden-import", "servicemanager",
            "--collect-all", "pywin32"
        ])

    try:
        subprocess.run(cmd, check=True)
        print("   [OK] Windows executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Failed to build Windows executable: {e}")
        return False


def build_linux_binary():
    """Build Linux binary using PyInstaller"""
    print("\n[*] Building Linux binary...")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("   [WARN] PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    version = get_version()
    binary_name = f"hass_mqtt_agent_{version}"

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", binary_name,
        "--add-data", "config:config",
        "--add-data", "scripts:scripts",
        "--hidden-import", "paho.mqtt.client",
        "--hidden-import", "yaml",
        "--hidden-import", "psutil",
        "--collect-all", "paho",
        "main.py"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("   [OK] Linux binary built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Failed to build Linux binary: {e}")
        return False


def organize_artifacts():
    """Organize build artifacts into version-specific folder"""
    print("\n📂 Organizing build artifacts...")

    version = get_version()
    build_root = Path("build")
    version_dir = build_root / version

    # Create version directory
    version_dir.mkdir(parents=True, exist_ok=True)
    print(f"   Created: {version_dir}")

    artifacts_moved = 0

    # Move wheel from dist/
    dist_dir = Path("dist")
    if dist_dir.exists():
        for wheel in dist_dir.glob("*.whl"):
            dest = version_dir / wheel.name
            shutil.copy2(wheel, dest)
            print(f"   Copied: {wheel.name} -> {dest}")
            artifacts_moved += 1

    # Move Windows executable from dist/
    pyinstaller_dist = Path("dist")
    if pyinstaller_dist.exists():
        # Look for .exe files
        for exe in pyinstaller_dist.glob("*.exe"):
            new_name = f"hass_mqtt_agent_{version}.exe"
            dest = version_dir / new_name
            shutil.copy2(exe, dest)
            print(f"   Copied: {exe.name} -> {dest}")
            artifacts_moved += 1

        # Look for Linux binary (no extension or specific pattern)
        for binary in pyinstaller_dist.iterdir():
            if binary.is_file() and not binary.suffix and binary.name.startswith('hass_mqtt_agent'):
                new_name = f"hass_mqtt_agent_{version}"
                dest = version_dir / new_name
                shutil.copy2(binary, dest)
                # Make it executable
                dest.chmod(0o755)
                print(f"   Copied: {binary.name} -> {dest}")
                artifacts_moved += 1

    if artifacts_moved == 0:
        print("   [WARN] No artifacts found to organize")
        return False

    print(f"   [OK] Organized {artifacts_moved} artifact(s)")
    return True


def create_checksums():
    """Create SHA256 checksums for all artifacts"""
    print("\n[*] Creating checksums...")

    version = get_version()
    version_dir = Path("build") / version

    if not version_dir.exists():
        print("   [WARN] No artifacts to checksum")
        return

    import hashlib

    checksums = []
    for artifact in sorted(version_dir.iterdir()):
        if artifact.is_file() and artifact.name != "checksums.txt":
            sha256 = hashlib.sha256()
            with open(artifact, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)

            checksum = sha256.hexdigest()
            checksums.append(f"{checksum}  {artifact.name}")
            print(f"   {artifact.name}: {checksum}")

    # Write checksums file
    checksums_file = version_dir / "checksums.txt"
    with open(checksums_file, 'w') as f:
        f.write('\n'.join(checksums) + '\n')

    print(f"   [OK] Checksums saved to {checksums_file}")


def print_summary():
    """Print build summary"""
    version = get_version()
    version_dir = Path("build") / version

    print("\n" + "="*60)
    print("Build Summary")
    print("="*60)
    print(f"Version: {version}")
    print(f"Build directory: {version_dir}")
    print("\nArtifacts:")

    if version_dir.exists():
        for artifact in sorted(version_dir.iterdir()):
            size = artifact.stat().st_size / (1024 * 1024)  # MB
            print(f"  [*] {artifact.name} ({size:.2f} MB)")
    else:
        print("  [WARN] No artifacts found")

    print("="*60)


def main():
    """Main build process"""
    print("=" * 60)
    print("")
    print("       HASS MQTT Agent - Build Script")
    print("")
    print("=" * 60)
    print()

    try:
        version = get_version()
        print(f"Version: {version}\n")
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {project_root}\n")

    # Build steps
    steps = []

    # Always build wheel
    steps.append(("Clean build directories", clean_build_dirs))
    steps.append(("Build Python wheel", build_wheel))

    # Platform-specific builds
    if sys.platform == "win32":
        steps.append(("Build Windows executable", build_windows_executable))
    elif sys.platform.startswith("linux"):
        steps.append(("Build Linux binary", build_linux_binary))

    steps.append(("Organize artifacts", organize_artifacts))
    steps.append(("Create checksums", create_checksums))

    # Execute steps
    for step_name, step_func in steps:
        result = step_func()
        if result is False:
            print(f"\n[ERROR] Build failed at step: {step_name}")
            return 1

    # Print summary
    print_summary()

    print("\n[OK] Build completed successfully!")
    print(f"\nTo build on other platforms, run this script on that platform.")
    print(f"Artifacts are in: build/{version}/\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

