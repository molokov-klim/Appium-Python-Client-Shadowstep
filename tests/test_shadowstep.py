import os
import subprocess
import time

from shadowstep.shadowstep import Shadowstep


class TestShadowstepBase:
    """
    A class to test the connection to the Shadowstep application.
    """

    def test_connect(self, app: Shadowstep) -> None:
        """
        Test the connection to the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the driver of the app instance is not None.
        """
        assert app.driver is not None


class TestShadowstep:
    """
    A class to test various functionalities of the Shadowstep application.
    """

    def test_get_element(self, app: Shadowstep) -> None:
        """
        Test retrieving an element from the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the locator of the retrieved element matches the expected locator.
        """
        element = app.get_element(locator={'content-desc': 'Phone'})
        assert element.locator == {'content-desc': 'Phone'}


class TestElement:
    """
    A class to test element interactions within the Shadowstep application.
    """

    def test_tap(self, app: Shadowstep) -> None:
        """
        Test tapping on an element in the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the response from the adb command contains 'com.android.dialer'
            after tapping on the element.
        """
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response


class TestAdb:
    """
    A class to test ADB (Android Debug Bridge) functionalities within the Shadowstep application.
    """

    def test_get_devices(self, app: Shadowstep, udid: str) -> None:
        """
        Test retrieving connected devices through ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the specified UDID is in the list of connected devices.
        """
        assert udid in app.adb.get_devices()

    def test_get_device_model(self, app: Shadowstep, udid: str) -> None:
        """
        Test retrieving the device model through ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that 'Pixel' is part of the device model string.
        """
        assert "Pixel" in app.adb.get_device_model()

    def test_push(self, app: Shadowstep, udid: str) -> None:
        """
        Test pushing a file to the device using ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the file was successfully pushed to the specified directory on the device.
        """
        app.adb.push(source=os.path.join('test_data', 'test_file'),
                     destination=os.path.join('sdcard/Download/test_file'),
                     udid=udid)
        response = str(subprocess.check_output(f'adb -s {udid} shell "ls sdcard/Download"'))
        assert 'test_file' in response
        subprocess.run(f"adb -s {udid} shell rm /sdcard/Download/test_file")

    def test_pull(self, app: Shadowstep, udid: str) -> None:
        """
        Test pulling a file from the device using ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the file was successfully pulled from the device to the local machine.
        """
        app.adb.push(source=os.path.join('test_data', 'test_file'),
                     destination='sdcard/Download/test_file',
                     udid=udid)
        assert not os.path.exists('test_file')
        app.adb.pull(source='sdcard/Download/test_file',
                     destination='test_file',
                     udid=udid)
        assert os.path.exists('test_file')
        os.remove('test_file')
        subprocess.run(f"adb -s {udid} shell rm /sdcard/Download/test_file")

    def test_install_app(self, app: Shadowstep, udid: str) -> None:
        """
        Test installing an application on the device using ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the application was installed and can be found in the list of installed packages.
        """
        app.adb.install_app(source=os.path.join('apk', 'notepad.apk'),
                            udid=udid)
        package = "com.farmerbb.notepad"
        result = subprocess.check_output(f"adb -s {udid} shell pm list packages").decode().strip()
        assert any([line.strip().endswith(package) for line in result.splitlines()])
        subprocess.run(f"adb -s {udid} uninstall com.farmerbb.notepad")
        time.sleep(55)
        assert not any([line.strip().endswith(package) for line in result.splitlines()])
