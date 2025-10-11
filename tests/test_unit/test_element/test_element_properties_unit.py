# ruff: noqa
# pyright: ignore
"""Unit tests for shadowstep/element/properties.py module."""
from typing import Any
from unittest.mock import Mock, patch
import pytest

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.element.properties import ElementProperties
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException
from shadowstep.shadowstep import Shadowstep


class TestElementProperties:
    """Test suite for ElementProperties class."""

    def _create_test_element(self, mock_driver: Mock, timeout: float = 1.0) -> tuple[Shadowstep, Any]:
        """Helper method to create test element with mocked driver."""
        app = Shadowstep()
        app.driver = mock_driver
        el = app.get_element({"resource-id": "test-id"})
        el.timeout = timeout
        return app, el

    # Tests for __init__ method
    @pytest.mark.unit
    def test_element_properties_initialization(self):
        """Test ElementProperties initialization."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        properties = ElementProperties(el)
        
        assert properties.element is el
        assert properties.shadowstep is el.shadowstep
        assert properties.converter is el.converter
        assert properties.utilities is el.utilities
        assert properties.logger is not None

    # Tests for get_attribute method
    @pytest.mark.unit
    def test_get_attribute_success(self):
        """Test successful get_attribute operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "test-value"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.get_attribute("test-attr")
        
        assert result == "test-value"
        mock_native_element.get_attribute.assert_called_once_with("test-attr")

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_get_attribute_handles_no_such_driver_exception(self, mock_handle_error):
        """Test get_attribute handles NoSuchDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=NoSuchDriverException("No driver")):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.properties.get_attribute("test-attr")
        
        assert "Failed to" in str(exc_info.value)
        mock_handle_error.assert_called()

    @pytest.mark.unit
    def test_get_attribute_handles_stale_element_reference_exception(self):
        """Test get_attribute handles StaleElementReferenceException and retries."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "value"
        
        app, el = self._create_test_element(mock_driver)
        
        get_native_calls = [
            StaleElementReferenceException("Stale"),
            mock_native_element,
            mock_native_element
        ]
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=get_native_calls):
                result = el.properties.get_attribute("attr")
        
        assert result == "value"

    # Tests for get_attributes method
    @pytest.mark.unit
    def test_get_attributes_success(self):
        """Test successful get_attributes operation."""
        mock_driver = Mock()
        mock_driver.page_source = '<root><element id="test"/></root>'
        
        app, el = self._create_test_element(mock_driver)
        
        attrs = {"id": "test", "class": "test-class"}
        
        with patch.object(el.properties, '_resolve_xpath_for_attributes', return_value="//element"):
            with patch.object(el.utilities, 'extract_el_attrs_from_source', return_value=[attrs]):
                result = el.properties.get_attributes()
        
        assert result == attrs

    @pytest.mark.unit
    def test_get_attributes_returns_empty_dict_when_xpath_fails(self):
        """Test get_attributes returns empty dict when xpath resolution fails."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, '_resolve_xpath_for_attributes', return_value=None):
            result = el.properties.get_attributes()
        
        assert result == {}

    @pytest.mark.unit
    def test_get_attributes_returns_empty_dict_when_no_attrs_extracted(self):
        """Test get_attributes returns empty dict when no attributes extracted."""
        mock_driver = Mock()
        mock_driver.page_source = '<root></root>'
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, '_resolve_xpath_for_attributes', return_value="//element"):
            with patch.object(el.utilities, 'extract_el_attrs_from_source', return_value=[]):
                result = el.properties.get_attributes()
        
        assert result == {}

    # Tests for get_property method
    @pytest.mark.unit
    def test_get_property_success(self):
        """Test successful get_property operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_property.return_value = "property-value"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.get_property("test-property")
        
        assert result == "property-value"

    # Tests for get_dom_attribute method
    @pytest.mark.unit
    def test_get_dom_attribute_success(self):
        """Test successful get_dom_attribute operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_dom_attribute.return_value = "dom-value"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.get_dom_attribute("data-id")
        
        assert result == "dom-value"

    # Tests for is_displayed method
    @pytest.mark.unit
    def test_is_displayed_returns_true(self):
        """Test is_displayed returns True when element is displayed."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.is_displayed.return_value = True
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.is_displayed()
        
        assert result is True

    @pytest.mark.unit
    def test_is_displayed_returns_false_on_no_such_element(self):
        """Test is_displayed returns False when NoSuchElementException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchElementException("Not found")):
                result = el.properties.is_displayed()
        
        assert result is False

    # Tests for is_visible method
    @pytest.mark.unit
    def test_is_visible_returns_true(self):
        """Test is_visible returns True when element is visible."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, '_check_element_visibility', return_value=True):
            result = el.properties.is_visible()
        
        assert result is True

    @pytest.mark.unit
    def test_is_visible_returns_false(self):
        """Test is_visible returns False when element is not visible."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.properties, '_check_element_visibility', return_value=False):
            result = el.properties.is_visible()
        
        assert result is False

    @pytest.mark.unit
    def test_is_visible_raises_exception_on_timeout(self):
        """Test is_visible raises exception when visibility check times out."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el.properties, '_check_element_visibility', return_value=None):
            with pytest.raises(ShadowstepElementException) as exc_info:
                el.properties.is_visible()
        
        assert "Failed to" in str(exc_info.value)

    # Tests for is_selected method
    @pytest.mark.unit
    def test_is_selected_returns_true(self):
        """Test is_selected returns True when element is selected."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.is_selected.return_value = True
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.is_selected()
        
        assert result is True

    @pytest.mark.unit
    def test_is_selected_returns_false_on_no_such_element(self):
        """Test is_selected returns False when NoSuchElementException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchElementException("Not found")):
                result = el.properties.is_selected()
        
        assert result is False

    # Tests for is_enabled method
    @pytest.mark.unit
    def test_is_enabled_returns_true(self):
        """Test is_enabled returns True when element is enabled."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.is_enabled.return_value = True
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.is_enabled()
        
        assert result is True

    @pytest.mark.unit
    def test_is_enabled_returns_false_on_no_such_element(self):
        """Test is_enabled returns False when NoSuchElementException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=NoSuchElementException("Not found")):
                result = el.properties.is_enabled()
        
        assert result is False

    # Tests for is_contains method
    @pytest.mark.unit
    def test_is_contains_returns_true(self):
        """Test is_contains returns True when child element found."""
        mock_driver = Mock()
        mock_child_element = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        child_locator = ("xpath", "//child")
        
        with patch.object(el, '_get_web_element', return_value=mock_child_element):
            result = el.properties.is_contains(child_locator)
        
        assert result is True

    @pytest.mark.unit
    def test_is_contains_returns_false_on_no_such_element(self):
        """Test is_contains returns False when NoSuchElementException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        child_locator = {"class": "child"}
        
        with patch.object(el, '_get_web_element', side_effect=NoSuchElementException("Not found")):
            result = el.properties.is_contains(child_locator)
        
        assert result is False

    # Tests for tag_name method
    @pytest.mark.unit
    def test_tag_name_success(self):
        """Test successful tag_name operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.tag_name = "android.widget.TextView"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.tag_name()
        
        assert result == "android.widget.TextView"

    # Tests for attributes method
    @pytest.mark.unit
    def test_attributes_calls_get_attributes(self):
        """Test attributes method calls get_attributes."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        expected_attrs = {"id": "test", "class": "test-class"}
        
        with patch.object(el.properties, 'get_attributes', return_value=expected_attrs):
            result = el.properties.attributes()
        
        assert result == expected_attrs

    # Tests for text method
    @pytest.mark.unit
    def test_text_success(self):
        """Test successful text operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.text = "Element text"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.text()
        
        assert result == "Element text"

    # Tests for resource_id method
    @pytest.mark.unit
    def test_resource_id_success(self):
        """Test successful resource_id operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="com.example:id/button"):
                result = el.properties.resource_id()
        
        assert result == "com.example:id/button"

    # Tests for class_ method
    @pytest.mark.unit
    def test_class_success(self):
        """Test successful class_ operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="android.widget.Button"):
                result = el.properties.class_()
        
        assert result == "android.widget.Button"

    # Tests for index method
    @pytest.mark.unit
    def test_index_success(self):
        """Test successful index operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="5"):
                result = el.properties.index()
        
        assert result == "5"

    # Tests for package method
    @pytest.mark.unit
    def test_package_success(self):
        """Test successful package operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="com.example.app"):
                result = el.properties.package()
        
        assert result == "com.example.app"

    # Tests for class_name method
    @pytest.mark.unit
    def test_class_name_success(self):
        """Test successful class_name operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="Button"):
                result = el.properties.class_name()
        
        assert result == "Button"

    # Tests for bounds method
    @pytest.mark.unit
    def test_bounds_success(self):
        """Test successful bounds operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="[0,0][100,100]"):
                result = el.properties.bounds()
        
        assert result == "[0,0][100,100]"

    # Tests for checked method
    @pytest.mark.unit
    def test_checked_success(self):
        """Test successful checked operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.checked()
        
        assert result == "true"

    # Tests for checkable method
    @pytest.mark.unit
    def test_checkable_success(self):
        """Test successful checkable operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="false"):
                result = el.properties.checkable()
        
        assert result == "false"

    # Tests for enabled method
    @pytest.mark.unit
    def test_enabled_success(self):
        """Test successful enabled operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.enabled()
        
        assert result == "true"

    # Tests for focusable method
    @pytest.mark.unit
    def test_focusable_success(self):
        """Test successful focusable operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.focusable()
        
        assert result == "true"

    # Tests for focused method
    @pytest.mark.unit
    def test_focused_success(self):
        """Test successful focused operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="false"):
                result = el.properties.focused()
        
        assert result == "false"

    # Tests for long_clickable method
    @pytest.mark.unit
    def test_long_clickable_success(self):
        """Test successful long_clickable operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.long_clickable()
        
        assert result == "true"

    # Tests for password method
    @pytest.mark.unit
    def test_password_success(self):
        """Test successful password operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.password()
        
        assert result == "true"

    # Tests for scrollable method
    @pytest.mark.unit
    def test_scrollable_success(self):
        """Test successful scrollable operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.scrollable()
        
        assert result == "true"

    # Tests for selected method
    @pytest.mark.unit
    def test_selected_success(self):
        """Test successful selected operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="false"):
                result = el.properties.selected()
        
        assert result == "false"

    # Tests for displayed method
    @pytest.mark.unit
    def test_displayed_success(self):
        """Test successful displayed operation."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el.properties, 'get_attribute', return_value="true"):
                result = el.properties.displayed()
        
        assert result == "true"

    # Tests for shadow_root method
    @pytest.mark.unit
    def test_shadow_root_success(self):
        """Test successful shadow_root operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_shadow_root = Mock()
        mock_native_element.shadow_root = mock_shadow_root
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.shadow_root()
        
        assert result is mock_shadow_root

    # Tests for size method
    @pytest.mark.unit
    def test_size_success(self):
        """Test successful size operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.size = {"width": 100, "height": 50}
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.size()
        
        assert result == {"width": 100, "height": 50}

    # Tests for value_of_css_property method
    @pytest.mark.unit
    def test_value_of_css_property_success(self):
        """Test successful value_of_css_property operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.value_of_css_property.return_value = "red"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.value_of_css_property("color")
        
        assert result == "red"

    # Tests for location method
    @pytest.mark.unit
    def test_location_success(self):
        """Test successful location operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.location = {"x": 100, "y": 200}
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.location()
        
        assert result == {"x": 100, "y": 200}

    # Tests for rect method
    @pytest.mark.unit
    def test_rect_success(self):
        """Test successful rect operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.rect = {"x": 50, "y": 75, "width": 100, "height": 50}
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.rect()
        
        assert result == {"x": 50, "y": 75, "width": 100, "height": 50}

    # Tests for aria_role method
    @pytest.mark.unit
    def test_aria_role_success(self):
        """Test successful aria_role operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.aria_role = "button"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.aria_role()
        
        assert result == "button"

    # Tests for accessible_name method
    @pytest.mark.unit
    def test_accessible_name_success(self):
        """Test successful accessible_name operation."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.accessible_name = "Submit Button"
        
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', return_value=mock_native_element):
                result = el.properties.accessible_name()
        
        assert result == "Submit Button"

    # Tests for _resolve_xpath_for_attributes method
    @pytest.mark.unit
    def test_resolve_xpath_for_attributes_success(self):
        """Test successful _resolve_xpath_for_attributes operation."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        el.locator = ("xpath", "//test")
        
        result = el.properties._resolve_xpath_for_attributes()
        
        assert result == "//test"

    @pytest.mark.unit
    def test_resolve_xpath_for_attributes_handles_exception(self):
        """Test _resolve_xpath_for_attributes handles exception."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        with patch.object(el.converter, 'to_xpath', side_effect=Exception("Conversion error")):
            result = el.properties._resolve_xpath_for_attributes()
        
        assert result is None

    # Tests for _check_element_visibility method
    @pytest.mark.unit
    def test_check_element_visibility_returns_true(self):
        """Test _check_element_visibility returns True when element is visible."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "true"
        mock_native_element.location = {"x": 10, "y": 20}
        mock_native_element.size = {"width": 100, "height": 50}
        
        app, el = self._create_test_element(mock_driver)
        el.shadowstep.terminal = Mock()
        el.shadowstep.terminal.get_screen_resolution = Mock(return_value=(1080, 1920))
        
        with patch.object(el, 'get_native', return_value=mock_native_element):
            result = el.properties._check_element_visibility()
        
        assert result is True

    @pytest.mark.unit
    def test_check_element_visibility_returns_false_when_not_displayed(self):
        """Test _check_element_visibility returns False when element not displayed."""
        mock_driver = Mock()
        mock_native_element = Mock()
        mock_native_element.get_attribute.return_value = "false"
        
        app, el = self._create_test_element(mock_driver)
        el.shadowstep.terminal = Mock()
        el.shadowstep.terminal.get_screen_resolution = Mock(return_value=(1080, 1920))
        
        with patch.object(el, 'get_native', return_value=mock_native_element):
            result = el.properties._check_element_visibility()
        
        assert result is False

    @pytest.mark.unit
    def test_check_element_visibility_returns_false_on_no_such_element(self):
        """Test _check_element_visibility returns False on NoSuchElementException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        el.shadowstep.terminal = Mock()
        el.shadowstep.terminal.get_screen_resolution = Mock(return_value=(1080, 1920))
        
        with patch.object(el, 'get_native', side_effect=NoSuchElementException("Not found")):
            result = el.properties._check_element_visibility()
        
        assert result is False

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_check_element_visibility_returns_none_on_driver_error(self, mock_handle_error):
        """Test _check_element_visibility returns None on driver error."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver)
        el.shadowstep.terminal = Mock()
        el.shadowstep.terminal.get_screen_resolution = Mock(return_value=(1080, 1920))
        
        with patch.object(el, 'get_native', side_effect=NoSuchDriverException("No driver")):
            result = el.properties._check_element_visibility()
        
        assert result is None
        mock_handle_error.assert_called()

    # Tests for _check_element_bounds method
    @pytest.mark.unit
    def test_check_element_bounds_returns_true_when_in_bounds(self):
        """Test _check_element_bounds returns True when element is in bounds."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        location = {"x": 10, "y": 20}
        size = {"width": 100, "height": 50}
        
        result = el.properties._check_element_bounds(location, size, 1080, 1920)
        
        assert result is True

    @pytest.mark.unit
    def test_check_element_bounds_returns_false_when_out_of_bounds_right(self):
        """Test _check_element_bounds returns False when element is out of bounds (right)."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        location = {"x": 1000, "y": 20}
        size = {"width": 200, "height": 50}  # x + width > screen_width
        
        result = el.properties._check_element_bounds(location, size, 1080, 1920)
        
        assert result is False

    @pytest.mark.unit
    def test_check_element_bounds_returns_false_when_out_of_bounds_bottom(self):
        """Test _check_element_bounds returns False when element is out of bounds (bottom)."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        location = {"x": 10, "y": 1900}
        size = {"width": 100, "height": 50}  # y + height > screen_height
        
        result = el.properties._check_element_bounds(location, size, 1080, 1920)
        
        assert result is False

    @pytest.mark.unit
    def test_check_element_bounds_returns_false_when_negative_x(self):
        """Test _check_element_bounds returns False when x is negative."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        location = {"x": -10, "y": 20}
        size = {"width": 100, "height": 50}
        
        result = el.properties._check_element_bounds(location, size, 1080, 1920)
        
        assert result is False

    @pytest.mark.unit
    def test_check_element_bounds_returns_false_when_negative_y(self):
        """Test _check_element_bounds returns False when y is negative."""
        mock_driver = Mock()
        app, el = self._create_test_element(mock_driver)
        
        location = {"x": 10, "y": -5}
        size = {"width": 100, "height": 50}
        
        result = el.properties._check_element_bounds(location, size, 1080, 1920)
        
        assert result is False

    # Additional exception handling tests
    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_text_handles_invalid_session_id_exception(self, mock_handle_error):
        """Test text handles InvalidSessionIdException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', side_effect=InvalidSessionIdException("Invalid session")):
            with pytest.raises(ShadowstepElementException):
                el.properties.text()
        
        mock_handle_error.assert_called()

    @pytest.mark.unit
    @patch("shadowstep.element.utilities.ElementUtilities.handle_driver_error")
    def test_size_handles_webdriver_exception(self, mock_handle_error):
        """Test size handles WebDriverException."""
        mock_driver = Mock()
        
        app, el = self._create_test_element(mock_driver, timeout=0.1)
        
        with patch.object(el, 'get_driver', return_value=mock_driver):
            with patch.object(el, 'get_native', side_effect=WebDriverException("Error")):
                with pytest.raises(ShadowstepElementException):
                    el.properties.size()
        
        mock_handle_error.assert_called()

