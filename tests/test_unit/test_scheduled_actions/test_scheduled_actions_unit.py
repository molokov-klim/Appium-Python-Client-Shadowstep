# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Unit tests for ScheduledActions class."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from shadowstep.scheduled_actions.action_history import ActionHistory
from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.scheduled_actions.scheduled_actions import ScheduledActions


class TestScheduledActionsSchedule:
    """Unit tests for ScheduledActions.schedule method."""

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_schedule_with_single_step(self, mock_mobile_commands_class: MagicMock) -> None:
        """Test scheduling action with single step."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile
        mock_mobile.schedule_action.return_value = {"success": True}

        scheduled_actions = ScheduledActions()
        name = "myAction"
        step = ActionStep.gesture_click("click", ("id", "button"))

        # Act
        result = scheduled_actions.schedule(name, [step])

        # Assert
        mock_mobile.schedule_action.assert_called_once()
        call_args = mock_mobile.schedule_action.call_args[0][0]
        assert call_args["name"] == name
        assert len(call_args["steps"]) == 1
        assert call_args["steps"][0]["type"] == "gesture"
        assert call_args["times"] == 1
        assert call_args["intervalMs"] == 1000
        assert call_args["maxHistoryItems"] == 20

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_schedule_with_multiple_steps(self, mock_mobile_commands_class: MagicMock) -> None:
        """Test scheduling action with multiple steps."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile
        mock_mobile.schedule_action.return_value = {"success": True}

        scheduled_actions = ScheduledActions()
        name = "complexAction"
        steps = [
            ActionStep.gesture_click("click1", ("id", "button1")),
            ActionStep.gesture_long_click("longClick", ("id", "button2")),
            ActionStep.screenshot("capture"),
        ]

        # Act
        result = scheduled_actions.schedule(name, steps)

        # Assert
        mock_mobile.schedule_action.assert_called_once()
        call_args = mock_mobile.schedule_action.call_args[0][0]
        assert call_args["name"] == name
        assert len(call_args["steps"]) == 3
        assert call_args["steps"][0]["payload"]["subtype"] == "click"
        assert call_args["steps"][1]["payload"]["subtype"] == "longClick"
        assert call_args["steps"][2]["type"] == "screenshot"

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_schedule_with_custom_parameters(self, mock_mobile_commands_class: MagicMock) -> None:
        """Test scheduling with custom parameters."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile
        mock_mobile.schedule_action.return_value = {"success": True}

        scheduled_actions = ScheduledActions()
        name = "customAction"
        step = ActionStep.source("getSource")

        # Act
        result = scheduled_actions.schedule(
            name,
            [step],
            max_pass=5,
            max_fail=3,
            times=10,
            interval_ms=500,
            max_history_items=50,
        )

        # Assert
        mock_mobile.schedule_action.assert_called_once()
        call_args = mock_mobile.schedule_action.call_args[0][0]
        assert call_args["name"] == name
        assert call_args["maxPass"] == 5
        assert call_args["maxFail"] == 3
        assert call_args["times"] == 10
        assert call_args["intervalMs"] == 500
        assert call_args["maxHistoryItems"] == 50

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_schedule_with_empty_name_raises_error(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that scheduling with empty name raises ValueError."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile

        scheduled_actions = ScheduledActions()
        step = ActionStep.gesture_click("click", ("id", "button"))

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            scheduled_actions.schedule("", [step])

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_schedule_with_empty_steps_raises_error(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that scheduling with empty steps raises ValueError."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile

        scheduled_actions = ScheduledActions()

        # Act & Assert
        with pytest.raises(ValueError, match="Steps list cannot be empty"):
            scheduled_actions.schedule("myAction", [])


class TestScheduledActionsUnschedule:
    """Unit tests for ScheduledActions.unschedule method."""

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_unschedule_returns_action_history(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that unschedule returns ActionHistory object."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile
        history_data = {
            "name": "myAction",
            "executionCount": 5,
            "passed": 3,
            "failed": 2,
            "stepResults": [],
        }
        mock_mobile.unschedule_action.return_value = history_data

        scheduled_actions = ScheduledActions()
        name = "myAction"

        # Act
        result = scheduled_actions.unschedule(name)

        # Assert
        mock_mobile.unschedule_action.assert_called_once_with({"name": name})
        assert isinstance(result, ActionHistory)
        assert result.name == "myAction"
        assert result.execution_count == 5
        assert result.passed_count == 3
        assert result.failed_count == 2

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_unschedule_with_empty_name_raises_error(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that unscheduling with empty name raises ValueError."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile

        scheduled_actions = ScheduledActions()

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            scheduled_actions.unschedule("")


class TestScheduledActionsGetHistory:
    """Unit tests for ScheduledActions.get_history method."""

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_get_history_returns_action_history(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that get_history returns ActionHistory object."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile
        history_data = {
            "name": "testAction",
            "executionCount": 10,
            "passed": 8,
            "failed": 2,
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
            ],
        }
        mock_mobile.get_action_history.return_value = history_data

        scheduled_actions = ScheduledActions()
        name = "testAction"

        # Act
        result = scheduled_actions.get_history(name)

        # Assert
        mock_mobile.get_action_history.assert_called_once_with({"name": name})
        assert isinstance(result, ActionHistory)
        assert result.name == "testAction"
        assert result.execution_count == 10
        assert result.passed_count == 8
        assert result.failed_count == 2
        assert len(result.step_results) == 2

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_get_history_with_empty_name_raises_error(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that getting history with empty name raises ValueError."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile

        scheduled_actions = ScheduledActions()

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            scheduled_actions.get_history("")


class TestScheduledActionsInit:
    """Unit tests for ScheduledActions initialization."""

    @patch("shadowstep.scheduled_actions.scheduled_actions.MobileCommands")
    def test_init_creates_mobile_commands_instance(
        self,
        mock_mobile_commands_class: MagicMock,
    ) -> None:
        """Test that initialization creates MobileCommands instance."""
        # Arrange
        mock_mobile = MagicMock()
        mock_mobile_commands_class.return_value = mock_mobile

        # Act
        scheduled_actions = ScheduledActions()

        # Assert
        mock_mobile_commands_class.assert_called_once()
        assert scheduled_actions._mobile_commands == mock_mobile
        assert scheduled_actions.logger is not None

