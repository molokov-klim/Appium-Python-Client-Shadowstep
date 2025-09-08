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
from collections.abc import Callable

from appium.webdriver.webdriver import WebDriver
from selenium.common import WebDriverException
from websocket import WebSocket, WebSocketConnectionClosedException, create_connection

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
            poll_interval: float = DEFAULT_POLL_INTERVAL
    ) -> None:
        """Initialize ShadowstepLogcat.
        
        Args:
            driver_getter: Function that returns the current WebDriver instance.
            poll_interval: Interval between reconnection attempts in seconds.
            
        Raises:
            ValueError: If poll_interval is negative.
        """
        if poll_interval < 0:
            raise ValueError("poll_interval must be non-negative")
            
        self._driver_getter = driver_getter
        self._poll_interval = poll_interval

        self._thread: threading.Thread | None = None
        self._stop_evt = threading.Event()
        self._filename: str | None = None
        self._ws: WebSocket | None = None
        self.port: int | None = None
        self._filters = None
        self._compiled_filter_pattern = None
        self._filter_set = None


    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, value):
        self._filters = value
        if value:
            import re
            escaped_filters = [re.escape(f) for f in value]
            self._compiled_filter_pattern = re.compile('|'.join(escaped_filters))
            self._filter_set = set(value)
        else:
            self._compiled_filter_pattern = None
            self._filter_set = None

    def _should_filter_line(self, line: str) -> bool:
        if not self._compiled_filter_pattern:
            return False

        if not self._compiled_filter_pattern.search(line):
            return False

        parts = line.split()
        if len(parts) >= 6:
            for i, part in enumerate(parts):
                if part in {'I', 'D', 'W', 'E', 'V'} and i + 1 < len(parts):
                    tag_part = parts[i + 1]
                    if ':' in tag_part:
                        tag = tag_part.split(':', 1)[0]
                        return tag in self._filter_set

        return True


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __del__(self):
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
            raise ValueError("filename cannot be empty")
            
        if self._thread and self._thread.is_alive():
            logger.info("Logcat already running")
            return

        self._stop_evt.clear()
        self._filename = filename
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="ShadowstepLogcat"
        )
        self._thread.start()
        logger.info(f"Started logcat to '{filename}'")

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
            driver = self._driver_getter()
            if driver is not None:
                driver.execute_script("mobile: stopLogsBroadcast")
        except WebDriverException as e:
            logger.warning(f"Failed to stop broadcast: {e!r}")

        # Wait for background thread to complete and file to close
        if self._thread:
            self._thread.join()
            self._thread = None
            self._filename = None

        logger.info("Logcat thread terminated, file closed")

    def _run(self) -> None:  # noqa: C901
        """Main logcat capture loop running in background thread.
        
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
            with open(self._filename, "a", buffering=1, encoding="utf-8") as f:
                while not self._stop_evt.is_set():
                    try:
                        # Start broadcast
                        driver = self._driver_getter()
                        if driver is None:
                            logger.warning("Driver is None, skipping logcat iteration")
                            time.sleep(self._poll_interval)
                            continue
                        driver.execute_script("mobile: startLogsBroadcast")

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
                        if base_ws.endswith("/wd/hub"):
                            base_ws = base_ws[:-7]  # Remove "/wd/hub"

                        # Try both endpoints
                        endpoints = [
                            f"{base_ws}/ws/session/{session_id}/appium/device/logcat",
                            f"{base_ws}/ws/session/{session_id}/appium/logcat",
                        ]
                        ws = None
                        for url in endpoints:
                            try:
                                ws = create_connection(url, timeout=WEBSOCKET_TIMEOUT)
                                logger.info(f"Logcat WebSocket connected: {url}")
                                break
                            except Exception as ex:
                                logger.debug(f"Cannot connect to {url}: {ex!r}")
                        if not ws:
                            raise RuntimeError("Cannot connect to any logcat WS endpoint")

                        # Store ws reference so stop() can close it
                        self._ws = ws

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
                                break  # Reconnect
                            except Exception as ex:
                                logger.debug(f"Ignoring recv error: {ex!r}")
                                continue

                        # Clear reference and close socket
                        try:
                            ws.close()
                        except Exception as ex:
                            logger.debug(f"Error closing WebSocket: {ex!r}")
                        finally:
                            self._ws = None

                        # Pause before reconnection
                        time.sleep(self._poll_interval)

                    except Exception as inner:
                        logger.error(f"Logcat stream error, retry in {self._poll_interval}s: {inner!r}", exc_info=True)
                        time.sleep(self._poll_interval)

        except Exception as e:
            logger.error(f"Cannot open logcat file '{self._filename}': {e!r}")
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
                http_url = getattr(driver.command_executor._client_config, "remote_server_addr", "")
            else:
                http_url = ""
        return http_url
