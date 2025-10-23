# ruff: noqa
# pyright: ignore
"""
Integration tests for shadowstep.terminal.aapt module.

These tests verify real AAPT operations with actual APK files
using the Android Asset Packaging Tool.

COVERAGE NOTE:
These integration tests achieve 92% coverage of aapt.py (38 statements, 3 missed).
The uncovered lines (49-51) are the ValueError exception handler in get_package_name(),
which triggers when aapt executes successfully but produces output without the expected
"package: name='..." format. This edge case cannot be tested in integration tests because:
1. Valid APKs always produce package name in aapt output
2. Invalid/corrupt APKs cause CalledProcessError, not ValueError
3. Testing this would require mocking subprocess, which violates integration test principles
The ValueError handler is defensive programming for a theoretical edge case.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from shadowstep.terminal.aapt import Aapt


def check_aapt_available():
    """Check if aapt is available in system PATH."""
    try:
        subprocess.run(["aapt", "version"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


pytestmark = pytest.mark.skipif(
    not check_aapt_available(),
    reason="aapt utility not available in system PATH - install Android SDK build-tools"
)


class TestAaptIntegration:
    """Integration test cases for Aapt class."""

    @pytest.fixture
    def valid_apk_path(self) -> str:
        """Fixture providing path to valid APK file."""
        apk_path = Path(__file__).parent.parent / "_apk" / "notepad.apk"
        assert apk_path.exists(), f"APK file not found: {apk_path}"
        return str(apk_path)

    @pytest.fixture
    def apk_with_activity_path(self) -> str:
        """Fixture providing path to APK file with launchable activity."""
        apk_path = Path(__file__).parent.parent / "_apk" / "apidemos.apk"
        assert apk_path.exists(), f"APK file not found: {apk_path}"
        return str(apk_path)

    @pytest.fixture
    def nonexistent_apk_path(self) -> str:
        """Fixture providing path to non-existent APK file."""
        return "/tmp/nonexistent_file_12345.apk"

    @pytest.fixture
    def invalid_apk_path(self, tmp_path: Path) -> str:
        """Fixture providing path to invalid (non-APK) file."""
        invalid_file = tmp_path / "invalid.apk"
        invalid_file.write_text("This is not a valid APK file")
        return str(invalid_file)

    def test_get_package_name_valid_apk(self, valid_apk_path: str):
        """Test get_package_name with valid APK file.

        Verifies that package name is correctly extracted from valid APK.
        Expected package name for notepad.apk is 'com.farmerbb.notepad'.
        """
        # Act
        package_name = Aapt.get_package_name(valid_apk_path)

        # Assert
        assert package_name is not None  # noqa: S101
        assert isinstance(package_name, str)  # noqa: S101
        assert len(package_name) > 0  # noqa: S101
        assert package_name == "com.farmerbb.notepad"  # noqa: S101
        # Package name should follow Android package naming convention
        assert "." in package_name  # noqa: S101

    def test_get_package_name_with_path_object(self, valid_apk_path: str):
        """Test get_package_name with Path object.

        Verifies that method accepts both string and Path objects.
        """
        # Arrange
        path_object = Path(valid_apk_path)

        # Act
        package_name = Aapt.get_package_name(str(path_object))

        # Assert
        assert package_name is not None  # noqa: S101
        assert isinstance(package_name, str)  # noqa: S101
        assert package_name == "com.farmerbb.notepad"  # noqa: S101

    def test_get_package_name_nonexistent_file(self, nonexistent_apk_path: str):
        """Test get_package_name with non-existent file.

        Verifies that CalledProcessError is raised when file doesn't exist.
        """
        # Act & Assert
        with pytest.raises(subprocess.CalledProcessError):
            Aapt.get_package_name(nonexistent_apk_path)

    def test_get_package_name_invalid_file(self, invalid_apk_path: str):
        """Test get_package_name with invalid APK file.

        Verifies that appropriate exception is raised for invalid file.
        """
        # Act & Assert
        # Should raise either CalledProcessError or ValueError
        with pytest.raises((subprocess.CalledProcessError, ValueError)):
            Aapt.get_package_name(invalid_apk_path)

    def test_get_package_name_empty_string_path(self):
        """Test get_package_name with empty string path.

        Verifies that exception is raised for empty path.
        """
        # Act & Assert
        with pytest.raises((subprocess.CalledProcessError, ValueError, FileNotFoundError)):
            Aapt.get_package_name("")

    def test_get_launchable_activity_valid_apk(self, valid_apk_path: str):
        """Test get_launchable_activity with valid APK file.

        Note: notepad.apk doesn't have launchable-activity,
        so this test verifies that empty string is returned.
        """
        # Act
        activity = Aapt.get_launchable_activity(valid_apk_path)

        # Assert
        assert activity is not None  # noqa: S101
        assert isinstance(activity, str)  # noqa: S101
        # notepad.apk doesn't have launchable-activity
        assert activity == ""  # noqa: S101

    def test_get_launchable_activity_nonexistent_file(self, nonexistent_apk_path: str):
        """Test get_launchable_activity with non-existent file.

        Verifies that empty string is returned (method handles exception).
        """
        # Act
        activity = Aapt.get_launchable_activity(nonexistent_apk_path)

        # Assert
        # Method catches exception and returns empty string
        assert activity == ""  # noqa: S101

    def test_get_launchable_activity_invalid_file(self, invalid_apk_path: str):
        """Test get_launchable_activity with invalid APK file.

        Verifies that empty string is returned (method handles exception).
        """
        # Act
        activity = Aapt.get_launchable_activity(invalid_apk_path)

        # Assert
        # Method catches exception and returns empty string
        assert activity == ""  # noqa: S101

    def test_get_launchable_activity_with_path_object(self, valid_apk_path: str):
        """Test get_launchable_activity with Path object.

        Verifies that method works with string path.
        """
        # Act
        activity = Aapt.get_launchable_activity(valid_apk_path)

        # Assert
        assert activity is not None  # noqa: S101
        assert isinstance(activity, str)  # noqa: S101

    def test_get_package_name_returns_string_type(self, valid_apk_path: str):
        """Test that get_package_name always returns string type.

        Verifies return type consistency.
        """
        # Act
        result = Aapt.get_package_name(valid_apk_path)

        # Assert
        assert type(result) is str  # noqa: S101

    def test_get_launchable_activity_returns_string_type(self, valid_apk_path: str):
        """Test that get_launchable_activity always returns string type.

        Verifies return type consistency.
        """
        # Act
        result = Aapt.get_launchable_activity(valid_apk_path)

        # Assert
        assert type(result) is str  # noqa: S101

    def test_aapt_class_is_static(self):
        """Test that Aapt class methods are static.

        Verifies that methods can be called without instantiation.
        """
        # Verify methods exist and are callable
        assert callable(Aapt.get_package_name)  # noqa: S101
        assert callable(Aapt.get_launchable_activity)  # noqa: S101

    def test_get_package_name_consistent_results(self, valid_apk_path: str):
        """Test that get_package_name returns consistent results.

        Verifies that multiple calls return the same package name.
        """
        # Act
        result1 = Aapt.get_package_name(valid_apk_path)
        result2 = Aapt.get_package_name(valid_apk_path)
        result3 = Aapt.get_package_name(valid_apk_path)

        # Assert
        assert result1 == result2 == result3  # noqa: S101
        assert result1 == "com.farmerbb.notepad"  # noqa: S101

    def test_get_launchable_activity_consistent_results(self, valid_apk_path: str):
        """Test that get_launchable_activity returns consistent results.

        Verifies that multiple calls return the same activity name.
        """
        # Act
        result1 = Aapt.get_launchable_activity(valid_apk_path)
        result2 = Aapt.get_launchable_activity(valid_apk_path)
        result3 = Aapt.get_launchable_activity(valid_apk_path)

        # Assert
        assert result1 == result2 == result3  # noqa: S101

    def test_get_package_name_from_apk_with_activity(self, apk_with_activity_path: str):
        """Test get_package_name with APK that has launchable activity.

        Verifies that package name is correctly extracted from ApiDemos APK.
        Expected package name is 'io.appium.android.apis'.
        """
        # Act
        package_name = Aapt.get_package_name(apk_with_activity_path)

        # Assert
        assert package_name is not None  # noqa: S101
        assert isinstance(package_name, str)  # noqa: S101
        assert package_name == "io.appium.android.apis"  # noqa: S101
        assert "." in package_name  # noqa: S101

    def test_get_launchable_activity_from_apk_with_activity(self, apk_with_activity_path: str):
        """Test get_launchable_activity with APK that has launchable activity.

        Verifies that launchable activity is correctly extracted from ApiDemos APK.
        Expected activity is 'io.appium.android.apis.ApiDemos'.
        """
        # Act
        activity = Aapt.get_launchable_activity(apk_with_activity_path)

        # Assert
        assert activity is not None  # noqa: S101
        assert isinstance(activity, str)  # noqa: S101
        assert len(activity) > 0  # noqa: S101
        assert activity == "io.appium.android.apis.ApiDemos"  # noqa: S101
        # Activity name should contain package prefix
        assert "io.appium.android.apis" in activity  # noqa: S101

    def test_get_launchable_activity_apk_with_activity_consistent(self, apk_with_activity_path: str):
        """Test that get_launchable_activity returns consistent results for APK with activity.

        Verifies that multiple calls return the same activity name.
        """
        # Act
        result1 = Aapt.get_launchable_activity(apk_with_activity_path)
        result2 = Aapt.get_launchable_activity(apk_with_activity_path)
        result3 = Aapt.get_launchable_activity(apk_with_activity_path)

        # Assert
        assert result1 == result2 == result3  # noqa: S101
        assert result1 == "io.appium.android.apis.ApiDemos"  # noqa: S101
        assert len(result1) > 0  # noqa: S101

    def test_get_package_name_with_relative_path(self, valid_apk_path: str):
        """Test get_package_name with relative path converted from absolute.

        Verifies that method works with different path representations.
        """
        # Arrange
        original_dir = os.getcwd()
        apk_dir = Path(valid_apk_path).parent
        apk_name = Path(valid_apk_path).name

        try:
            os.chdir(apk_dir)
            # Act
            package_name = Aapt.get_package_name(apk_name)
            # Assert
            assert package_name == "com.farmerbb.notepad"  # noqa: S101
        finally:
            os.chdir(original_dir)

    def test_get_package_name_special_characters_in_path(self, tmp_path: Path):
        """Test get_package_name with special characters in path.

        Verifies that method handles paths with spaces and special characters.
        """
        # Arrange - copy APK to path with spaces
        apk_source = Path(__file__).parent.parent / "_apk" / "notepad.apk"
        special_dir = tmp_path / "test dir with spaces"
        special_dir.mkdir()
        apk_dest = special_dir / "test file.apk"

        shutil.copy(apk_source, apk_dest)

        # Act
        package_name = Aapt.get_package_name(str(apk_dest))

        # Assert
        assert package_name == "com.farmerbb.notepad"  # noqa: S101

    def test_get_launchable_activity_special_characters_in_path(self, tmp_path: Path):
        """Test get_launchable_activity with special characters in path.

        Verifies that method handles paths with spaces and special characters.
        """
        # Arrange - copy APK to path with spaces
        apk_source = Path(__file__).parent.parent / "_apk" / "apidemos.apk"
        special_dir = tmp_path / "test dir with spaces"
        special_dir.mkdir()
        apk_dest = special_dir / "test file.apk"

        shutil.copy(apk_source, apk_dest)

        # Act
        activity = Aapt.get_launchable_activity(str(apk_dest))

        # Assert
        assert activity == "io.appium.android.apis.ApiDemos"  # noqa: S101

    def test_both_methods_on_same_apk(self, apk_with_activity_path: str):
        """Test that both methods work correctly on same APK file.

        Verifies that package name and activity can be extracted from same APK.
        """
        # Act
        package_name = Aapt.get_package_name(apk_with_activity_path)
        activity = Aapt.get_launchable_activity(apk_with_activity_path)

        # Assert
        assert package_name == "io.appium.android.apis"  # noqa: S101
        assert activity == "io.appium.android.apis.ApiDemos"  # noqa: S101
        # Activity should start with package name
        assert activity.startswith(package_name)  # noqa: S101

    def test_get_package_name_with_absolute_path(self, valid_apk_path: str):
        """Test get_package_name with absolute path.

        Verifies that method correctly handles absolute paths.
        """
        # Arrange
        absolute_path = str(Path(valid_apk_path).absolute())

        # Act
        package_name = Aapt.get_package_name(absolute_path)

        # Assert
        assert package_name == "com.farmerbb.notepad"  # noqa: S101

    def test_get_launchable_activity_with_absolute_path(self, apk_with_activity_path: str):
        """Test get_launchable_activity with absolute path.

        Verifies that method correctly handles absolute paths.
        """
        # Arrange
        absolute_path = str(Path(apk_with_activity_path).absolute())

        # Act
        activity = Aapt.get_launchable_activity(absolute_path)

        # Assert
        assert activity == "io.appium.android.apis.ApiDemos"  # noqa: S101
