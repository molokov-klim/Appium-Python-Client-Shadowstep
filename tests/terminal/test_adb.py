# tests/terminal/test_adb.py
import os
import subprocess

from shadowstep.shadowstep import Shadowstep


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
        assert udid in app.adb.get_devices()  # noqa: S101

    def test_get_device_model(self, app: Shadowstep, udid: str) -> None:
        """
        Test retrieving the device model through ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that 'Pixel' is part of the device model string.
        """
        assert "Pixel" in app.adb.get_device_model(udid=udid)  # noqa: S101

    def test_push(self, app: Shadowstep, udid: str) -> None:
        """
        Test pushing a file to the device using ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the file was successfully pushed to the specified directory on the device.
        """
        app.adb.push(source=os.path.join("_test_data", "test_file"),
                     destination=os.path.join("sdcard/Download/test_file"),
                     udid=udid)
        response = str(subprocess.check_output(["adb", "-s", f"{udid}", "shell", "ls", "sdcard/Download"]))  # noqa: S603, S607
        assert "test_file" in response  # noqa: S101
        subprocess.run(["adb", "-s", f"{udid}", "shell", "rm", "/sdcard/Download/test_file"])  # noqa: S603, S607  # noqa: S603, S607

    def test_pull(self, app: Shadowstep, udid: str) -> None:
        """
        Test pulling a file from the device using ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the file was successfully pulled from the device to the local machine.
        """
        app.adb.push(source=os.path.join("_test_data", "test_file"),
                     destination="sdcard/Download/test_file",
                     udid=udid)
        assert not os.path.exists("test_file")  # noqa: S101
        app.adb.pull(source="sdcard/Download/test_file",
                     destination="test_file",
                     udid=udid)
        assert os.path.exists("test_file")  # noqa: S101
        os.remove("test_file")
        subprocess.run(["adb", "-s", f"{udid}", "shell", "rm", "/sdcard/Download/test_file"])  # noqa: S603, S607

    def test_install_app(self, app: Shadowstep, udid: str) -> None:
        """
        Test installing an application on the device using ADB.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.
            udid : str. The unique device identifier for the connected device.

        Asserts:
            Asserts that the application was installed and can be found in the list of installed packages.
            And not in the list after uninstall.
        """
        app.adb.install_app(source=os.path.join("_apk", "notepad.apk"),
                            udid=udid)
        package = "com.farmerbb.notepad"
        result = subprocess.check_output(["adb", "-s", f"{udid}", "shell", "pm", "list", "packages"]).decode().strip()  # noqa: S603, S607
        assert any(line.strip().endswith(package) for line in result.splitlines())  # noqa: S101
        subprocess.run(["adb", "-s", f"{udid}", "uninstall", "com.farmerbb.notepad"])  # noqa: S603, S607
        result = subprocess.check_output(["adb", "-s", f"{udid}", "shell", "pm", "list", "packages"]).decode().strip()  # noqa: S603, S607
        assert not any(line.strip().endswith(package) for line in result.splitlines())  # noqa: S101
