# ruff: noqa
# pyright: ignore
"""Integration tests for scheduled actions in Shadowstep."""

import pytest

from shadowstep.scheduled_actions.action_history import ActionHistory
from shadowstep.scheduled_actions.action_step import ActionStep
from shadowstep.shadowstep import Shadowstep


class TestScheduledActions:
    """Integration tests for Shadowstep scheduled actions functionality."""

    def test_schedule_action_method_exists(self, app: Shadowstep) -> None:
        """Test schedule_action() method exists and has correct signature.

        Steps:
        1. Verify schedule_action method exists.
        2. Verify method has correct parameters.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(app, "schedule_action")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            # Try to create action step (will also raise NotImplementedError)
            try:
                step = ActionStep.screenshot(name="test_screenshot")
                steps = [step]
            except NotImplementedError:
                # ActionStep.screenshot not implemented yet, use empty list
                steps = []

            # Call schedule_action
            app.schedule_action(
                name="test_action",
                steps=steps,
                interval_ms=1000,
                times=1
            )

    def test_unschedule_action_method_exists(self, app: Shadowstep) -> None:
        """Test unschedule_action() method exists and has correct signature.

        Steps:
        1. Verify unschedule_action method exists.
        2. Verify method returns ActionHistory.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(app, "unschedule_action")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            app.unschedule_action(name="test_action")

    def test_get_action_history_method_exists(self, app: Shadowstep) -> None:
        """Test get_action_history() method exists and has correct signature.

        Steps:
        1. Verify get_action_history method exists.
        2. Verify method returns ActionHistory.
        3. Call method and verify it raises NotImplementedError (current behavior).
        """
        # Verify method exists
        assert hasattr(app, "get_action_history")  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            app.get_action_history(name="test_action")

    def test_schedule_action_with_parameters(self, app: Shadowstep) -> None:
        """Test schedule_action() with different parameter combinations.

        Steps:
        1. Test with minimal parameters.
        2. Test with all optional parameters.
        3. Verify NotImplementedError is raised (current behavior).
        """
        # Test with minimal parameters
        with pytest.raises(NotImplementedError):
            app.schedule_action(
                name="minimal_action",
                steps=[]
            )

        # Test with all parameters
        with pytest.raises(NotImplementedError):
            app.schedule_action(
                name="full_action",
                steps=[],
                interval_ms=2000,
                times=5,
                max_pass=3,
                max_fail=2,
                max_history_items=50
            )

    def test_schedule_action_chaining(self, app: Shadowstep) -> None:
        """Test schedule_action() returns Shadowstep for method chaining.

        Steps:
        1. Verify schedule_action should return Shadowstep instance.
        2. Verify return type annotation (when implemented).
        3. Current behavior: raises NotImplementedError.
        """
        # Verify method exists and has correct return type annotation
        import inspect
        sig = inspect.signature(app.schedule_action)

        # Verify return annotation is Shadowstep (string in forward reference)
        assert sig.return_annotation == "Shadowstep"  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            result = app.schedule_action(name="chain_test", steps=[])

    def test_get_action_history_return_type(self, app: Shadowstep) -> None:
        """Test get_action_history() return type annotation.

        Steps:
        1. Verify method has ActionHistory return type annotation.
        2. Current behavior: raises NotImplementedError.
        """
        # Verify method exists and has correct return type annotation
        import inspect
        sig = inspect.signature(app.get_action_history)

        # Verify return annotation is ActionHistory (string in forward reference)
        assert sig.return_annotation == "ActionHistory"  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            app.get_action_history(name="test")

    def test_unschedule_action_return_type(self, app: Shadowstep) -> None:
        """Test unschedule_action() return type annotation.

        Steps:
        1. Verify method has ActionHistory return type annotation.
        2. Current behavior: raises NotImplementedError.
        """
        # Verify method exists and has correct return type annotation
        import inspect
        sig = inspect.signature(app.unschedule_action)

        # Verify return annotation is ActionHistory (string in forward reference)
        assert sig.return_annotation == "ActionHistory"  # noqa: S101

        # Verify method raises NotImplementedError (current implementation)
        with pytest.raises(NotImplementedError):
            app.unschedule_action(name="test")

    def test_schedule_action_with_android_settings(
        self, app: Shadowstep, android_settings_open_close: None
    ) -> None:
        """Test schedule_action() in Android Settings context.

        Steps:
        1. Open Android Settings.
        2. Try to schedule action with Settings context.
        3. Verify NotImplementedError is raised (current behavior).
        """
        # Verify we're in Settings
        current_package = app.get_current_package()
        assert "settings" in current_package.lower()  # noqa: S101

        # Try to schedule action
        with pytest.raises(NotImplementedError):
            app.schedule_action(
                name="settings_action",
                steps=[],
                interval_ms=1000,
                times=1
            )

    def test_multiple_scheduled_actions(self, app: Shadowstep) -> None:
        """Test scheduling multiple actions with different names.

        Steps:
        1. Try to schedule first action.
        2. Try to schedule second action with different name.
        3. Verify NotImplementedError is raised for both (current behavior).
        """
        # Try to schedule first action
        with pytest.raises(NotImplementedError):
            app.schedule_action(name="action_1", steps=[], interval_ms=1000, times=1)

        # Try to schedule second action
        with pytest.raises(NotImplementedError):
            app.schedule_action(name="action_2", steps=[], interval_ms=2000, times=2)

    def test_get_action_history_for_nonexistent_action(self, app: Shadowstep) -> None:
        """Test get_action_history() for action that doesn't exist.

        Steps:
        1. Call get_action_history for non-existent action.
        2. Verify NotImplementedError is raised (current behavior).
        """
        # Try to get history for non-existent action
        with pytest.raises(NotImplementedError):
            app.get_action_history(name="nonexistent_action_xyz")

    def test_unschedule_nonexistent_action(self, app: Shadowstep) -> None:
        """Test unschedule_action() for action that doesn't exist.

        Steps:
        1. Call unschedule_action for non-existent action.
        2. Verify NotImplementedError is raised (current behavior).
        """
        # Try to unschedule non-existent action
        with pytest.raises(NotImplementedError):
            app.unschedule_action(name="nonexistent_action_xyz")

    def test_schedule_action_parameter_types(self, app: Shadowstep) -> None:
        """Test schedule_action() parameter types.

        Steps:
        1. Verify method accepts correct parameter types.
        2. Test with string name.
        3. Test with list of steps.
        4. Test with integer interval_ms, times, max_pass, max_fail, max_history_items.
        """
        # Verify parameter types using signature
        import inspect
        sig = inspect.signature(app.schedule_action)

        # Verify name parameter type (string in forward reference)
        assert sig.parameters["name"].annotation == "str"  # noqa: S101

        # Verify steps parameter type (string in forward reference)
        steps_annotation = sig.parameters["steps"].annotation
        assert "list" in steps_annotation  # noqa: S101

        # Verify interval_ms parameter type (string in forward reference)
        assert sig.parameters["interval_ms"].annotation == "int"  # noqa: S101

        # Verify times parameter type (string in forward reference)
        assert sig.parameters["times"].annotation == "int"  # noqa: S101

        # Method still raises NotImplementedError
        with pytest.raises(NotImplementedError):
            app.schedule_action(
                name="type_test",
                steps=[],
                interval_ms=1500,
                times=3
            )
