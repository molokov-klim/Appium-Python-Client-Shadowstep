# ruff: noqa
# pyright: ignore
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any

import pytest

from shadowstep.shadowstep import Shadowstep

# Silence noisy third-party libraries
logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("asyncio.selector_events").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("websockets").setLevel(logging.CRITICAL)
logging.getLogger("charset_normalizer").setLevel(logging.CRITICAL)

IS_CI = os.getenv("CI", "false").lower() == "true"

UDID = "emulator-5554" if IS_CI else "127.0.0.1:6555"

APPIUM_IP = "127.0.0.1"
APPIUM_PORT = 4723

APPIUM_COMMAND_EXECUTOR = f"http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub"

CAPABILITIES = {
    "platformName": "android",
    "appium:automationName": "uiautomator2",
    "appium:UDID": UDID,
    "appium:noReset": True,
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 900,
}
application = Shadowstep()


@pytest.fixture(scope="session")
def app():
    """Session-scoped fixture for initializing and connecting Shadowstep to a virtual Android device.

    Yields:
        Shadowstep: Connected Shadowstep instance for tests.
    """
    global application
    global UDID

    # Clear any existing instance
    application.disconnect()
    time.sleep(2)

    application.connect(
        server_ip=APPIUM_IP,
        server_port=APPIUM_PORT,
        command_executor=APPIUM_COMMAND_EXECUTOR,
        capabilities=CAPABILITIES,
        ssh_user=os.getenv("SHADOWSTEP_SSH_USER", ""),
        ssh_password=os.getenv("SHADOWSTEP_SSH_PASSWORD", ""),
    )

    # Wait for connection to be fully established
    max_wait_time = 60  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        if application.is_connected() and application.driver.session_id is not None:
            break
        time.sleep(1)

    # Final verification
    if not (application.is_connected() and application.driver.session_id is not None):
        raise RuntimeError("Failed to establish connection within timeout period")

    yield application
    application.disconnect()


@pytest.fixture
def udid():
    """Provides the UDID of the virtual device used in tests.

    Yields:
        str: Device UDID.
    """
    return UDID


@pytest.fixture(autouse=False)
def press_home(app: Shadowstep):
    app.terminal.press_home()
    yield
    app.terminal.press_home()


@pytest.fixture
def android_settings_open_close(app: Shadowstep, handle_not_responding: Any):
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app("com.android.settings")
    app.terminal.start_activity(
        package="com.android.settings", activity="com.android.settings.Settings"
    )
    app.get_element({"text": "Connected devices"}).wait(timeout=10)
    time.sleep(1)
    yield
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app("com.android.settings")


@pytest.fixture
def handle_not_responding(app: Shadowstep):
    close_app = app.get_element({"text": "Close app"})
    close_app.timeout = 1.5
    if close_app.is_visible():
        close_app.tap()
    close_app.wait_for_not()


@pytest.fixture
def stability(press_home: None):
    time.sleep(3)
    return


@pytest.fixture
def touch_sounds(app: Shadowstep, android_settings_open_close: None):
    sounds_and_vibrations_element = app.scroll_to_element({"text": "Sound & vibration"})
    assert sounds_and_vibrations_element.is_visible()  # noqa: S101  # noqa: S101
    sounds_and_vibrations_element.tap(duration=3)
    time.sleep(5)
    touch_sounds_element = app.scroll_to_element({"text": "Touch sounds"})
    assert touch_sounds_element.is_visible()  # noqa: S101  # noqa: S101
    time.sleep(5)


@pytest.fixture
def android_settings_recycler(app: Shadowstep, android_settings_open_close: None):
    return app.get_element(
        locator={
            "resource-id": "com.android.settings:id/main_content_scrollable_container",
        }
    )


@pytest.fixture
def connected_devices_image_path():
    return "_test_data/connected_devices.png"


@pytest.fixture
def system_image_path():
    return "_test_data/system.png"


@pytest.fixture
def cleanup_pages():
    yield
    for folder in ("pages", "mergedpages"):
        path = Path(folder)
        if path.exists() and path.is_dir():
            shutil.rmtree(path)


@pytest.fixture
def cleanup_log():
    """Cleanup all logcat test files after test execution."""
    yield
    # List of all logcat test files that might be created
    log_files = [
        "logcat_test.log",
        "/tests/logcat_test.log",
        "logcat_duplicate_test.log",
        "logcat_filtered_test.log",
        "logcat_restart1.log",
        "logcat_restart2.log",
        "logcat_context_test.log",
        "logcat_port_test.log",
        "logcat_append_test.log",
        "logcat_thread_name_test.log",
        "logcat_websocket_test.log",
        "logcat_filter_verification.log",
    ]

    for log_file in log_files:
        path = Path(log_file)
        if path.exists() and path.is_file():
            path.unlink()
