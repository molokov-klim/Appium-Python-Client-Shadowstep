import logging
import sys

from icecream import ic
from loguru import logger
import subprocess
import pytest

from shadowstep.shadowstep import Shadowstep

# Please use virtual device Google Pixel 10.0
UDID = '192.168.56.101:5555'

logger.remove()
format_string = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level>| "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(sys.stdout, format=format_string, level=logging.INFO, colorize=True)


# Appium server must be run on localhost

@pytest.fixture(scope='session', autouse=True)
def app(request):
    application = Shadowstep()

    caps = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": UDID,
        "appium:noReset": True,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 900,
    }
    application.connect(server_ip='127.0.0.1',
                        server_port=4723,
                        capabilities=caps)
    application.adb.press_home()

    def app_finalizer(application):
        application.adb.press_home()
        application.disconnect()
    yield application

    request.addfinalizer(lambda: app_finalizer(application))


@pytest.fixture()
def udid():
    yield UDID


@pytest.fixture(scope="function", autouse=True)
def press_home(app):
    app.adb.press_home()
    # command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME']
    # subprocess.run(command, check=True)
