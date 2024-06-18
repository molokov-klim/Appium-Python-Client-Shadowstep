import os
import subprocess
import time


class TestShadowstepBase:

    def test_connect(self, app):
        assert app.driver is not None


class TestShadowstep:

    def test_get_element(self, app):
        element = app.get_element(locator={'content-desc': 'Phone'})
        assert element.locator == {'content-desc': 'Phone'}


class TestElement:

    def test_tap(self, app):
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response


class TestAdb:

    def test_get_devices(self, app, udid):
        assert udid in app.adb.get_devices()

    def test_get_device_model(self, app, udid):
        assert "Pixel" in app.adb.get_device_model()

    def test_push(self, app, udid):
        app.adb.push(source=os.path.join('test_data', 'test_file'),
                     destination=os.path.join('sdcard/Download/test_file'),
                     udid=udid)
        response = str(subprocess.check_output(f'adb -s {udid} shell "ls sdcard/Download"'))
        assert 'test_file' in response
        subprocess.run(f"adb -s {udid} shell rm /sdcard/Download/test_file")

    def test_pull(self, app, udid):
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

    def test_install_app(self, app, udid):
        app.adb.install_app(source=os.path.join('apk', 'notepad.apk'),
                            udid=udid)
        print("++++++++++++++++++++++")
        print("++++++++++++++++++++++")
        package = "com.farmerbb.notepad"
        result = subprocess.check_output(f"adb -s {udid} shell pm list packages").decode().strip()
        assert any([line.strip().endswith(package) for line in result.splitlines()])
        subprocess.run(f"adb -s {udid} uninstall com.farmerbb.notepad")
        time.sleep(55)
        assert not any([line.strip().endswith(package) for line in result.splitlines()])
