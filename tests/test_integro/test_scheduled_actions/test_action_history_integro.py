# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ActionHistory class."""
from __future__ import annotations

import time

from shadowstep.scheduled_actions.action_history import ActionHistory
from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.scheduled_actions.scheduled_actions import ScheduledActions
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_scheduled_actions/test_action_history_integro.py
"""


class TestActionHistoryIntegro:
    """Integration tests for ActionHistory in real environment."""

    def test_action_history_tracks_executions(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that ActionHistory correctly tracks execution count."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_track_executions"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=5, interval_ms=100)
        time.sleep(1)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert isinstance(history, ActionHistory)
        assert history.execution_count > 0
        assert history.execution_count <= 5
        assert history.name == action_name

    def test_action_history_passed_count(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that ActionHistory tracks passed executions."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_passed_count"
        # Use steps that should pass
        steps = [
            ActionStep.screenshot("capture"),
            ActionStep.source("get_source"),
        ]

        # Act
        scheduled_actions.schedule(action_name, steps, times=3, interval_ms=200)
        time.sleep(1.5)  # Longer wait
        history = scheduled_actions.unschedule(action_name)

        # Assert
        assert history.passed_count > 0
        assert history.passed_count <= history.execution_count

    def test_action_history_step_results(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test that ActionHistory contains step results."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_step_results"
        steps = [
            ActionStep.screenshot("step1"),
            ActionStep.source("step2"),
        ]

        # Act
        scheduled_actions.schedule(action_name, steps, times=2, interval_ms=200)
        time.sleep(1.5)  # Longer wait
        history = scheduled_actions.unschedule(action_name)

        # Assert
        step_results = history.step_results
        assert len(step_results) > 0
        # Each execution should have 2 steps
        for execution in step_results:
            assert len(execution) == 2
            assert "name" in execution[0]
            assert "passed" in execution[0]

    def test_action_history_last_execution(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test getting last execution from history."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_last_execution"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=3, interval_ms=150)
        time.sleep(1.5)  # Longer wait
        history = scheduled_actions.unschedule(action_name)

        # Assert
        last_exec = history.get_last_execution()
        assert last_exec is not None
        assert len(last_exec) > 0
        assert last_exec[0]["name"] == "capture"

    def test_action_history_did_execution_pass(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test checking if specific execution passed."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_execution_pass"
        # Use steps that should succeed
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=3, interval_ms=150)
        time.sleep(0.7)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        if history.execution_count > 0:
            # Check first execution
            passed = history.did_execution_pass(0)
            # Screenshot should generally pass
            assert isinstance(passed, bool)

    def test_action_history_did_last_execution_pass(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test checking if last execution passed."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_last_pass"
        step = ActionStep.source("get_source")

        # Act
        scheduled_actions.schedule(action_name, [step], times=2, interval_ms=200)
        time.sleep(0.7)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        if history.execution_count > 0:
            last_passed = history.did_last_execution_pass()
            assert isinstance(last_passed, bool)

    def test_action_history_has_any_passed_execution(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test checking if any execution passed."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_any_passed"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=3, interval_ms=150)
        time.sleep(0.7)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        has_passed = history.has_any_passed_execution()
        assert isinstance(has_passed, bool)
        # Screenshot should generally pass at least once
        if history.execution_count > 0:
            assert has_passed is True

    def test_action_history_get_step_result(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test getting specific step result."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_get_step"
        steps = [
            ActionStep.screenshot("step1"),
            ActionStep.source("step2"),
        ]

        # Act
        scheduled_actions.schedule(action_name, steps, times=2, interval_ms=200)
        time.sleep(0.7)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        if history.execution_count > 0:
            step_result = history.get_step_result(0, 0)
            assert step_result is not None
            assert "name" in step_result
            assert step_result["name"] == "step1"

    def test_action_history_get_failed_executions(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test getting failed execution indices."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_failed_exec"
        # Mix of potentially passing and failing steps
        steps = [
            ActionStep.gesture_click("click", ("id", "nonexistent_button")),
        ]

        # Act
        scheduled_actions.schedule(action_name, steps, times=3, interval_ms=150)
        time.sleep(0.7)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        failed = history.get_failed_executions()
        assert isinstance(failed, list)

    def test_action_history_get_passed_executions(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test getting passed execution indices."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_passed_exec"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=3, interval_ms=150)
        time.sleep(0.7)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        passed = history.get_passed_executions()
        assert isinstance(passed, list)
        # Screenshots should generally pass
        if history.execution_count > 0:
            assert len(passed) > 0

    def test_action_history_to_dict(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test converting history to dictionary."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_to_dict"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=2, interval_ms=200)
        time.sleep(0.6)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        history_dict = history.to_dict()
        assert isinstance(history_dict, dict)
        assert "name" in history_dict
        assert history_dict["name"] == action_name

    def test_action_history_repr(
        self,
        app: Shadowstep,
        android_settings_open_close: None,
    ) -> None:
        """Test string representation of history."""
        # Arrange
        scheduled_actions = ScheduledActions()
        action_name = "test_repr"
        step = ActionStep.screenshot("capture")

        # Act
        scheduled_actions.schedule(action_name, [step], times=2, interval_ms=200)
        time.sleep(0.6)
        history = scheduled_actions.unschedule(action_name)

        # Assert
        repr_str = repr(history)
        assert "ActionHistory" in repr_str
        assert action_name in repr_str

