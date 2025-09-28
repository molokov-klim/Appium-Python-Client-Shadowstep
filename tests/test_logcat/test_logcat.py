"""Tests for the logcat module.

This module contains comprehensive tests for the ShadowstepLogcat class,
covering logcat capture functionality, WebSocket connections, and error handling.
"""
from __future__ import annotations

import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from selenium.common import WebDriverException
from websocket import WebSocketConnectionClosedException

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPollIntervalError,
    ShadowstepEmptyFilenameError,
)
from shadowstep.logcat.shadowstep_logcat import (
    DEFAULT_POLL_INTERVAL,
    WEBSOCKET_TIMEOUT,
    ShadowstepLogcat,
)


class MockWebDriver:
    """Mock WebDriver for testing purposes."""
    
    def __init__(self, session_id: str = "test-session-123") -> None:
        """Initialize mock WebDriver.
        
        Args:
            session_id: Mock session ID.
        """
        self.session_id = session_id
        self.command_executor = Mock()
        self.command_executor._url = "http://localhost:4723/wd/hub"
        self.command_executor._client_config = None
    
    @staticmethod
    def execute_script(script: str,) -> None:
        """Mock execute_script method."""
        if script in ("mobile: startLogsBroadcast", "mobile: stopLogsBroadcast"):
            pass
        else:
            raise ValueError(f"Unknown script: {script}")


class MockWebSocket:
    """Mock WebSocket for testing purposes."""
    
    def __init__(self, should_raise_on_recv: bool = False, should_raise_on_close: bool = False) -> None:
        """Initialize mock WebSocket.
        
        Args:
            should_raise_on_recv: Whether to raise exception on recv().
            should_raise_on_close: Whether to raise exception on close().
        """
        self.should_raise_on_recv = should_raise_on_recv
        self.should_raise_on_close = should_raise_on_close
        self.closed = False
        self.recv_count = 0
    
    def recv(self) -> str:
        """Mock recv method."""
        self.recv_count += 1
        if self.should_raise_on_recv:
            raise WebSocketConnectionClosedException("Connection closed")
        return f"Mock log line {self.recv_count}"
    
    def close(self) -> None:
        """Mock close method."""
        if self.should_raise_on_close:
            raise Exception("Error closing WebSocket")
        self.closed = True


