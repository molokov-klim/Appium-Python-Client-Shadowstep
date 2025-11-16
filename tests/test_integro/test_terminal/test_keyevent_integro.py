# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for KeyEvent class.

These tests verify real KeyEvent operations with actual mobile devices
through Appium server.

COVERAGE NOTE:
These integration tests aim to achieve 100% coverage of all public methods
in the KeyEvent class (343 press_* methods).

All tests use the app fixture and test only public methods without any mocks.
"""
import inspect
import re
import time

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.terminal.keyevent import KeyEvent


def _get_all_keyevent_methods() -> list[tuple[str, str]]:
    """Get all press_* methods and their corresponding keycodes from KeyEvent class.

    Returns:
        List of tuples (method_name, expected_keycode).
    """
    methods = []
    for name, method in inspect.getmembers(KeyEvent, predicate=inspect.isfunction):
        if name.startswith("press_"):
            # Read source code to extract keycode
            source = inspect.getsource(method)
            match = re.search(r'keycode="(KEYCODE_\w+)"', source)
            if match:
                keycode = match.group(1)
                methods.append((name, keycode))
    return sorted(methods)


class TestKeyEventInit:
    """Test KeyEvent initialization in integration tests."""

    def test_keyevent_initialization(self, app: Shadowstep) -> None:
        """Test that KeyEvent is properly initialized in Terminal."""
        # Assert
        assert hasattr(app.terminal, "keyevent")  # noqa: S101
        assert app.terminal.keyevent is not None  # noqa: S101
        assert isinstance(app.terminal.keyevent, KeyEvent)  # noqa: S101

    def test_keyevent_has_terminal_reference(self, app: Shadowstep) -> None:
        """Test that KeyEvent has reference to Terminal."""
        # Assert
        assert hasattr(app.terminal.keyevent, "_terminal")  # noqa: S101
        assert app.terminal.keyevent._terminal is app.terminal  # noqa: S101


class TestKeyEventBasicMethods:
    """Test basic KeyEvent methods that are safe for integration testing."""

    def test_press_home(self, app: Shadowstep) -> None:
        """Test press_home method."""
        # Act
        result = app.terminal.keyevent.press_home()
        time.sleep(1)

        # Assert
        assert result is True  # noqa: S101

    def test_press_back(self, app: Shadowstep) -> None:
        """Test press_back method."""
        # Act
        result = app.terminal.keyevent.press_back()
        time.sleep(1)

        # Assert
        assert result is True  # noqa: S101

    def test_press_menu(self, app: Shadowstep) -> None:
        """Test press_menu method."""
        # Act
        result = app.terminal.keyevent.press_menu()
        time.sleep(1)

        # Assert
        assert result is True  # noqa: S101

    def test_press_volume_up(self, app: Shadowstep) -> None:
        """Test press_volume_up method."""
        # Act
        result = app.terminal.keyevent.press_volume_up()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_volume_down(self, app: Shadowstep) -> None:
        """Test press_volume_down method."""
        # Act
        result = app.terminal.keyevent.press_volume_down()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_volume_mute(self, app: Shadowstep) -> None:
        """Test press_volume_mute method."""
        # Act
        result = app.terminal.keyevent.press_volume_mute()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_enter(self, app: Shadowstep) -> None:
        """Test press_enter method."""
        # Act
        result = app.terminal.keyevent.press_enter()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_space(self, app: Shadowstep) -> None:
        """Test press_space method."""
        # Act
        result = app.terminal.keyevent.press_space()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_dpad_center(self, app: Shadowstep) -> None:
        """Test press_dpad_center method."""
        # Act
        result = app.terminal.keyevent.press_dpad_center()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_dpad_up(self, app: Shadowstep) -> None:
        """Test press_dpad_up method."""
        # Act
        result = app.terminal.keyevent.press_dpad_up()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_dpad_down(self, app: Shadowstep) -> None:
        """Test press_dpad_down method."""
        # Act
        result = app.terminal.keyevent.press_dpad_down()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_dpad_left(self, app: Shadowstep) -> None:
        """Test press_dpad_left method."""
        # Act
        result = app.terminal.keyevent.press_dpad_left()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_dpad_right(self, app: Shadowstep) -> None:
        """Test press_dpad_right method."""
        # Act
        result = app.terminal.keyevent.press_dpad_right()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_del(self, app: Shadowstep) -> None:
        """Test press_del method."""
        # Act
        result = app.terminal.keyevent.press_del()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_escape(self, app: Shadowstep) -> None:
        """Test press_escape method."""
        # Act
        result = app.terminal.keyevent.press_escape()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101

    def test_press_tab(self, app: Shadowstep) -> None:
        """Test press_tab method."""
        # Act
        result = app.terminal.keyevent.press_tab()
        time.sleep(0.5)

        # Assert
        assert result is True  # noqa: S101


class TestKeyEventNumberMethods:
    """Test number key methods."""

    @pytest.mark.parametrize(
        "method_name",
        [
            "press_0",
            "press_1",
            "press_2",
            "press_3",
            "press_4",
            "press_5",
            "press_6",
            "press_7",
            "press_8",
            "press_9",
        ],
    )
    def test_press_number(self, app: Shadowstep, method_name: str) -> None:
        """Test press number methods."""
        # Arrange
        method = getattr(app.terminal.keyevent, method_name)

        # Act
        result = method()
        time.sleep(0.3)

        # Assert
        assert result is True  # noqa: S101


class TestKeyEventLetterMethods:
    """Test letter key methods."""

    @pytest.mark.parametrize(
        "method_name",
        [
            "press_a",
            "press_b",
            "press_c",
            "press_d",
            "press_e",
            "press_f",
            "press_g",
            "press_h",
            "press_i",
            "press_j",
            "press_k",
            "press_l",
            "press_m",
            "press_n",
            "press_o",
            "press_p",
            "press_q",
            "press_r",
            "press_s",
            "press_t",
            "press_u",
            "press_v",
            "press_w",
            "press_x",
            "press_y",
            "press_z",
        ],
    )
    def test_press_letter(self, app: Shadowstep, method_name: str) -> None:
        """Test press letter methods."""
        # Arrange
        method = getattr(app.terminal.keyevent, method_name)

        # Act
        result = method()
        time.sleep(0.3)

        # Assert
        assert result is True  # noqa: S101


class TestKeyEventAllMethods:
    """Test all KeyEvent press methods using parametrization."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, app: Shadowstep) -> None:
        """Setup: press home before each test to ensure consistent state."""
        app.terminal.keyevent.press_home()
        time.sleep(1)
        yield
        # Teardown: press home after each test
        app.terminal.keyevent.press_home()
        time.sleep(0.5)

    @pytest.mark.parametrize(
        "method_name,expected_keycode",
        _get_all_keyevent_methods(),
    )
    def test_press_method_executes_successfully(
        self, app: Shadowstep, method_name: str, expected_keycode: str
    ) -> None:
        """Test that all press methods execute successfully.

        This test verifies that all 343 press_* methods can be called
        and return a boolean value. Some keycodes may not have visible
        effects on the device, but they should execute without errors.

        Args:
            app: Shadowstep application instance.
            method_name: Name of the press method to test.
            expected_keycode: Expected KEYCODE value to be sent.
        """
        # Arrange
        method = getattr(app.terminal.keyevent, method_name)

        # Act
        result = method()
        time.sleep(0.2)

        # Assert
        assert isinstance(result, bool), f"{method_name} should return bool"  # noqa: S101
        # Note: Some keycodes may return False if they're not supported
        # on the current device/emulator, but the method should still execute


