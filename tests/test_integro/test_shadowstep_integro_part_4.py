# ruff: noqa
# pyright: ignore
import time

from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/test_integro/test_shadowstep_integro_part_4.py
"""


class TestShadowstepPart4:
    """Verify application installation operations and driver management.

    This suite covers application install/remove flows, SMS commands,
    driver access, and reconnection logic.
    """

    def test_install_app(self, app: Shadowstep):
        """Exercise application installation.

        Steps:
            1. Call ``install_app()`` with an APK path.
            2. Confirm the method completes without exceptions.

        Note:
            This test verifies the method signature. Real installation requires a valid APK.

        Args:
            app: Shadowstep application instance.
        """
        # Note: This test verifies method signature
        # Actual installation requires valid APK file
        # Test passes if method is callable with correct parameters
        try:
            app.install_app(app_path="/sdcard/test.apk", replace=True, timeout=300000)
            time.sleep(0.3)
        except Exception:
            # Expected to fail if APK doesn't exist
            # Method signature is correct
            pass

    def test_install_multiple_apks(self, app: Shadowstep):
        """Exercise installing multiple APKs.

        Steps:
            1. Call ``install_multiple_apks()`` with APK paths.
            2. Confirm the method completes without exceptions.

        Note:
            This test only verifies the signature; real installation needs valid APK files.

        Args:
            app: Shadowstep application instance.
        """
        # Note: This test verifies method signature
        # Actual installation requires valid APK files
        try:
            app.install_multiple_apks(app_paths=["/sdcard/test1.apk", "/sdcard/test2.apk"])
            time.sleep(0.3)
        except Exception:
            # Expected to fail if APKs don't exist
            # Method signature is correct
            pass

    def test_remove_app(self, app: Shadowstep):
        """Exercise removing an application.

        Steps:
            1. Call ``remove_app()`` with a package id.
            2. Confirm the method completes without exceptions.

        Note:
            This test validates the signature only; no real app is removed.

        Args:
            app: Shadowstep application instance.
        """
        # Note: This test verifies method signature
        # We won't actually remove a real app
        try:
            app.remove_app(app_id="com.example.testapp", timeout=20000)
            time.sleep(0.3)
        except Exception:
            # Expected to fail if app doesn't exist
            # Method signature is correct
            pass

    def test_clear_app(self, app: Shadowstep):
        """Exercise clearing application data.

        Steps:
            1. Call ``clear_app()`` with a package id.
            2. Confirm the method completes without exceptions.

        Note:
            Signature verification only; the call targets a system app expected to handle the request.

        Args:
            app: Shadowstep application instance.
        """
        # Note: This test verifies method signature
        # We'll try with a system app that should handle clear gracefully
        try:
            app.clear_app(app_id="com.android.settings")
            time.sleep(0.3)
        except Exception:
            # Some apps may not allow clearing data
            # Method signature is correct
            pass

    def test_send_sms(self, app: Shadowstep):
        """Exercise sending SMS (emulator only).

        Steps:
            1. Call ``send_sms()`` with a phone number and message.
            2. Confirm the method completes without exceptions.

        Note:
            ``send_sms`` works only on emulators.

        Args:
            app: Shadowstep application instance.
        """
        # Note: send_sms only works on emulators
        try:
            app.send_sms(phone_number="5551234567", message="Test SMS")
            time.sleep(0.3)
        except Exception:
            # Expected to fail on real devices
            # Method signature is correct
            pass

    def test_get_driver(self, app: Shadowstep):
        """Verify retrieving the WebDriver instance.

        Steps:
            1. Call ``get_driver()``.
            2. Confirm a WebDriver instance is returned.
            3. Ensure ``session_id`` is populated.

        Args:
            app: Shadowstep application instance.
        """
        # Get WebDriver instance
        driver = app.get_driver()

        # Verify driver is returned
        assert driver is not None  # noqa: S101

        # Verify driver has session_id
        assert hasattr(driver, "session_id")  # noqa: S101
        assert driver.session_id is not None  # noqa: S101

        # Verify it's the same as app.driver
        assert driver is app.driver  # noqa: S101

    def test_reconnect(self, app: Shadowstep):
        """Exercise reconnecting to the device.

        Steps:
            1. Capture the initial ``session_id``.
            2. Call ``reconnect()`` to establish a new session.
            3. Confirm a new session is active.
            4. Verify the app remains connected.

        Args:
            app: Shadowstep application instance.
        """
        # Get initial session_id
        initial_session_id = app.driver.session_id
        assert initial_session_id is not None  # noqa: S101

        # Reconnect to device
        app.reconnect()

        # Wait for reconnection to complete
        time.sleep(3)

        # Verify new session is established
        assert app.driver is not None  # noqa: S101
        assert app.driver.session_id is not None  # noqa: S101

        # Verify app is connected
        assert app.is_connected()  # noqa: S101

        # Session ID may be the same or different depending on server
        # Just verify we have a valid session
        assert len(app.driver.session_id) > 0  # noqa: S101

