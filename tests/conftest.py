# tests/conftest.py
import logging
import shutil
import time
from pathlib import Path

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

UDID = "127.0.0.1:6555"  # GooglePixel
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

    application.connect(server_ip=APPIUM_IP,
                        server_port=APPIUM_PORT,
                        command_executor=APPIUM_COMMAND_EXECUTOR,
                        capabilities=CAPABILITIES)
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
def android_settings_open_close(app: Shadowstep):
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app("com.android.settings")
    app.terminal.start_activity(package="com.android.settings", activity="com.android.settings.Settings")
    time.sleep(3)
    yield
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app("com.android.settings")


@pytest.fixture
def stability(press_home: None):
    time.sleep(3)
    return


@pytest.fixture
def touch_sounds(app: Shadowstep, android_settings_open_close: None):
    sounds_and_vibrations_element = app.find_and_get_element({"text": "Sound & vibration"})
    # sounds_and_vibrations_element = app.find_and_get_element({'text': 'Sound & vibration'})
    assert sounds_and_vibrations_element.is_visible()  # noqa: S101  # noqa: S101
    sounds_and_vibrations_element.tap(duration=3)
    time.sleep(5)
    touch_sounds_element = app.find_and_get_element({"text": "Touch sounds"})
    # touch_sounds_element = app.find_and_get_element({'text': 'Sound enhancement'})
    assert touch_sounds_element.is_visible()  # noqa: S101  # noqa: S101
    time.sleep(5)


@pytest.fixture
def android_settings_recycler(app: Shadowstep, android_settings_open_close: None):
    return app.get_element(
        locator={"resource-id": "com.android.settings:id/main_content_scrollable_container",
                 })


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
    yield
    path = Path("logcat_test.log")
    if path.exists() and path.is_file():
        path.unlink()
    path = Path("/tests/logcat_test.log")
    if path.exists() and path.is_file():
        path.unlink()
