# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Unit tests for ActionHistory class."""
from __future__ import annotations

from shadowstep.scheduled_actions.action_history import ActionHistory


class TestActionHistoryBasicProperties:
    """Unit tests for ActionHistory basic properties."""

    def test_name_property(self) -> None:
        """Test that name property returns correct value."""
        # Arrange
        data = {"name": "myAction", "executionCount": 0, "passed": 0, "failed": 0}
        history = ActionHistory(data)

        # Act & Assert
        assert history.name == "myAction"

    def test_execution_count_property(self) -> None:
        """Test that execution_count property returns correct value."""
        # Arrange
        data = {"name": "test", "executionCount": 5, "passed": 3, "failed": 2}
        history = ActionHistory(data)

        # Act & Assert
        assert history.execution_count == 5

    def test_passed_count_property(self) -> None:
        """Test that passed_count property returns correct value."""
        # Arrange
        data = {"name": "test", "executionCount": 5, "passed": 3, "failed": 2}
        history = ActionHistory(data)

        # Act & Assert
        assert history.passed_count == 3

    def test_failed_count_property(self) -> None:
        """Test that failed_count property returns correct value."""
        # Arrange
        data = {"name": "test", "executionCount": 5, "passed": 3, "failed": 2}
        history = ActionHistory(data)

        # Act & Assert
        assert history.failed_count == 2

    def test_properties_with_missing_data(self) -> None:
        """Test properties handle missing data gracefully."""
        # Arrange
        data = {}  # Empty data
        history = ActionHistory(data)

        # Act & Assert
        assert history.name == ""
        assert history.execution_count == 0
        assert history.passed_count == 0
        assert history.failed_count == 0


class TestActionHistoryStepResults:
    """Unit tests for ActionHistory step results methods."""

    def test_step_results_property(self) -> None:
        """Test step_results property returns list of executions."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act
        results = history.step_results

        # Assert
        assert len(results) == 2
        assert results[0][0]["name"] == "step1"
        assert results[0][0]["passed"] is True
        assert results[1][0]["passed"] is False

    def test_step_results_empty(self) -> None:
        """Test step_results returns empty list when no results."""
        # Arrange
        data = {"name": "test"}
        history = ActionHistory(data)

        # Act
        results = history.step_results

        # Assert
        assert results == []

    def test_get_last_execution(self) -> None:
        """Test get_last_execution returns last execution results."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": True}],
            ],
        }
        history = ActionHistory(data)

        # Act
        last = history.get_last_execution()

        # Assert
        assert last is not None
        assert len(last) == 1
        assert last[0]["passed"] is True

    def test_get_last_execution_returns_none_when_empty(self) -> None:
        """Test get_last_execution returns None when no executions."""
        # Arrange
        data = {"name": "test", "stepResults": []}
        history = ActionHistory(data)

        # Act
        last = history.get_last_execution()

        # Assert
        assert last is None


