import logging
import subprocess
import pytest

from shadowstep.shadowstep import Shadowstep

# Please use virtual device Google Pixel 10.0
UDID = '192.168.208.101:5555'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Appium server must be run on localhost

@pytest.fixture(scope='session', autouse=True)
def app(request):
    application = Shadowstep()

    caps = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": UDID,
        "appium:noReset": True,
        "appium: autoGrantPermissions": True,
        "appium: newCommandTimeout": 600000,
    }
    application.connect(server_ip='127.0.0.1',
                        server_port=4723,
                        capabilities=caps)

    def app_finalizer(application):
        application.disconnect()

    yield application

    request.addfinalizer(lambda: app_finalizer(application))


@pytest.fixture()
def udid():
    yield UDID


@pytest.fixture(scope="function", autouse=True)
def press_home():
    command = ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME']
    subprocess.run(command, check=True)
