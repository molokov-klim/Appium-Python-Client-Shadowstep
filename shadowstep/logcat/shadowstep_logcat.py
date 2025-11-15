"""Logcat module for capturing Android device logs via WebSocket.

This module provides functionality for streaming Android device logs through
WebSocket connections to Appium server, with automatic reconnection and
file output capabilities.
"""

from __future__ import annotations

import contextlib
import logging
import re
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from selenium.common import WebDriverException
from websocket import (  # type: ignore[import-untyped]
    WebSocket,
    WebSocketConnectionClosedException,
    WebSocketException,
    create_connection,  # type: ignore[reportUnknownVariableType]
)

from shadowstep.ui_automator.mobile_commands import MobileCommands

if TYPE_CHECKING:
    import types
    from collections.abc import Callable

    from appium.webdriver.webdriver import WebDriver

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepEmptyFilenameError,
    ShadowstepLogcatConnectionError,
    ShadowstepPollIntervalError,
)

# Constants
MIN_LOG_PARTS_COUNT = 6

logger = logging.getLogger(__name__)

# Constants
DEFAULT_POLL_INTERVAL = 1.0
WEBSOCKET_TIMEOUT = 5


class ShadowstepLogcat:
    """Android device logcat capture via WebSocket connection.

    This class provides functionality to capture Android device logs through
    WebSocket connections to Appium server. It supports automatic reconnection,
    file output, and graceful shutdown.

    Attributes:
        _driver_getter: Function that returns the current WebDriver instance.
        _poll_interval: Interval between reconnection attempts in seconds.
        _thread: Background thread for logcat capture.
        _stop_evt: Event to signal thread termination.
        _filename: Output file path for logcat data.
        _ws: Current WebSocket connection.

    """

    def __init__(
        self,
        driver_getter: Callable[[], WebDriver | None],
        poll_interval: float = DEFAULT_POLL_INTERVAL,
    ) -> None:
        """Initialize ShadowstepLogcat.

        Args:
            driver_getter: Function that returns the current WebDriver instance.
            poll_interval: Interval between reconnection attempts in seconds.

        Raises:
            ValueError: If poll_interval is negative.

        """
        if poll_interval < 0:
            msg = "poll_interval must be non-negative"
            raise ShadowstepPollIntervalError(msg)

        self.mobile_commands = MobileCommands()

        self._driver_getter = driver_getter
        self._poll_interval = poll_interval

        self._thread: threading.Thread | None = None
        self._stop_evt = threading.Event()
        self._filename: str | None = None
        self._ws: WebSocket | None = None
        self.port: int | None = None
        self._filters: list[str] | None = None
        self._compiled_filter_pattern: re.Pattern[Any] | None = None
        self._filter_set: set[str] | None = None

    def _raise_logcat_connection_error(self) -> None:
        """Raise ShadowstepLogcatConnectionError for WebSocket connection failure.

        Raises:
            ShadowstepLogcatConnectionError: Always raised

        """
        raise ShadowstepLogcatConnectionError

    @property
    def filters(self) -> list[str] | None:
        """Get the current logcat filters.

        Returns:
            list[str] | None: List of filter patterns or None if no filters set.

        """
        return self._filters

    @filters.setter
    def filters(self, value: list[str]) -> None:
        self._filters = value
        if value:
            escaped_filters = [re.escape(f) for f in value]
            self._compiled_filter_pattern = re.compile("|".join(escaped_filters))
            self._filter_set = set(value)
        else:
            self._compiled_filter_pattern = None
            self._filter_set = None

    def _should_filter_line(self, line: str) -> bool:
        if not self._compiled_filter_pattern:
            return False

        if not self._compiled_filter_pattern.search(line):
            return False

        if self._filters is None:
            return False

        for filter_text in self._filters:
            if filter_text in line:
                return True

        parts = line.split()
        if len(parts) >= MIN_LOG_PARTS_COUNT:
            for i, part in enumerate(parts):
                if part in {"I", "D", "W", "E", "V"} and i + 1 < len(parts):
                    tag_part = parts[i + 1]
                    if ":" in tag_part:
                        tag = tag_part.split(":", 1)[0]
                        return tag in self._filter_set  # type: ignore[arg-type]

        return True

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit method to stop logcat capture.

        Args:
            exc_type: Exception type if any.
            exc_val: Exception value if any.
            exc_tb: Exception traceback if any.

        """
        logger.debug(exc_type, exc_val, exc_tb)
        self.stop()

    def __del__(self) -> None:
        """Destructor to ensure logcat capture is stopped on object deletion.

        Suppresses any exceptions during cleanup to prevent issues during
        garbage collection.
        """
        with contextlib.suppress(Exception):
            self.stop()

    def start(self, filename: str, port: int | None = None) -> None:
        """Start logcat capture to specified file.

        Args:
            filename: Path to the output file for logcat data.
            port: port of Appium server instance

        Raises:
            ValueError: If filename is empty.

        """
        self.port = port
        if not filename:
            msg = "filename cannot be empty"
            raise ShadowstepEmptyFilenameError(msg)

        if self._thread and self._thread.is_alive():
            logger.info("Logcat already running")
            return

        self._stop_evt.clear()
        self._filename = filename
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="ShadowstepLogcat",
        )
        self._thread.start()
        logger.info("Started logcat to '%s'", filename)

    def stop(self) -> None:
        """Stop logcat capture and cleanup resources.

        This method performs graceful shutdown by:
        1. Setting stop event to signal thread termination
        2. Closing WebSocket connection to interrupt blocking recv()
        3. Sending command to stop log broadcast
        4. Waiting for background thread to complete
        """
        # Set flag for thread to exit gracefully
        self._stop_evt.set()

        # Close WebSocket to interrupt blocking recv()
        if self._ws:
            with contextlib.suppress(Exception):
                self._ws.close()

        # Send command to stop broadcast
        try:
            self._driver_getter()
            self.mobile_commands.stop_logs_broadcast()
        except (WebDriverException, AttributeError) as e:
            logger.warning("Failed to stop broadcast: %r", e)

        # Wait for background thread to complete and file to close
        if self._thread:
            self._thread.join()
            self._thread = None
            self._filename = None

        logger.info("Logcat thread terminated, file closed")

    def _run(self) -> None:  # noqa: C901, PLR0915, PLR0912
        """Run main logcat capture loop in background thread.

        This method handles the complete logcat capture workflow:
        1. Opens output file
        2. Establishes WebSocket connection to Appium
        3. Streams log data to file
        4. Handles reconnection on connection loss
        """
        if not self._filename:
            logger.error("No filename specified for logcat")
            return

        try:
            with Path(self._filename).open("a", buffering=1, encoding="utf-8") as f:
                while not self._stop_evt.is_set():
                    try:
                        # Start broadcast
                        driver = self._driver_getter()
                        if driver is None:
                            logger.warning("Driver is None, skipping logcat iteration")
                            time.sleep(self._poll_interval)
                            continue
                        self.mobile_commands.stop_logs_broadcast()  # kill descriptor
                        self.mobile_commands.start_logs_broadcast()

                        # Build shadowstep WebSocket URL
                        session_id = driver.session_id

                        http_url = self._get_http_url(driver)
                        match = re.search(r":(\d+)$", http_url)
                        old_port = int(match.group(1)) if match else None
                        if self.port:
                            http_url = http_url.replace(str(old_port), str(self.port))

                        scheme, rest = http_url.split("://", 1)
                        ws_scheme = "ws" if scheme == "http" else "wss"
                        base_ws = f"{ws_scheme}://{rest}"
                        base_ws = base_ws.removesuffix("/wd/hub")  # Remove "/wd/hub"

                        # Try both endpoints
                        endpoints = [
                            f"{base_ws}/ws/session/{session_id}/appium/device/logcat",
                            f"{base_ws}/ws/session/{session_id}/appium/logcat",
                        ]
                        ws = None
                        for url in endpoints:
                            try:
                                ws = create_connection(
                                    url,
                                    timeout=WEBSOCKET_TIMEOUT,
                                    enable_multithread=True,
                                )
                                logger.info("Logcat WebSocket connected: %s", url)
                                break
                            except (OSError, WebSocketException) as ex:
                                logger.debug("Cannot connect to %s: %r", url, ex)
                        if not ws:
                            self._raise_logcat_connection_error()

                        # Store ws reference so stop() can close it
                        self._ws = ws
                        assert (
                            ws is not None
                        )  # For type checker: ws is guaranteed not to be None here

                        # Read until stop event
                        while not self._stop_evt.is_set():
                            try:
                                line = ws.recv()
                                if isinstance(line, bytes):
                                    line = line.decode(errors="ignore", encoding="utf-8")

                                if self._should_filter_line(line):
                                    continue

                                f.write(line + "\n")
                            except WebSocketConnectionClosedException:
                                self.mobile_commands.stop_logs_broadcast()  # kill descriptor
                                time.sleep(self._poll_interval)
                                break  # reconnect
                            except (TimeoutError, ConnectionError) as ex:
                                logger.debug("Connection issue: %r", ex)
                                self.mobile_commands.stop_logs_broadcast()  # kill descriptor
                                time.sleep(self._poll_interval)
                                continue
                            except OSError:
                                logger.warning("OSError occurred in logcat")
                                self.mobile_commands.stop_logs_broadcast()  # kill descriptor
                                time.sleep(self._poll_interval)
                                break
                            except Exception:
                                logger.exception("Unexpected error during logcat streaming")
                                self.mobile_commands.stop_logs_broadcast()  # kill descriptor
                                time.sleep(self._poll_interval)

                        # Clear reference and close socket
                        try:
                            ws.close()
                        except WebSocketException as ex:
                            logger.debug("Error closing WebSocket: %r", ex)
                        finally:
                            self._ws = None
                            self.mobile_commands.stop_logs_broadcast()  # kill descriptor
                            time.sleep(self._poll_interval)

                        # Pause before reconnection
                        time.sleep(self._poll_interval)

                    except Exception:
                        logger.exception("Logcat stream error, retry in %ss", self._poll_interval)
                        time.sleep(self._poll_interval)

        except Exception:
            logger.exception("Cannot open logcat file '%s'", self._filename)
        finally:
            logger.info("Logcat thread terminated, file closed")

    def _get_http_url(self, driver: WebDriver) -> str:
        """Extract HTTP URL from WebDriver command executor.

        Args:
            driver: WebDriver instance to extract URL from.

        Returns:
            HTTP URL string for the WebDriver command executor.

        """
        http_url = getattr(driver.command_executor, "_url", None)
        if not http_url:
            http_url = getattr(driver.command_executor, "_client_config", None)
            if http_url:
                http_url = getattr(driver.command_executor._client_config, "remote_server_addr", "")  # noqa: SLF001 # type: ignore[reportPrivateUsage]
            else:
                http_url = ""
        return http_url
