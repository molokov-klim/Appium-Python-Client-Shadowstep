"""Singleton pattern implementation for WebDriver."""
import gc
import json
import logging
from typing import Any, cast

import requests
from appium.webdriver.webdriver import WebDriver
from utils.utils import get_current_func_name

logger = logging.getLogger(__name__)


class WebDriverSingleton(WebDriver):
    """Singleton pattern implementation for WebDriver."""

    _instance = None
    _driver = None
    _command_executor = None

    def __new__(cls, *args: Any, **kwargs: Any) -> WebDriver:
        """Create or return existing WebDriver instance.

        Args:
            *args: Positional arguments for WebDriver.
            **kwargs: Keyword arguments for WebDriver.

        Returns:
            WebDriver: The singleton WebDriver instance.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._driver = WebDriver(*args, **kwargs)
            cls._command_executor = kwargs["command_executor"]
        return cls._driver  # type: ignore[return-value]

    @classmethod
    def _get_session_id(cls, kwargs: Any) -> str:
        logger.debug("%s", get_current_func_name())
        res = requests.get(kwargs["command_executor"] + "/sessions", timeout=30)
        res_json = json.loads(res.text)
        sessions = res_json.get("value", [])
        if sessions:
            for session in sessions:
                session_id = session.get("id")
                if session_id:
                    return str(session_id)
        return "unknown_session_id"

    @classmethod
    def clear_instance(cls) -> None:
        """Remove current instance and clean up WebDriverSingleton resources."""
        logger.debug("%s", get_current_func_name())
        cls._driver = None
        cls._instance = None  # Remove reference to instance for memory release
        gc.collect()

    @classmethod
    def get_driver(cls) -> WebDriver:
        """Get the WebDriver instance.

        Returns:
            WebDriver: The current WebDriver instance.

        """
        logger.debug("%s", get_current_func_name())
        return cast("WebDriver", cls._driver)
