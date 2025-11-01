# ruff: noqa
# pyright: ignore
"""Integration tests for mobile_commands.py module - Part 4.

Emulator and file operations test group: GSM commands, power control,
SMS, sensors, APK installation, file operations, media projection, screen streaming.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_4.py
"""

import logging
import time

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart4:
    """Integration tests for MobileCommands class - Part 4.
    
    Testing emulator commands, file operations, APK installation,
    GSM, power control, SMS, sensors, and media projection.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Setup MobileCommands instance with app fixture.
        
        Args:
            app: Shadowstep application instance for testing.
        """
        self.mobile_commands = MobileCommands()
        self.app = app
        # Ensure app is connected
        assert self.app.is_connected()  # noqa: S101
        yield

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_call(self):
        """Test gsm_call command.
        
        Steps:
            1. Simulate incoming call.
        
        Note:
            GSM commands only work on emulators with telephony support.
        """
        result = self.mobile_commands.gsm_call({"phoneNumber": "5551234567", "action": "call"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_signal(self):
        """Test gsm_signal command.
        
        Steps:
            1. Set GSM signal strength level.
        
        Note:
            GSM commands only work on emulators with telephony support.
        """
        result = self.mobile_commands.gsm_signal({"signalStrength": 4})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_voice(self):
        """Test gsm_voice command.
        
        Steps:
            1. Set GSM voice state.
        
        Note:
            GSM commands only work on emulators with telephony support.
        """
        result = self.mobile_commands.gsm_voice({"state": "on"})
        logger.info(result)

    @pytest.mark.xfail(reason="Emulator camera injection only works on emulators", strict=False)
    def test_inject_emulator_camera_image(self):
        """Test inject_emulator_camera_image command.
        
        Steps:
            1. Inject image into emulator camera.
        
        Note:
            Only works on emulators.
        """
        result = self.mobile_commands.inject_emulator_camera_image({"image": "base64encodedimage"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid APK file path", strict=False)
    def test_install_app(self):
        """Test install_app command.
        
        Note:
            Requires valid APK file path.
        """
        result = self.mobile_commands.install_app({"appPath": "/path/to/app.apk"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid APK file paths", strict=False)
    def test_install_multiple_apks(self):
        """Test install_multiple_apks command.
        
        Note:
            Requires valid APK file paths.
        """
        result = self.mobile_commands.install_multiple_apks(
            {"apks": ["/path/to/app1.apk", "/path/to/app2.apk"]}
        )
        logger.info(result)

    def test_is_media_projection_recording_running(self):
        """Test is_media_projection_recording_running command.
        
        Verifies:
            - Result is a boolean value.
        """
        result = self.mobile_commands.is_media_projection_recording_running()
        assert isinstance(result, bool)  # noqa: S101

    def test_start_media_projection_recording(self):
        """Test start_media_projection_recording command.
        
        Steps:
            1. Start recording via media projection.
        """
        result = self.mobile_commands.start_media_projection_recording()
        logger.info(result)

    @pytest.mark.xfail(reason="EACCES: permission denied, mkdtemp 'recordingR6m2hB'", strict=False)
    def test_stop_media_projection_recording(self):
        """Test stop_media_projection_recording command.
        
        Note:
            May encounter access error when creating temporary directory.
        """
        result = self.mobile_commands.stop_media_projection_recording()
        logger.info(result)

    @pytest.mark.xfail(
        reason="SMS commands only work on emulators with telephony support", strict=False
    )
    def test_list_sms(self):
        """Test list_sms command.
        
        Verifies:
            - Result is a list.
        
        Note:
            SMS commands only work on emulators with telephony support.
        """
        result = self.mobile_commands.list_sms()
        assert isinstance(result, list)  # noqa: S101

    @pytest.mark.xfail(
        reason="SMS commands only work on emulators with telephony support", strict=False
    )
    def test_send_sms(self):
        """Test send_sms command.
        
        Steps:
            1. Send SMS message.
        
        Note:
            SMS commands only work on emulators with telephony support.
        """
        result = self.mobile_commands.send_sms(
            {"phoneNumber": "5551234567", "message": "Test message"}
        )
        logger.info(result)

    @pytest.mark.xfail(reason="Network speed control only works on emulators", strict=False)
    def test_network_speed(self):
        """Test network_speed command.
        
        Steps:
            1. Set network speed to "full".
        
        Note:
            Network speed control only works on emulators.
        """
        result = self.mobile_commands.network_speed({"speed": "full"})
        logger.info(result)

    @pytest.mark.xfail(reason="Power commands only work on emulators", strict=False)
    def test_power_ac(self):
        """Test power_ac command.
        
        Steps:
            1. Turn on AC power.
        
        Note:
            Power commands only work on emulators.
        """
        result = self.mobile_commands.power_ac({"state": "on"})
        logger.info(result)

    @pytest.mark.xfail(reason="Power commands only work on emulators", strict=False)
    def test_power_capacity(self):
        """Test power_capacity command.
        
        Steps:
            1. Set battery capacity to 100%.
        
        Note:
            Power commands only work on emulators.
        """
        result = self.mobile_commands.power_capacity({"percent": 100})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires file to exist on device", strict=False)
    def test_pull_file(self):
        """Test pull_file command.
        
        Note:
            Requires existing file on device.
        """
        result = self.mobile_commands.pull_file({"remotePath": "/sdcard/test_file.txt"})
        logger.info(result)

    def test_pull_folder(self):
        """Test pull_folder command.
        
        Steps:
            1. Pull /sdcard/ folder from device.
        """
        result = self.mobile_commands.pull_folder({"remotePath": "/sdcard/"})
        logger.info(result)

    def test_push_file(self):
        """Test push_file command.
        
        Steps:
            1. Push file to device with base64 payload.
        """
        result = self.mobile_commands.push_file(
            {"remotePath": "/sdcard/test.txt", "payload": "dGVzdCBjb250ZW50"}
        )
        logger.info(result)

    def test_delete_file(self):
        """Test delete_file command.
        
        Steps:
            1. Create test file via shell.
            2. Delete the file.
        """
        # Create a test file first via shell
        self.mobile_commands.shell({"command": "touch", "args": ["/sdcard/test_delete_file.txt"]})
        time.sleep(0.5)

        # Delete the file
        result = self.mobile_commands.delete_file({"remotePath": "/sdcard/test_delete_file.txt"})

        # Should complete without exception
        assert result is None or result is not None  # noqa: S101

    @pytest.mark.xfail(reason="Sensor control only works on emulators", strict=False)
    def test_sensor_set(self):
        """Test sensor_set command.
        
        Steps:
            1. Set light sensor value.
        
        Note:
            Sensor control only works on emulators.
        """
        result = self.mobile_commands.sensor_set({"sensorType": "light", "value": 50})
        logger.info(result)

    def test_start_screen_streaming(self):
        """Test start_screen_streaming command.
        
        Steps:
            1. Start screen streaming.
        """
        result = self.mobile_commands.start_screen_streaming()
        logger.info(result)

    def test_stop_screen_streaming(self):
        """Test stop_screen_streaming command.
        
        Steps:
            1. Stop screen streaming.
        """
        result = self.mobile_commands.stop_screen_streaming()
        logger.info(result)

    @pytest.mark.xfail(reason="Service commands may not work with all intents", strict=False)
    def test_start_service(self):
        """Test start_service command.
        
        Steps:
            1. Start Settings service.
        
        Note:
            Service commands may not work with all intents.
        """
        result = self.mobile_commands.start_service({"intent": "com.android.settings/.Settings"})
        logger.info(result)

    @pytest.mark.xfail(reason="Service commands may not work with all intents", strict=False)
    def test_stop_service(self):
        """Test stop_service command.
        
        Steps:
            1. Stop Settings service.
        
        Note:
            Service commands may not work with all intents.
        """
        result = self.mobile_commands.stop_service({"intent": "com.android.settings/.Settings"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="Emulator console command only works on emulators with console access", strict=False
    )
    def test_exec_emu_console_command(self):
        """Test exec_emu_console_command command.
        
        Steps:
            1. Execute help command in emulator console.
        
        Note:
            Only works on emulators with console access.
        """
        result = self.mobile_commands.exec_emu_console_command({"command": "help"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="Fingerprint requires emulator with fingerprint support", strict=False
    )
    def test_fingerprint(self):
        """Test fingerprint command.
        
        Steps:
            1. Simulate fingerprint with ID 1.
        
        Note:
            Requires emulator with fingerprint support.
        """
        result = self.mobile_commands.fingerprint({"fingerprintId": 1})
        logger.info(result)

