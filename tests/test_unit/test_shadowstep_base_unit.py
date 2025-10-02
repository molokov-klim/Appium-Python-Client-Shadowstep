class TestShadowstepBaseUnit:
    def test_appium_disconnected_error_initialization(self):
        """Test AppiumDisconnectedError initialization with parameters."""
        from shadowstep.shadowstep_base import AppiumDisconnectedError

        error = AppiumDisconnectedError("Test error", "screenshot_data", ["trace1", "trace2"])
        assert error.msg == "Test error"
        assert error.screen == "screenshot_data"
        assert error.stacktrace == ["trace1", "trace2"]

    def test_appium_disconnected_error_default_initialization(self):
        """Test AppiumDisconnectedError initialization with default parameters."""
        from shadowstep.shadowstep_base import AppiumDisconnectedError

        error = AppiumDisconnectedError()
        assert error.msg is None
        assert error.screen is None
        assert error.stacktrace is None

    def test_webdriver_singleton_get_session_id_with_sessions(self):
        """Test WebDriverSingleton._get_session_id with available sessions."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"value": [{"id": "session123"}]}'

        with patch("requests.get", return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "session123"

    def test_webdriver_singleton_get_session_id_no_sessions(self):
        """Test WebDriverSingleton._get_session_id with no sessions."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"value": []}'

        with patch("requests.get", return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    def test_webdriver_singleton_get_session_id_no_value_key(self):
        """Test WebDriverSingleton._get_session_id with no value key."""
        from shadowstep.shadowstep_base import WebDriverSingleton
        from unittest.mock import patch, Mock

        mock_response = Mock()
        mock_response.text = '{"other": []}'

        with patch("requests.get", return_value=mock_response):
            result = WebDriverSingleton._get_session_id({"command_executor": "http://test"})
            assert result == "unknown_session_id"

    def test_webdriver_singleton_clear_instance(self):
        """Test WebDriverSingleton.clear_instance method."""
        from shadowstep.shadowstep_base import WebDriverSingleton

        # Set some values
        WebDriverSingleton._instance = "test_instance"
        WebDriverSingleton._driver = "test_driver"

        WebDriverSingleton.clear_instance()

        assert WebDriverSingleton._instance is None
        assert WebDriverSingleton._driver is None

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
