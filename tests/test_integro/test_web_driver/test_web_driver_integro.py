# ruff: noqa
# pyright: ignore
"""Integration tests for WebDriverSingleton class."""

import inspect

import pytest
from appium.webdriver.webdriver import WebDriver

from shadowstep.shadowstep import Shadowstep
from shadowstep.web_driver.web_driver_singleton import WebDriverSingleton


class TestWebDriverSingleton:
    """Integration tests for WebDriverSingleton functionality."""

    def test_web_driver_singleton_class_exists(self, app: Shadowstep) -> None:
        """Test WebDriverSingleton class can be imported.

        Steps:
        1. Import WebDriverSingleton class.
        2. Verify class has expected attributes.
        3. Verify class has correct docstring.
        """
        # Verify class exists and has docstring
        assert WebDriverSingleton is not None  # noqa: S101
        assert WebDriverSingleton.__doc__ is not None  # noqa: S101
        assert "singleton" in WebDriverSingleton.__doc__.lower()  # noqa: S101

    def test_web_driver_singleton_has_expected_methods(self, app: Shadowstep) -> None:
        """Test WebDriverSingleton has expected public methods.

        Steps:
        1. Verify get_driver method exists.
        2. Verify clear_instance method exists.
        3. Verify both are classmethods.
        """
        # Verify methods exist
        assert hasattr(WebDriverSingleton, "get_driver")  # noqa: S101
        assert hasattr(WebDriverSingleton, "clear_instance")  # noqa: S101

        # Verify they are classmethods
        assert isinstance(inspect.getattr_static(WebDriverSingleton, "get_driver"), classmethod)  # noqa: S101
        assert isinstance(inspect.getattr_static(WebDriverSingleton, "clear_instance"), classmethod)  # noqa: S101

    def test_get_driver_returns_valid_driver(self, app: Shadowstep) -> None:
        """Test get_driver() returns a valid WebDriver instance.

        Steps:
        1. Call WebDriverSingleton.get_driver().
        2. Verify it returns a WebDriver instance.
        3. Verify driver has session_id attribute.
        4. Verify session_id is not None.
        """
        # Get driver from singleton
        driver = WebDriverSingleton.get_driver()

        # Verify it's a WebDriver instance
        assert driver is not None  # noqa: S101
        assert isinstance(driver, WebDriver)  # noqa: S101

        # Verify driver has session_id
        assert hasattr(driver, "session_id")  # noqa: S101
        assert driver.session_id is not None  # noqa: S101

    def test_get_driver_returns_same_instance_as_app_driver(self, app: Shadowstep) -> None:
        """Test get_driver() returns the same instance as app.driver.

        Steps:
        1. Get driver from app.driver.
        2. Get driver from WebDriverSingleton.get_driver().
        3. Verify they are the same instance (same id).
        """
        # Get driver from app
        app_driver = app.driver

        # Get driver from singleton
        singleton_driver = WebDriverSingleton.get_driver()

        # Verify they are the same instance
        assert app_driver is singleton_driver  # noqa: S101
        assert id(app_driver) == id(singleton_driver)  # noqa: S101

    def test_get_driver_signature(self, app: Shadowstep) -> None:
        """Test get_driver() has correct method signature.

        Steps:
        1. Get method signature for get_driver.
        2. Verify return annotation is WebDriver.
        3. Verify method has no parameters (except cls).
        """
        sig = inspect.signature(WebDriverSingleton.get_driver)

        # Verify return annotation
        assert sig.return_annotation == WebDriver  # noqa: S101

        # Verify no parameters except cls (classmethods don't show cls in signature)
        params = [p for p in sig.parameters.keys()]
        assert len(params) == 0  # noqa: S101

    def test_clear_instance_method_exists(self, app: Shadowstep) -> None:
        """Test clear_instance() method exists and can be called.

        Steps:
        1. Verify clear_instance method exists.
        2. Verify it's a classmethod.
        3. Verify it returns None.

        Note: We don't actually call it to avoid disrupting the test session.
        """
        # Verify method exists
        assert hasattr(WebDriverSingleton, "clear_instance")  # noqa: S101

        # Verify it's a classmethod
        assert isinstance(inspect.getattr_static(WebDriverSingleton, "clear_instance"), classmethod)  # noqa: S101

        # Verify signature
        sig = inspect.signature(WebDriverSingleton.clear_instance)
        assert sig.return_annotation in (None, type(None), inspect.Signature.empty)  # noqa: S101

    def test_clear_instance_signature(self, app: Shadowstep) -> None:
        """Test clear_instance() has correct method signature.

        Steps:
        1. Get method signature for clear_instance.
        2. Verify method has no parameters (except cls).
        3. Verify return type is None or empty.
        """
        sig = inspect.signature(WebDriverSingleton.clear_instance)

        # Verify no parameters except cls (classmethods don't show cls in signature)
        params = [p for p in sig.parameters.keys()]
        assert len(params) == 0  # noqa: S101

        # Verify return annotation
        assert sig.return_annotation in (None, type(None), inspect.Signature.empty)  # noqa: S101

    def test_singleton_pattern_multiple_get_driver_calls(self, app: Shadowstep) -> None:
        """Test singleton pattern - multiple get_driver() calls return same instance.

        Steps:
        1. Call get_driver() multiple times.
        2. Verify all calls return the same instance.
        3. Verify session_id is the same across all calls.
        """
        # Get driver multiple times
        driver1 = WebDriverSingleton.get_driver()
        driver2 = WebDriverSingleton.get_driver()
        driver3 = WebDriverSingleton.get_driver()

        # Verify all are the same instance
        assert driver1 is driver2  # noqa: S101
        assert driver2 is driver3  # noqa: S101
        assert id(driver1) == id(driver2) == id(driver3)  # noqa: S101

        # Verify session_id is the same
        assert driver1.session_id == driver2.session_id  # noqa: S101
        assert driver2.session_id == driver3.session_id  # noqa: S101

    def test_driver_has_expected_webdriver_methods(self, app: Shadowstep) -> None:
        """Test driver returned by get_driver() has expected WebDriver methods.

        Steps:
        1. Get driver from get_driver().
        2. Verify it has standard WebDriver methods.
        3. Verify methods are callable.
        """
        driver = WebDriverSingleton.get_driver()

        # Verify standard WebDriver methods exist
        expected_methods = [
            "get_window_size",
            "find_element",
            "find_elements",
            "quit",
            "get_screenshot_as_png",
        ]

        for method_name in expected_methods:
            assert hasattr(driver, method_name)  # noqa: S101
            assert callable(getattr(driver, method_name))  # noqa: S101

    def test_driver_session_id_is_valid_string(self, app: Shadowstep) -> None:
        """Test driver's session_id is a valid string.

        Steps:
        1. Get driver from get_driver().
        2. Get session_id from driver.
        3. Verify session_id is a string.
        4. Verify session_id is not empty.
        """
        driver = WebDriverSingleton.get_driver()

        # Get session_id
        session_id = driver.session_id

        # Verify it's a valid string
        assert isinstance(session_id, str)  # noqa: S101
        assert len(session_id) > 0  # noqa: S101
        assert session_id != ""  # noqa: S101

    def test_driver_can_get_window_size(self, app: Shadowstep) -> None:
        """Test driver can perform basic operations like get_window_size().

        Steps:
        1. Get driver from get_driver().
        2. Call get_window_size().
        3. Verify result is a dict with width and height.
        4. Verify width and height are positive integers.
        """
        driver = WebDriverSingleton.get_driver()

        # Get window size
        size = driver.get_window_size()

        # Verify result format
        assert isinstance(size, dict)  # noqa: S101
        assert "width" in size  # noqa: S101
        assert "height" in size  # noqa: S101

        # Verify values are positive integers
        assert isinstance(size["width"], int)  # noqa: S101
        assert isinstance(size["height"], int)  # noqa: S101
        assert size["width"] > 0  # noqa: S101
        assert size["height"] > 0  # noqa: S101

    def test_web_driver_singleton_class_attributes(self, app: Shadowstep) -> None:
        """Test WebDriverSingleton has expected class attributes.

        Steps:
        1. Verify _instance attribute exists.
        2. Verify _driver attribute exists.
        3. Verify _command_executor attribute exists.
        """
        # Verify class attributes exist
        assert hasattr(WebDriverSingleton, "_instance")  # noqa: S101
        assert hasattr(WebDriverSingleton, "_driver")  # noqa: S101
        assert hasattr(WebDriverSingleton, "_command_executor")  # noqa: S101

    def test_get_driver_docstring(self, app: Shadowstep) -> None:
        """Test get_driver() has proper docstring.

        Steps:
        1. Get docstring of get_driver method.
        2. Verify docstring is not None.
        3. Verify docstring contains relevant keywords.
        """
        docstring = WebDriverSingleton.get_driver.__doc__

        # Verify docstring exists and contains relevant info
        assert docstring is not None  # noqa: S101
        assert "WebDriver" in docstring  # noqa: S101
        assert "Get" in docstring or "get" in docstring  # noqa: S101

    def test_clear_instance_docstring(self, app: Shadowstep) -> None:
        """Test clear_instance() has proper docstring.

        Steps:
        1. Get docstring of clear_instance method.
        2. Verify docstring is not None.
        3. Verify docstring contains relevant keywords.
        """
        docstring = WebDriverSingleton.clear_instance.__doc__

        # Verify docstring exists and contains relevant info
        assert docstring is not None  # noqa: S101
        assert "clear" in docstring.lower() or "remove" in docstring.lower()  # noqa: S101
