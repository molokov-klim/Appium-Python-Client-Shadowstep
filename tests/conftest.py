import logging
import time

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

UDID = '192.168.30.101:5555'  # GooglePixel
APPIUM_IP = '127.0.0.1'
APPIUM_PORT = 4723

APPIUM_COMMAND_EXECUTOR = f'http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub'

CAPABILITIES = {
    "platformName": "android",
    "appium:automationName": "uiautomator2",
    "appium:UDID": UDID,
    "appium:noReset": True,
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 900,
}


@pytest.fixture(scope='session')
def app(request):
    """Session-scoped fixture for initializing and connecting Shadowstep to a virtual Android device.

    Args:
        request: Pytest built-in request object for registering finalizers.

    Yields:
        Shadowstep: Connected Shadowstep instance for tests.
    """
    application = Shadowstep()
    global UDID

    application.connect(server_ip=APPIUM_IP,
                        server_port=APPIUM_PORT,
                        command_executor=APPIUM_COMMAND_EXECUTOR,
                        capabilities=CAPABILITIES)
    yield application
    application.disconnect()


@pytest.fixture()
def udid() -> str:
    """Provides the UDID of the virtual device used in tests.

    Yields:
        str: Device UDID.
    """
    yield UDID


@pytest.fixture(scope="function", autouse=False)
def press_home(app: Shadowstep):
    app.terminal.press_home()
    yield
    app.terminal.press_home()


@pytest.fixture(scope="function")
def android_settings_open_close(app: Shadowstep):
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app('com.android.settings')
    app.terminal.start_activity(package='com.android.settings', activity='com.android.settings.Settings')
    time.sleep(3)
    yield
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app('com.android.settings')


@pytest.fixture
def stability(press_home: None):
    time.sleep(1)
    yield


@pytest.fixture(scope="function")
def touch_sounds(app: Shadowstep, android_settings_open_close):
    sounds_and_vibrations_element = app.find_and_get_element({'text': 'Sound & vibration'})
    # sounds_and_vibrations_element = app.find_and_get_element({'text': 'Звук и вибрация'})
    assert sounds_and_vibrations_element.is_visible()
    sounds_and_vibrations_element.tap(duration=3)
    time.sleep(5)
    touch_sounds_element = app.find_and_get_element({'text': 'Touch sounds'})
    # touch_sounds_element = app.find_and_get_element({'text': 'Улучшение звука'})
    assert touch_sounds_element.is_visible()
    time.sleep(5)


@pytest.fixture()
def android_settings_recycler(app: Shadowstep, android_settings_open_close):
    yield app.get_element(
        locator={'resource-id': 'com.android.settings:id/main_content_scrollable_container',
                 })


@pytest.fixture()
def connected_devices_image_path():
    yield "test_data/connected_devices.png"


@pytest.fixture()
def system_image_path():
    yield "test_data/system.png"
