from unittest.mock import patch, Mock, MagicMock

import pytest
from selenium.common.exceptions import InvalidSessionIdException, NoSuchDriverException

from shadowstep.shadowstep import Shadowstep

# Test capabilities for testing
CAPABILITIES = {
    "platformName": "Android",
    "deviceName": "test_device",
    "app": "test_app.apk"
}

app = Shadowstep()

class TestShadowstepBaseUnit:

    def test_get_driver_method(self):
        """Test get_driver method."""

        with patch("shadowstep.shadowstep_base.WebDriverSingleton.get_driver") as mock_get_driver:
            mock_get_driver.return_value = "test_driver"
            result = app.get_driver()
            assert result == "test_driver"
            mock_get_driver.assert_called_once()

    def test_is_session_active_on_grid_success(self):
        """Test _is_session_active_on_grid with successful response."""

        mock_driver = Mock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {"nodes": [{"slots": [{"session": {"sessionId": "test_session_id"}}]}]}
        }
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is True

    def test_is_session_active_on_grid_no_session(self):
        """Test _is_session_active_on_grid with no matching session."""

        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {"nodes": [{"slots": [{"session": {"sessionId": "different_session_id"}}]}]}
        }
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_grid_exception(self):
        """Test _is_session_active_on_grid with exception."""

        with patch("requests.get", side_effect=Exception("Network error")):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_standalone_success(self):
        """Test _is_session_active_on_standalone with successful response."""

        mock_driver = Mock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "test_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_standalone()
            assert result is True

    def test_is_session_active_on_standalone_no_match(self):
        """Test _is_session_active_on_standalone with no matching session."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "different_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_standalone()
            assert result is False

    def test_is_session_active_on_standalone_exception(self):
        """Test _is_session_active_on_standalone with exception."""

        with patch("requests.get", side_effect=Exception("Network error")):
            result = app._is_session_active_on_standalone()
            assert result is False

    def test_is_session_active_on_standalone_new_style_success(self):
        """Test _is_session_active_on_standalone_new_style with successful response."""

        mock_driver = Mock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "test_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_standalone_new_style()
            assert result is True

    def test_is_session_active_on_standalone_new_style_no_match(self):
        """Test _is_session_active_on_standalone_new_style with no matching session."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": [{"id": "different_session_id", "ready": True}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_standalone_new_style()
            assert result is False

    def test_is_session_active_on_standalone_new_style_exception(self):
        """Test _is_session_active_on_standalone_new_style with exception."""

        with patch("requests.get", side_effect=Exception("Network error")):
            result = app._is_session_active_on_standalone_new_style()
            assert result is False

    def test_wait_for_session_id_success(self):
        """Test _wait_for_session_id with successful session ID assignment."""

        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"
        with patch.object(app, "driver", mock_driver):
            with patch("time.time", side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                with patch("time.sleep"):
                    # Should not raise exception
                    result = app._wait_for_session_id(timeout=5)
                    assert result == "test_session_id"

    def test_wait_for_session_id_timeout(self):
        """Test _wait_for_session_id with timeout."""

        import pytest

        mock_driver = MagicMock()
        mock_driver.session_id = None
        with patch.object(app, "driver", mock_driver):
            with patch("time.time", side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                with patch("time.sleep"):
                    with patch(
                            "shadowstep.shadowstep_base.WebDriverSingleton.get_driver",
                            return_value=mock_driver,
                    ):
                        with pytest.raises(
                                RuntimeError, match="WebDriver session_id was not assigned in time"
                        ):
                            app._wait_for_session_id(timeout=5)

    def test_get_ignored_dirs(self):
        """Test _get_ignored_dirs method."""

        with patch("sys.base_prefix", "/usr/local/python"):
            with patch(
                    "site.getsitepackages",
                    return_value=["/usr/local/python/lib/python3.9/site-packages"],
            ):
                with patch(
                        "sys.path",
                        ["/usr/local/python/lib/python3.9/site-packages", "/usr/local/python/lib"],
                ):
                    result = app._get_ignored_dirs()
                    assert isinstance(result, set)
                    assert "venv" in result
                    assert ".venv" in result
                    assert "__pycache__" in result

    def test_connect_with_ssh_credentials(self):
        """Test connect method with SSH credentials."""

        # Mock the WebDriver and Transport
        with patch("shadowstep.shadowstep_base.WebDriverSingleton") as mock_singleton:
            with patch("shadowstep.shadowstep_base.Transport") as mock_transport:
                with patch("shadowstep.shadowstep_base.Terminal") as mock_terminal:
                    with patch("shadowstep.shadowstep_base.Adb") as mock_adb:
                        with patch("requests.delete"):  # Mock disconnect call
                            # Disconnect first
                            app.disconnect()

                            mock_driver = MagicMock()
                            mock_driver.session_id = "test_session_id"
                            mock_singleton.return_value = mock_driver

                            app.connect(
                                capabilities=CAPABILITIES,
                                server_ip="127.0.0.1",
                                server_port=4723,
                                ssh_user="test_user",
                                ssh_password="test_password",
                            )

                            # Verify SSH transport was created
                            mock_transport.assert_called_once_with(
                                server="127.0.0.1", port=22, user="test_user", password="test_password"
                            )
                            mock_terminal.assert_called_once()
                            mock_adb.assert_called_once()

    def test_disconnect_with_invalid_session_exception(self):
        """Test disconnect method with InvalidSessionIdException."""

        # Mock driver and requests.delete to raise InvalidSessionIdException
        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        with patch("requests.delete", side_effect=InvalidSessionIdException("Invalid session")):
            app.disconnect()
            # Should not raise exception, just log debug message

    def test_disconnect_with_no_such_driver_exception(self):
        """Test disconnect method with NoSuchDriverException."""

        # Mock driver and requests.delete to raise NoSuchDriverException
        mock_driver = MagicMock()
        mock_driver.session_id = "test_session_id"
        app.driver = mock_driver

        with patch("requests.delete", side_effect=NoSuchDriverException("No such driver")):
            app.disconnect()
            # Should not raise exception, just log debug message

    def test_is_session_active_on_grid_no_slots(self):
        """Test _is_session_active_on_grid with nodes but no slots."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": {"nodes": [{"slots": []}]}}
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is False

    def test_is_session_active_on_grid_no_session_in_slot(self):
        """Test _is_session_active_on_grid with slots but no session."""

        mock_response = Mock()
        mock_response.json.return_value = {"value": {"nodes": [{"slots": [{"session": None}]}]}}
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = app._is_session_active_on_grid()
            assert result is False

    @pytest.mark.unit
    def test_appium_disconnected_error_initialization(self):
        """Test AppiumDisconnectedError initialization with parameters."""
        from shadowstep.shadowstep_base import AppiumDisconnectedError

        error = AppiumDisconnectedError("Test error", "screenshot_data", ["trace1", "trace2"])
        assert error.msg == "Test error"
        assert error.screen == "screenshot_data"
        assert error.stacktrace == ["trace1", "trace2"]

    @pytest.mark.unit
    def test_appium_disconnected_error_default_initialization(self):
        """Test AppiumDisconnectedError initialization with default parameters."""
        from shadowstep.shadowstep_base import AppiumDisconnectedError

        error = AppiumDisconnectedError()
        assert error.msg is None
        assert error.screen is None
        assert error.stacktrace is None

    @pytest.mark.unit
    def test_webdriver_singleton_get_session_id_with_sessions(self):
        """Test WebDriverSingleton._get_session_id with available sessions."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"value": [{"id": "session123"}]}'

        with patch("requests.get", return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "session123"

    @pytest.mark.unit
    def test_webdriver_singleton_get_session_id_no_sessions(self):
        """Test WebDriverSingleton._get_session_id with no sessions."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"value": []}'

        with patch("requests.get", return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    @pytest.mark.unit
    def test_webdriver_singleton_get_session_id_no_value_key(self):
        """Test WebDriverSingleton._get_session_id with no value key."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"other": []}'

        with patch("requests.get", return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    @pytest.mark.unit
    def test_webdriver_singleton_clear_instance(self):
        """Test WebDriverSingleton.clear_instance method."""
        from shadowstep.shadowstep_base import WebDriverSingleton

        # Set some values
        WebDriverSingleton._instance = "test_instance"
        WebDriverSingleton._driver = "test_driver"

        WebDriverSingleton.clear_instance()

        assert WebDriverSingleton._instance is None
        assert WebDriverSingleton._driver is None

    @pytest.mark.unit
    def test_webdriver_singleton_get_driver(self):
        """Test WebDriverSingleton.get_driver method."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch

        with patch("shadowstep.shadowstep_base.cast") as mock_cast:
            mock_cast.return_value = "test_driver"
            WebDriverSingleton._driver = "test_driver"

            result = WebDriverSingleton.get_driver()
            assert result == "test_driver"
            mock_cast.assert_called_once_with("WebDriver", "test_driver")

    @pytest.mark.unit
    def test_shadowstep_base_initialization(self):
        """Test ShadowstepBase initialization."""
        from shadowstep.shadowstep_base import ShadowstepBase

        base = ShadowstepBase()
        assert base.logger is not None
        assert base.driver is None
        assert base.server_ip is None
        assert base.server_port is None
        assert base.capabilities is None
        assert base.options is None
        assert base.extensions is None
        assert base.ssh_password is None
        assert base.ssh_user is None
        assert base.ssh_port == 22
        assert base.command_executor is None
        assert base.transport is None
        assert base.terminal is None
        assert base.adb is None
        assert isinstance(base._ignored_auto_discover_dirs, set)
        assert isinstance(base._ignored_base_path_parts, set)
