# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Unit tests for KeyEvent class using mocks."""
import re
from unittest.mock import Mock

import pytest

from shadowstep.terminal.keyevent import KeyEvent


def _get_all_keyevent_methods() -> list[tuple[str, str]]:
    """Get all press_* methods and their corresponding keycodes from KeyEvent class.

    Returns:
        List of tuples (method_name, expected_keycode).
    """
    import inspect
    from shadowstep.terminal.keyevent import KeyEvent

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
    """Test KeyEvent initialization."""

    @pytest.mark.unit
    def test_init(self) -> None:
        """Test KeyEvent initialization with Terminal mock."""
        # Arrange
        mock_terminal = Mock()

        # Act
        keyevent = KeyEvent(mock_terminal)

        # Assert
        assert keyevent._terminal is mock_terminal  # noqa: S101

    @pytest.mark.unit
    def test_init_terminal_assignment(self) -> None:
        """Test that terminal is correctly assigned during initialization."""
        # Arrange
        mock_terminal = Mock()
        mock_terminal.input_keycode = Mock(return_value=True)

        # Act
        keyevent = KeyEvent(mock_terminal)

        # Assert
        assert hasattr(keyevent, "_terminal")  # noqa: S101
        assert keyevent._terminal == mock_terminal  # noqa: S101


class TestKeyEventPressMethods:
    """Test all press_* methods of KeyEvent class."""

    @pytest.fixture
    def mock_terminal(self) -> Mock:
        """Create a mock Terminal instance."""
        terminal = Mock()
        terminal.input_keycode = Mock(return_value=True)
        return terminal

    @pytest.fixture
    def keyevent(self, mock_terminal: Mock) -> KeyEvent:
        """Create KeyEvent instance with mocked Terminal."""
        return KeyEvent(mock_terminal)

    @pytest.mark.parametrize(
        "method_name,expected_keycode",
        _get_all_keyevent_methods(),
    )
    @pytest.mark.unit
    def test_press_method_calls_terminal_with_correct_keycode(
        self,
        keyevent: KeyEvent,
        mock_terminal: Mock,
        method_name: str,
        expected_keycode: str,
    ) -> None:
        """Test that press method calls terminal.input_keycode with correct keycode.

        Args:
            keyevent: KeyEvent instance with mocked terminal.
            mock_terminal: Mock Terminal instance.
            method_name: Name of the press method to test.
            expected_keycode: Expected KEYCODE value to be passed.
        """
        # Arrange
        method = getattr(keyevent, method_name)
        mock_terminal.input_keycode.return_value = True

        # Act
        result = method()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode=expected_keycode)
        assert result is True  # noqa: S101

    @pytest.mark.parametrize(
        "method_name,expected_keycode",
        _get_all_keyevent_methods(),
    )
    @pytest.mark.unit
    def test_press_method_returns_false_on_failure(
        self,
        keyevent: KeyEvent,
        mock_terminal: Mock,
        method_name: str,
        expected_keycode: str,
    ) -> None:
        """Test that press method returns False when terminal.input_keycode returns False.

        Args:
            keyevent: KeyEvent instance with mocked terminal.
            mock_terminal: Mock Terminal instance.
            method_name: Name of the press method to test.
            expected_keycode: Expected KEYCODE value to be passed.
        """
        # Arrange
        method = getattr(keyevent, method_name)
        mock_terminal.input_keycode.return_value = False

        # Act
        result = method()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode=expected_keycode)
        assert result is False  # noqa: S101

    @pytest.mark.parametrize(
        "method_name,expected_keycode",
        _get_all_keyevent_methods(),
    )
    @pytest.mark.unit
    def test_press_method_returns_true_on_success(
        self,
        keyevent: KeyEvent,
        mock_terminal: Mock,
        method_name: str,
        expected_keycode: str,
    ) -> None:
        """Test that press method returns True when terminal.input_keycode returns True.

        Args:
            keyevent: KeyEvent instance with mocked terminal.
            mock_terminal: Mock Terminal instance.
            method_name: Name of the press method to test.
            expected_keycode: Expected KEYCODE value to be passed.
        """
        # Arrange
        method = getattr(keyevent, method_name)
        mock_terminal.input_keycode.return_value = True

        # Act
        result = method()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode=expected_keycode)
        assert result is True  # noqa: S101


class TestKeyEventSpecificMethods:
    """Test specific keyevent methods for edge cases."""

    @pytest.fixture
    def mock_terminal(self) -> Mock:
        """Create a mock Terminal instance."""
        terminal = Mock()
        terminal.input_keycode = Mock(return_value=True)
        return terminal

    @pytest.fixture
    def keyevent(self, mock_terminal: Mock) -> KeyEvent:
        """Create KeyEvent instance with mocked Terminal."""
        return KeyEvent(mock_terminal)

    @pytest.mark.unit
    def test_press_home_calls_input_keycode(self, keyevent: KeyEvent, mock_terminal: Mock) -> None:
        """Test that press_home calls terminal.input_keycode with KEYCODE_HOME."""
        # Act
        result = keyevent.press_home()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_HOME")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_back_calls_input_keycode(self, keyevent: KeyEvent, mock_terminal: Mock) -> None:
        """Test that press_back calls terminal.input_keycode with KEYCODE_BACK."""
        # Act
        result = keyevent.press_back()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_BACK")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_menu_calls_input_keycode(self, keyevent: KeyEvent, mock_terminal: Mock) -> None:
        """Test that press_menu calls terminal.input_keycode with KEYCODE_MENU."""
        # Act
        result = keyevent.press_menu()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_MENU")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_volume_up_calls_input_keycode(
        self, keyevent: KeyEvent, mock_terminal: Mock
    ) -> None:
        """Test that press_volume_up calls terminal.input_keycode with KEYCODE_VOLUME_UP."""
        # Act
        result = keyevent.press_volume_up()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_VOLUME_UP")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_volume_down_calls_input_keycode(
        self, keyevent: KeyEvent, mock_terminal: Mock
    ) -> None:
        """Test that press_volume_down calls terminal.input_keycode with KEYCODE_VOLUME_DOWN."""
        # Act
        result = keyevent.press_volume_down()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_VOLUME_DOWN")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_enter_calls_input_keycode(self, keyevent: KeyEvent, mock_terminal: Mock) -> None:
        """Test that press_enter calls terminal.input_keycode with KEYCODE_ENTER."""
        # Act
        result = keyevent.press_enter()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_ENTER")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_space_calls_input_keycode(self, keyevent: KeyEvent, mock_terminal: Mock) -> None:
        """Test that press_space calls terminal.input_keycode with KEYCODE_SPACE."""
        # Act
        result = keyevent.press_space()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_SPACE")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_dpad_center_calls_input_keycode(
        self, keyevent: KeyEvent, mock_terminal: Mock
    ) -> None:
        """Test that press_dpad_center calls terminal.input_keycode with KEYCODE_DPAD_CENTER."""
        # Act
        result = keyevent.press_dpad_center()

        # Assert
        mock_terminal.input_keycode.assert_called_once_with(keycode="KEYCODE_DPAD_CENTER")
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_press_method_propagates_exception(
        self, keyevent: KeyEvent, mock_terminal: Mock
    ) -> None:
        """Test that exceptions from terminal.input_keycode are propagated."""
        # Arrange
        mock_terminal.input_keycode.side_effect = ValueError("Test error")

        # Act & Assert
        with pytest.raises(ValueError, match="Test error"):
            keyevent.press_home()

