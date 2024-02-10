import pytest

from shadowstep.shadowstep import Shadowstep


@pytest.fixture(scope='session', autouse=True)
def application(request):
    app = Shadowstep()

    caps = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": '00108921526791',
        "appium:noReset": True,
        "appium: autoGrantPermissions": True,
        "appium: newCommandTimeout": 600000,
    }
    app.connect(server_ip='10.77.171.211',
                server_port=4723,
                capabilities=caps)

    def app_finalizer(app):
        app.disconnect()

    yield app

    request.addfinalizer(lambda: app_finalizer(app))
