# noqa
# type: ignore
"""CI-specific configuration for Shadowstep tests.

This module provides CI-optimized fixtures and configurations
that override the default conftest.py settings when running in GitHub Actions.
"""
import logging
import os
import time
from pathlib import Path

import pytest

from shadowstep.shadowstep import Shadowstep

# Detect CI environment
IS_CI = os.getenv("CI", "false").lower() == "true"

# CI-optimized logging (less verbose)
if IS_CI:
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("websockets").setLevel(logging.ERROR)

# CI-specific configuration
if IS_CI:
    # GitHub Actions emulator configuration
    UDID = "emulator-5554"  # Default emulator UDID in GitHub Actions
    APPIUM_IP = "127.0.0.1"
    APPIUM_PORT = 4723
else:
    # Local development configuration (fallback to main conftest.py)
    UDID = "127.0.0.1:6555"  # Your local setup
    APPIUM_IP = "127.0.0.1"
    APPIUM_PORT = 4723

APPIUM_COMMAND_EXECUTOR = f"http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub"

# CI-optimized capabilities
CI_CAPABILITIES = {
    "platformName": "android",
    "appium:automationName": "uiautomator2",
    "appium:UDID": UDID,
    "appium:noReset": True,
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 300,  # Shorter timeout for CI
    "appium:androidInstallTimeout": 90000,  # APK install timeout
    "appium:adbExecTimeout": 20000,  # ADB command timeout
}

# Only override in CI environment
if IS_CI:
    application = Shadowstep()

    @pytest.fixture(scope="session")
    def app():
        """CI-optimized session fixture for Shadowstep."""
        global application
        
        # Wait for emulator to be ready
        max_retries = 30
        for attempt in range(max_retries):
            try:
                application.connect(
                    server_ip=APPIUM_IP,
                    server_port=APPIUM_PORT,
                    command_executor=APPIUM_COMMAND_EXECUTOR,
                    capabilities=CI_CAPABILITIES
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logging.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                time.sleep(5)
        
        yield application
        
        try:
            application.disconnect()
        except Exception:
            # Ignore disconnect errors in CI
            pass

    @pytest.fixture
    def udid():
        """CI UDID fixture."""
        return UDID

    @pytest.fixture(autouse=False)
    def press_home_ci(app: Shadowstep):
        """CI-optimized home press with error handling."""
        try:
            app.terminal.press_home()
        except Exception:
            pass  # Ignore errors in CI
        
        yield
        
        try:
            app.terminal.press_home()
        except Exception:
            pass  # Ignore errors in CI

    @pytest.fixture
    def android_settings_open_close_ci(app: Shadowstep):
        """CI-optimized Android settings fixture."""
        try:
            app.terminal.press_back()
            app.terminal.press_back()
            app.terminal.close_app("com.android.settings")
            app.terminal.start_activity(
                package="com.android.settings", 
                activity="com.android.settings.Settings"
            )
            time.sleep(2)  # Shorter wait in CI
        except Exception:
            pass  # Continue even if setup fails
        
        yield
        
        try:
            app.terminal.press_back()
            app.terminal.press_back()
            app.terminal.close_app("com.android.settings")
        except Exception:
            pass  # Ignore cleanup errors in CI

    @pytest.fixture
    def stability_ci(press_home_ci: None):
        """CI-optimized stability fixture with shorter waits."""
        time.sleep(1)  # Shorter stability wait in CI
        return

    @pytest.fixture
    def cleanup_pages_ci():
        """CI-optimized cleanup with error handling."""
        yield
        
        try:
            for folder in ("pages", "mergedpages"):
                path = Path(folder)
                if path.exists() and path.is_dir():
                    import shutil
                    shutil.rmtree(path)
        except Exception:
            pass  # Ignore cleanup errors in CI

    @pytest.fixture
    def cleanup_log_ci():
        """CI-optimized log cleanup."""
        yield
        
        try:
            for log_path in ("logcat_test.log", "/tests/logcat_test.log"):
                path = Path(log_path)
                if path.exists() and path.is_file():
                    path.unlink()
        except Exception:
            pass  # Ignore cleanup errors in CI
