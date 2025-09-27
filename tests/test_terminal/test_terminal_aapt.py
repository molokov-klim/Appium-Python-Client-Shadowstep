# tests/terminal/test_terminal_aapt.py
"""
Tests for shadowstep.terminal.aapt module.
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from shadowstep.terminal.aapt import Aapt


class TestAapt:
    """Test cases for Aapt class."""

    def test_get_package_name_success(self):
        """Test successful package name extraction."""
        # Arrange
        mock_output = b"package: name='com.example.app' versionCode='1' versionName='1.0'"
        expected_package = "com.example.app"
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = Aapt.get_package_name(apk_path)

            # Assert
            assert result == expected_package  # noqa: S101
            mock_subprocess.assert_called_once_with(["aapt", "dump", "badging", apk_path])

    def test_get_package_name_subprocess_error(self):
        """Test package name extraction with subprocess error."""
        # Arrange
        apk_path = "/path/to/invalid._apk"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "aapt")), \
             pytest.raises(subprocess.CalledProcessError):
            # Act & Assert
                Aapt.get_package_name(apk_path)

    def test_get_package_name_value_error(self):
        """Test package name extraction with ValueError (package name not found)."""
        # Arrange
        mock_output = b"invalid output without package name"
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output), \
             pytest.raises(ValueError, match=".*"):  # noqa: PT011
            # Act & Assert
                Aapt.get_package_name(apk_path)

    def test_get_launchable_activity_success(self):
        """Test successful launchable activity extraction."""
        # Arrange
        mock_output = """package: name='com.example.app' versionCode='1' versionName='1.0'
launchable-activity: name='com.example.app.MainActivity' label='App' icon=''
application: label='App' icon=''"""
        expected_activity = "com.example.app.MainActivity"
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            result = Aapt.get_launchable_activity(apk_path)

            # Assert
            assert result == expected_activity  # noqa: S101
            mock_subprocess.assert_called_once_with(["aapt", "dump", "badging", apk_path], universal_newlines=True)

    def test_get_launchable_activity_subprocess_error(self):
        """Test launchable activity extraction with subprocess error."""
        # Arrange
        apk_path = "/path/to/invalid._apk"

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "aapt")):
            # Act
            result = Aapt.get_launchable_activity(apk_path)

            # Assert
            assert result == ""  # noqa: S101

    def test_get_launchable_activity_stop_iteration(self):
        """Test launchable activity extraction with StopIteration (no launchable-activity found)."""
        # Arrange
        mock_output = """package: name='com.example.app' versionCode='1' versionName='1.0'
application: label='App' icon=''"""
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Aapt.get_launchable_activity(apk_path)

            # Assert
            assert result == ""  # noqa: S101

    def test_get_launchable_activity_empty_output(self):
        """Test launchable activity extraction with empty output."""
        # Arrange
        mock_output = ""
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Aapt.get_launchable_activity(apk_path)

            # Assert
            assert result == ""  # noqa: S101

    def test_get_launchable_activity_multiple_activities(self):
        """Test launchable activity extraction with multiple activities (should return first)."""
        # Arrange
        mock_output = """package: name='com.example.app' versionCode='1' versionName='1.0'
launchable-activity: name='com.example.app.MainActivity' label='Main' icon=''
launchable-activity: name='com.example.app.SecondActivity' label='Second' icon=''
application: label='App' icon=''"""
        expected_activity = "com.example.app.MainActivity"
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output):
            # Act
            result = Aapt.get_launchable_activity(apk_path)

            # Assert
            assert result == expected_activity  # noqa: S101

    def test_get_package_name_with_path_construction(self):
        """Test that Path is used correctly in get_package_name."""
        # Arrange
        mock_output = b"package: name='com.example.app' versionCode='1' versionName='1.0'"
        apk_path = "app._apk"
        expected_path = str(Path(apk_path))

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
                # Act
                Aapt.get_package_name(apk_path)

                # Assert
                mock_subprocess.assert_called_once_with(["aapt", "dump", "badging", expected_path])

    def test_get_launchable_activity_direct_path(self):
        """Test that get_launchable_activity uses path directly without os.path.join."""
        # Arrange
        mock_output = """package: name='com.example.app' versionCode='1' versionName='1.0'
launchable-activity: name='com.example.app.MainActivity' label='App' icon=''"""
        apk_path = "/path/to/app._apk"

        with patch("subprocess.check_output", return_value=mock_output) as mock_subprocess:
            # Act
            Aapt.get_launchable_activity(apk_path)

            # Assert
            mock_subprocess.assert_called_once_with(["aapt", "dump", "badging", apk_path], universal_newlines=True)
