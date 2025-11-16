# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ActionStep class."""
from __future__ import annotations

import time

from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.scheduled_actions.scheduled_actions import ScheduledActions
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_scheduled_actions/test_action_step_integro.py
"""


class TestActionStepIntegro:
    """Integration tests for ActionStep in real environment."""

    def test_action_step_screenshot_executes(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that screenshot action step executes successfully."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_screenshot"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=1)
        time.sleep(1.5)  # Longer wait to ensure execution
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert history.execution_count > 0
        assert history.passed_count > 0
        # Check that step executed
        last_exec = history.get_last_execution()
        assert last_exec is not None
        assert last_exec[0]["name"] == "capture"

    def test_action_step_source_executes(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that source action step executes successfully."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_source"
        step = ActionStep.source("get_page_source")

        # Act
        scheduled_actions.schedule(action_name, [step], times=1)
        time.sleep(0.5)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert history.execution_count > 0
        # Source step should execute successfully
        last_exec = history.get_last_execution()
        assert last_exec is not None
        assert last_exec[0]["name"] == "get_page_source"

    def test_action_step_gesture_click_with_valid_element(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test gesture click action step with a valid element."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_click"
        
        # Use a locator that exists in Android settings
        step = ActionStep.gesture_click(
            "click_search",
            ("id", "com.android.settings:id/search_action_bar_title"),
        )

        # Act
        scheduled_actions.schedule(action_name, [step], times=1)
        time.sleep(0.5)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert history.execution_count > 0
        last_exec = history.get_last_execution()
        assert last_exec is not None
        assert last_exec[0]["name"] == "click_search"

    def test_action_step_gesture_click_with_nonexistent_element(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test gesture click fails gracefully with nonexistent element."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_click_fail"
        
        # Use a locator that doesn't exist
        step = ActionStep.gesture_click(
            "click_nonexistent",
            ("id", "com.nonexistent.app:id/button"),
        )

        # Act
        scheduled_actions.schedule(action_name, [step], times=1)
        time.sleep(0.5)
        history = scheduled_actions.unschedule(action_name)

        # Assert - should have executed but might have failed
        assert history.execution_count > 0
        last_exec = history.get_last_execution()
        assert last_exec is not None
        # The step should have been attempted
        assert last_exec[0]["name"] == "click_nonexistent"

    def test_multiple_action_steps_in_sequence(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test multiple action steps execute in sequence."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_sequence"
        
        steps = [
            ActionStep.source("step1"),
            ActionStep.screenshot("step2"),
            ActionStep.source("step3"),
        ]

        # Act
        scheduled_actions.schedule(action_name, steps, times=1)
        time.sleep(1.5)  # Longer wait
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert history.execution_count > 0
        last_exec = history.get_last_execution()
        assert last_exec is not None
        assert len(last_exec) == 3
        assert last_exec[0]["name"] == "step1"
        assert last_exec[1]["name"] == "step2"
        assert last_exec[2]["name"] == "step3"

    def test_action_step_to_dict_structure(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that ActionStep.to_dict produces valid structure for scheduling."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_dict_structure"
        
        # Create steps and check their dict representation
        step1 = ActionStep.screenshot("test_screenshot")
        step2 = ActionStep.source("test_source")
        
        dict1 = step1.to_dict()
        dict2 = step2.to_dict()
        
        # Verify structure
        assert "type" in dict1
        assert "name" in dict1
        assert "payload" in dict1
        
        # Act - Use these steps in scheduling
        scheduled_actions.schedule(action_name, [step1, step2], times=1)
        time.sleep(1.5)  # Longer wait
        history = scheduled_actions.unschedule(action_name)

        # Assert - Action should execute successfully
        assert history.execution_count > 0

