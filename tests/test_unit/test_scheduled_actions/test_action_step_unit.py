# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Unit tests for ActionStep class."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from shadowstep.scheduled_actions.action_step import ActionStep


class TestActionStepGestureClick:
    """Unit tests for ActionStep.gesture_click method."""

    def test_gesture_click_with_tuple_locator(self) -> None:
        """Test gesture_click with tuple locator."""
        # Arrange
        name = "click_button"
        locator = ("id", "com.example:id/button")

        # Act
        step = ActionStep.gesture_click(name, locator)

        # Assert
        assert step.type == "gesture"
        assert step.name == name
        assert step.payload["subtype"] == "click"
        assert step.payload["locator"]["strategy"] == "id"
        assert step.payload["locator"]["selector"] == "com.example:id/button"

    def test_gesture_click_with_dict_locator(self) -> None:
        """Test gesture_click with dict locator."""
        # Arrange
        name = "click_button"
        locator = {"strategy": "accessibility id", "selector": "Submit"}

        # Act
        step = ActionStep.gesture_click(name, locator)

        # Assert
        assert step.type == "gesture"
        assert step.name == name
        assert step.payload["subtype"] == "click"
        assert step.payload["locator"]["strategy"] == "accessibility id"
        assert step.payload["locator"]["selector"] == "Submit"

    def test_gesture_click_with_element_locator(self) -> None:
        """Test gesture_click with Element object."""
        # Arrange
        from shadowstep.element.element import Element  # noqa: PLC0415

        name = "click_element"
        mock_element = MagicMock(spec=Element)
        mock_element.locator = ("xpath", "//button[@text='OK']")

        # Act
        step = ActionStep.gesture_click(name, mock_element)

        # Assert
        assert step.type == "gesture"
        assert step.name == name
        assert step.payload["subtype"] == "click"
        assert step.payload["locator"]["strategy"] == "xpath"
        assert step.payload["locator"]["selector"] == "//button[@text='OK']"

    def test_gesture_click_with_invalid_dict_locator(self) -> None:
        """Test gesture_click with invalid dict locator raises ValueError."""
        # Arrange
        name = "click_button"
        locator = {"strategy": "id"}  # Missing selector

        # Act & Assert
        with pytest.raises(ValueError, match="must contain 'strategy' and 'selector'"):
            ActionStep.gesture_click(name, locator)

    def test_gesture_click_with_invalid_locator_type(self) -> None:
        """Test gesture_click with invalid locator type raises ValueError."""
        # Arrange
        name = "click_button"
        locator = "invalid_locator"  # type: ignore[arg-type]

        # Act & Assert
        with pytest.raises(ValueError, match="must be a tuple or dict"):
            ActionStep.gesture_click(name, locator)

    def test_gesture_click_to_dict(self) -> None:
        """Test converting gesture_click step to dictionary."""
        # Arrange
        name = "click_button"
        locator = ("id", "button_id")
        step = ActionStep.gesture_click(name, locator)

        # Act
        result = step.to_dict()

        # Assert
        assert result["type"] == "gesture"
        assert result["name"] == name
        assert result["payload"]["subtype"] == "click"
        assert result["payload"]["locator"]["strategy"] == "id"
        assert result["payload"]["locator"]["selector"] == "button_id"


class TestActionStepGestureLongClick:
    """Unit tests for ActionStep.gesture_long_click method."""

    def test_gesture_long_click_with_tuple_locator(self) -> None:
        """Test gesture_long_click with tuple locator."""
        # Arrange
        name = "long_click_button"
        locator = ("id", "com.example:id/button")

        # Act
        step = ActionStep.gesture_long_click(name, locator)

        # Assert
        assert step.type == "gesture"
        assert step.name == name
        assert step.payload["subtype"] == "longClick"
        assert step.payload["locator"]["strategy"] == "id"
        assert step.payload["locator"]["selector"] == "com.example:id/button"

    def test_gesture_long_click_with_dict_locator(self) -> None:
        """Test gesture_long_click with dict locator."""
        # Arrange
        name = "long_click_item"
        locator = {"strategy": "xpath", "selector": "//item[@index='0']"}

        # Act
        step = ActionStep.gesture_long_click(name, locator)

        # Assert
        assert step.type == "gesture"
        assert step.name == name
        assert step.payload["subtype"] == "longClick"
        assert step.payload["locator"]["strategy"] == "xpath"
        assert step.payload["locator"]["selector"] == "//item[@index='0']"


class TestActionStepGestureDoubleClick:
    """Unit tests for ActionStep.gesture_double_click method."""

    def test_gesture_double_click(self) -> None:
        """Test gesture_double_click creates correct step."""
        # Arrange
        name = "double_click_image"
        element_id = "element-123"
        x = 150
        y = 200

        # Act
        step = ActionStep.gesture_double_click(name, element_id, x, y)

        # Assert
        assert step.type == "gesture"
        assert step.name == name
        assert step.payload["subtype"] == "doubleClick"
        assert step.payload["elementId"] == element_id
        assert step.payload["x"] == x
        assert step.payload["y"] == y


class TestActionStepSource:
    """Unit tests for ActionStep.source method."""

    def test_source_step(self) -> None:
        """Test source step creates correct step."""
        # Arrange
        name = "capture_source"

        # Act
        step = ActionStep.source(name)

        # Assert
        assert step.type == "source"
        assert step.name == name
        assert step.payload["subtype"] == "xml"

    def test_source_to_dict(self) -> None:
        """Test converting source step to dictionary."""
        # Arrange
        name = "page_source"
        step = ActionStep.source(name)

        # Act
        result = step.to_dict()

        # Assert
        assert result["type"] == "source"
        assert result["name"] == name
        assert result["payload"]["subtype"] == "xml"


class TestActionStepScreenshot:
    """Unit tests for ActionStep.screenshot method."""

    def test_screenshot_step(self) -> None:
        """Test screenshot step creates correct step."""
        # Arrange
        name = "take_screenshot"

        # Act
        step = ActionStep.screenshot(name)

        # Assert
        assert step.type == "screenshot"
        assert step.name == name
        assert step.payload["subtype"] == "png"

    def test_screenshot_to_dict(self) -> None:
        """Test converting screenshot step to dictionary."""
        # Arrange
        name = "screen_capture"
        step = ActionStep.screenshot(name)

        # Act
        result = step.to_dict()

        # Assert
        assert result["type"] == "screenshot"
        assert result["name"] == name
        assert result["payload"]["subtype"] == "png"


class TestActionStepInit:
    """Unit tests for ActionStep initialization."""

    def test_init_creates_step_with_correct_attributes(self) -> None:
        """Test that ActionStep.__init__ sets attributes correctly."""
        # Arrange
        step_type = "gesture"
        name = "test_step"
        payload = {"subtype": "click", "locator": {"strategy": "id", "selector": "btn"}}

        # Act
        step = ActionStep(step_type, name, payload)

        # Assert
        assert step.type == step_type
        assert step.name == name
        assert step.payload == payload

    def test_to_dict_returns_correct_structure(self) -> None:
        """Test that to_dict returns correct structure."""
        # Arrange
        step_type = "source"
        name = "capture"
        payload = {"subtype": "xml"}
        step = ActionStep(step_type, name, payload)

        # Act
        result = step.to_dict()

        # Assert
        assert isinstance(result, dict)
        assert result["type"] == step_type
        assert result["name"] == name
        assert result["payload"] == payload

