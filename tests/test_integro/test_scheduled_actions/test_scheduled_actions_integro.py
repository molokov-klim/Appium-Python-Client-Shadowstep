# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ScheduledActions class."""
from __future__ import annotations

import time

import pytest

from shadowstep.scheduled_actions.action_history import ActionHistory
from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.scheduled_actions.scheduled_actions import ScheduledActions
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_scheduled_actions/test_scheduled_actions_integro.py
"""


class TestScheduledActionsIntegro:
    """Integration tests for ScheduledActions."""

    def test_schedule_and_unschedule_simple_action(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test scheduling a simple action and unscheduling it."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_simple_action"

        # Create a simple screenshot action
        steps = [ActionStep.screenshot("capture_screen")]

        # Act - Schedule the action
        scheduled_actions.schedule(
            name=action_name,
            steps=steps,
            times=5,
            interval_ms=100,
        )

        # Wait for some executions
        time.sleep(1)

        # Unschedule and get history
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert isinstance(history, ActionHistory)
        assert history.name == action_name
        assert history.execution_count > 0
        assert len(history.step_results) > 0

    def test_schedule_page_source_capture(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test scheduling page source capture action."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "capture_page_source"

        # Create page source capture action
        steps = [ActionStep.source("get_source")]

        # Act
        scheduled_actions.schedule(
            name=action_name,
            steps=steps,
            times=3,
            interval_ms=200,
        )

        # Wait for executions (longer wait to ensure at least one execution)
        time.sleep(1.5)

        # Cleanup and get history
        history = scheduled_actions.unschedule(action_name)

        # Assert history is available
        assert isinstance(history, ActionHistory)
        assert history.execution_count > 0

    def test_schedule_multiple_steps(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test scheduling action with multiple steps."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "multi_step_action"

        # Create multi-step action
        steps = [
            ActionStep.source("step1_source"),
            ActionStep.screenshot("step2_screenshot"),
        ]

        # Act
        scheduled_actions.schedule(
            name=action_name,
            steps=steps,
            times=2,
            interval_ms=500,
        )

        # Wait for executions (longer to ensure completion)
        time.sleep(2)

        # Unschedule and check
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert history.execution_count > 0
        assert len(history.step_results) > 0
        # Each execution should have 2 steps
        for execution in history.step_results:
            assert len(execution) == 2

    def test_schedule_with_max_pass_limit(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that action stops after max_pass limit."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "max_pass_action"

        steps = [ActionStep.screenshot("capture")]

        # Act - Schedule with max_pass=2
        scheduled_actions.schedule(
            name=action_name,
            steps=steps,
            max_pass=2,
            times=10,  # Would run 10 times, but max_pass should stop it
            interval_ms=100,
        )

        # Wait enough time for all 10 attempts
        time.sleep(2)

        # Get history
        history = scheduled_actions.unschedule(action_name)

        # Assert - should have stopped at 2 passes
        assert history.passed_count <= 2

    def test_get_history_while_action_running(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test getting history while action is still running."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "running_action"

        steps = [ActionStep.screenshot("capture")]

        # Act
        scheduled_actions.schedule(
            name=action_name,
            steps=steps,
            times=20,
            interval_ms=200,
        )

        # Wait a bit
        time.sleep(0.5)

        # Get history while running
        history1 = scheduled_actions.get_history(action_name)
        count1 = history1.execution_count

        # Wait more
        time.sleep(0.5)

        # Get history again
        history2 = scheduled_actions.get_history(action_name)
        count2 = history2.execution_count

        # Cleanup
        scheduled_actions.unschedule(action_name)

        # Assert - count should increase
        assert count2 >= count1

    def test_schedule_with_custom_history_limit(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test scheduling with custom max_history_items."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "limited_history"

        steps = [ActionStep.screenshot("capture")]

        # Act - Schedule with small history limit
        scheduled_actions.schedule(
            name=action_name,
            steps=steps,
            times=10,
            interval_ms=100,
            max_history_items=3,
        )

        # Wait for executions
        time.sleep(1.5)

        # Get history
        history = scheduled_actions.unschedule(action_name)

        # Assert - should not have more than max_history_items
        assert len(history.step_results) <= 3

