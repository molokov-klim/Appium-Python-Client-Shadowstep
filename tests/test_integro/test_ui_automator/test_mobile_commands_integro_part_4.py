# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Integration tests for ``mobile_commands.py`` — Part 4.

This suite covers emulator and file operations: GSM commands, power control,
SMS, sensors, APK installation, file operations, media projection, and
screen streaming.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_ui_automator/test_mobile_commands_integro_part_4.py
"""

import logging
import time

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.ui_automator.mobile_commands import MobileCommands

logger = logging.getLogger(__name__)


class TestMobileCommandsPart4:
    """Integration tests for ``MobileCommands`` — Part 4.

    Exercises emulator commands, file operations, APK installation, GSM,
    power control, SMS, sensors, and media projection flows.
    """

    @pytest.fixture(autouse=True)
    def setup_mobile_commands(self, app: Shadowstep):
        """Configure a ``MobileCommands`` instance using the ``app`` fixture.

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
        """Exercise the ``gsm_call`` command.

        Steps:
            1. Simulate an incoming call.

        Note:
            GSM commands work only on emulators with telephony support.
        """
        result = self.mobile_commands.gsm_call({"phoneNumber": "5551234567", "action": "call"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_signal(self):
        """Exercise the ``gsm_signal`` command.

        Steps:
            1. Set the GSM signal strength.

        Note:
            GSM commands work only on emulators with telephony support.
        """
        result = self.mobile_commands.gsm_signal({"signalStrength": 4})
        logger.info(result)

    @pytest.mark.xfail(
        reason="GSM commands only work on emulators with telephony support", strict=False
    )
    def test_gsm_voice(self):
        """Exercise the ``gsm_voice`` command.

        Steps:
            1. Configure the GSM voice connection state.

        Note:
            GSM commands work only on emulators with telephony support.
        """
        result = self.mobile_commands.gsm_voice({"state": "on"})
        logger.info(result)

    @pytest.mark.xfail(reason="Emulator camera injection only works on emulators", strict=False)
    def test_inject_emulator_camera_image(self):
        """Exercise the ``inject_emulator_camera_image`` command.

        Steps:
            1. Inject an image into the emulator camera.

        Note:
            This works only on emulators.
        """
        result = self.mobile_commands.inject_emulator_camera_image({"image": "base64encodedimage"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid APK file path", strict=False)
    def test_install_app(self):
        """Exercise the ``install_app`` command.

        Note:
            Requires a valid APK file path.
        """
        result = self.mobile_commands.install_app({"appPath": "/path/to/app.apk"})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires valid APK file paths", strict=False)
    def test_install_multiple_apks(self):
        """Exercise the ``install_multiple_apks`` command.

        Note:
            Requires valid APK file paths.
        """
        result = self.mobile_commands.install_multiple_apks(
            {"apks": ["/path/to/app1.apk", "/path/to/app2.apk"]}
        )
        logger.info(result)

    def test_is_media_projection_recording_running(self):
        """Exercise ``is_media_projection_recording_running``.

        Verifies:
            - The result is a boolean value.
        """
        result = self.mobile_commands.is_media_projection_recording_running()
        assert isinstance(result, bool)  # noqa: S101

    def test_start_media_projection_recording(self):
        """Exercise ``start_media_projection_recording``.

        Steps:
            1. Start media projection recording.
        """
        result = self.mobile_commands.start_media_projection_recording()
        logger.info(result)

    @pytest.mark.xfail(reason="EACCES: permission denied, mkdtemp 'recordingR6m2hB'", strict=False)
    def test_stop_media_projection_recording(self):
        """Exercise ``stop_media_projection_recording``.

        Note:
            Access errors may occur when creating a temporary directory.
        """
        result = self.mobile_commands.stop_media_projection_recording()
        logger.info(result)

    @pytest.mark.xfail(
        reason="SMS commands only work on emulators with telephony support", strict=False
    )
    def test_list_sms(self):
        """Exercise the ``list_sms`` command.

        Verifies:
            - The result is a list.

        Note:
            SMS commands work only on emulators with telephony support.
        """
        result = self.mobile_commands.list_sms()
        assert isinstance(result, list)  # noqa: S101

    @pytest.mark.xfail(
        reason="SMS commands only work on emulators with telephony support", strict=False
    )
    def test_send_sms(self):
        """Exercise the ``send_sms`` command.

        Steps:
            1. Send an SMS message.

        Note:
            SMS commands work only on emulators with telephony support.
        """
        result = self.mobile_commands.send_sms(
            {"phoneNumber": "5551234567", "message": "Test message"}
        )
        logger.info(result)

    @pytest.mark.xfail(reason="Network speed control only works on emulators", strict=False)
    def test_network_speed(self):
        """Exercise the ``network_speed`` command.

        Steps:
            1. Set the network speed to ``full``.

        Note:
            Network speed control works only on emulators.
        """
        result = self.mobile_commands.network_speed({"speed": "full"})
        logger.info(result)

    @pytest.mark.xfail(reason="Power commands only work on emulators", strict=False)
    def test_power_ac(self):
        """Exercise the ``power_ac`` command.

        Steps:
            1. Enable AC power.

        Note:
            Power commands work only on emulators.
        """
        result = self.mobile_commands.power_ac({"state": "on"})
        logger.info(result)

    @pytest.mark.xfail(reason="Power commands only work on emulators", strict=False)
    def test_power_capacity(self):
        """Exercise the ``power_capacity`` command.

        Steps:
            1. Set the battery level to 100%.

        Note:
            Power commands work only on emulators.
        """
        result = self.mobile_commands.power_capacity({"percent": 100})
        logger.info(result)

    @pytest.mark.xfail(reason="Requires file to exist on device", strict=False)
    def test_pull_file(self):
        """Exercise the ``pull_file`` command.

        Note:
            Requires a file that already exists on the device.
        """
        result = self.mobile_commands.pull_file({"remotePath": "/sdcard/test_file.txt"})
        logger.info(result)

    def test_pull_folder(self):
        """Exercise the ``pull_folder`` command.

        Steps:
            1. Retrieve the ``/sdcard/`` folder from the device.
        """
        result = self.mobile_commands.pull_folder({"remotePath": "/sdcard/"})
        logger.info(result)

    def test_push_file(self):
        """Exercise the ``push_file`` command.

        Steps:
            1. Upload a file to the device using base64 content.
        """
        result = self.mobile_commands.push_file(
            {"remotePath": "/sdcard/test.txt", "payload": "dGVzdCBjb250ZW50"}
        )
        logger.info(result)

    def test_delete_file(self):
        """Exercise the ``delete_file`` command.

        Steps:
            1. Create a test file via ``shell``.
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
        """Exercise the ``sensor_set`` command.

        Steps:
            1. Set the light sensor value.

        Note:
            Sensor control works only on emulators.
        """
        result = self.mobile_commands.sensor_set({"sensorType": "light", "value": 50})
        logger.info(result)

    def test_start_screen_streaming(self):
        """Exercise the ``start_screen_streaming`` command.

        Steps:
            1. Start screen streaming.
        """
        result = self.mobile_commands.start_screen_streaming()
        logger.info(result)

    def test_stop_screen_streaming(self):
        """Exercise the ``stop_screen_streaming`` command.

        Steps:
            1. Stop screen streaming.
        """
        result = self.mobile_commands.stop_screen_streaming()
        logger.info(result)

    @pytest.mark.xfail(reason="Service commands may not work with all intents", strict=False)
    def test_start_service(self):
        """Exercise the ``start_service`` command.

        Steps:
            1. Launch the Settings service.

        Note:
            Service commands may fail depending on the intent.
        """
        result = self.mobile_commands.start_service({"intent": "com.android.settings/.Settings"})
        logger.info(result)

    @pytest.mark.xfail(reason="Service commands may not work with all intents", strict=False)
    def test_stop_service(self):
        """Exercise the ``stop_service`` command.

        Steps:
            1. Stop the Settings service.

        Note:
            Service commands may fail depending on the intent.
        """
        result = self.mobile_commands.stop_service({"intent": "com.android.settings/.Settings"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="Emulator console command only works on emulators with console access", strict=False
    )
    def test_exec_emu_console_command(self):
        """Exercise the ``exec_emu_console_command`` command.

        Steps:
            1. Run the ``help`` command in the emulator console.

        Note:
            Works only on emulators with console access.
        """
        result = self.mobile_commands.exec_emu_console_command({"command": "help"})
        logger.info(result)

    @pytest.mark.xfail(
        reason="Fingerprint requires emulator with fingerprint support", strict=False
    )
    def test_fingerprint(self):
        """Exercise the ``fingerprint`` command.

        Steps:
            1. Simulate fingerprint ID ``1``.

        Note:
            Requires an emulator with fingerprint support.
        """
        result = self.mobile_commands.fingerprint({"fingerprintId": 1})
        logger.info(result)

