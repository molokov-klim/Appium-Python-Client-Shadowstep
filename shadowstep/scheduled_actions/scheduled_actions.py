# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Scheduled actions management for Shadowstep framework.

This module provides functionality for managing and executing
scheduled actions in the Shadowstep automation framework,
including action queuing, execution, and history tracking.
https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scheduleaction
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from shadowstep.scheduled_actions.action_history import ActionHistory
from shadowstep.ui_automator.mobile_commands import MobileCommands
from shadowstep.utils.utils import get_current_func_name

if TYPE_CHECKING:
    from shadowstep.scheduled_actions.action_step import ActionStep

logger = logging.getLogger(__name__)


class ScheduledActions:
    """Manages scheduled actions in the Shadowstep automation framework.

    This class provides a high-level API for scheduling, managing, and
    analyzing scheduled actions that run asynchronously in the background.
    Scheduled actions can be used for:
    - Handling popups that appear at unpredictable times
    - Capturing screenshots/page source at intervals
    - Performing repeated gestures or interactions
    """

    def __init__(self) -> None:
        """Initialize ScheduledActions with mobile commands."""
        self._mobile_commands = MobileCommands()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def schedule(  # noqa: PLR0913
        self,
        name: str,
        steps: list[ActionStep],
        max_pass: int | None = None,
        max_fail: int | None = None,
        times: int = 1,
        interval_ms: int = 1000,
        max_history_items: int = 20,
    ) -> Any:
        """Schedule an action for asynchronous execution.

        Args:
            name: Unique name for this scheduled action.
            steps: List of ActionStep objects to execute sequentially.
            max_pass: Max times action can pass before stopping. Optional.
            max_fail: Max times action can fail before stopping. Optional.
            times: Total times to execute the action. Defaults to 1.
            interval_ms: Milliseconds between executions. Defaults to 1000.
            max_history_items: Max history items to store. Defaults to 20.

        Returns:
            Any: Result from the mobile: scheduleAction command.

        Raises:
            ValueError: If steps list is empty or name is empty.

        """
        self.logger.debug("%s", get_current_func_name())

        if not name:
            error_msg = "Action name cannot be empty"
            raise ValueError(error_msg)

        if not steps:
            error_msg = "Steps list cannot be empty"
            raise ValueError(error_msg)

        # Convert ActionStep objects to dict format
        steps_dict = [step.to_dict() for step in steps]

        params: dict[str, Any] = {
            "name": name,
            "steps": steps_dict,
            "times": times,
            "intervalMs": interval_ms,
            "maxHistoryItems": max_history_items,
        }

        # Add optional parameters
        if max_pass is not None:
            params["maxPass"] = max_pass
        if max_fail is not None:
            params["maxFail"] = max_fail

        self.logger.info("Scheduling action '%s' with %d steps", name, len(steps))
        return self._mobile_commands.schedule_action(params)

    def unschedule(self, name: str) -> ActionHistory:
        """Unschedule a previously scheduled action and get its history.

        Args:
            name: Name of the action to unschedule.

        Returns:
            ActionHistory: History of the unscheduled action.

        Raises:
            ValueError: If name is empty.

        """
        self.logger.debug("%s", get_current_func_name())

        if not name:
            error_msg = "Action name cannot be empty"
            raise ValueError(error_msg)

        self.logger.info("Unscheduling action '%s'", name)
        params = {"name": name}
        result = self._mobile_commands.unschedule_action(params)
        # Add action name to result since Appium doesn't return it
        result["name"] = name
        return ActionHistory(result)

    def get_history(self, name: str) -> ActionHistory:
        """Get execution history of a scheduled action.

        Args:
            name: Name of the action to query.

        Returns:
            ActionHistory: Execution history of the action.

        Raises:
            ValueError: If name is empty.

        """
        self.logger.debug("%s", get_current_func_name())

        if not name:
            error_msg = "Action name cannot be empty"
            raise ValueError(error_msg)

        self.logger.info("Getting history for action '%s'", name)
        params = {"name": name}
        result = self._mobile_commands.get_action_history(params)
        # Add action name to result since Appium doesn't return it
        result["name"] = name
        return ActionHistory(result)
