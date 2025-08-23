from .applications.android_settings.android_settings import AndroidSettings


class TestElementPageObject:

    def test_android_settings_demo(self, app_android_settings: AndroidSettings):
        app = app_android_settings
        app.open()
        app.shadowstep.navigator.navigate(from_page=app.page_settings,
                                          to_page=app.page_network_internet)
        assert app.page_network_internet.is_current_page()
        app.shadowstep.navigator.navigate(from_page=app.page_network_internet,
                                          to_page=app.page_settings)

        app.shadowstep.navigator.navigate(from_page=app.page_settings,
                                          to_page=app.page_connected_devices)
        assert app.page_connected_devices.is_current_page()
        app.shadowstep.navigator.navigate(from_page=app.page_connected_devices,
                                          to_page=app.page_settings)
        app.close()