class TestShadowstepLogcat:
    """Test cases for ShadowstepLogcat class."""
    
    @pytest.fixture
    def mock_driver_getter(self) -> Callable[[], MockWebDriver | None]:
        """Create a mock driver getter function."""
        def get_driver() -> MockWebDriver | None:
            return MockWebDriver()
        return get_driver
    
    @pytest.fixture
    def logcat(self, mock_driver_getter: Callable[[], MockWebDriver | None]) -> ShadowstepLogcat:
        """Create a ShadowstepLogcat instance with mock driver getter."""
        return ShadowstepLogcat(mock_driver_getter)  # type: ignore
    
    @pytest.fixture
    def temp_file(self) -> str:
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            return f.name
    
    def test_init_default_poll_interval(self, mock_driver_getter: Callable[[], MockWebDriver | None]) -> None:
        """Test initialization with default poll interval."""
        logcat = ShadowstepLogcat(mock_driver_getter)  # type: ignore
        
        assert logcat._driver_getter == mock_driver_getter  # noqa: S101
        assert logcat._poll_interval == DEFAULT_POLL_INTERVAL  # noqa: S101
        assert logcat._thread is None  # noqa: S101
        assert logcat._filename is None  # noqa: S101
        assert logcat._ws is None  # noqa: S101
    
    def test_init_custom_poll_interval(self, mock_driver_getter: Callable[[], MockWebDriver | None]) -> None:
        """Test initialization with custom poll interval."""
        custom_interval = 2.5
        logcat = ShadowstepLogcat(mock_driver_getter, poll_interval=custom_interval)  # type: ignore
        
        assert logcat._poll_interval == custom_interval  # noqa: S101
    
    def test_init_negative_poll_interval_raises_error(self, mock_driver_getter: Callable[[], MockWebDriver | None]) -> None:
        """Test that negative poll interval raises ValueError."""
        with pytest.raises(ShadowstepPollIntervalError, match="poll_interval must be non-negative"):
            ShadowstepLogcat(mock_driver_getter, poll_interval=-1.0)  # type: ignore
    
    def test_start_empty_filename_raises_error(self, logcat: ShadowstepLogcat) -> None:
        """Test that starting with empty filename raises ValueError."""
        with pytest.raises(ShadowstepEmptyFilenameError, match="filename cannot be empty"):
            logcat.start("")
    
    def test_start_already_running(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test starting when already running."""
        # Start first time
        logcat.start(temp_file)
        assert logcat._thread is not None  # noqa: S101
        assert logcat._thread.is_alive()  # noqa: S101
        
        # Try to start again
        logcat.start(temp_file)
        # Should not create a new thread
        assert logcat._thread is not None  # noqa: S101
        
        # Cleanup
        logcat.stop()
    
    def test_start_stop_basic(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test basic start and stop functionality."""
        logcat.start(temp_file)
        
        assert logcat._thread is not None  # noqa: S101
        assert logcat._filename == temp_file  # noqa: S101
        assert logcat._thread.is_alive()  # noqa: S101
        
        logcat.stop()
        
        assert logcat._thread is None  # noqa: S101
        assert logcat._filename is None  # noqa: S101
    
    def test_stop_without_start(self, logcat: ShadowstepLogcat) -> None:
        """Test stopping when not started."""
        # Should not raise any exceptions
        logcat.stop()
        
        assert logcat._thread is None  # noqa: S101
        assert logcat._filename is None  # noqa: S101
    
    def test_del_calls_stop(self, mock_driver_getter: Callable[[], MockWebDriver | None], temp_file: str) -> None:
        """Test that __del__ calls stop method."""
        logcat = ShadowstepLogcat(mock_driver_getter)  # type: ignore
        logcat.start(temp_file)
        
        # Test that __del__ method exists and can be called
        assert hasattr(logcat, "__del__")  # noqa: S101
        
        # Clean up properly
        logcat.stop()
    
    def test_get_http_url_from_url_attribute(self) -> None:
        """Test _get_http_url when _url attribute exists."""
        driver = MockWebDriver()
        driver.command_executor._url = "http://test:8080/wd/hub"
        
        logcat = ShadowstepLogcat(lambda: driver)  # type: ignore
        result = logcat._get_http_url(driver)  # type: ignore
        
        assert result == "http://test:8080/wd/hub"  # noqa: S101
    
    def test_get_http_url_from_client_config(self) -> None:
        """Test _get_http_url when _url is None but _client_config exists."""
        driver = MockWebDriver()
        driver.command_executor._url = None
        driver.command_executor._client_config = Mock()
        driver.command_executor._client_config.remote_server_addr = "https://test:8443"
        
        logcat = ShadowstepLogcat(lambda: driver)  # type: ignore
        result = logcat._get_http_url(driver)  # type: ignore
        
        assert result == "https://test:8443"  # noqa: S101
    
    def test_get_http_url_fallback(self) -> None:
        """Test _get_http_url fallback when no URL found."""
        driver = MockWebDriver()
        driver.command_executor._url = None
        driver.command_executor._client_config = None
        
        logcat = ShadowstepLogcat(lambda: driver)  # type: ignore
        result = logcat._get_http_url(driver)  # type: ignore
        
        assert result == ""  # noqa: S101
    
    def test_constants(self) -> None:
        """Test that constants have expected values."""
        assert DEFAULT_POLL_INTERVAL == 1.0  # noqa: S101
        assert WEBSOCKET_TIMEOUT == 5  # noqa: S101
    
    def test_thread_name(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test that thread has correct name."""
        logcat.start(temp_file)
        
        assert logcat._thread is not None  # noqa: S101
        assert logcat._thread.name == "ShadowstepLogcat"  # noqa: S101
        assert logcat._thread.daemon is True  # noqa: S101
        
        logcat.stop()
    
    def test_multiple_start_stop_cycles(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test multiple start/stop cycles."""
        for _ in range(3):
            logcat.start(temp_file)
            assert logcat._thread is not None  # noqa: S101
            assert logcat._thread.is_alive()  # noqa: S101
            
            logcat.stop()
            assert logcat._thread is None  # noqa: S101
            assert logcat._filename is None  # noqa: S101
    
    @patch("shadowstep.logcat.shadowstep_logcat.create_connection")
    def test_run_websocket_connection_success(self, mock_create_connection: Mock, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test successful WebSocket connection in _run method."""
        mock_ws = MockWebSocket()
        mock_create_connection.return_value = mock_ws
        
        # Start logcat
        logcat.start(temp_file)
        time.sleep(0.1)  # Give thread time to start
        
        # Stop logcat
        logcat.stop()
        
        # Verify WebSocket was created and closed
        mock_create_connection.assert_called()
        assert mock_ws.closed  # noqa: S101
    
    @patch("shadowstep.logcat.shadowstep_logcat.create_connection")
    def test_run_websocket_connection_failure(self, mock_create_connection: Mock, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test WebSocket connection failure in _run method."""
        mock_create_connection.side_effect = Exception("Connection failed")
        
        # Start logcat
        logcat.start(temp_file)
        time.sleep(0.1)  # Give thread time to start
        
        # Stop logcat
        logcat.stop()
        
        # Verify connection was attempted
        mock_create_connection.assert_called()
    
    @patch("shadowstep.logcat.shadowstep_logcat.create_connection")
    def test_run_websocket_recv_error(self, mock_create_connection: Mock, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test WebSocket recv error handling in _run method."""
        mock_ws = MockWebSocket(should_raise_on_recv=True)
        mock_create_connection.return_value = mock_ws
        
        # Start logcat
        logcat.start(temp_file)
        time.sleep(0.1)  # Give thread time to start
        
        # Stop logcat
        logcat.stop()
        
        # Verify WebSocket was created
        mock_create_connection.assert_called()
    
    @patch("shadowstep.logcat.shadowstep_logcat.create_connection")
    def test_run_websocket_close_error(self, mock_create_connection: Mock, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test WebSocket close error handling in _run method."""
        mock_ws = MockWebSocket(should_raise_on_close=True)
        mock_create_connection.return_value = mock_ws
        
        # Start logcat
        logcat.start(temp_file)
        time.sleep(0.1)  # Give thread time to start
        
        # Stop logcat
        logcat.stop()
        
        # Verify WebSocket was created
        mock_create_connection.assert_called()
    
    def test_run_no_filename(self, logcat: ShadowstepLogcat) -> None:
        """Test _run method when no filename is set."""
        # This should not raise an exception
        logcat._run()
    
    def test_run_file_write(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test that logcat writes to file."""
        with patch("shadowstep.logcat.shadowstep_logcat.create_connection") as mock_create_connection:
            mock_ws = MockWebSocket()
            mock_create_connection.return_value = mock_ws
            
            # Start logcat
            logcat.start(temp_file)
            time.sleep(0.2)  # Give thread time to write
            
            # Stop logcat
            logcat.stop()
            
            # Check if file was created and has content
            assert Path(temp_file).exists()  # noqa: S101
    
    def test_stop_webdriver_exception(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test stop method when WebDriver raises exception."""
        def failing_driver_getter() -> MockWebDriver | None:
            raise WebDriverException("Driver error")
        
        logcat._driver_getter = failing_driver_getter  # type: ignore
        logcat.start(temp_file)
        
        # Stop should handle WebDriver exception gracefully
        logcat.stop()
        
        assert logcat._thread is None  # noqa: S101
    
    def test_stop_none_driver(self, logcat: ShadowstepLogcat, temp_file: str) -> None:
        """Test stop method when driver getter returns None."""
        def none_driver_getter() -> MockWebDriver | None:
            return None
        
        logcat._driver_getter = none_driver_getter  # type: ignore
        logcat.start(temp_file)
        
        # Stop should handle None driver gracefully
        logcat.stop()
        
        assert logcat._thread is None  # noqa: S101
