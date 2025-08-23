# tests/applications/android_settings/android_settings.py
from shadowstep.shadowstep import Shadowstep

from .pages.page_connected_devices.page_connected_devices import PageConnectedDevices
from .pages.page_network_internet.page_network_internet import PageNetworkInternet
from .pages.page_settings.page_settings import PageSettings


class AndroidSettings:
    def __init__(self):
        super().__init__()
        self._package = 'com.android.settings'
        self._launchable_activity = 'com.android.settings.Settings'
        self.shadowstep: Shadowstep = Shadowstep()

        # pages
        self.page_settings = PageSettings()
        self.page_network_internet = PageNetworkInternet()
        self.page_connected_devices = PageConnectedDevices()

    def open(self):
        self.shadowstep.terminal.start_activity(package=self._package, activity=self._launchable_activity)

    def close(self):
        self.shadowstep.terminal.close_app(package=self._package)
