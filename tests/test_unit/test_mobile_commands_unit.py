# ruff: noqa
# pyright: ignore
"""Tests for MobileCommands class."""

import pytest
from unittest.mock import Mock, patch
from shadowstep.mobile_commands import MobileCommands
from shadowstep.shadowstep import Shadowstep


class TestMobileCommands:
    """Test cases for MobileCommands class."""

    @pytest.fixture
    def mock_shadowstep(self):
        """Create a mock Shadowstep instance."""
        return Mock(spec=Shadowstep)

    @pytest.fixture
    def mobile_commands(self, mock_shadowstep):
        """Create MobileCommands instance with mocked dependencies."""
        mobile_commands = MobileCommands(mock_shadowstep)
        # Mock the is_connected method that the fail_safe decorator needs
        mobile_commands.is_connected = Mock(return_value=True)
        return mobile_commands

    @pytest.mark.unit
    def test_initialization(self, mock_shadowstep):
        """Test MobileCommands initialization."""
        mobile_commands = MobileCommands(mock_shadowstep)
        assert mobile_commands.shadowstep is mock_shadowstep
        assert mobile_commands.driver is None
        assert mobile_commands.logger is not None

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_activate_app(self, mock_get_driver, mobile_commands):
        """Test activate_app method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appId": "com.example.app"}
        result = mobile_commands.activate_app(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: activateApp", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_battery_info(self, mock_get_driver, mobile_commands):
        """Test battery_info method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"format": "percentage"}
        result = mobile_commands.battery_info(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: batteryInfo", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_battery_info_no_params(self, mock_get_driver, mobile_commands):
        """Test battery_info method with no parameters."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.battery_info()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: batteryInfo", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_clear_element(self, mock_get_driver, mobile_commands):
        """Test clear_element method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"elementId": "element123"}
        result = mobile_commands.clear_element(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: clearElement", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_device_info(self, mock_get_driver, mobile_commands):
        """Test device_info method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.device_info()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: deviceInfo", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_fingerprint(self, mock_get_driver, mobile_commands):
        """Test fingerprint method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"fingerprintId": 1}
        result = mobile_commands.fingerprint(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: fingerprint", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_clipboard(self, mock_get_driver, mobile_commands):
        """Test get_clipboard method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.get_clipboard()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getClipboard", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_current_activity(self, mock_get_driver, mobile_commands):
        """Test get_current_activity method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.get_current_activity()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getCurrentActivity", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_current_package(self, mock_get_driver, mobile_commands):
        """Test get_current_package method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.get_current_package()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getCurrentPackage", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_device_time(self, mock_get_driver, mobile_commands):
        """Test get_device_time method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.get_device_time()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getDeviceTime", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_performance_data(self, mock_get_driver, mobile_commands):
        """Test get_performance_data method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"packageName": "com.example.app", "dataType": "cpuinfo"}
        result = mobile_commands.get_performance_data(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getPerformanceData", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_performance_data_types(self, mock_get_driver, mobile_commands):
        """Test get_performance_data_types method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.get_performance_data_types()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getPerformanceDataTypes", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_settings(self, mock_get_driver, mobile_commands):
        """Test get_settings method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.get_settings()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getSettings", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_hide_keyboard(self, mock_get_driver, mobile_commands):
        """Test hide_keyboard method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.hide_keyboard()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: hideKeyboard", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_install_app(self, mock_get_driver, mobile_commands):
        """Test install_app method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appPath": "/path/to/app.apk"}
        result = mobile_commands.install_app(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: installApp", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_is_app_installed(self, mock_get_driver, mobile_commands):
        """Test is_app_installed method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appId": "com.example.app"}
        result = mobile_commands.is_app_installed(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: isAppInstalled", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_long_press_key(self, mock_get_driver, mobile_commands):
        """Test long_press_key method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"keycode": 4}
        result = mobile_commands.long_press_key(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: longPressKey", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_open_notifications(self, mock_get_driver, mobile_commands):
        """Test open_notifications method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.open_notifications()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: openNotifications", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_open_settings(self, mock_get_driver, mobile_commands):
        """Test open_settings method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.open_settings()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: openSettings", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_press_key(self, mock_get_driver, mobile_commands):
        """Test press_key method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"keycode": 4}
        result = mobile_commands.press_key(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: pressKey", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_query_app_state(self, mock_get_driver, mobile_commands):
        """Test query_app_state method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appId": "com.example.app"}
        result = mobile_commands.query_app_state(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: queryAppState", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_remove_app(self, mock_get_driver, mobile_commands):
        """Test remove_app method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appId": "com.example.app"}
        result = mobile_commands.remove_app(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: removeApp", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_replace_element_value(self, mock_get_driver, mobile_commands):
        """Test replace_element_value method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"elementId": "element123", "value": "new text"}
        result = mobile_commands.replace_element_value(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: replaceElementValue", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_scroll_back_to(self, mock_get_driver, mobile_commands):
        """Test scroll_back_to method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"elementId": "element123"}
        result = mobile_commands.scroll_back_to(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: scrollBackTo", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_send_sms(self, mock_get_driver, mobile_commands):
        """Test send_sms method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"phoneNumber": "1234567890", "message": "test message"}
        result = mobile_commands.send_sms(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: sendSMS", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_set_clipboard(self, mock_get_driver, mobile_commands):
        """Test set_clipboard method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"text": "clipboard text"}
        result = mobile_commands.set_clipboard(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: setClipboard", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_set_text(self, mock_get_driver, mobile_commands):
        """Test set_text method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"elementId": "element123", "text": "new text"}
        result = mobile_commands.set_text(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: setText", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_shell(self, mock_get_driver, mobile_commands):
        """Test shell method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"command": "ls", "args": ["-la"]}
        result = mobile_commands.shell(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: shell", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_start_activity(self, mock_get_driver, mobile_commands):
        """Test start_activity method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appPackage": "com.example.app", "appActivity": ".MainActivity"}
        result = mobile_commands.start_activity(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: startActivity", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_start_logs_broadcast(self, mock_get_driver, mobile_commands):
        """Test start_logs_broadcast method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.start_logs_broadcast()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: startLogsBroadcast", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_stop_logs_broadcast(self, mock_get_driver, mobile_commands):
        """Test stop_logs_broadcast method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.stop_logs_broadcast()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: stopLogsBroadcast", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_terminate_app(self, mock_get_driver, mobile_commands):
        """Test terminate_app method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"appId": "com.example.app"}
        result = mobile_commands.terminate_app(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: terminateApp", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_toggle_location_services(self, mock_get_driver, mobile_commands):
        """Test toggle_location_services method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        result = mobile_commands.toggle_location_services()
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: toggleLocationServices", {})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_update_settings(self, mock_get_driver, mobile_commands):
        """Test update_settings method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"setting": "value"}
        result = mobile_commands.update_settings(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: updateSettings", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_get_text(self, mock_get_driver, mobile_commands):
        """Test get_text method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"elementId": "element123"}
        result = mobile_commands.get_text(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: getText", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_perform_editor_action(self, mock_get_driver, mobile_commands):
        """Test perform_editor_action method."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        params = {"elementId": "element123", "action": "done"}
        result = mobile_commands.perform_editor_action(params)
        
        assert result is mobile_commands
        mock_driver.execute_script.assert_called_once_with("mobile: performEditorAction", params)

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_execute_with_driver(self, mock_get_driver, mobile_commands):
        """Test _execute method with valid driver."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        mobile_commands._execute("test: command", {"param": "value"})
        
        mock_driver.execute_script.assert_called_once_with("test: command", {"param": "value"})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_execute_with_none_driver(self, mock_get_driver, mobile_commands):
        """Test _execute method with None driver raises exception."""
        mock_get_driver.return_value = None
        
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException
        
        with pytest.raises(ShadowstepException, match="WebDriver is not available"):
            mobile_commands._execute("test: command", {"param": "value"})

    @pytest.mark.unit
    @patch('shadowstep.mobile_commands.WebDriverSingleton.get_driver')
    def test_execute_with_none_params(self, mock_get_driver, mobile_commands):
        """Test _execute method with None params."""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        mobile_commands._execute("test: command", None)
        
        mock_driver.execute_script.assert_called_once_with("test: command", {})