class TestActionHistoryExecutionStatus:
    """Unit tests for execution status checking methods."""

    def test_did_execution_pass_all_steps_passed(self) -> None:
        """Test did_execution_pass returns True when all steps passed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [
                    {"name": "step1", "passed": True},
                    {"name": "step2", "passed": True},
                ],
            ],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.did_execution_pass(0) is True

    def test_did_execution_pass_some_steps_failed(self) -> None:
        """Test did_execution_pass returns False when some steps failed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [
                    {"name": "step1", "passed": True},
                    {"name": "step2", "passed": False},
                ],
            ],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.did_execution_pass(0) is False

    def test_did_execution_pass_invalid_index(self) -> None:
        """Test did_execution_pass returns False for invalid index."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [[{"name": "step1", "passed": True}]],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.did_execution_pass(5) is False
        assert history.did_execution_pass(-1) is False

    def test_did_last_execution_pass_true(self) -> None:
        """Test did_last_execution_pass returns True when last passed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": True}],
            ],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.did_last_execution_pass() is True

    def test_did_last_execution_pass_false(self) -> None:
        """Test did_last_execution_pass returns False when last failed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.did_last_execution_pass() is False

    def test_did_last_execution_pass_empty_results(self) -> None:
        """Test did_last_execution_pass returns False when no results."""
        # Arrange
        data = {"name": "test", "stepResults": []}
        history = ActionHistory(data)

        # Act & Assert
        assert history.did_last_execution_pass() is False

    def test_has_any_passed_execution_true(self) -> None:
        """Test has_any_passed_execution returns True when at least one passed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.has_any_passed_execution() is True

    def test_has_any_passed_execution_false(self) -> None:
        """Test has_any_passed_execution returns False when all failed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act & Assert
        assert history.has_any_passed_execution() is False


class TestActionHistoryStepQueries:
    """Unit tests for querying specific step results."""

    def test_get_step_result(self) -> None:
        """Test get_step_result returns correct step."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [
                    {"name": "step1", "passed": True, "result": "OK"},
                    {"name": "step2", "passed": False, "result": "Error"},
                ],
            ],
        }
        history = ActionHistory(data)

        # Act
        step = history.get_step_result(0, 1)

        # Assert
        assert step is not None
        assert step["name"] == "step2"
        assert step["passed"] is False
        assert step["result"] == "Error"

    def test_get_step_result_invalid_execution_index(self) -> None:
        """Test get_step_result returns None for invalid execution index."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [[{"name": "step1", "passed": True}]],
        }
        history = ActionHistory(data)

        # Act
        step = history.get_step_result(5, 0)

        # Assert
        assert step is None

    def test_get_step_result_invalid_step_index(self) -> None:
        """Test get_step_result returns None for invalid step index."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [[{"name": "step1", "passed": True}]],
        }
        history = ActionHistory(data)

        # Act
        step = history.get_step_result(0, 5)

        # Assert
        assert step is None


class TestActionHistoryExecutionFilters:
    """Unit tests for filtering executions by status."""

    def test_get_failed_executions(self) -> None:
        """Test get_failed_executions returns indices of failed executions."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act
        failed = history.get_failed_executions()

        # Assert
        assert failed == [1, 3]

    def test_get_failed_executions_empty(self) -> None:
        """Test get_failed_executions returns empty list when all passed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": True}],
            ],
        }
        history = ActionHistory(data)

        # Act
        failed = history.get_failed_executions()

        # Assert
        assert failed == []

    def test_get_passed_executions(self) -> None:
        """Test get_passed_executions returns indices of passed executions."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": True}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act
        passed = history.get_passed_executions()

        # Assert
        assert passed == [0, 2]

    def test_get_passed_executions_empty(self) -> None:
        """Test get_passed_executions returns empty list when all failed."""
        # Arrange
        data = {
            "name": "test",
            "stepResults": [
                [{"name": "step1", "passed": False}],
                [{"name": "step1", "passed": False}],
            ],
        }
        history = ActionHistory(data)

        # Act
        passed = history.get_passed_executions()

        # Assert
        assert passed == []


class TestActionHistoryUtilities:
    """Unit tests for utility methods."""

    def test_to_dict(self) -> None:
        """Test to_dict returns raw data."""
        # Arrange
        data = {
            "name": "test",
            "executionCount": 5,
            "passed": 3,
            "failed": 2,
            "stepResults": [],
        }
        history = ActionHistory(data)

        # Act
        result = history.to_dict()

        # Assert
        assert result == data

    def test_repr(self) -> None:
        """Test __repr__ returns proper string representation."""
        # Arrange
        data = {
            "name": "myAction",
            "executionCount": 10,
            "passed": 7,
            "failed": 3,
        }
        history = ActionHistory(data)

        # Act
        repr_str = repr(history)

        # Assert
        assert "ActionHistory" in repr_str
        assert "myAction" in repr_str
        assert "executions=10" in repr_str
        assert "passed=7" in repr_str
        assert "failed=3" in repr_str

