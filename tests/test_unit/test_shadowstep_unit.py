from shadowstep.shadowstep import Shadowstep
from unittest.mock import patch


class TestShadowstepUnit:
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

    def test_get_instance_class_method(self):
        """Test get_instance class method returns singleton instance."""
        # Clear any existing instances
        Shadowstep._instance = None

        instance1 = Shadowstep.get_instance()
        instance2 = Shadowstep.get_instance()

        assert instance1 is instance2
        assert isinstance(instance1, Shadowstep)

    def test_initialization_with_existing_instance(self):
        """Test initialization when instance already exists."""
        # Create an instance first
        instance1 = Shadowstep()
        instance1._initialized = True

        # Mock the parent __init__ to avoid actual initialization
        with patch("shadowstep.shadowstep.ShadowstepBase.__init__"):
            instance2 = Shadowstep()
            assert instance1 is instance2


    def test_auto_discover_pages_with_nonexistent_path(self, app: Shadowstep):
        """Test _auto_discover_pages with nonexistent path."""
        from unittest.mock import patch, Mock

        # Mock sys.path to include a nonexistent path
        with patch("sys.path", ["/nonexistent/path"]):
            with patch("pathlib.Path.exists", return_value=False):
                app._auto_discover_pages()
                # Should not raise exception, just skip the path

    def test_auto_discover_pages_with_file_path(self, app: Shadowstep):
        """Test _auto_discover_pages with file path (not directory)."""
        from unittest.mock import patch, Mock

        # Mock sys.path to include a file path
        with patch("sys.path", ["/some/file.txt"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=False):
                    app._auto_discover_pages()
                    # Should not raise exception, just skip the path

    def test_auto_discover_pages_with_ignored_dir(self, app: Shadowstep):
        """Test _auto_discover_pages with ignored directory name."""
        from unittest.mock import patch, Mock

        # Mock sys.path to include an ignored directory
        with patch("sys.path", ["/some/__pycache__"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=True):
                    with patch("pathlib.Path.name", "__pycache__"):
                        app._auto_discover_pages()
                        # Should not raise exception, just skip the path

    def test_auto_discover_pages_with_nonexistent_path_condition(self, app: Shadowstep):
        """Test _auto_discover_pages with nonexistent path condition (line 118)."""
        from unittest.mock import patch

        # Mock sys.path to include a path that doesn't exist
        with patch("sys.path", ["/nonexistent/path"]):
            with patch("pathlib.Path.exists", return_value=False):
                app._auto_discover_pages()
                # Should not raise exception, just skip the path

    def test_auto_discover_pages_with_file_path_condition(self, app: Shadowstep):
        """Test _auto_discover_pages with file path condition (line 118)."""
        from unittest.mock import patch

        # Mock sys.path to include a file path (not directory)
        with patch("sys.path", ["/some/file.txt"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_dir", return_value=False):
                    app._auto_discover_pages()
                    # Should not raise exception, just skip the path

    def test_auto_discover_pages_with_ignored_dir_condition(self, app: Shadowstep):
        """Test _auto_discover_pages with ignored directory condition (line 124)."""
        from unittest.mock import patch, Mock

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
                                        with patch.object(app, "_register_pages_from_module"):
                                            # Mock a directory that should be ignored
                                            with patch(
                                                "pathlib.Path",
                                                side_effect=lambda x: Mock(name="__pycache__"),
                                            ):
                                                app._auto_discover_pages()
                                                # Should not raise exception, just skip the path

    def test_auto_discover_pages_with_import_error(self, app: Shadowstep):
        """Test _auto_discover_pages with import error."""
        from unittest.mock import patch, Mock

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
                                        with patch.object(app, "logger") as mock_logger:
                                            # Reset the discovery flag to allow re-discovery
                                            app._pages_discovered = False
                                            app._auto_discover_pages()
                                            # Should log warning about import error
                                            assert mock_logger.warning.call_count >= 1

    def test_register_pages_from_module_with_non_page_class(self, app: Shadowstep):
        """Test _register_pages_from_module with class that doesn't start with 'Page'."""
        from unittest.mock import Mock, patch
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
                app._register_pages_from_module(mock_module)

                # Verify the class was NOT registered because it doesn't start with 'Page'
                assert "NonPageClass" not in app.pages

    def test_register_pages_from_module_success(self, app: Shadowstep):
        """Test _register_pages_from_module with successful registration."""
        from unittest.mock import Mock, patch
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
                app._register_pages_from_module(mock_module)

                # Verify the page was registered
                assert "PageTest" in app.pages

    def test_register_pages_from_module_exception(self, app: Shadowstep):
        """Test _register_pages_from_module with exception."""
        from unittest.mock import Mock, patch

        mock_module = Mock()
        mock_module.__name__ = "test_module"

        with patch("inspect.getmembers", side_effect=Exception("Test error")):
            # Should not raise exception, just log warning
            app._register_pages_from_module(mock_module)

    def test_list_registered_pages(self, app: Shadowstep):
        """Test list_registered_pages method."""
        from unittest.mock import Mock, patch

        # Add some mock pages
        mock_page1 = Mock()
        mock_page1.__name__ = "Page1"
        mock_page1.__module__ = "test_module"
        mock_page2 = Mock()
        mock_page2.__name__ = "Page2"
        mock_page2.__module__ = "test_module"
        app.pages = {"Page1": mock_page1, "Page2": mock_page2}

        with patch.object(app, "logger") as mock_logger:
            app.list_registered_pages()

            # Verify logging was called
            assert mock_logger.info.call_count >= 1

    def test_get_page_success(self, app: Shadowstep):
        """Test get_page method with existing page."""
        from unittest.mock import Mock

        mock_page_class = Mock()
        mock_page_instance = Mock()
        mock_page_class.return_value = mock_page_instance
        app.pages = {"TestPage": mock_page_class}

        result = app.get_page("TestPage")

        assert result is mock_page_instance
        mock_page_class.assert_called_once()

    def test_get_page_not_found(self, app: Shadowstep):
        """Test get_page method with non-existing page."""
        import pytest

        app.pages = {}

        with pytest.raises(
            ValueError, match="Page 'NonExistentPage' not found in registered pages"
        ):
            app.get_page("NonExistentPage")

    def test_resolve_page_success(self, app: Shadowstep):
        """Test resolve_page method with existing page."""
        from unittest.mock import Mock

        mock_page_class = Mock()
        mock_page_instance = Mock()
        mock_page_class.return_value = mock_page_instance
        app.pages = {"TestPage": mock_page_class}

        result = app.resolve_page("TestPage")

        assert result is mock_page_instance
        mock_page_class.assert_called_once()

    def test_resolve_page_not_found(self, app: Shadowstep):
        """Test resolve_page method with non-existing page."""
        import pytest

        app.pages = {}

        with pytest.raises(ValueError, match="Page 'NonExistentPage' not found"):
            app.resolve_page("NonExistentPage")

    def test_get_elements(self, app: Shadowstep):
        """Test get_elements method."""
        from unittest.mock import Mock, patch

        mock_element = Mock()
        mock_elements = [Mock(), Mock()]
        mock_element.get_elements.return_value = mock_elements

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = app.get_elements({"class": "test"})

            assert result is mock_elements
            mock_element.get_elements.assert_called_once()

    def test_get_image(self, app: Shadowstep):
        """Test get_image method."""
        from unittest.mock import Mock, patch

        mock_image = Mock()

        with patch("shadowstep.shadowstep.ShadowstepImage", return_value=mock_image):
            result = app.get_image("test_image.png")

            assert result is mock_image

    def test_get_images(self, app: Shadowstep):
        """Test get_images method."""
        from unittest.mock import Mock, patch

        mock_image = Mock()

        with patch("shadowstep.shadowstep.ShadowstepImage", return_value=mock_image):
            result = app.get_images("test_image.png")

            assert result == [mock_image]

    def test_schedule_action_not_implemented(self, app: Shadowstep):
        """Test schedule_action method raises NotImplementedError."""
        import pytest

        with pytest.raises(NotImplementedError):
            app.schedule_action("test", [])

    def test_get_action_history_not_implemented(self, app: Shadowstep):
        """Test get_action_history method raises NotImplementedError."""
        import pytest

        with pytest.raises(NotImplementedError):
            app.get_action_history("test")

    def test_unschedule_action_not_implemented(self, app: Shadowstep):
        """Test unschedule_action method raises NotImplementedError."""
        import pytest

        with pytest.raises(NotImplementedError):
            app.unschedule_action("test")

    def test_start_logcat_with_filters(self, app: Shadowstep):
        """Test start_logcat method with filters."""
        from unittest.mock import patch

        with patch.object(app._logcat, "start") as mock_start:
            filters = ["test_filter"]
            app.start_logcat("test.log", port=4723, filters=filters)

            assert app._logcat.filters == filters
            mock_start.assert_called_once_with("test.log", 4723)

    def test_start_logcat_without_filters(self, app: Shadowstep):
        """Test start_logcat method without filters."""
        from unittest.mock import patch

        with patch.object(app._logcat, "start") as mock_start:
            app.start_logcat("test.log")

            mock_start.assert_called_once_with("test.log", None)

    def test_stop_logcat(self, app: Shadowstep):
        """Test stop_logcat method."""
        from unittest.mock import patch

        with patch.object(app._logcat, "stop") as mock_stop:
            app.stop_logcat()

            mock_stop.assert_called_once()

    def test_find_and_get_element_success(self, app: Shadowstep):
        """Test find_and_get_element method with successful find."""
        from unittest.mock import Mock, patch

        mock_scrollable = Mock()
        mock_element = Mock()
        mock_scrollable.scroll_to_element.return_value = mock_element

        with patch.object(app, "get_elements", return_value=[mock_scrollable]):
            result = app.find_and_get_element({"class": "test"})

            assert result is mock_element
            mock_scrollable.scroll_to_element.assert_called_once()

    def test_find_and_get_element_not_found(self, app: Shadowstep):
        """Test find_and_get_element method when element not found."""
        from unittest.mock import patch
        import pytest

        with patch.object(app, "get_elements", return_value=[]):
            with pytest.raises(Exception):  # ShadowstepException
                app.find_and_get_element({"class": "test"})

    def test_find_and_get_element_scroll_failure(self, app: Shadowstep):
        """Test find_and_get_element method when scroll fails."""
        from unittest.mock import Mock, patch
        import pytest

        mock_scrollable = Mock()
        mock_scrollable.scroll_to_element.side_effect = Exception("Scroll failed")

        with patch.object(app, "get_elements", return_value=[mock_scrollable]):
            with pytest.raises(Exception):  # ShadowstepException
                app.find_and_get_element({"class": "test"})

    def test_is_text_visible_success(self, app: Shadowstep):
        """Test is_text_visible method with visible text."""
        from unittest.mock import Mock, patch

        mock_element = Mock()
        mock_element.is_visible.return_value = True

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = app.is_text_visible("test text")

            assert result is True
            mock_element.is_visible.assert_called_once()

    def test_is_text_visible_not_visible(self, app: Shadowstep):
        """Test is_text_visible method with not visible text."""
        from unittest.mock import Mock, patch

        mock_element = Mock()
        mock_element.is_visible.return_value = False

        with patch("shadowstep.shadowstep.Element", return_value=mock_element):
            result = app.is_text_visible("test text")

            assert result is False

    def test_is_text_visible_exception(self, app: Shadowstep):
        """Test is_text_visible method with exception."""
        from unittest.mock import patch

        with patch("shadowstep.shadowstep.Element", side_effect=Exception("Test error")):
            result = app.is_text_visible("test text")

            assert result is False

    def test_scroll_invalid_direction(self, app: Shadowstep):
        """Test scroll method with invalid direction."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="scroll failed after 3 attempts"):
            app.scroll(0, 0, 100, 100, "invalid", 0.5, 1000)

    def test_scroll_invalid_percent(self, app: Shadowstep):
        """Test scroll method with invalid percent."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="scroll failed after 3 attempts"):
            app.scroll(0, 0, 100, 100, "up", 1.5, 1000)

    def test_scroll_negative_speed(self, app: Shadowstep):
        """Test scroll method with negative speed."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="scroll failed after 3 attempts"):
            app.scroll(0, 0, 100, 100, "up", 0.5, -1)

    def test_scroll_success(self, app: Shadowstep):
        """Test scroll method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.scroll(100, 200, 300, 400, "up", 0.5, 1000)

                    # Verify the method returns self
                    assert result is app

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

    def test_long_click_negative_duration(self, app: Shadowstep):
        """Test long_click method with negative duration."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="long_click failed after 3 attempts"):
            app.long_click(100, 100, -1)

    def test_long_click_success(self, app: Shadowstep):
        """Test long_click method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.long_click(100, 200, 1000)

                    # Verify the method returns self
                    assert result is app

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: longClickGesture", {"x": 100, "y": 200, "duration": 1000}
                    )

    def test_double_click_success(self, app: Shadowstep):
        """Test double_click method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.double_click(100, 200)

                    # Verify the method returns self
                    assert result is app

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: doubleClickGesture", {"x": 100, "y": 200}
                    )

    def test_click_success(self, app: Shadowstep):
        """Test click method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.click(100, 200)

                    # Verify the method returns self
                    assert result is app

                    # Verify _execute was called with correct parameters
                    mock_execute.assert_called_once_with(
                        "mobile: clickGesture", {"x": 100, "y": 200}
                    )

    def test_drag_success(self, app: Shadowstep):
        """Test drag method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.drag(100, 200, 300, 400, 1000)

                    # Verify the method returns self
                    assert result is app

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

    def test_fling_success(self, app: Shadowstep):
        """Test fling method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.fling(100, 200, 300, 400, "up", 1000)

                    # Verify the method returns self
                    assert result is app

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

    def test_pinch_open_success(self, app: Shadowstep):
        """Test pinch_open method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.pinch_open(100, 200, 300, 400, 0.5, 1000)

                    # Verify the method returns self
                    assert result is app

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

    def test_pinch_close_success(self, app: Shadowstep):
        """Test pinch_close method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.pinch_close(100, 200, 300, 400, 0.5, 1000)

                    # Verify the method returns self
                    assert result is app

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

    def test_swipe_success(self, app: Shadowstep):
        """Test swipe method with valid parameters."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch.object(app, "_execute") as mock_execute:
                    result = app.swipe(100, 200, 300, 400, "up", 0.5, 1000)

                    # Verify the method returns self
                    assert result is app

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

    def test_swipe_right_to_left_success(self, app: Shadowstep):
        """Test swipe_right_to_left method with valid parameters."""
        from unittest.mock import Mock, patch
        from shadowstep.shadowstep_base import WebDriverSingleton

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(app, "swipe", return_value=app) as mock_swipe:
                result = app.swipe_right_to_left()

                # Verify the method returns self
                assert result is app

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

    def test_swipe_left_to_right_success(self, app: Shadowstep):
        """Test swipe_left_to_right method with valid parameters."""
        from unittest.mock import Mock, patch
        from shadowstep.shadowstep_base import WebDriverSingleton

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(app, "swipe", return_value=app) as mock_swipe:
                result = app.swipe_left_to_right()

                # Verify the method returns self
                assert result is app

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

    def test_swipe_top_to_bottom_success(self, app: Shadowstep):
        """Test swipe_top_to_bottom method with valid parameters."""
        from unittest.mock import Mock, patch
        from shadowstep.shadowstep_base import WebDriverSingleton

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(app, "swipe", return_value=app) as mock_swipe:
                result = app.swipe_top_to_bottom()

                # Verify the method returns self
                assert result is app

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

    def test_swipe_bottom_to_top_success(self, app: Shadowstep):
        """Test swipe_bottom_to_top method with valid parameters."""
        from unittest.mock import Mock, patch
        from shadowstep.shadowstep_base import WebDriverSingleton

        mock_driver = Mock()
        mock_driver.get_window_size.return_value = {"width": 1000, "height": 2000}

        with patch.object(WebDriverSingleton, "get_driver", return_value=mock_driver):
            with patch.object(app, "swipe", return_value=app) as mock_swipe:
                result = app.swipe_bottom_to_top()

                # Verify the method returns self
                assert result is app

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

    def test_get_screenshot_success(self, app: Shadowstep):
        """Test get_screenshot method with valid driver."""
        from unittest.mock import Mock, patch
        import base64

        mock_driver = Mock()
        mock_driver.get_screenshot_as_base64.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                result = app.get_screenshot()

                # Verify the method returns decoded screenshot
                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    def test_save_source_success(self, app: Shadowstep):
        """Test save_source method with valid driver."""
        from unittest.mock import Mock, patch, mock_open

        mock_driver = Mock()
        mock_driver.page_source = "test page source"

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open()) as mock_file:
                    result = app.save_source("/test/path", "test.xml")

                    # Verify the method returns True
                    assert result is True

                    # Verify file was opened and written to
                    mock_file.assert_called_once_with("wb")
                    mock_file().write.assert_called_once_with("test page source".encode("utf-8"))

    def test_push_success(self, app: Shadowstep):
        """Test push method with valid driver."""
        from unittest.mock import Mock, patch, mock_open
        import base64

        mock_driver = Mock()
        mock_file_content = b"test file content"
        expected_data = base64.b64encode(mock_file_content).decode("utf-8")

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=mock_file_content)):
                    result = app.push("/local/path", "/remote/path")

                    # Verify the method returns self
                    assert result is app

                    # Verify push_file was called with correct parameters
                    mock_driver.push_file.assert_called_once_with(
                        destination_path="/remote/path", base64data=expected_data
                    )

    def test_get_screenshot_no_driver_condition(self, app: Shadowstep):
        """Test get_screenshot method with None driver condition."""
        from unittest.mock import patch
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.get_screenshot()

    def test_save_source_no_driver_condition(self, app: Shadowstep):
        """Test save_source method with None driver condition."""
        from unittest.mock import patch
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.save_source("/test/path", "test.xml")

    def test_push_no_driver_condition(self, app: Shadowstep):
        """Test push method with None driver condition."""
        from unittest.mock import patch, mock_open
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=b"test content")):
                    with pytest.raises(ShadowstepException):
                        app.push("/local/path", "/remote/path")

    def test_drag_negative_speed(self, app: Shadowstep):
        """Test drag method with negative speed."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="drag failed after 3 attempts"):
            app.drag(0, 0, 100, 100, -1)

    def test_fling_invalid_direction(self, app: Shadowstep):
        """Test fling method with invalid direction."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="fling failed after 3 attempts"):
            app.fling(0, 0, 100, 100, "invalid", 1000)

    def test_fling_zero_speed(self, app: Shadowstep):
        """Test fling method with zero speed."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="fling failed after 3 attempts"):
            app.fling(0, 0, 100, 100, "up", 0)

    def test_pinch_open_invalid_percent(self, app: Shadowstep):
        """Test pinch_open method with invalid percent."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="pinch_open failed after 3 attempts"):
            app.pinch_open(0, 0, 100, 100, 1.5, 1000)

    def test_pinch_open_negative_speed(self, app: Shadowstep):
        """Test pinch_open method with negative speed."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="pinch_open failed after 3 attempts"):
            app.pinch_open(0, 0, 100, 100, 0.5, -1)

    def test_pinch_close_invalid_percent(self, app: Shadowstep):
        """Test pinch_close method with invalid percent."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="pinch_close failed after 3 attempts"):
            app.pinch_close(0, 0, 100, 100, 1.5, 1000)

    def test_pinch_close_negative_speed(self, app: Shadowstep):
        """Test pinch_close method with negative speed."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="pinch_close failed after 3 attempts"):
            app.pinch_close(0, 0, 100, 100, 0.5, -1)

    def test_swipe_invalid_direction(self, app: Shadowstep):
        """Test swipe method with invalid direction."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="swipe failed after 3 attempts"):
            app.swipe(0, 0, 100, 100, "invalid", 0.5, 1000)

    def test_swipe_invalid_percent(self, app: Shadowstep):
        """Test swipe method with invalid percent."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="swipe failed after 3 attempts"):
            app.swipe(0, 0, 100, 100, "up", 1.5, 1000)

    def test_swipe_negative_speed(self, app: Shadowstep):
        """Test swipe method with negative speed."""
        import pytest
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with pytest.raises(ShadowstepException, match="swipe failed after 3 attempts"):
            app.swipe(0, 0, 100, 100, "up", 0.5, -1)

    def test_save_screenshot(self, app: Shadowstep):
        """Test save_screenshot method."""
        from unittest.mock import patch, Mock, mock_open
        from pathlib import Path

        mock_screenshot_data = b"fake_screenshot_data"

        with patch.object(app, "get_screenshot", return_value=mock_screenshot_data):
            with patch("pathlib.Path.open", mock_open()) as mock_file:
                result = app.save_screenshot("/test/path", "test.png")

                assert result is True
                mock_file.assert_called_once_with("wb")

    def test_get_screenshot_with_driver(self, app: Shadowstep):
        """Test get_screenshot method with valid driver."""
        from unittest.mock import patch, Mock
        import base64

        mock_driver = Mock()
        mock_driver.get_screenshot_as_base64.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                result = app.get_screenshot()

                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    def test_get_screenshot_no_driver(self, app: Shadowstep):
        """Test get_screenshot method with no driver."""
        import pytest
        from unittest.mock import patch, Mock
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        # Mock driver to be None and prevent reconnection
        mock_driver = None
        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", Mock(return_value=False)):
                with patch.object(app, "connect", side_effect=RuntimeError("Connection failed")):
                    # When driver is None, get_screenshot should raise RuntimeError
                    # which will be converted to ShadowstepException by @fail_safe
                    with pytest.raises(ShadowstepException):
                        app.get_screenshot()

    def test_save_source(self, app: Shadowstep):
        """Test save_source method."""
        from unittest.mock import patch, Mock, mock_open
        from pathlib import Path

        mock_driver = Mock()
        mock_driver.page_source = "test page source"
        app.driver = mock_driver

        with patch("pathlib.Path.open", mock_open()) as mock_file:
            result = app.save_source("/test/path", "test.xml")

            assert result is True
            mock_file.assert_called_once_with("wb")

    def test_save_source_no_driver(self, app: Shadowstep):
        """Test save_source method with no driver."""
        import pytest
        from unittest.mock import patch
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.save_source("/test/path", "test.xml")

    def test_tap_with_duration(self, app: Shadowstep):
        """Test tap method with duration."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                result = app.tap(100, 200, 500)

                assert result is app
                mock_driver.tap.assert_called_once_with([(100, 200)], 500)

    def test_tap_without_duration(self, app: Shadowstep):
        """Test tap method without duration."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                result = app.tap(100, 200)

                assert result is app
                mock_driver.tap.assert_called_once_with([(100, 200)], 100)

    def test_tap_no_driver(self, app: Shadowstep):
        """Test tap method with no driver."""
        import pytest
        from unittest.mock import patch
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.tap(100, 200)

    def test_start_recording_screen(self, app: Shadowstep):
        """Test start_recording_screen method."""
        from unittest.mock import Mock, patch

        mock_driver = Mock()

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                app.start_recording_screen()

                mock_driver.start_recording_screen.assert_called_once()

    def test_start_recording_screen_no_driver(self, app: Shadowstep):
        """Test start_recording_screen method with no driver."""
        import pytest
        from unittest.mock import patch
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.start_recording_screen()

    def test_stop_recording_screen(self, app: Shadowstep):
        """Test stop_recording_screen method."""
        from unittest.mock import Mock, patch
        import base64

        mock_driver = Mock()
        mock_driver.stop_recording_screen.return_value = "dGVzdA=="  # base64 for "test"

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                result = app.stop_recording_screen()

                expected = base64.b64decode("dGVzdA==")
                assert result == expected

    def test_stop_recording_screen_no_driver(self, app: Shadowstep):
        """Test stop_recording_screen method with no driver."""
        import pytest
        from unittest.mock import patch
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.stop_recording_screen()

    def test_push_file(self, app: Shadowstep):
        """Test push method."""
        from unittest.mock import Mock, patch, mock_open
        from pathlib import Path
        import base64

        mock_driver = Mock()
        test_data = b"test file content"

        with patch.object(app, "driver", mock_driver):
            with patch.object(app, "is_connected", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=test_data)) as mock_file:
                    result = app.push("/local/path", "/remote/path")

                    assert result is app
                    expected_data = base64.b64encode(test_data).decode("utf-8")
                    mock_driver.push_file.assert_called_once_with(
                        destination_path="/remote/path", base64data=expected_data
                    )

    def test_push_file_no_driver(self, app: Shadowstep):
        """Test push method with no driver."""
        import pytest
        from unittest.mock import patch
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

        with patch.object(app, "driver", None):
            with patch.object(app, "is_connected", return_value=True):
                with pytest.raises(ShadowstepException):
                    app.push("/local/path", "/remote/path")

    def test_update_settings_not_implemented(self, app: Shadowstep):
        """Test update_settings method raises NotImplementedError."""
        import pytest

        with pytest.raises(NotImplementedError):
            app.update_settings()

    def test_execute_method(self, app: Shadowstep):
        """Test _execute method."""
        from unittest.mock import Mock

        mock_driver = Mock()
        app.driver = mock_driver

        app._execute("test: command", {"param": "value"})

        mock_driver.execute_script.assert_called_once_with("test: command", {"param": "value"})
