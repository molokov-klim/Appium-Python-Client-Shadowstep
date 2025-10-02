import time

import pytest

from shadowstep.shadowstep import Shadowstep, ShadowstepImage


@pytest.mark.skip(reason="ShadowstepImage needs major refactoring")
class TestImage:

    def test_image_is_visible(self, app: Shadowstep, android_settings_open_close: None,
                              connected_devices_image_path: str):
        app.save_screenshot()
        image = app.get_image(image=connected_devices_image_path)
        assert isinstance(image, ShadowstepImage)  # noqa: S101
        assert image.is_visible() is True  # noqa: S101

    def test_image_wait(self, app: Shadowstep, android_settings_open_close: None, connected_devices_image_path: str):
        image = app.get_image(image=connected_devices_image_path, timeout=3.0)
        assert image.wait() is True  # noqa: S101

    def test_image_wait_not(self, app: Shadowstep, android_settings_open_close: None,
                            connected_devices_image_path: str):
        image = app.get_image(image=connected_devices_image_path, timeout=1.0)
        assert not image.wait_not()  # noqa: S101

    def test_image_tap(self, app: Shadowstep, android_settings_open_close: None, connected_devices_image_path: str):
        image = app.get_image(image=connected_devices_image_path)
        assert image.is_visible(), "Image must be visible before tap"  # noqa: S101
        result = image.tap()
        assert isinstance(result, ShadowstepImage)  # noqa: S101
        assert app.get_element(  # noqa: S101
            {"content-desc": "Connected devices", "resource-id": "com.android.settings:id/collapsing_toolbar"}).wait()

    def test_image_tap_duration(self, app: Shadowstep, android_settings_open_close: None,
                                connected_devices_image_path: str):
        image = app.get_image(image=connected_devices_image_path)
        result = image.tap(duration=2)
        assert isinstance(result, ShadowstepImage)  # noqa: S101
        assert app.get_element(  # noqa: S101
            {"content-desc": "Connected devices", "resource-id": "com.android.settings:id/collapsing_toolbar"}).wait()

    def test_image_scroll_down(self, app: Shadowstep, android_settings_open_close: None, system_image_path: str):
        image = app.get_image(image=system_image_path, timeout=2.0)
        result = image.scroll_down(max_attempts=3)
        assert isinstance(result, ShadowstepImage)  # noqa: S101
        time.sleep(30)

    def test_image_zoom_unzoom(self, app: Shadowstep, android_settings_open_close: None,
                               connected_devices_image_path: str):
        image = app.get_image(image=connected_devices_image_path)
        assert isinstance(image.zoom(), ShadowstepImage)  # noqa: S101
        assert isinstance(image.unzoom(), ShadowstepImage)  # noqa: S101

    def test_image_drag_to_coordinates(self, app: Shadowstep, android_settings_open_close: None,
                                       connected_devices_image_path: str):
        image = app.get_image(image=connected_devices_image_path)
        result = image.drag(to=(100, 100))
        assert isinstance(result, ShadowstepImage)  # noqa: S101

    def test_image_is_contains(self, app: Shadowstep, android_settings_open_close: None,
                               connected_devices_image_path: str):
        container = app.get_image(image=connected_devices_image_path)
        # Self-contained check (should be True)
        assert container.is_contains(connected_devices_image_path) is True  # noqa: S101
