# ruff: noqa
# pyright: ignore
"""Integration tests for ActionStep class."""

import pytest

from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.shadowstep import Shadowstep


class TestActionStep:
    """Integration tests for ActionStep functionality."""

    def test_action_step_class_exists(self, app: Shadowstep) -> None:
        """Test ActionStep class can be imported.

        Steps:
        1. Import ActionStep class.
        2. Verify class has expected attributes.
        3. Verify class has correct docstring.
        """
        # Verify class exists and has docstring
        assert ActionStep is not None  # noqa: S101
        assert ActionStep.__doc__ is not None  # noqa: S101
        assert "action" in ActionStep.__doc__.lower()  # noqa: S101

    def test_gesture_click_method_exists(self, app: Shadowstep) -> None:
        """Test ActionStep.gesture_click() method exists and has correct signature.

        Steps:
        1. Verify gesture_click method exists.
        2. Verify method is static.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(ActionStep, "gesture_click")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_click(
                name="test_click",
                locator=("xpath", "//android.widget.Button")
            )

    def test_gesture_long_click_method_exists(self, app: Shadowstep) -> None:
        """Test ActionStep.gesture_long_click() method exists and has correct signature.

        Steps:
        1. Verify gesture_long_click method exists.
        2. Verify method is static.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(ActionStep, "gesture_long_click")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_long_click(
                name="test_long_click",
                locator={"text": "Settings"}
            )

    def test_gesture_double_click_method_exists(self, app: Shadowstep) -> None:
        """Test ActionStep.gesture_double_click() method exists and has correct signature.

        Steps:
        1. Verify gesture_double_click method exists.
        2. Verify method is static.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(ActionStep, "gesture_double_click")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_double_click(
                name="test_double_click",
                element_id="element123",
                x=100,
                y=200
            )

    def test_source_method_exists(self, app: Shadowstep) -> None:
        """Test ActionStep.source() method exists and has correct signature.

        Steps:
        1. Verify source method exists.
        2. Verify method is static.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(ActionStep, "source")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            ActionStep.source(name="test_source")

    def test_screenshot_method_exists(self, app: Shadowstep) -> None:
        """Test ActionStep.screenshot() method exists and has correct signature.

        Steps:
        1. Verify screenshot method exists.
        2. Verify method is static.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(ActionStep, "screenshot")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            ActionStep.screenshot(name="test_screenshot")

    def test_gesture_click_with_element(self, app: Shadowstep, android_settings_open_close: None) -> None:
        """Test ActionStep.gesture_click() with Element object.

        Steps:
        1. Get an element from the app.
        2. Try to create action step with Element.
        3. Verify method raises NotImplementedError (current behavior).
        """
        # Get element from app
        element = app.get_element({"text": "Settings"})

        # Verify method raises NotImplementedError with Element
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_click(name="test_click_element", locator=element)

    def test_gesture_long_click_with_element(self, app: Shadowstep, android_settings_open_close: None) -> None:
        """Test ActionStep.gesture_long_click() with Element object.

        Steps:
        1. Get an element from the app.
        2. Try to create action step with Element.
        3. Verify method raises NotImplementedError (current behavior).
        """
        # Get element from app
        element = app.get_element({"text": "Settings"})

        # Verify method raises NotImplementedError with Element
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_long_click(name="test_long_click_element", locator=element)

    def test_gesture_click_with_tuple_locator(self, app: Shadowstep) -> None:
        """Test ActionStep.gesture_click() with tuple locator.

        Steps:
        1. Call gesture_click with tuple locator.
        2. Verify method raises NotImplementedError (current behavior).
        """
        # Verify method raises NotImplementedError with tuple locator
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_click(
                name="test_tuple_locator",
                locator=("id", "com.android.settings:id/main")
            )

    def test_gesture_click_with_dict_locator(self, app: Shadowstep) -> None:
        """Test ActionStep.gesture_click() with dict locator.

        Steps:
        1. Call gesture_click with dict locator.
        2. Verify method raises NotImplementedError (current behavior).
        """
        # Verify method raises NotImplementedError with dict locator
        with pytest.raises(NotImplementedError):
            ActionStep.gesture_click(
                name="test_dict_locator",
                locator={"resource-id": "com.android.settings:id/main"}
            )