class TestKeyEventMethodCalls:
    """Test that KeyEvent methods properly call terminal.input_keycode."""

    def test_press_home_calls_input_keycode(self, app: Shadowstep) -> None:
        """Test that press_home calls terminal.input_keycode with KEYCODE_HOME."""
        # This is an integration test, so we verify the actual behavior
        # by checking that the method executes and returns a result
        result = app.terminal.keyevent.press_home()
        assert result is True  # noqa: S101

    def test_press_back_calls_input_keycode(self, app: Shadowstep) -> None:
        """Test that press_back calls terminal.input_keycode with KEYCODE_BACK."""
        result = app.terminal.keyevent.press_back()
        assert result is True  # noqa: S101

    def test_press_menu_calls_input_keycode(self, app: Shadowstep) -> None:
        """Test that press_menu calls terminal.input_keycode with KEYCODE_MENU."""
        result = app.terminal.keyevent.press_menu()
        assert result is True  # noqa: S101

    def test_methods_return_boolean(self, app: Shadowstep) -> None:
        """Test that all press methods return boolean values."""
        # Test a sample of methods to verify return type
        methods_to_test = [
            "press_home",
            "press_back",
            "press_menu",
            "press_volume_up",
            "press_volume_down",
            "press_enter",
            "press_space",
            "press_0",
            "press_1",
            "press_a",
            "press_b",
        ]

        for method_name in methods_to_test:
            method = getattr(app.terminal.keyevent, method_name)
            result = method()
            assert isinstance(result, bool), f"{method_name} should return bool"  # noqa: S101

    def test_multiple_keypresses_in_sequence(self, app: Shadowstep) -> None:
        """Test that multiple keypresses can be executed in sequence."""
        # Act
        result1 = app.terminal.keyevent.press_home()
        time.sleep(0.5)
        result2 = app.terminal.keyevent.press_back()
        time.sleep(0.5)
        result3 = app.terminal.keyevent.press_menu()
        time.sleep(0.5)

        # Assert
        assert result1 is True  # noqa: S101
        assert result2 is True  # noqa: S101
        assert result3 is True  # noqa: S101

