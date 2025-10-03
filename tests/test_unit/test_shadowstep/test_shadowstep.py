import base64
from unittest.mock import patch, Mock, mock_open

import pytest

from shadowstep.shadowstep import Shadowstep
from shadowstep.shadowstep_base import WebDriverSingleton
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_quality.py
"""

shadowstep = Shadowstep()


class TestShadowstepUnit:
    @pytest.mark.unit
    def test_singleton_behavior(self):
        """Test that Shadowstep implements singleton pattern correctly."""
        # Clear any existing instances
        Shadowstep._instance = None

        # Create first instance
        instance1 = Shadowstep()
        assert instance1 is not None

        # Create second instance - should return the same instance
        instance2 = Shadowstep()
        assert instance1 is instance2

    @pytest.mark.unit
    def test_get_instance_class_method(self):
        """Test get_instance class method returns singleton instance."""
        # Clear any existing instances
        Shadowstep._instance = None

        instance1 = Shadowstep.get_instance()
        instance2 = Shadowstep.get_instance()

        assert instance1 is instance2
        assert isinstance(instance1, Shadowstep)

    @pytest.mark.unit
    def test_initialization_with_existing_instance(self):
        """Test initialization when instance already exists."""
        # Create an instance first
        instance1 = Shadowstep()
        instance1._initialized = True

        # Mock the parent __init__ to avoid actual initialization
        with patch("shadowstep.shadowstep.ShadowstepBase.__init__"):
            instance2 = Shadowstep()
            assert instance1 is instance2

    @pytest.mark.unit
    def test_auto_discover_pages_with_nonexistent_path(self):
        """Test _auto_discover_pages with nonexistent path."""

        # Mock sys.path to include a nonexistent path
        with patch("sys.path", ["/nonexistent/path"]):
            with patch("pathlib.Path.exists", return_value=False):
                shadowstep._auto_discover_pages() # type: ignore
                # Should not raise exception, just skip the path

    @pytest.mark.unit
    def test_auto_discover_pages_with_file_path(self):
        """Test _auto_discover_pages with file path (not directory)."""

        # Mock sys.path to include a file path
        with patch("sys.path", ["/some/file.txt"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=False):
                    shadowstep._auto_discover_pages() # type: ignore
                    # Should not raise exception, just skip the path

    @pytest.mark.unit
    def test_auto_discover_pages_with_ignored_dir(self):
        """Test _auto_discover_pages with ignored directory name."""

        # Mock sys.path to include an ignored directory
        with patch("sys.path", ["/some/__pycache__"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=True):
                    with patch("pathlib.Path.name", "__pycache__"):
                        shadowstep._auto_discover_pages() # type: ignore
                        # Should not raise exception, just skip the path

    @pytest.mark.unit
    def test_auto_discover_pages_with_nonexistent_path_condition(self):
        """Test _auto_discover_pages with nonexistent path condition (line 118)."""

        # Mock sys.path to include a path that doesn't exist
        with patch("sys.path", ["/nonexistent/path"]):
            with patch("pathlib.Path.exists", return_value=False):
                shadowstep._auto_discover_pages() # type: ignore
                # Should not raise exception, just skip the path

    @pytest.mark.unit
    def test_auto_discover_pages_with_file_path_condition(self):
        """Test _auto_discover_pages with file path condition (line 118)."""

        # Mock sys.path to include a file path (not directory)
        with patch("sys.path", ["/some/file.txt"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=False):
                    shadowstep._auto_discover_pages() # type: ignore
                    # Should not raise exception, just skip the path

    @pytest.mark.unit
    def test_auto_discover_pages_with_ignored_dir_condition(self):
        """Test _auto_discover_pages with ignored directory condition (line 124)."""

        # Mock sys.path to include a valid path
        with patch("sys.path", ["/valid/path"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=True):
                    with patch("pathlib.Path.name", "valid"):
                        with patch("os.walk", return_value=[("/valid/path", [], ["page_test.py"])]):
                            with patch(
                                    "pathlib.Path.relative_to", return_value=Mock(parts=["page_test"])
                            ):
                                with patch(
                                        "pathlib.Path.with_suffix",
                                        return_value=Mock(parts=["page_test"]),
                                ):
                                    with patch("importlib.import_module", return_value=Mock()):
                                        with patch.object(shadowstep, "_register_pages_from_module"):
                                            # Mock a directory that should be ignored
                                            with patch(
                                                    "pathlib.Path",
                                                    side_effect=lambda x: Mock(name="__pycache__"), # type: ignore
                                            ):
                                                shadowstep._auto_discover_pages() # type: ignore
                                                # Should not raise exception, just skip the path

    @pytest.mark.unit
    def test_auto_discover_pages_with_import_error(self):
        """Test _auto_discover_pages with import error."""

        # Mock sys.path to include a valid path
        with patch("sys.path", ["/valid/path"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=True):
                    with patch("pathlib.Path.name", "valid"):
                        with patch("os.walk", return_value=[("/valid/path", [], ["page_test.py"])]):
                            with patch(
                                    "pathlib.Path.relative_to", return_value=Mock(parts=["page_test"])
                            ):
                                with patch(
                                        "pathlib.Path.with_suffix",
                                        return_value=Mock(parts=["page_test"]),
                                ):
                                    with patch(
                                            "importlib.import_module",
                                            side_effect=ImportError("Module not found"),
                                    ):
                                        with patch.object(shadowstep, "logger") as mock_logger:
                                            # Reset the discovery flag to allow re-discovery
                                            shadowstep._pages_discovered = False    # type: ignore
                                            shadowstep._auto_discover_pages() # type: ignore
                                            # Should log warning about import error
                                            assert mock_logger.warning.call_count >= 1

    @pytest.mark.unit
    def test_register_pages_from_module_with_non_page_class(self):
        """Test _register_pages_from_module with class that doesn't start with 'Page'."""

        from shadowstep.page_base import PageBaseShadowstep

        # Create a mock module with a class that doesn't start with 'Page'
        mock_module = Mock()
        mock_module.__name__ = "test_module"

        # Create a real class that inherits from PageBaseShadowstep but doesn't start with 'Page'
        class NonPageClass(PageBaseShadowstep):
            @property
            def edges(self):
                return {}

        # Mock inspect.getmembers to return our mock class
        with patch("inspect.getmembers", return_value=[("NonPageClass", NonPageClass)]):
            with patch("inspect.isclass", return_value=True):
                shadowstep._register_pages_from_module(mock_module)

                # Verify the class was NOT registered because it doesn't start with 'Page'
                assert "NonPageClass" not in shadowstep.pages

    @pytest.mark.unit
    def test_register_pages_from_module_success(self):
        """Test _register_pages_from_module with successful registration."""

        from shadowstep.page_base import PageBaseShadowstep

        # Create a mock module with a page class
        mock_module = Mock()
        mock_module.__name__ = "test_module"

        # Create a real class that inherits from PageBaseShadowstep
        class MockPageClass(PageBaseShadowstep):
            @property
            def edges(self):
                return {"next_page": lambda: None}

        # Mock inspect.getmembers to return our mock class
        with patch("inspect.getmembers", return_value=[("PageTest", MockPageClass)]):
            with patch("inspect.isclass", return_value=True):
                shadowstep._register_pages_from_module(mock_module)

                # Verify the page was registered
                assert "PageTest" in shadowstep.pages

    @pytest.mark.unit
    def test_register_pages_from_module_exception(self):
        """Test _register_pages_from_module with exception."""

        mock_module = Mock()
        mock_module.__name__ = "test_module"

        with patch("inspect.getmembers", side_effect=Exception("Test error")):
            # Should not raise exception, just log warning
            shadowstep._register_pages_from_module(mock_module)

    @pytest.mark.unit
    def test_list_registered_pages(self):
        """Test list_registered_pages method."""

        # Add some mock pages
        mock_page1 = Mock()
        mock_page1.__name__ = "Page1"
        mock_page1.__module__ = "test_module"
        mock_page2 = Mock()
        mock_page2.__name__ = "Page2"
        mock_page2.__module__ = "test_module"
        shadowstep.pages = {"Page1": mock_page1, "Page2": mock_page2}

        with patch.object(shadowstep, "logger") as mock_logger:
            shadowstep.list_registered_pages()

            # Verify logging was called
            assert mock_logger.info.call_count >= 1

    @pytest.mark.unit
    def test_get_page_success(self):
        """Test get_page method with existing page."""

        mock_page_class = Mock()
        mock_page_instance = Mock()
        mock_page_class.return_value = mock_page_instance
        shadowstep.pages = {"TestPage": mock_page_class}

        result = shadowstep.get_page("TestPage")

        assert result is mock_page_instance
        mock_page_class.assert_called_once()

    @pytest.mark.unit
    def test_get_page_not_found(self):
        """Test get_page method with non-existing page."""

        shadowstep.pages = {}

        with pytest.raises(
                ValueError, match="Page 'NonExistentPage' not found in registered pages"
        ):
            shadowstep.get_page("NonExistentPage")

    @pytest.mark.unit
    def test_resolve_page_success(self):
        """Test resolve_page method with existing page."""

        mock_page_class = Mock()
        mock_page_instance = Mock()
        mock_page_class.return_value = mock_page_instance
        shadowstep.pages = {"TestPage": mock_page_class}

        result = shadowstep.resolve_page("TestPage")

        assert result is mock_page_instance
        mock_page_class.assert_called_once()

    @pytest.mark.unit
    def test_resolve_page_not_found(self):
        """Test resolve_page method with non-existing page."""

        shadowstep.pages = {}

        with pytest.raises(ValueError, match="Page 'NonExistentPage' not found"):
            shadowstep.resolve_page("NonExistentPage")

    @pytest.mark.unit
    def test_get_elements(self):
        """Test get_elements method."""

        mock_element = Mock()
        mock_elements = [Mock()()]
        mock_element.get_elements.return_value = mock_elements

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = shadowstep.get_elements({"class": "test"})

            assert result is mock_elements
            mock_element.get_elements.assert_called_once()

    @pytest.mark.unit
    def test_get_image(self):
        """Test get_image method."""

        mock_image = Mock()

        with patch("shadowstep.shadowstep.ShadowstepImage", return_value=mock_image):
            result = shadowstep.get_image("test_image.png")

            assert result is mock_image

    @pytest.mark.unit
    def test_get_images(self):
        """Test get_images method."""

        mock_image = Mock()

        with patch("shadowstep.shadowstep.ShadowstepImage", return_value=mock_image):
            result = shadowstep.get_images("test_image.png")

            assert result == [mock_image]

    @pytest.mark.unit
    def test_schedule_action_not_implemented(self):
        """Test schedule_action method raises NotImplementedError."""

        with pytest.raises(NotImplementedError):
            shadowstep.schedule_action("test", [])

    @pytest.mark.unit
    def test_get_action_history_not_implemented(self):
        """Test get_action_history method raises NotImplementedError."""

        with pytest.raises(NotImplementedError):
            shadowstep.get_action_history("test")

    @pytest.mark.unit
    def test_unschedule_action_not_implemented(self):
        """Test unschedule_action method raises NotImplementedError."""

        with pytest.raises(NotImplementedError):
            shadowstep.unschedule_action("test")

    @pytest.mark.unit
    def test_start_logcat_with_filters(self):
        """Test start_logcat method with filters."""

        with patch.object(shadowstep._logcat, "start") as mock_start:
            filters = ["test_filter"]
            shadowstep.start_logcat("test.log", port=4723, filters=filters)

            assert shadowstep._logcat.filters == filters
            mock_start.assert_called_once_with("test.log", 4723)

    @pytest.mark.unit
    def test_start_logcat_without_filters(self):
        """Test start_logcat method without filters."""

        with patch.object(shadowstep._logcat, "start") as mock_start:
            shadowstep.start_logcat("test.log")

            mock_start.assert_called_once_with("test.log", None)

    @pytest.mark.unit
    def test_stop_logcat(self):
        """Test stop_logcat method."""

        with patch.object(shadowstep._logcat, "stop") as mock_stop:
            shadowstep.stop_logcat()

            mock_stop.assert_called_once()

    @pytest.mark.unit
    def test_find_and_get_element_success(self):
        """Test find_and_get_element method with successful find."""

        mock_scrollable = Mock()
        mock_element = Mock()
        mock_scrollable.scroll_to_element.return_value = mock_element

        with patch.object(shadowstep, "get_elements", return_value=[mock_scrollable]):
            result = shadowstep.find_and_get_element({"class": "test"})

            assert result is mock_element
            mock_scrollable.scroll_to_element.assert_called_once()

    @pytest.mark.unit
    def test_find_and_get_element_not_found(self):
        """Test find_and_get_element method when element not found."""

        with patch.object(shadowstep, "get_elements", return_value=[]):
            with pytest.raises(Exception):  # ShadowstepException
                shadowstep.find_and_get_element({"class": "test"})

    @pytest.mark.unit
    def test_find_and_get_element_scroll_failure(self):
        """Test find_and_get_element method when scroll fails."""

        mock_scrollable = Mock()
        mock_scrollable.scroll_to_element.side_effect = Exception("Scroll failed")

        with patch.object(shadowstep, "get_elements", return_value=[mock_scrollable]):
            with pytest.raises(Exception):  # ShadowstepException
                shadowstep.find_and_get_element({"class": "test"})

    @pytest.mark.unit
    def test_is_text_visible_success(self):
        """Test is_text_visible method with visible text."""

        mock_element = Mock()
        mock_element.is_visible.return_value = True

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = shadowstep.is_text_visible("test text")

            assert result is True
            mock_element.is_visible.assert_called_once()

    @pytest.mark.unit
    def test_is_text_visible_not_visible(self):
        """Test is_text_visible method with not visible text."""

        mock_element = Mock()
        mock_element.is_visible.return_value = False

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = shadowstep.is_text_visible("test text")

            assert result is False

    @pytest.mark.unit
    def test_is_text_visible_exception(self):
        """Test is_text_visible method with exception."""

        with patch("shadowstep.shadowstep.Element", side_effect=Exception("Test error")):
            result = shadowstep.is_text_visible("test text")

            assert result is False

    @pytest.mark.unit
    def test_scroll_invalid_direction(self):
        """Test scroll method with invalid direction."""

        with pytest.raises(ShadowstepException, match="scroll failed after 3 attempts"):
            shadowstep.scroll(0, 0, 100, 100, "invalid", 0.5, 1000)

    @pytest.mark.unit
    def test_scroll_invalid_percent(self):
        """Test scroll method with invalid percent."""

        with pytest.raises(ShadowstepException, match="scroll failed after 3 attempts"):
            shadowstep.scroll(0, 0, 100, 100, "up", 1.5, 1000)

    @pytest.mark.unit
    def test_scroll_negative_speed(self):
        """Test scroll method with negative speed."""

        with pytest.raises(ShadowstepException, match="scroll failed after 3 attempts"):
            shadowstep.scroll(0, 0, 100, 100, "up", 0.5, -1)

    @pytest.mark.unit
    def test_scroll_success(self):
        """Test scroll method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.scroll(100, 200, 300, 400, "up", 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: scrollGesture",
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "direction": "up",
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_long_click_negative_duration(self):
        """Test long_click method with negative duration."""

        with pytest.raises(ShadowstepException, match="long_click failed after 3 attempts"):
            shadowstep.long_click(100, 100, -1)

    @pytest.mark.unit
    def test_long_click_success(self):
        """Test long_click method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.long_click(100, 200, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: longClickGesture", {"x": 100, "y": 200, "duration": 1000}
                    )

    @pytest.mark.unit
    def test_double_click_success(self):
        """Test double_click method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.double_click(100, 200)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: doubleClickGesture", {"x": 100, "y": 200}
                    )

    @pytest.mark.unit
    def test_click_success(self):
        """Test click method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.click(100, 200)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: clickGesture", {"x": 100, "y": 200}
                    )

    @pytest.mark.unit
    def test_drag_success(self):
        """Test drag method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.drag(100, 200, 300, 400, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: dragGesture",
                        {
                            "startX": 100,
                            "startY": 200,
                            "endX": 300,
                            "endY": 400,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_fling_success(self):
        """Test fling method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.fling(100, 200, 300, 400, "up", 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: flingGesture",
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "direction": "up",
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_pinch_open_success(self):
        """Test pinch_open method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.pinch_open(100, 200, 300, 400, 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: pinchOpenGesture",
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_pinch_close_success(self):
        """Test pinch_close method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.pinch_close(100, 200, 300, 400, 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: pinchCloseGesture",
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_swipe_success(self):
        """Test swipe method with valid parameters."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "_execute") as mock_execute:
                    result = shadowstep.swipe(100, 200, 300, 400, "up", 0.5, 1000)

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: swipeGesture",
                        {
                            "left": 100,
                            "top": 200,
                            "width": 300,
                            "height": 400,
                            "direction": "up",
                            "percent": 0.5,
                            "speed": 1000,
                        },
                    )

    @pytest.mark.unit
    def test_swipe_right_to_left_success(self):
        """Test swipe_right_to_left method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_right_to_left()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=0,
                        top=1000,  # height // 2
                        width=1000,
                        height=666,  # height // 3
                        direction="left",
                        percent=1.0,
                        speed=1000,
                    )

    @pytest.mark.unit
    def test_swipe_left_to_right_success(self):
        """Test swipe_left_to_right method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_left_to_right()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=0,
                        top=1000,  # height // 2
                        width=1000,
                        height=666,  # height // 3
                        direction="right",
                        percent=1.0,
                        speed=1000,
                    )

    @pytest.mark.unit
    def test_swipe_top_to_bottom_success(self):
        """Test swipe_top_to_bottom method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_top_to_bottom()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=500,  # width // 2
                        top=0,
                        width=333,  # width // 3
                        height=2000,
                        direction="down",
                        percent=1.0,
                        speed=5000,
                    )

    @pytest.mark.unit
    def test_swipe_bottom_to_top_success(self):
        """Test swipe_bottom_to_top method with valid parameters."""

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch.object(shadowstep, "swipe", return_value=shadowstep) as mock_swipe:
                    result = shadowstep.swipe_bottom_to_top()

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify swipe was called with correct parameters
                    mock_swipe.assert_called_once_with(
                        left=500,  # width // 2
                        top=0,
                        width=333,  # width // 3
                        height=2000,
                        direction="up",
                        percent=1.0,
                        speed=5000,
                    )

    @pytest.mark.unit
    def test_get_screenshot_success(self):
        """Test get_screenshot method with valid driver."""

        mock_driver = Mock()
        mock_driver.get_screenshot_as_base64.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.get_screenshot()

                # Verify the method returns decoded screenshot
                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    @pytest.mark.unit
    def test_save_source_success(self):
        """Test save_source method with valid driver."""

        mock_driver = Mock()
        mock_driver.page_source = "test page source"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open()) as mock_file:
                    result = shadowstep.save_source("/test/path", "test.xml")

                    # Verify the method returns True
                    assert result is True

                    # Verify file was opened and written to
                    mock_file.assert_called_once_with("wb")
                    mock_file().write.assert_called_once_with("test page source".encode("utf-8"))

    @pytest.mark.unit
    def test_push_success(self):
        """Test push method with valid driver."""

        mock_driver = Mock()
        mock_file_content = b"test file content"
        expected_data = base64.b64encode(mock_file_content).decode("utf-8")

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=mock_file_content)):
                    result = shadowstep.push("/local/path", "/remote/path")

                    # Verify the method returns self
                    assert result is shadowstep

                    # Verify push_file was called with correct parameters
                    mock_driver.push_file.assert_called_once_with(
                        destination_path="/remote/path", base64data=expected_data
                    )

    @pytest.mark.unit
    def test_get_screenshot_no_driver_condition(self):
        """Test get_screenshot method with None driver condition."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.get_screenshot()

    @pytest.mark.unit
    def test_save_source_no_driver_condition(self):
        """Test save_source method with None driver condition."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.save_source("/test/path", "test.xml")

    @pytest.mark.unit
    def test_push_no_driver_condition(self):
        """Test push method with None driver condition."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=b"test content")):
                    with pytest.raises(ShadowstepException):
                        shadowstep.push("/local/path", "/remote/path")

    @pytest.mark.unit
    def test_drag_negative_speed(self):
        """Test drag method with negative speed."""

        with pytest.raises(ShadowstepException, match="drag failed after 3 attempts"):
            shadowstep.drag(0, 0, 100, 100, -1)

    @pytest.mark.unit
    def test_fling_invalid_direction(self):
        """Test fling method with invalid direction."""

        with pytest.raises(ShadowstepException, match="fling failed after 3 attempts"):
            shadowstep.fling(0, 0, 100, 100, "invalid", 1000)

    @pytest.mark.unit
    def test_fling_zero_speed(self):
        """Test fling method with zero speed."""

        with pytest.raises(ShadowstepException, match="fling failed after 3 attempts"):
            shadowstep.fling(0, 0, 100, 100, "up", 0)

    @pytest.mark.unit
    def test_pinch_open_invalid_percent(self):
        """Test pinch_open method with invalid percent."""

        with pytest.raises(ShadowstepException, match="pinch_open failed after 3 attempts"):
            shadowstep.pinch_open(0, 0, 100, 100, 1.5, 1000)

    @pytest.mark.unit
    def test_pinch_open_negative_speed(self):
        """Test pinch_open method with negative speed."""

        with pytest.raises(ShadowstepException, match="pinch_open failed after 3 attempts"):
            shadowstep.pinch_open(0, 0, 100, 100, 0.5, -1)

    @pytest.mark.unit
    def test_pinch_close_invalid_percent(self):
        """Test pinch_close method with invalid percent."""

        with pytest.raises(ShadowstepException, match="pinch_close failed after 3 attempts"):
            shadowstep.pinch_close(0, 0, 100, 100, 1.5, 1000)

    @pytest.mark.unit
    def test_pinch_close_negative_speed(self):
        """Test pinch_close method with negative speed."""

        with pytest.raises(ShadowstepException, match="pinch_close failed after 3 attempts"):
            shadowstep.pinch_close(0, 0, 100, 100, 0.5, -1)

    @pytest.mark.unit
    def test_swipe_invalid_direction(self):
        """Test swipe method with invalid direction."""

        with pytest.raises(ShadowstepException, match="swipe failed after 3 attempts"):
            shadowstep.swipe(0, 0, 100, 100, "invalid", 0.5, 1000)

    @pytest.mark.unit
    def test_swipe_invalid_percent(self):
        """Test swipe method with invalid percent."""

        with pytest.raises(ShadowstepException, match="swipe failed after 3 attempts"):
            shadowstep.swipe(0, 0, 100, 100, "up", 1.5, 1000)

    @pytest.mark.unit
    def test_swipe_negative_speed(self):
        """Test swipe method with negative speed."""

        with pytest.raises(ShadowstepException, match="swipe failed after 3 attempts"):
            shadowstep.swipe(0, 0, 100, 100, "up", 0.5, -1)

    @pytest.mark.unit
    def test_save_screenshot(self):
        """Test save_screenshot method."""

        mock_screenshot_data = b"fake_screenshot_data"

        with patch.object(shadowstep, "is_connected", return_value=True):
            with patch.object(shadowstep, "get_screenshot", return_value=mock_screenshot_data):
                with patch("pathlib.Path.open", mock_open()) as mock_file:
                    result = shadowstep.save_screenshot("/test/path", "test.png")

                    assert result is True
                    mock_file.assert_called_once_with("wb")

    @pytest.mark.unit
    def test_get_screenshot_with_driver(self):
        """Test get_screenshot method with valid driver."""

        mock_driver = Mock()
        mock_driver.get_screenshot_as_base64.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.get_screenshot()

                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    @pytest.mark.unit
    def test_get_screenshot_no_driver(self):
        """Test get_screenshot method with no driver."""

        # Mock driver to be None and prevent reconnection
        mock_driver = None
        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=False):
                with patch.object(shadowstep, "connect", side_effect=RuntimeError("Connection failed")):
                    # When driver is None, get_screenshot should raise RuntimeError
                    # which will be converted to ShadowstepException by @fail_safe
                    with pytest.raises(ShadowstepException):
                        shadowstep.get_screenshot()

    @pytest.mark.unit
    def test_save_source(self):
        """Test save_source method."""

        mock_driver = Mock()
        mock_driver.page_source = "test page source"
        original_driver = shadowstep.driver
        shadowstep.driver = mock_driver

        try:
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open()) as mock_file:
                    result = shadowstep.save_source("/test/path", "test.xml")

                    assert result is True
                    mock_file.assert_called_once_with("wb")
        finally:
            shadowstep.driver = original_driver

    @pytest.mark.unit
    def test_save_source_no_driver(self):
        """Test save_source method with no driver."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.save_source("/test/path", "test.xml")

    @pytest.mark.unit
    def test_tap_with_duration(self):
        """Test tap method with duration."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.tap(100, 200, 500)

                assert result is shadowstep
                mock_driver.tap.assert_called_once_with([(100, 200)], 500)

    @pytest.mark.unit
    def test_tap_without_duration(self):
        """Test tap method without duration."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.tap(100, 200)

                assert result is shadowstep
                mock_driver.tap.assert_called_once_with([(100, 200)], 100)

    @pytest.mark.unit
    def test_tap_no_driver(self):
        """Test tap method with no driver."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.tap(100, 200)

    @pytest.mark.unit
    def test_start_recording_screen(self):
        """Test start_recording_screen method."""

        mock_driver = Mock()

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                shadowstep.start_recording_screen()

                mock_driver.start_recording_screen.assert_called_once()

    @pytest.mark.unit
    def test_start_recording_screen_no_driver(self):
        """Test start_recording_screen method with no driver."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.start_recording_screen()

    @pytest.mark.unit
    def test_stop_recording_screen(self):
        """Test stop_recording_screen method."""

        mock_driver = Mock()
        mock_driver.stop_recording_screen.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                result = shadowstep.stop_recording_screen()

                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    @pytest.mark.unit
    def test_stop_recording_screen_no_driver(self):
        """Test stop_recording_screen method with no driver."""

        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.stop_recording_screen()

    @pytest.mark.unit
    def test_push_file(self):
        """Test push method."""

        mock_driver = Mock()
        test_data = b"test file content"
        with patch.object(shadowstep, "driver", mock_driver):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=test_data)) as mock_file:
                    result = shadowstep.push("/local/path", "/remote/path")
                    assert result is shadowstep
                    expected_data = base64.b64encode(test_data).decode("utf-8")
                    mock_driver.push_file.assert_called_once_with(
                        destination_path="/remote/path", base64data=expected_data
                    )

    @pytest.mark.unit
    def test_push_file_no_driver(self):
        """Test push method with no driver."""
        with patch.object(shadowstep, "driver", None):
            with patch.object(shadowstep, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    shadowstep.push("/local/path", "/remote/path")

    @pytest.mark.unit
    def test_update_settings_not_implemented(self):
        """Test update_settings method raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            shadowstep.update_settings()

    @pytest.mark.unit
    def test_execute_method(self):
        """Test _execute method."""
        mock_driver = Mock()
        shadowstep.driver = mock_driver
        shadowstep._execute("test: command", {"param": "value"})
        mock_driver.execute_script.assert_called_once_with("test: command", {"param": "value"})
