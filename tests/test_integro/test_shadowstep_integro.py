# ruff: noqa
# pyright: ignore
import tempfile
import time
from pathlib import Path

import pytest

from shadowstep.element.element import Element
from shadowstep.image.image import ShadowstepImage
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/base/test_shadowstep.py
"""


class TestShadowstep:
    """
    A class to test various functionalities of the Shadowstep application.
    """

    def test_get_element(self, app: Shadowstep, stability: None) -> None:
        """
        Test retrieving an element from the Shadowstep application.

        Args:
            app : Shadowstep. The instance of the Shadowstep application to be tested.

        Asserts:
            Asserts that the locator of the retrieved element matches the expected locator.
        """
        element = app.get_element(
            locator={"class": "android.widget.FrameLayout"},
            timeout=29,
            poll_frequency=0.7,
            ignored_exceptions=[TimeoutError],
        )
        assert element.locator == {"class": "android.widget.FrameLayout"}  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101
        assert element.driver is None  # noqa: S101
        assert element.shadowstep is not None  # noqa: S101
        assert element.timeout == 29  # noqa: S101
        assert element.poll_frequency == 0.7  # noqa: S101
        assert element.ignored_exceptions == [TimeoutError]  # noqa: S101
        element.tap()
        assert element.driver is not None  # noqa: S101

    def test_find_and_get_element(self, app: Shadowstep, android_settings_open_close: None):
        el = app.find_and_get_element({"class": "android.widget.TextView"})
        assert el.get_attribute("class") == "android.widget.TextView"  # noqa: S101

    def test_get_page_not_found(self, app: Shadowstep):
        """Test get_page() raises ValueError when page not found.

        Steps:
        1. Call get_page() with a non-existent page name.
        2. Verify that ValueError is raised with appropriate message.
        """
        # Call get_page() with non-existent page name
        with pytest.raises(ValueError) as exc_info:
            app.get_page("NonExistentPageXYZ123")

        # Verify error message contains page name
        error_message = str(exc_info.value)
        assert "NonExistentPageXYZ123" in error_message  # noqa: S101
        assert "not found" in error_message  # noqa: S101

    def test_resolve_page_not_found(self, app: Shadowstep):
        """Test resolve_page() raises ValueError when page not found.

        Steps:
        1. Call resolve_page() with a non-existent page name.
        2. Verify that ValueError is raised with appropriate message.
        """
        # Call resolve_page() with non-existent page name
        with pytest.raises(ValueError) as exc_info:
            app.resolve_page("NonExistentResolvePageXYZ123")

        # Verify error message contains page name
        error_message = str(exc_info.value)
        assert "NonExistentResolvePageXYZ123" in error_message  # noqa: S101
        assert "not found" in error_message  # noqa: S101

    def test_get_elements_multiple_elements(
        self, app: Shadowstep, android_settings_open_close: None
    ):
        """Test get_elements() returns multiple elements matching locator.

        Steps:
        1. Call get_elements() with a locator that matches multiple elements.
        2. Verify that a list of Element instances is returned.
        3. Verify that all elements are properly initialized with shadowstep reference.
        4. Verify that timeout and poll_frequency are set correctly.
        """
        # Step 1: Call get_elements() with a locator that matches multiple elements
        locator = ("xpath", "//android.widget.TextView")
        timeout = 10
        poll_frequency = 0.5

        elements = app.get_elements(locator=locator, timeout=timeout, poll_frequency=poll_frequency)

        # Step 2: Verify that a list of Element instances is returned
        assert isinstance(elements, list)  # noqa: S101
        assert len(elements) > 0  # noqa: S101

        # Step 3: Verify that all elements are properly initialized
        for element in elements:
            assert isinstance(element, Element)  # noqa: S101
            assert element.shadowstep is app  # noqa: S101
            assert element.timeout == timeout  # noqa: S101
            assert element.poll_frequency == poll_frequency  # noqa: S101

    def test_is_text_visible_success(self, app: Shadowstep, android_settings_open_close: None):
        """Test is_text_visible() returns True when text element is visible.

        Steps:
        1. Call is_text_visible() with text that exists on Settings screen.
        2. Verify that True is returned.
        """
        # Using "Settings" text which should be visible on Android Settings page
        result = app.is_text_visible("Settings")

        assert result is True  # noqa: S101

    def test_is_text_visible_not_found(self, app: Shadowstep):
        """Test is_text_visible() returns False when text element is not found.

        Steps:
        1. Call is_text_visible() with non-existent text.
        2. Verify that False is returned.
        3. Verify that no exceptions are raised.
        """
        # Call with non-existent text
        result = app.is_text_visible("NonExistentText12345XYZ")

        # Verify False is returned and no exception was raised
        assert result is False  # noqa: S101

    def test_tap_coordinates(self, app: Shadowstep, android_settings_open_close: None):
        """Test tap() performs tap gesture at specified coordinates.

        Steps:
        1. Find an element on the Settings screen.
        2. Get its coordinates.
        3. Call tap() at those coordinates.
        4. Verify the tap action completes without errors.
        """
        # Find a visible element
        element = app.get_element({"text": "Settings"})

        # Get element location
        location = element.location
        x = location["x"] + 10
        y = location["y"] + 10

        # Perform tap gesture
        result = app.tap(x=x, y=y, duration=100)

        # Verify tap returns self for chaining
        assert result is app  # noqa: S101

    def test_click_coordinates(self, app: Shadowstep, android_settings_open_close: None):
        """Test click() performs click gesture at specified coordinates.

        Steps:
        1. Find an element on the Settings screen.
        2. Get its coordinates.
        3. Call click() at those coordinates.
        4. Verify the click action completes without errors.
        """
        # Find a visible element
        element = app.get_element({"text": "Settings"})

        # Get element location
        location = element.location
        x = location["x"] + 10
        y = location["y"] + 10

        # Perform click gesture
        result = app.click(x=x, y=y)

        # Verify click returns self for chaining
        assert result is app  # noqa: S101

    def test_double_click_coordinates(self, app: Shadowstep, android_settings_open_close: None):
        """Test double_click() performs double click gesture at specified coordinates.

        Steps:
        1. Find an element on the Settings screen.
        2. Get its coordinates.
        3. Call double_click() at those coordinates.
        4. Verify the double click action completes without errors.
        """
        # Find a visible element
        element = app.get_element({"text": "Settings"})

        # Get element location
        location = element.location
        x = location["x"] + 10
        y = location["y"] + 10

        # Perform double click gesture
        result = app.double_click(x=x, y=y)

        # Verify double_click returns self for chaining
        assert result is app  # noqa: S101

    def test_long_click_coordinates(self, app: Shadowstep, android_settings_open_close: None):
        """Test long_click() performs long click gesture at specified coordinates.

        Steps:
        1. Find an element on the Settings screen.
        2. Get its coordinates.
        3. Call long_click() at those coordinates with duration.
        4. Verify the long click action completes without errors.
        """
        # Find a visible element
        element = app.get_element({"text": "Settings"})

        # Get element location
        location = element.location
        x = location["x"] + 10
        y = location["y"] + 10

        # Perform long click gesture
        result = app.long_click(x=x, y=y, duration=1000)

        # Verify long_click returns self for chaining
        assert result is app  # noqa: S101

    def test_swipe_gesture(self, app: Shadowstep, android_settings_open_close: None):
        """Test swipe() performs swipe gesture in specified area.

        Steps:
        1. Get screen dimensions.
        2. Call swipe() with valid parameters.
        3. Verify the swipe action completes without errors.
        """
        # Get window size
        driver = app.driver
        size = driver.get_window_size()
        width = size["width"]
        height = size["height"]

        # Perform swipe gesture
        result = app.swipe(
            left=width // 4,
            top=height // 2,
            width=width // 2,
            height=height // 4,
            direction="up",
            percent=0.5,
            speed=5000,
        )

        # Verify swipe returns self for chaining
        assert result is app  # noqa: S101

    def test_swipe_right_to_left(self, app: Shadowstep, android_settings_open_close: None):
        """Test swipe_right_to_left() performs horizontal swipe from right to left.

        Steps:
        1. Call swipe_right_to_left().
        2. Verify the swipe action completes without errors.
        """
        # Perform swipe gesture
        result = app.swipe_right_to_left()

        # Verify swipe_right_to_left returns self for chaining
        assert result is app  # noqa: S101

    def test_swipe_left_to_right(self, app: Shadowstep, android_settings_open_close: None):
        """Test swipe_left_to_right() performs horizontal swipe from left to right.

        Steps:
        1. Call swipe_left_to_right().
        2. Verify the swipe action completes without errors.
        """
        # Perform swipe gesture
        result = app.swipe_left_to_right()

        # Verify swipe_left_to_right returns self for chaining
        assert result is app  # noqa: S101

    def test_swipe_top_to_bottom(self, app: Shadowstep, android_settings_open_close: None):
        """Test swipe_top_to_bottom() performs vertical swipe from top to bottom.

        Steps:
        1. Call swipe_top_to_bottom().
        2. Verify the swipe action completes without errors.
        """
        # Perform swipe gesture
        result = app.swipe_top_to_bottom(percent=0.5, speed=5000)

        # Verify swipe_top_to_bottom returns self for chaining
        assert result is app  # noqa: S101

    def test_swipe_bottom_to_top(self, app: Shadowstep, android_settings_open_close: None):
        """Test swipe_bottom_to_top() performs vertical swipe from bottom to top.

        Steps:
        1. Call swipe_bottom_to_top().
        2. Verify the swipe action completes without errors.
        """
        # Perform swipe gesture
        result = app.swipe_bottom_to_top(percent=0.5, speed=5000)

        # Verify swipe_bottom_to_top returns self for chaining
        assert result is app  # noqa: S101

    def test_scroll_gesture(self, app: Shadowstep, android_settings_open_close: None):
        """Test scroll() performs scroll gesture in specified area.

        Steps:
        1. Get screen dimensions.
        2. Call scroll() with valid parameters.
        3. Verify the scroll action completes without errors.
        """
        # Get window size
        driver = app.driver
        size = driver.get_window_size()
        width = size["width"]
        height = size["height"]

        # Perform scroll gesture
        result = app.scroll(
            left=width // 4,
            top=height // 4,
            width=width // 2,
            height=height // 2,
            direction="down",
            percent=0.5,
            speed=5000,
        )

        # Verify scroll returns self for chaining
        assert result is app  # noqa: S101

    def test_drag_gesture(self, app: Shadowstep, android_settings_open_close: None):
        """Test drag() performs drag gesture from one point to another.

        Steps:
        1. Get screen dimensions.
        2. Call drag() with start and end coordinates.
        3. Verify the drag action completes without errors.
        """
        # Get window size
        driver = app.driver
        size = driver.get_window_size()
        width = size["width"]
        height = size["height"]

        # Perform drag gesture
        result = app.drag(
            start_x=width // 2,
            start_y=height // 2,
            end_x=width // 2 + 100,
            end_y=height // 2 + 100,
            speed=2500,
        )

        # Verify drag returns self for chaining
        assert result is app  # noqa: S101

    def test_fling_gesture(self, app: Shadowstep, android_settings_open_close: None):
        """Test fling() performs fling gesture in specified area.

        Steps:
        1. Get screen dimensions.
        2. Call fling() with valid parameters.
        3. Verify the fling action completes without errors.
        """
        # Get window size
        driver = app.driver
        size = driver.get_window_size()
        width = size["width"]
        height = size["height"]

        # Perform fling gesture
        result = app.fling(
            left=width // 4,
            top=height // 4,
            width=width // 2,
            height=height // 2,
            direction="up",
            speed=7500,
        )

        # Verify fling returns self for chaining
        assert result is app  # noqa: S101

    def test_pinch_open_gesture(self, app: Shadowstep, android_settings_open_close: None):
        """Test pinch_open() performs pinch-open gesture in specified area.

        Steps:
        1. Get screen dimensions.
        2. Call pinch_open() with valid parameters.
        3. Verify the pinch-open action completes without errors.
        """
        # Get window size
        driver = app.driver
        size = driver.get_window_size()
        width = size["width"]
        height = size["height"]

        # Perform pinch-open gesture
        result = app.pinch_open(
            left=width // 4,
            top=height // 4,
            width=width // 2,
            height=height // 2,
            percent=0.5,
            speed=2500,
        )

        # Verify pinch_open returns self for chaining
        assert result is app  # noqa: S101

    def test_pinch_close_gesture(self, app: Shadowstep, android_settings_open_close: None):
        """Test pinch_close() performs pinch-close gesture in specified area.

        Steps:
        1. Get screen dimensions.
        2. Call pinch_close() with valid parameters.
        3. Verify the pinch-close action completes without errors.
        """
        # Get window size
        driver = app.driver
        size = driver.get_window_size()
        width = size["width"]
        height = size["height"]

        # Perform pinch-close gesture
        result = app.pinch_close(
            left=width // 4,
            top=height // 4,
            width=width // 2,
            height=height // 2,
            percent=0.5,
            speed=2500,
        )

        # Verify pinch_close returns self for chaining
        assert result is app  # noqa: S101

    def test_get_screenshot(self, app: Shadowstep, android_settings_open_close: None):
        """Test get_screenshot() returns screenshot as bytes.

        Steps:
        1. Call get_screenshot().
        2. Verify that bytes are returned.
        3. Verify that the data is not empty.
        """
        # Get screenshot
        screenshot = app.get_screenshot()

        # Verify screenshot is bytes
        assert isinstance(screenshot, bytes)  # noqa: S101
        assert len(screenshot) > 0  # noqa: S101

    def test_save_screenshot(self, app: Shadowstep, android_settings_open_close: None):
        """Test save_screenshot() saves screenshot to file.

        Steps:
        1. Call save_screenshot() with path and filename.
        2. Verify that the file is created.
        3. Clean up the file.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = "test_screenshot.png"

            # Save screenshot
            result = app.save_screenshot(path=tmpdir, filename=filename)

            # Verify result is True
            assert result is True  # noqa: S101

            # Verify file exists
            file_path = Path(tmpdir) / filename
            assert file_path.exists()  # noqa: S101
            assert file_path.stat().st_size > 0  # noqa: S101

    def test_save_source(self, app: Shadowstep, android_settings_open_close: None):
        """Test save_source() saves page source to file.

        Steps:
        1. Call save_source() with path and filename.
        2. Verify that the file is created.
        3. Clean up the file.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = "test_source.xml"

            # Save source
            result = app.save_source(path=tmpdir, filename=filename)

            # Verify result is True
            assert result is True  # noqa: S101

            # Verify file exists
            file_path = Path(tmpdir) / filename
            assert file_path.exists()  # noqa: S101
            assert file_path.stat().st_size > 0  # noqa: S101

    def test_get_instance(self, app: Shadowstep):
        """Test get_instance() returns the singleton instance.

        Steps:
        1. Call get_instance().
        2. Verify that it returns the same instance as app.
        """
        # Get instance
        instance = Shadowstep.get_instance()

        # Verify it's the same instance
        assert instance is app  # noqa: S101

    def test_start_stop_logcat(self, app: Shadowstep, cleanup_log: None):
        """Test start_logcat() and stop_logcat() control logcat recording.

        Steps:
        1. Call start_logcat() with filename.
        2. Call stop_logcat().
        3. Verify no exceptions are raised.
        """
        # Start logcat
        app.start_logcat(filename="logcat_test.log")

        # Wait a bit for some logs
        time.sleep(2)

        # Stop logcat
        app.stop_logcat()

        # No exception means success

    def test_get_image(self, app: Shadowstep, connected_devices_image_path: str):
        """Test get_image() returns ShadowstepImage wrapper.

        Steps:
        1. Call get_image() with image path.
        2. Verify that ShadowstepImage instance is returned.
        3. Verify that instance has correct attributes.
        """
        # Get image
        image = app.get_image(image=connected_devices_image_path, threshold=0.5, timeout=5.0)

        # Verify image is ShadowstepImage instance
        assert isinstance(image, ShadowstepImage)  # noqa: S101
        assert image._base is app  # noqa: S101

    def test_get_images(self, app: Shadowstep, connected_devices_image_path: str):
        """Test get_images() returns list of ShadowstepImage wrappers.

        Steps:
        1. Call get_images() with image path.
        2. Verify that list is returned.
        3. Verify that list contains ShadowstepImage instances.
        """
        # Get images
        images = app.get_images(image=connected_devices_image_path, threshold=0.5, timeout=5.0)

        # Verify images is a list
        assert isinstance(images, list)  # noqa: S101
        assert len(images) > 0  # noqa: S101

        # Verify all elements are ShadowstepImage instances
        for image in images:
            assert isinstance(image, ShadowstepImage)  # noqa: S101
            assert image._base is app  # noqa: S101

    def test_push_file(self, app: Shadowstep):
        """Test push() pushes file to device.

        Steps:
        1. Create a temporary file.
        2. Call push() to upload file to device.
        3. Verify the operation completes without errors.
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmpfile:
            tmpfile.write("test content")
            tmpfile_path = tmpfile.name

        try:
            # Push file to device
            result = app.push(
                source_file_path=tmpfile_path, destination_file_path="/sdcard/test_push_file.txt"
            )

            # Verify push returns self for chaining
            assert result is app  # noqa: S101
        finally:
            # Clean up temporary file
            Path(tmpfile_path).unlink(missing_ok=True)

    def test_start_stop_recording_screen(self, app: Shadowstep, android_settings_open_close: None):
        """Test start_recording_screen() and stop_recording_screen() control screen recording.

        Steps:
        1. Call start_recording_screen().
        2. Wait for a short time.
        3. Call stop_recording_screen().
        4. Verify that video bytes are returned.
        """
        # Start recording
        app.start_recording_screen()

        # Record for 3 seconds
        time.sleep(3)

        # Stop recording
        video = app.stop_recording_screen()

        # Verify video is bytes
        assert isinstance(video, bytes)  # noqa: S101
        assert len(video) > 0  # noqa: S101
