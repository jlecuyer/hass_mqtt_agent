"""
Unit tests for setup_config.py script
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO


# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from setup_config import get_input, get_yes_no, get_game_folders, get_custom_commands


class TestSetupConfig(unittest.TestCase):
    """Test cases for setup_config.py"""

    def test_get_input_with_default(self):
        """Test get_input with default value"""
        with patch('builtins.input', return_value=''):
            result = get_input("Test", default="default_value")
            self.assertEqual(result, "default_value")

    def test_get_input_with_value(self):
        """Test get_input with user-provided value"""
        with patch('builtins.input', return_value='user_value'):
            result = get_input("Test", default="default_value")
            self.assertEqual(result, "user_value")

    def test_get_input_required_empty(self):
        """Test get_input with required field and empty input"""
        with patch('builtins.input', side_effect=['', '', 'valid_value']):
            result = get_input("Test", required=True)
            self.assertEqual(result, "valid_value")

    def test_get_yes_no_default_true(self):
        """Test get_yes_no with default True"""
        with patch('builtins.input', return_value=''):
            result = get_yes_no("Test", default=True)
            self.assertTrue(result)

    def test_get_yes_no_yes(self):
        """Test get_yes_no with 'yes' input"""
        with patch('builtins.input', return_value='yes'):
            result = get_yes_no("Test", default=False)
            self.assertTrue(result)

    def test_get_yes_no_no(self):
        """Test get_yes_no with 'no' input"""
        with patch('builtins.input', return_value='no'):
            result = get_yes_no("Test", default=True)
            self.assertFalse(result)

    def test_get_yes_no_invalid_then_valid(self):
        """Test get_yes_no with invalid then valid input"""
        with patch('builtins.input', side_effect=['invalid', 'y']):
            result = get_yes_no("Test")
            self.assertTrue(result)

    @patch('os.path.exists')
    def test_get_game_folders_valid(self, mock_exists):
        """Test get_game_folders with valid folders"""
        mock_exists.return_value = True

        with patch('builtins.input', side_effect=['/games/folder1', '/games/folder2', '']):
            folders = get_game_folders()
            self.assertEqual(len(folders), 2)
            self.assertIn('/games/folder1', folders)
            self.assertIn('/games/folder2', folders)

    @patch('os.path.exists')
    def test_get_game_folders_nonexistent(self, mock_exists):
        """Test get_game_folders with nonexistent folder"""
        mock_exists.return_value = False

        with patch('builtins.input', side_effect=['/nonexistent', 'y', '']):
            folders = get_game_folders()
            self.assertEqual(len(folders), 1)
            self.assertIn('/nonexistent', folders)

    @patch('os.path.exists')
    def test_get_game_folders_skip_nonexistent(self, mock_exists):
        """Test get_game_folders skipping nonexistent folder"""
        mock_exists.return_value = False

        with patch('builtins.input', side_effect=['/nonexistent', 'n', '']):
            folders = get_game_folders()
            self.assertEqual(len(folders), 0)

    def test_get_custom_commands(self):
        """Test get_custom_commands"""
        with patch('builtins.input', side_effect=['cmd1', 'echo test1', 'cmd2', 'echo test2', '']):
            commands = get_custom_commands()
            self.assertEqual(len(commands), 2)
            self.assertEqual(commands['cmd1'], 'echo test1')
            self.assertEqual(commands['cmd2'], 'echo test2')

    def test_get_custom_commands_empty_command(self):
        """Test get_custom_commands with empty command"""
        with patch('builtins.input', side_effect=['cmd1', '', '']):
            commands = get_custom_commands()
            self.assertEqual(len(commands), 0)


if __name__ == '__main__':
    unittest.main()

