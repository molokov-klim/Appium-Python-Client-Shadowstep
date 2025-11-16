# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Action history tracking for scheduled actions.

This module provides the ActionHistory class for tracking
and managing the history of scheduled actions in the
Shadowstep automation framework.
"""
from __future__ import annotations

from typing import Any


class ActionHistory:
    """Tracks the history of scheduled actions for debugging and analysis.

    This class provides methods to analyze and query the execution history
    of scheduled actions, including pass/fail counts, step results, and
    execution details.
    """

    def __init__(self, history_data: dict[str, Any]) -> None:
        """Initialize ActionHistory with raw history data.

        Args:
            history_data: Raw history data from mobile: getActionHistory command.

        """
        self._data: dict[str, Any] = history_data

    @property
    def name(self) -> str:
        """Get the action name.

        Returns:
            str: Name of the action.

        """
        return str(self._data.get("name", ""))

    @property
    def execution_count(self) -> int:
        """Get total execution count.

        Returns:
            int: Number of times the action was executed.

        """
        # Appium uses "repeats" key instead of "executionCount"
        return int(self._data.get("repeats", self._data.get("executionCount", 0)))

    @property
    def passed_count(self) -> int:
        """Get the number of passed executions.

        Returns:
            int: Number of times the action passed.

        """
        # Calculate from step results if not provided
        if "passed" in self._data:
            return int(self._data.get("passed", 0))

        # Count passed executions from step results
        passed = 0
        for execution in self.step_results:
            if all(step.get("passed", False) for step in execution):
                passed += 1
        return passed

    @property
    def failed_count(self) -> int:
        """Get the number of failed executions.

        Returns:
            int: Number of times the action failed.

        """
        # Calculate from step results if not provided
        if "failed" in self._data:
            return int(self._data.get("failed", 0))

        # Count failed executions from step results
        failed = 0
        for execution in self.step_results:
            if not all(step.get("passed", False) for step in execution):
                failed += 1
        return failed

    @property
    def step_results(self) -> list[list[dict[str, Any]]]:
        """Get step results for all executions.

        Returns:
            list[list[dict[str, Any]]]: List of execution results.
                Each execution is a list of step results.

        """
        return list(self._data.get("stepResults", []))

    def get_last_execution(self) -> list[dict[str, Any]] | None:
        """Get the results of the last execution.

        Returns:
            list[dict[str, Any]] | None: Last execution step results or None.

        """
        results = self.step_results
        return results[-1] if results else None

    def did_execution_pass(self, execution_index: int) -> bool:
        """Check if a specific execution passed.

        Args:
            execution_index: Index of the execution to check.

        Returns:
            bool: True if all steps in the execution passed, False otherwise.

        """
        results = self.step_results
        if 0 <= execution_index < len(results):
            execution = results[execution_index]
            return all(step.get("passed", False) for step in execution)
        return False

    def did_last_execution_pass(self) -> bool:
        """Check if the last execution passed.

        Returns:
            bool: True if the last execution passed, False otherwise.

        """
        results = self.step_results
        if not results:
            return False
        return self.did_execution_pass(len(results) - 1)

    def has_any_passed_execution(self) -> bool:
        """Check if any execution fully passed.

        Returns:
            bool: True if at least one execution passed all steps.

        """
        return any(
            self.did_execution_pass(i) for i in range(len(self.step_results))
        )

    def get_step_result(
        self,
        execution_index: int,
        step_index: int,
    ) -> dict[str, Any] | None:
        """Get a specific step result from a specific execution.

        Args:
            execution_index: Index of the execution.
            step_index: Index of the step within the execution.

        Returns:
            dict[str, Any] | None: Step result or None if not found.

        """
        results = self.step_results
        if 0 <= execution_index < len(results):
            execution = results[execution_index]
            if 0 <= step_index < len(execution):
                return dict(execution[step_index])
        return None

    def get_failed_executions(self) -> list[int]:
        """Get indices of all failed executions.

        Returns:
            list[int]: List of execution indices that failed.

        """
        return [
            i
            for i in range(len(self.step_results))
            if not self.did_execution_pass(i)
        ]

    def get_passed_executions(self) -> list[int]:
        """Get indices of all passed executions.

        Returns:
            list[int]: List of execution indices that passed.

        """
        return [
            i
            for i in range(len(self.step_results))
            if self.did_execution_pass(i)
        ]

    def to_dict(self) -> dict[str, Any]:
        """Get raw history data as dictionary.

        Returns:
            dict[str, Any]: Raw history data.

        """
        return dict(self._data)

    def __repr__(self) -> str:
        """Return string representation of ActionHistory.

        Returns:
            str: String representation.

        """
        return (
            f"ActionHistory(name={self.name!r}, "
            f"executions={self.execution_count}, "
            f"passed={self.passed_count}, "
            f"failed={self.failed_count})"
        )

