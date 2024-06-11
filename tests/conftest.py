import os
import pytest

from shadowstep.shadowstep import Shadowstep

# Please use virtual device Google Pixel 10.0
UDID = '192.168.208.101:5555'


# Appium server must be run on localhost

@pytest.fixture(scope='session', autouse=True)
def application(request):
    app = Shadowstep()

    caps = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": UDID,
        "appium:noReset": True,
        "appium: autoGrantPermissions": True,
        "appium: newCommandTimeout": 600000,
    }
    app.connect(server_ip='127.0.0.1',
                server_port=4723,
                capabilities=caps)

    def app_finalizer(app):
        app.disconnect()

    yield app

    request.addfinalizer(lambda: app_finalizer(app))
