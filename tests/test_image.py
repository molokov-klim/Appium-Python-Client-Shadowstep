import time

import pytest
from shadowstep.shadowstep import ShadowstepImage, Shadowstep


def test_image_is_visible(app: Shadowstep, android_settings, connected_devices_image_path):
    app.save_screenshot()
    image = app.get_image(image=connected_devices_image_path)
    assert isinstance(image, ShadowstepImage)
    assert image.is_visible() is True


def test_image_wait(app: Shadowstep, android_settings, connected_devices_image_path):
    image = app.get_image(image=connected_devices_image_path, timeout=3.0)
    assert image.wait() is True


def test_image_wait_not(app: Shadowstep, android_settings, connected_devices_image_path):
    image = app.get_image(image=connected_devices_image_path, timeout=1.0)
    assert not image.wait_not()


def test_image_tap(app: Shadowstep, android_settings, connected_devices_image_path):
    image = app.get_image(image=connected_devices_image_path)
    assert image.is_visible(), "Image must be visible before tap"
    result = image.tap()
    assert isinstance(result, ShadowstepImage)
    assert app.get_element(
        {'content-desc': 'Connected devices', 'resource-id': 'com.android.settings:id/collapsing_toolbar'}).wait()


def test_image_tap_duration(app: Shadowstep, android_settings, connected_devices_image_path):
    image = app.get_image(image=connected_devices_image_path)
    result = image.tap(duration=1.5)
    assert isinstance(result, ShadowstepImage)
    assert app.get_element(
        {'content-desc': 'Connected devices', 'resource-id': 'com.android.settings:id/collapsing_toolbar'}).wait()


def test_image_scroll_down(app: Shadowstep, android_settings, system_image_path):
    image = app.get_image(image=system_image_path, timeout=2.0)
    result = image.scroll_down(max_attempts=3)
    assert isinstance(result, ShadowstepImage)
    time.sleep(30)


def test_image_zoom_unzoom(app: Shadowstep, android_settings, connected_devices_image_path):
    image = app.get_image(image=connected_devices_image_path)
    assert isinstance(image.zoom(), ShadowstepImage)
    assert isinstance(image.unzoom(), ShadowstepImage)


def test_image_drag_to_coordinates(app: Shadowstep, android_settings, connected_devices_image_path):
    image = app.get_image(image=connected_devices_image_path)
    result = image.drag(to=(100, 100))
    assert isinstance(result, ShadowstepImage)


def test_image_is_contains(app: Shadowstep, android_settings, connected_devices_image_path):
    container = app.get_image(image=connected_devices_image_path)
    # Self-contained check (should be True)
    assert container.is_contains(connected_devices_image_path) is True
