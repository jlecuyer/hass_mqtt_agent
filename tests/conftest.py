"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import os
import yaml
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield temp
    if os.path.exists(temp):
        shutil.rmtree(temp)


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary"""
    return {
        'mqtt': {
            'broker': '192.168.1.100',
            'port': 1883,
            'username': 'test_user',
            'password': 'test_pass',
            'client_id': 'test_client'
        },
        'homeassistant': {
            'discovery_prefix': 'homeassistant',
            'device_name': 'Test PC',
            'device_id': 'test_pc'
        },
        'agent': {
            'game_folders': ['/games'],
            'status_update_interval': 30,
            'custom_commands': {
                'test_cmd': 'echo test'
            }
        }
    }


@pytest.fixture
def config_file(sample_config, temp_dir):
    """Create a temporary config file"""
    config_path = os.path.join(temp_dir, 'config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def game_folder(temp_dir):
    """Create a temporary game folder with test executables"""
    games_dir = os.path.join(temp_dir, 'games')
    os.makedirs(games_dir)

    # Create test executables
    import sys
    if sys.platform == 'win32':
        game1 = os.path.join(games_dir, 'game1.exe')
        game2 = os.path.join(games_dir, 'game2.exe')
    else:
        game1 = os.path.join(games_dir, 'game1')
        game2 = os.path.join(games_dir, 'game2')

    # Create files
    open(game1, 'a').close()
    open(game2, 'a').close()

    # Make executable on Unix
    if sys.platform != 'win32':
        os.chmod(game1, 0o755)
        os.chmod(game2, 0o755)

    return games_dir

