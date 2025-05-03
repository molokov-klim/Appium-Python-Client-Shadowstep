import logging
import sys

import pytest
from shadowstep.shadowstep import Shadowstep

# Please use virtual device Google Pixel 10.0
UDID = '192.168.56.101:5555'

# Configure standard logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger("shadowstep")
logger.setLevel(logging.INFO)

# Silence noisy third-party libraries
logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("asyncio.selector_events").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("websockets").setLevel(logging.CRITICAL)
logging.getLogger("charset_normalizer").setLevel(logging.CRITICAL)




@pytest.fixture(scope='session', autouse=True)
def app(request) -> Shadowstep:
    """Session-scoped fixture for initializing and connecting Shadowstep to a virtual Android device.

    Args:
        request: Pytest built-in request object for registering finalizers.

    Yields:
        Shadowstep: Connected Shadowstep instance for tests.
    """
    application = Shadowstep()

    capabilities = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": UDID,
        "appium:noReset": True,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 900,
    }

    application.connect(server_ip='127.0.0.1', server_port=4723, capabilities=capabilities)
    application.adb.press_home()

    def finalizer():
        try:
            application.adb.press_home()
        except Exception as e:
            logger.warning(f"Failed to send HOME key: {e}")
        finally:
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


@pytest.fixture(scope="function", autouse=True)
def press_home(app: Shadowstep) -> None:
    """Ensures device returns to the HOME screen before each test function.

    Args:
        app (Shadowstep): The Shadowstep test application instance.
    """
    try:
        app.adb.press_home()
    except Exception as e:
        logger.warning(f"Failed to press HOME before test: {e}")
