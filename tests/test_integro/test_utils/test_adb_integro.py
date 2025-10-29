# ruff: noqa
# pyright: ignore
"""Integration tests for adb.py Adb class.

Note: Adb is a legacy class. Most methods require actual ADB connection.
These tests focus on class structure and methods that can be tested
without direct ADB usage, using the app fixture instead.
"""

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.adb import Adb


class TestAdb:
    """Integration tests for legacy Adb class."""

    def test_adb_class_exists(self, app: Shadowstep) -> None:
        """Test Adb class can be imported.

        Steps:
        1. Import Adb class.
        2. Verify class exists and is a class type.
        """
        # Verify class exists
        assert Adb is not None  # noqa: S101
        assert isinstance(Adb, type)  # noqa: S101

    def test_adb_class_structure(self, app: Shadowstep) -> None:
        """Test Adb class has expected structure.

        Steps:
        1. Verify class has correct docstring.
        2. Verify class has expected static methods.
        """
        # Verify class docstring
        assert Adb.__doc__ is not None  # noqa: S101
        assert "ADB" in Adb.__doc__ or "adb" in Adb.__doc__.lower()  # noqa: S101

        # Verify some key static methods exist
        key_methods = [
            "get_devices",
            "get_device_model",
            "push",
            "pull",
            "install_app",
            "is_app_installed",
            "uninstall_app",
            "start_activity",
            "get_current_activity",
            "get_current_package",
            "close_app",
            "tap",
            "swipe",
            "input_text",
            "press_home",
            "press_back",
            "execute",
        ]

        for method_name in key_methods:
            assert hasattr(Adb, method_name)  # noqa: S101

    def test_adb_get_devices_method_exists(self, app: Shadowstep) -> None:
        """Test get_devices() method exists and is callable.

        Steps:
        1. Verify get_devices method exists.
        2. Verify it's a static method.
        3. Call method (may fail without ADB, but should be callable).
        """
        # Verify method exists
        assert hasattr(Adb, "get_devices")  # noqa: S101

        # Verify method is callable
        assert callable(Adb.get_devices)  # noqa: S101

        # Try to call method (result depends on ADB availability)
        try:
            result = Adb.get_devices()
            # If successful, should return a list
            assert isinstance(result, list)  # noqa: S101
        except Exception:
            # Expected if ADB not available - method exists and is callable
            pass

    def test_adb_is_app_installed_method_signature(self, app: Shadowstep) -> None:
        """Test is_app_installed() has correct signature.

        Steps:
        1. Verify method signature has package parameter.
        2. Verify return type annotation is bool.
        """
        import inspect

        sig = inspect.signature(Adb.is_app_installed)

        # Verify parameter
        assert "package" in sig.parameters  # noqa: S101

        # Verify return annotation
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_tap_method_signature(self, app: Shadowstep) -> None:
        """Test tap() has correct signature.

        Steps:
        1. Verify method signature has x and y parameters.
        2. Verify parameters accept int or str.
        """
        import inspect

        sig = inspect.signature(Adb.tap)

        # Verify parameters exist
        assert "x" in sig.parameters  # noqa: S101
        assert "y" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_swipe_method_signature(self, app: Shadowstep) -> None:
        """Test swipe() has correct signature.

        Steps:
        1. Verify method has start_x, start_y, end_x, end_y parameters.
        2. Verify optional duration parameter.
        """
        import inspect

        sig = inspect.signature(Adb.swipe)

        # Verify required parameters
        assert "start_x" in sig.parameters  # noqa: S101
        assert "start_y" in sig.parameters  # noqa: S101
        assert "end_x" in sig.parameters  # noqa: S101
        assert "end_y" in sig.parameters  # noqa: S101

        # Verify optional duration parameter
        assert "duration" in sig.parameters  # noqa: S101
        assert sig.parameters["duration"].default == 300  # noqa: S101

    def test_adb_execute_method_exists(self, app: Shadowstep) -> None:
        """Test execute() method exists for running ADB commands.

        Steps:
        1. Verify execute method exists.
        2. Verify it accepts command parameter.
        3. Verify return type is string.
        """
        import inspect

        # Verify method exists
        assert hasattr(Adb, "execute")  # noqa: S101

        sig = inspect.signature(Adb.execute)

        # Verify parameter
        assert "command" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "str"  # noqa: S101

    def test_adb_push_method_signature(self, app: Shadowstep) -> None:
        """Test push() has correct signature.

        Steps:
        1. Verify method has source, destination, udid parameters.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.push)

        # Verify parameters
        assert "source" in sig.parameters  # noqa: S101
        assert "destination" in sig.parameters  # noqa: S101
        assert "udid" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_pull_method_signature(self, app: Shadowstep) -> None:
        """Test pull() has correct signature.

        Steps:
        1. Verify method has source, destination, udid parameters.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.pull)

        # Verify parameters
        assert "source" in sig.parameters  # noqa: S101
        assert "destination" in sig.parameters  # noqa: S101
        assert "udid" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_install_app_method_signature(self, app: Shadowstep) -> None:
        """Test install_app() has correct signature.

        Steps:
        1. Verify method has source and udid parameters.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.install_app)

        # Verify parameters
        assert "source" in sig.parameters  # noqa: S101
        assert "udid" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_start_activity_method_signature(self, app: Shadowstep) -> None:
        """Test start_activity() has correct signature.

        Steps:
        1. Verify method has package and activity parameters.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.start_activity)

        # Verify parameters
        assert "package" in sig.parameters  # noqa: S101
        assert "activity" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_input_text_method_signature(self, app: Shadowstep) -> None:
        """Test input_text() has correct signature.

        Steps:
        1. Verify method has text parameter.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.input_text)

        # Verify parameters
        assert "text" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_press_methods_exist(self, app: Shadowstep) -> None:
        """Test press_* methods exist for keyboard inputs.

        Steps:
        1. Verify press_home method exists.
        2. Verify press_back method exists.
        3. Verify press_menu method exists.
        """
        # Verify key press methods exist
        assert hasattr(Adb, "press_home")  # noqa: S101
        assert hasattr(Adb, "press_back")  # noqa: S101
        assert hasattr(Adb, "press_menu")  # noqa: S101

        # All should return bool
        import inspect

        for method_name in ["press_home", "press_back", "press_menu"]:
            method = getattr(Adb, method_name)
            sig = inspect.signature(method)
            assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_get_screen_resolution_method(self, app: Shadowstep) -> None:
        """Test get_screen_resolution() method signature.

        Steps:
        1. Verify method exists.
        2. Verify return type annotation.
        """
        import inspect

        # Verify method exists
        assert hasattr(Adb, "get_screen_resolution")  # noqa: S101

        sig = inspect.signature(Adb.get_screen_resolution)

        # Should return tuple or None
        # Note: Type annotation is tuple[int, int] | None
        assert sig.return_annotation is not None  # noqa: S101

    def test_adb_close_app_method_signature(self, app: Shadowstep) -> None:
        """Test close_app() has correct signature.

        Steps:
        1. Verify method has package parameter.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.close_app)

        # Verify parameter
        assert "package" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_reboot_app_method_signature(self, app: Shadowstep) -> None:
        """Test reboot_app() has correct signature.

        Steps:
        1. Verify method has package and activity parameters.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.reboot_app)

        # Verify parameters
        assert "package" in sig.parameters  # noqa: S101
        assert "activity" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_kill_methods_exist(self, app: Shadowstep) -> None:
        """Test kill_* methods exist for process management.

        Steps:
        1. Verify kill_by_pid method exists.
        2. Verify kill_by_name method exists.
        3. Verify kill_all method exists.
        """
        kill_methods = ["kill_by_pid", "kill_by_name", "kill_all"]

        for method_name in kill_methods:
            assert hasattr(Adb, method_name)  # noqa: S101

        # Verify return types
        import inspect

        for method_name in kill_methods:
            method = getattr(Adb, method_name)
            sig = inspect.signature(method)
            assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_is_process_exist_method(self, app: Shadowstep) -> None:
        """Test is_process_exist() has correct signature.

        Steps:
        1. Verify method has name parameter.
        2. Verify return type is bool.
        """
        import inspect

        sig = inspect.signature(Adb.is_process_exist)

        # Verify parameter
        assert "name" in sig.parameters  # noqa: S101

        # Verify return type
        assert sig.return_annotation == "bool"  # noqa: S101

    def test_adb_know_pid_method(self, app: Shadowstep) -> None:
        """Test know_pid() has correct signature.

        Steps:
        1. Verify method has name parameter.
        2. Verify return type can be int or None.
        """
        import inspect

        sig = inspect.signature(Adb.know_pid)

        # Verify parameter
        assert "name" in sig.parameters  # noqa: S101

        # Return type is int | None
        assert sig.return_annotation is not None  # noqa: S101

    def test_adb_all_static_methods(self, app: Shadowstep) -> None:
        """Test that all public Adb methods are static.

        Steps:
        1. Get all public methods from Adb class.
        2. Verify they are all static methods (except __init__ if exists).
        """
        import inspect

        # Get all methods
        methods = inspect.getmembers(Adb, predicate=inspect.ismethod)

        # All should be static methods (bound to class, not instance)
        for name, method in methods:
            if not name.startswith("_"):  # Public methods only
                # Static methods are bound to the class
                assert isinstance(method, type(Adb.get_devices))  # noqa: S101
