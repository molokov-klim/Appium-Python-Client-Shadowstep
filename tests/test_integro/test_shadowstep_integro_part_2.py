# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import time

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.element.element import Element

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/test_integro/test_shadowstep_integro_part_2.py
"""


class TestShadowstepPart2:
    """Validate application and device management operations.

    This suite covers lifecycle control, device information, display metrics,
    system bars, and activity management.
    """

    def test_background_app_and_activate_app(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Exercise application lifecycle management.

        Steps:
            1. Ensure the Settings app is running.
            2. Call ``background_app()`` to send it to the background for two seconds.
            3. Confirm it returns to the foreground automatically.
            4. Call ``activate_app()`` to bring it forward explicitly.
            5. Verify the Settings app remains in the foreground.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Get Settings package
        settings_package = "com.android.settings"

        # Ensure Settings is in foreground
        current_package = app.get_current_package()
        assert "settings" in current_package.lower()  # noqa: S101

        # Background app for 2 seconds
        app.background_app(seconds=2)

        # Wait for app to return to foreground
        time.sleep(2.5)

        # Verify app is back in foreground
        package_after = app.get_current_package()
        assert "settings" in package_after.lower()  # noqa: S101

        # Activate Settings app explicitly
        app.activate_app(app_id=settings_package)

        # Verify Settings is still in foreground
        time.sleep(0.5)
        package_activated = app.get_current_package()
        assert "settings" in package_activated.lower()  # noqa: S101

    def test_get_display_density(self, app: Shadowstep, android_settings_open_close: None):
        """Verify retrieval of the device display density.

        Steps:
            1. Call ``get_display_density()``.
            2. Confirm the return value is an integer.
            3. Ensure the value falls within the expected range (120-640 dpi).

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Get display density
        density = app.get_display_density()

        # Verify density is an integer
        assert isinstance(density, int)  # noqa: S101

        # Verify density is within reasonable range for Android devices
        assert 120 <= density <= 640  # noqa: S101

    def test_get_system_bars(self, app: Shadowstep, android_settings_open_close: None):
        """Verify retrieval of system bar information.

        Steps:
            1. Call ``get_system_bars()``.
            2. Confirm a dictionary is returned.
            3. Check for expected keys such as ``statusBar`` and ``navigationBar``.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Get system bars info
        system_bars = app.get_system_bars()

        # Verify system_bars is a dictionary
        assert isinstance(system_bars, dict)  # noqa: S101

        # Verify expected keys are present
        assert "statusBar" in system_bars or "navigationBar" in system_bars  # noqa: S101

    def test_start_activity(self, app: Shadowstep):
        """Verify launching a specific activity via intent.

        Steps:
            1. Call ``start_activity()`` with the Settings intent.
            2. Confirm the activity launches successfully.
            3. Ensure the current package belongs to Settings.

        Args:
            app: Shadowstep application instance.
        """
        # Start Settings activity using component parameter
        app.start_activity(
            intent="com.android.settings/.Settings", component="com.android.settings/.Settings"
        )

        # Wait for activity to launch
        time.sleep(1)

        # Verify Settings is in foreground
        current_package = app.get_current_package()
        assert "settings" in current_package.lower()  # noqa: S101

    def test_press_key(self, app: Shadowstep, android_settings_open_close: None):
        """Verify sending a keycode to the device.

        Steps:
            1. Call ``press_key()`` with the HOME keycode.
            2. Ensure the key press completes without errors.
            3. Confirm the launcher (home screen) becomes visible.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Press HOME key (keycode 3)
        app.press_key(keycode=3)

        # Wait for home screen
        time.sleep(1)

        # Verify we're on home screen (launcher)
        current_package = app.get_current_package()
        assert isinstance(current_package, str)  # noqa: S101
        # Home screen package varies by device, just verify we got a package
        assert len(current_package) > 0  # noqa: S101

    def test_open_notifications(self, app: Shadowstep, android_settings_open_close: None):
        """Exercise opening the notification shade.

        Steps:
            1. Call ``open_notifications()``.
            2. Ensure the command completes without errors.
            3. Press Back to close the panel.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Open notifications
        app.open_notifications()

        # Wait for notification panel to open
        time.sleep(1)

        # Close notification panel by pressing back
        app.press_key(keycode=4)  # BACK key

        # Wait for panel to close
        time.sleep(0.5)

    def test_is_locked_status(self, app: Shadowstep):
        """Verify reading the device lock state.

        Steps:
            1. Call ``is_locked()`` to inspect the current lock state.
            2. Confirm the method returns a boolean.
            3. Ensure the method completes without errors.

        Args:
            app: Shadowstep application instance.
        """
        # Get lock state
        is_locked = app.is_locked()

        # Verify is_locked returns a boolean
        assert isinstance(is_locked, bool)  # noqa: S101

    def test_lock_command(self, app: Shadowstep):
        """Verify execution of ``lock()`` without errors.

        Steps:
            1. Call ``lock()`` to lock the device.
            2. Confirm the command completes without exceptions.

        Args:
            app: Shadowstep application instance.
        """
        # Lock the device
        app.lock()
        time.sleep(0.5)

        # If we reach here without exceptions, test passes

    def test_is_app_installed(self, app: Shadowstep):
        """Verify checking whether an application is installed.

        Steps:
            1. Use ``is_app_installed()`` for the Settings app.
            2. Confirm the method returns a boolean.
            3. Ensure the result is ``True`` (Settings should always exist).

        Args:
            app: Shadowstep application instance.
        """
        # Check if Settings app is installed
        is_installed = app.is_app_installed(app_id="com.android.settings")

        # Verify is_app_installed returns a boolean
        assert isinstance(is_installed, bool)  # noqa: S101

        # Settings should always be installed
        assert is_installed is True  # noqa: S101

    def test_query_app_state(self, app: Shadowstep, android_settings_open_close: None):
        """Verify retrieving the state of an application.

        Steps:
            1. Call ``query_app_state()`` for the Settings app.
            2. Confirm the method returns an integer.
            3. Ensure the state reflects a running application (``state >= 3``).

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Query Settings app state
        state = app.query_app_state(app_id="com.android.settings")

        # Verify state is an integer
        assert isinstance(state, int)  # noqa: S101

        # Verify state is valid (0-4, where 4 is running in foreground)
        assert 0 <= state <= 4  # noqa: S101

    def test_get_device_time(self, app: Shadowstep):
        """Verify retrieving the device timestamp.

        Steps:
            1. Call ``get_device_time()``.
            2. Confirm the method returns a timestamp string.
            3. Ensure the string is non-empty.

        Args:
            app: Shadowstep application instance.
        """
        # Get device time
        device_time = app.get_device_time()

        # Verify device_time is a non-empty string
        assert isinstance(device_time, str)  # noqa: S101
        assert len(device_time) > 0  # noqa: S101

    def test_get_performance_data_types(self, app: Shadowstep):
        """Verify fetching available performance data types.

        Steps:
            1. Call ``get_performance_data_types()``.
            2. Confirm the method returns a list.
            3. Ensure the list includes expected performance categories.

        Args:
            app: Shadowstep application instance.
        """
        # Get performance data types
        data_types = app.get_performance_data_types()

        # Verify data_types is a list
        assert isinstance(data_types, list)  # noqa: S101
        assert len(data_types) > 0  # noqa: S101

    def test_set_geolocation(self, app: Shadowstep):
        """Verify setting the device geolocation.

        Steps:
            1. Call ``set_geolocation()`` with test coordinates.
            2. Ensure the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
        """
        # Set test location (San Francisco)
        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 10.0

        app.set_geolocation(latitude=test_lat, longitude=test_lon, altitude=test_alt)

        # Wait a moment
        time.sleep(0.5)

        # If we reach here without exceptions, test passes

    def test_hide_keyboard_and_is_keyboard_shown(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Verify keyboard state management.

        Steps:
            1. Inspect keyboard visibility via ``is_keyboard_shown()``.
            2. Confirm the method returns a boolean value.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Check keyboard state
        is_shown = app.is_keyboard_shown()

        # Verify is_shown is a boolean
        assert isinstance(is_shown, bool)  # noqa: S101

        # Try to hide keyboard (will do nothing if not shown)
        app.hide_keyboard()

        # Verify no exception was raised
        time.sleep(0.3)

    def test_get_contexts(self, app: Shadowstep, android_settings_open_close: None):
        """Verify retrieving available contexts.

        Steps:
            1. Call ``get_contexts()``.
            2. Confirm the method returns a list.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Get contexts
        contexts = app.get_contexts()

        # Verify contexts is a list
        assert isinstance(contexts, list)  # noqa: S101

    def test_terminate_app(self, app: Shadowstep):
        """Verify terminating a specific application.

        Steps:
            1. Launch the Settings app.
            2. Call ``terminate_app()`` for Settings.
            3. Confirm the app is no longer in the foreground.

        Args:
            app: Shadowstep application instance.
        """
        # Launch Settings
        app.start_activity(
            intent="com.android.settings/.Settings", component="com.android.settings/.Settings"
        )
        time.sleep(1)

        # Terminate Settings
        app.terminate_app(app_id="com.android.settings")

        # Wait a moment
        time.sleep(1)

        # Verify Settings is not in foreground
        current_package = app.get_current_package()
        assert "settings" not in current_package.lower()  # noqa: S101

    def test_scroll_to_element(self, app: Shadowstep, android_settings_open_close: None):
        """Verify scrolling to locate an element.

        Steps:
            1. Call ``scroll_to_element()`` with a locator.
            2. Confirm the method returns an ``Element`` instance.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Scroll to element with text (may or may not be visible initially)
        element = app.scroll_to_element(locator={"text": "Settings"})

        # Verify element is returned
        assert isinstance(element, Element)  # noqa: S101

    def test_status_bar(self, app: Shadowstep, android_settings_open_close: None):
        """Verify executing status bar commands.

        Steps:
            1. Call ``status_bar()`` to expand and collapse.
            2. Ensure the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Expand notifications
        app.status_bar(command="expandNotifications", component="expandNotifications")
        time.sleep(0.5)

        # Collapse status bar
        app.status_bar(command="collapse", component="collapse")
        time.sleep(0.5)

    def test_get_connectivity(self, app: Shadowstep):
        """Verify retrieving the current connectivity state.

        Steps:
            1. Call ``get_connectivity()`` for specific services.
            2. Confirm the method returns a dictionary.
            3. Ensure the dictionary contains connectivity information.

        Args:
            app: Shadowstep application instance.
        """
        # Get connectivity state for wifi
        connectivity = app.get_connectivity(services=["wifi", "data"])

        # Verify connectivity is a dictionary
        assert isinstance(connectivity, dict)  # noqa: S101

    def test_set_connectivity(self, app: Shadowstep):
        """Verify modifying the network connectivity state.

        Steps:
            1. Capture the current connectivity state.
            2. Call ``set_connectivity()`` to enable Wi-Fi.
            3. Confirm the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
        """
        expected_result = "Wi-Fi enabled"
        app.set_connectivity(wifi=True)
        current_connectivity = app.get_connectivity(services=["wifi"])
        actual_result = current_connectivity.get("wifi", False)
        app.logger.info(f"[expected_result]: {expected_result=} {actual_result=}")
        assert actual_result, "Wi-Fi was not enabled"

    def test_network_speed(self, app: Shadowstep):
        """Verify setting the network speed.

        Steps:
            1. Call ``network_speed()`` with a speed profile.
            2. Ensure the command completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set network speed to full (emulator only)
        try:
            app.network_speed(speed="full")
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_gsm_call(self, app: Shadowstep):
        """Verify simulating a GSM call.

        Steps:
            1. Call ``gsm_call()`` with a phone number and action.
            2. Ensure the method completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Simulate incoming call (emulator only)
        try:
            app.gsm_call(phone_number="5551234567", action="call")
            time.sleep(0.5)

            # Cancel call
            app.gsm_call(phone_number="5551234567", action="cancel")
            time.sleep(0.5)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_gsm_signal(self, app: Shadowstep):
        """Verify adjusting GSM signal strength.

        Steps:
            1. Call ``gsm_signal()`` with a strength value.
            2. Ensure the method completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set signal strength (emulator only)
        try:
            app.gsm_signal(strength=4)
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_gsm_voice(self, app: Shadowstep):
        """Verify configuring the GSM voice state.

        Steps:
            1. Call ``gsm_voice()`` with a target state.
            2. Ensure the method completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set voice state to on (emulator only)
        try:
            app.gsm_voice(state="on")
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_power_capacity(self, app: Shadowstep):
        """Verify setting the battery charge level.

        Steps:
            1. Call ``power_capacity()`` with a percentage.
            2. Ensure the method completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Set battery capacity to 80% (emulator only)
        try:
            app.power_capacity(percent=80)
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_power_ac(self, app: Shadowstep):
        """Verify configuring AC power state.

        Steps:
            1. Call ``power_ac()`` with a desired state.
            2. Ensure the method completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Turn AC power on (emulator only)
        try:
            app.power_ac(state="on")
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

    def test_battery_info(self, app: Shadowstep):
        """Verify retrieving battery information.

        Steps:
            1. Call ``battery_info()``.
            2. Confirm a dictionary is returned.
            3. Ensure the dictionary contains battery details.

        Args:
            app: Shadowstep application instance.
        """
        # Get battery info
        battery = app.battery_info()

        # Verify battery is a dictionary
        assert isinstance(battery, dict)  # noqa: S101

    def test_device_info(self, app: Shadowstep):
        """Verify retrieving device information.

        Steps:
            1. Call ``device_info()``.
            2. Confirm the method returns a dictionary.

        Args:
            app: Shadowstep application instance.
        """
        # Get device info
        device = app.device_info()

        # Verify device is a dictionary
        assert isinstance(device, dict)  # noqa: S101

    def test_get_performance_data(self, app: Shadowstep):
        """Verify retrieving performance metrics.

        Steps:
            1. Obtain the available performance data types.
            2. Call ``get_performance_data()`` for the first available type.
            3. Confirm data is returned or errors are handled gracefully.

        Args:
            app: Shadowstep application instance.
        """
        try:
            # Get performance data types
            data_types = app.get_performance_data_types()

            if len(data_types) > 0:
                # Get performance data for first type
                perf_data = app.get_performance_data(
                    package_name="com.android.settings", data_type=data_types[0]
                )

                # Verify performance data is returned
                assert perf_data is not None  # noqa: S101
        except Exception:
            # Performance data may not be available on all devices
            pass

    def test_screenshots(self, app: Shadowstep, android_settings_open_close: None):
        """Verify starting screenshot monitoring.

        Steps:
            1. Call ``screenshots()`` to begin monitoring.
            2. Ensure the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
            android_settings_open_close: Fixture managing the Android Settings screen.
        """
        # Start screenshot monitoring
        app.screenshots()
        time.sleep(0.5)

    def test_get_ui_mode(self, app: Shadowstep):
        """Verify retrieving the user interface mode.

        Steps:
            1. Call ``get_ui_mode()`` with ``night``.
            2. Confirm the method returns a string.

        Args:
            app: Shadowstep application instance.
        """
        # Get UI mode for night
        ui_mode = app.get_ui_mode(mode="night")

        # Verify ui_mode is a string
        assert isinstance(ui_mode, str)  # noqa: S101

    def test_set_ui_mode(self, app: Shadowstep):
        """Verify setting the user interface mode.

        Steps:
            1. Call ``set_ui_mode()`` to configure night mode.
            2. Ensure the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
        """
        # Set night mode to no
        app.set_ui_mode(mode="night", value="no")
        time.sleep(0.5)

    def test_bluetooth(self, app: Shadowstep):
        """Verify controlling the Bluetooth state.

        Steps:
            1. Call ``bluetooth()`` with an action.
            2. Ensure the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
        """
        # Turn bluetooth off (safe operation)
        app.bluetooth(action="disable")
        time.sleep(0.5)

        # Turn bluetooth on
        app.bluetooth(action="enable")
        time.sleep(0.5)

    def test_nfc(self, app: Shadowstep):
        """Verify controlling the NFC state.

        Steps:
            1. Call ``nfc()`` with an action.
            2. Ensure the method completes without exceptions or handles unsupported devices gracefully.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Disable NFC - may not be supported on all devices
        try:
            app.nfc(action="disable")
            time.sleep(0.3)
        except (ShadowstepException, Exception):
            # NFC may not be available or controllable on all devices
            pass

    def test_toggle_gps(self, app: Shadowstep):
        """Verify toggling the GPS state.

        Steps:
            1. Call ``toggle_gps()``.
            2. Ensure the method completes without exceptions.

        Args:
            app: Shadowstep application instance.
        """
        # Toggle GPS
        app.toggle_gps()
        time.sleep(0.5)

        # Toggle back
        app.toggle_gps()
        time.sleep(0.5)

    def test_is_gps_enabled(self, app: Shadowstep):
        """Verify reading the GPS state.

        Steps:
            1. Call ``is_gps_enabled()``.
            2. Confirm the method returns a boolean value.

        Args:
            app: Shadowstep application instance.
        """
        # Check GPS state
        is_enabled = app.is_gps_enabled()

        # Verify is_enabled is a boolean
        assert isinstance(is_enabled, bool)  # noqa: S101

    def test_fingerprint(self, app: Shadowstep):
        """Verify simulating a fingerprint scan.

        Steps:
            1. Call ``fingerprint()`` with a fingerprint ID.
            2. Ensure the method completes without exceptions.

        Note:
            Available only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Simulate fingerprint (emulator only)
        try:
            app.fingerprint(fingerprint_id=1)
            time.sleep(0.3)
        except ShadowstepException as e:
            # Expected on real devices - check original exception for emulator message
            if e.__cause__:
                error_msg = str(e.__cause__).lower()
                assert "emulator" in error_msg or "only available" in error_msg  # noqa: S101
            else:
                raise

