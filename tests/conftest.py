import logging
import sys
import time

import pytest
from wheel.metadata import yield_lines

from shadowstep.shadowstep import Shadowstep, logger



# Silence noisy third-party libraries
logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("adaptavist").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("asyncio.selector_events").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("websockets").setLevel(logging.CRITICAL)
logging.getLogger("charset_normalizer").setLevel(logging.CRITICAL)

UDID = None


@pytest.fixture(scope='session', autouse=True)
def app(request) -> Shadowstep:
    """Session-scoped fixture for initializing and connecting Shadowstep to a virtual Android device.

    Args:
        request: Pytest built-in request object for registering finalizers.

    Yields:
        Shadowstep: Connected Shadowstep instance for tests.
    """
    application = Shadowstep()
    global UDID

    REMOTE = False
    if REMOTE:
        UDID = '0010941234TEST30'  # STB6 COM
        APPIUM_IP = "10.77.171.211"
        APPIUM_PORT = 3334
        APPIUM_COMMAND_EXECUTOR = f'http://{APPIUM_IP}:{APPIUM_PORT}'
    else:
        # UDID = '10.77.124.56:5554'      # STB6 TCP
        UDID = '192.168.56.101:5555'  # GooglePixel
        APPIUM_IP = '127.0.0.1'
        APPIUM_PORT = 4723
        APPIUM_COMMAND_EXECUTOR = f'http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub'

    capabilities = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": UDID,
        "appium:noReset": True,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 900,
    }

    application.connect(server_ip=APPIUM_IP,
                        server_port=APPIUM_PORT,
                        command_executor=APPIUM_COMMAND_EXECUTOR,
                        capabilities=capabilities)

    def finalizer():
        application.disconnect()

    request.addfinalizer(finalizer)
    yield application


@pytest.fixture()
def udid() -> str:
    """Provides the UDID of the virtual device used in tests.

    Yields:
        str: Device UDID.
    """
    yield UDID

@pytest.fixture(scope="function", autouse=False)
def press_home(app: Shadowstep):
    yield
    app.terminal.press_home()

@pytest.fixture(scope="function")
def android_settings(app: Shadowstep):
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app('com.android.settings')
    app.terminal.start_activity(package='com.android.settings', activity='com.android.settings.Settings')
    time.sleep(3)
    yield
    app.terminal.press_back()
    app.terminal.press_back()
    app.terminal.close_app('com.android.settings')

@pytest.fixture(scope="function")
def touch_sounds(app: Shadowstep, android_settings):
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
def android_settings_recycler(app: Shadowstep, android_settings):
    yield app.get_element(
            locator={'resource-id': 'com.android.settings:id/main_content_scrollable_container',
                     })

@pytest.fixture()
def connected_devices_image_path():
    yield "tests/test_data/connected_devices.png"

@pytest.fixture()
def system_image_path():
    yield "tests/test_data/system.png"

