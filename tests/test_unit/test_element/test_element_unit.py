# ruff: noqa
# pyright: ignore
"""Unit tests for Element class using mocks."""
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from appium.webdriver.webelement import WebElement

from shadowstep.element.element import Element
from shadowstep.enums import GestureStrategy
from shadowstep.locator import UiSelector


@pytest.fixture(autouse=True)
def mock_element_internals():
    """Mock internal Element methods that interact with driver."""
    with patch('shadowstep.element.element.Element.get_driver'), \
         patch('shadowstep.element.element.Element._get_web_element'):
        yield


class TestElementInit:
    """Test Element initialization."""

    def test_init_with_tuple_locator(self):
        """Test initialization with tuple locator."""
        mock_shadowstep = Mock()
        locator = ("id", "test_id")

        element = Element(locator, mock_shadowstep, timeout=30)

        assert element.locator == locator
        assert element.shadowstep == mock_shadowstep
        assert element.timeout == 30
        assert element.poll_frequency == 0.5

    def test_init_with_dict_locator(self):
        """Test initialization with dict locator."""
        mock_shadowstep = Mock()
        locator = {"resource-id": "test_id", "class": "TextView"}

        element = Element(locator, mock_shadowstep)

        assert element.locator == locator

    def test_init_with_element_locator(self):
        """Test initialization with Element locator."""
        mock_shadowstep = Mock()
        base_locator = ("id", "test_id")
        base_element = Element(base_locator, mock_shadowstep)

        new_element = Element(base_element, mock_shadowstep)

        assert new_element.locator == base_locator

    def test_init_with_uiselector(self):
        """Test initialization with UiSelector."""
        mock_shadowstep = Mock()
        ui_selector = UiSelector().resourceId("test_id")

        with patch.object(ui_selector, '__str__', return_value='new UiSelector().resourceId("test_id")'):
            element = Element(ui_selector, mock_shadowstep)
            assert element.locator == 'new UiSelector().resourceId("test_id")'

    def test_init_with_native_element(self):
        """Test initialization with native WebElement."""
        mock_shadowstep = Mock()
        mock_native = Mock(spec=WebElement)
        locator = ("id", "test_id")

        element = Element(locator, mock_shadowstep, native=mock_native)

        assert element.native == mock_native

    def test_init_creates_subcomponents(self):
        """Test that initialization creates all subcomponents."""
        mock_shadowstep = Mock()
        locator = ("id", "test_id")

        element = Element(locator, mock_shadowstep)

        assert hasattr(element, 'utilities')
        assert hasattr(element, 'properties')
        assert hasattr(element, 'dom')
        assert hasattr(element, 'actions')
        assert hasattr(element, 'gestures')
        assert hasattr(element, 'coordinates')
        assert hasattr(element, 'screenshots')
        assert hasattr(element, 'waiting')

    def test_repr(self):
        """Test __repr__ method."""
        mock_shadowstep = Mock()
        locator = ("id", "test_id")

        element = Element(locator, mock_shadowstep)

        assert "Element(locator=" in repr(element)
        assert "test_id" in repr(element)


class TestElementDOM:
    """Test Element DOM methods."""

    def test_get_element(self):
        """Test get_element delegates to dom.get_element."""
        mock_shadowstep = Mock()
        element = Element(("id", "parent"), mock_shadowstep)
        element.dom.get_element = Mock(return_value=Mock(spec=Element))

        child_locator = ("id", "child")
        result = element.get_element(child_locator, timeout=10)

        element.dom.get_element.assert_called_once_with(child_locator, 10, 0.5, None)
        assert result is not None

    def test_get_elements(self):
        """Test get_elements delegates to dom.get_elements."""
        mock_shadowstep = Mock()
        element = Element(("id", "parent"), mock_shadowstep)
        mock_elements = [Mock(spec=Element), Mock(spec=Element)]
        element.dom.get_elements = Mock(return_value=mock_elements)

        child_locator = ("id", "child")
        result = element.get_elements(child_locator, timeout=10)

        element.dom.get_elements.assert_called_once_with(child_locator, 10, 0.5, None)
        assert len(result) == 2

    def test_get_parent(self):
        """Test get_parent delegates to dom.get_parent."""
        mock_shadowstep = Mock()
        element = Element(("id", "child"), mock_shadowstep)
        element.dom.get_parent = Mock(return_value=Mock(spec=Element))

        result = element.get_parent(timeout=5)

        element.dom.get_parent.assert_called_once_with(5, 0.5, None)
        assert result is not None

    def test_get_parents(self):
        """Test get_parents delegates to dom.get_parents."""
        mock_shadowstep = Mock()
        element = Element(("id", "child"), mock_shadowstep)
        mock_parents = [Mock(spec=Element), Mock(spec=Element)]
        element.dom.get_parents = Mock(return_value=mock_parents)

        result = element.get_parents(timeout=5)

        element.dom.get_parents.assert_called_once_with(5, 0.5, None)
        assert len(result) == 2

    def test_get_sibling(self):
        """Test get_sibling delegates to dom.get_sibling."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem1"), mock_shadowstep)
        element.dom.get_sibling = Mock(return_value=Mock(spec=Element))

        sibling_locator = ("id", "elem2")
        result = element.get_sibling(sibling_locator, timeout=5)

        element.dom.get_sibling.assert_called_once_with(sibling_locator, 5, 0.5, None)
        assert result is not None

    def test_get_siblings(self):
        """Test get_siblings delegates to dom.get_siblings."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem1"), mock_shadowstep)
        mock_siblings = [Mock(spec=Element), Mock(spec=Element)]
        element.dom.get_siblings = Mock(return_value=mock_siblings)

        sibling_locator = ("class", "sibling_class")
        result = element.get_siblings(sibling_locator, timeout=5)

        element.dom.get_siblings.assert_called_once_with(sibling_locator, 5, 0.5, None)
        assert len(result) == 2

    def test_get_cousin(self):
        """Test get_cousin delegates to dom.get_cousin."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.dom.get_cousin = Mock(return_value=Mock(spec=Element))

        cousin_locator = ("id", "cousin")
        result = element.get_cousin(cousin_locator, depth_to_parent=2, timeout=5)

        element.dom.get_cousin.assert_called_once_with(cousin_locator, 2, 5, 0.5, None)
        assert result is not None

    def test_get_cousins(self):
        """Test get_cousins delegates to dom.get_cousins."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        mock_cousins = [Mock(spec=Element), Mock(spec=Element)]
        element.dom.get_cousins = Mock(return_value=mock_cousins)

        cousin_locator = ("class", "cousin_class")
        result = element.get_cousins(cousin_locator, depth_to_parent=1, timeout=5)

        element.dom.get_cousins.assert_called_once_with(cousin_locator, 1, 5, 0.5, None)
        assert len(result) == 2


class TestElementActions:
    """Test Element action methods."""

    def test_send_keys(self):
        """Test send_keys delegates to actions.send_keys."""
        mock_shadowstep = Mock()
        element = Element(("id", "input"), mock_shadowstep)
        element.actions.send_keys = Mock(return_value=element)

        result = element.send_keys("test", "input")

        element.actions.send_keys.assert_called_once_with("test", "input")
        assert result == element

    def test_clear(self):
        """Test clear delegates to actions.clear."""
        mock_shadowstep = Mock()
        element = Element(("id", "input"), mock_shadowstep)
        element.actions.clear = Mock(return_value=element)

        result = element.clear()

        element.actions.clear.assert_called_once()
        assert result == element

    def test_set_value(self):
        """Test set_value delegates to actions.set_value."""
        mock_shadowstep = Mock()
        element = Element(("id", "input"), mock_shadowstep)
        element.actions.set_value = Mock(return_value=element)

        result = element.set_value("new_value")

        element.actions.set_value.assert_called_once_with("new_value")
        assert result == element

    def test_submit(self):
        """Test submit delegates to actions.submit."""
        mock_shadowstep = Mock()
        element = Element(("id", "form"), mock_shadowstep)
        element.actions.submit = Mock(return_value=element)

        result = element.submit()

        element.actions.submit.assert_called_once()
        assert result == element


class TestElementGestures:
    """Test Element gesture methods."""

    def test_tap(self):
        """Test tap delegates to gestures.tap."""
        mock_shadowstep = Mock()
        element = Element(("id", "button"), mock_shadowstep)
        
        with patch.object(element.gestures, 'tap', wraps=element.gestures.tap) as mock_tap:
            mock_tap.return_value = element
            result = element.tap(duration=100)

            mock_tap.assert_called_once_with(100)
            assert result == element

    def test_tap_and_move(self):
        """Test tap_and_move delegates to gestures.tap_and_move."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        
        with patch.object(element.gestures, 'tap_and_move', wraps=element.gestures.tap_and_move) as mock_tap:
            mock_tap.return_value = element
            result = element.tap_and_move(x=100, y=200)

            mock_tap.assert_called_once_with(None, 100, 200, None, None)
            assert result == element

    def test_click(self):
        """Test click delegates to gestures.click."""
        mock_shadowstep = Mock()
        element = Element(("id", "button"), mock_shadowstep)
        
        # Используем patch.object с wraps чтобы проверить реальное делегирование
        with patch.object(element.gestures, 'click', wraps=element.gestures.click) as mock_click:
            mock_click.return_value = element
            result = element.click(duration=50)

            mock_click.assert_called_once_with(50, GestureStrategy.AUTO)
            assert result == element

    def test_click_double(self):
        """Test click_double delegates to gestures.click_double."""
        mock_shadowstep = Mock()
        element = Element(("id", "button"), mock_shadowstep)
        
        with patch.object(element.gestures, 'double_click', wraps=element.gestures.double_click) as mock_dbl:
            mock_dbl.return_value = element
            result = element.double_click()

            mock_dbl.assert_called_once()
            assert result == element

    def test_drag(self):
        """Test drag delegates to gestures.drag."""
        mock_shadowstep = Mock()
        element = Element(("id", "draggable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'drag', wraps=element.gestures.drag) as mock_drag:
            mock_drag.return_value = element
            result = element.drag(100, 200, speed=3000)

            mock_drag.assert_called_once_with(100, 200, 3000, GestureStrategy.AUTO)
            assert result == element

    def test_fling_up(self):
        """Test fling_up calls fling with up direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'fling', wraps=element.gestures.fling) as mock_fling:
            mock_fling.return_value = element
            result = element.fling_up(speed=3000)

            mock_fling.assert_called_once_with(3000, "up", GestureStrategy.AUTO)
            assert result == element

    def test_fling_down(self):
        """Test fling_down calls fling with down direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'fling', wraps=element.gestures.fling) as mock_fling:
            mock_fling.return_value = element
            result = element.fling_down(speed=3000)

            mock_fling.assert_called_once_with(3000, "down", GestureStrategy.AUTO)
            assert result == element

    def test_fling_left(self):
        """Test fling_left calls fling with left direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'fling', wraps=element.gestures.fling) as mock_fling:
            mock_fling.return_value = element
            result = element.fling_left(speed=3000)

            mock_fling.assert_called_once_with(3000, "left", GestureStrategy.AUTO)
            assert result == element

    def test_fling_right(self):
        """Test fling_right calls fling with right direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'fling', wraps=element.gestures.fling) as mock_fling:
            mock_fling.return_value = element
            result = element.fling_right(speed=3000)

            mock_fling.assert_called_once_with(3000, "right", GestureStrategy.AUTO)
            assert result == element

    def test_fling(self):
        """Test fling delegates to gestures.fling."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'fling', wraps=element.gestures.fling) as mock_fling:
            mock_fling.return_value = element
            result = element.fling(speed=2500, direction="up")

            mock_fling.assert_called_once_with(2500, "up", GestureStrategy.AUTO)
            assert result == element

    def test_scroll_down(self):
        """Test scroll_down calls scroll with down direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll', wraps=element.gestures.scroll) as mock_scroll:
            mock_scroll.return_value = element
            result = element.scroll_down(percent=0.8, speed=2500)

            mock_scroll.assert_called_once_with("down", 0.8, 2500, False, GestureStrategy.AUTO)
            assert result == element

    def test_scroll_up(self):
        """Test scroll_up calls scroll with up direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll', wraps=element.gestures.scroll) as mock_scroll:
            mock_scroll.return_value = element
            result = element.scroll_up(percent=0.7, speed=2000)

            mock_scroll.assert_called_once_with("up", 0.7, 2000, False, GestureStrategy.AUTO)
            assert result == element

    def test_scroll_left(self):
        """Test scroll_left calls scroll with left direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll', wraps=element.gestures.scroll) as mock_scroll:
            mock_scroll.return_value = element
            result = element.scroll_left(percent=0.6, speed=1500)

            mock_scroll.assert_called_once_with("left", 0.6, 1500, False, GestureStrategy.AUTO)
            assert result == element

    def test_scroll_right(self):
        """Test scroll_right calls scroll with right direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll', wraps=element.gestures.scroll) as mock_scroll:
            mock_scroll.return_value = element
            result = element.scroll_right(percent=0.5, speed=1000)

            mock_scroll.assert_called_once_with("right", 0.5, 1000, False, GestureStrategy.AUTO)
            assert result == element

    def test_scroll(self):
        """Test scroll delegates to gestures.scroll."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll', wraps=element.gestures.scroll) as mock_scroll:
            mock_scroll.return_value = element
            result = element.scroll(direction="down", percent=0.7, speed=2000, return_bool=False)

            mock_scroll.assert_called_once_with("down", 0.7, 2000, False, GestureStrategy.AUTO)
            assert result == element

    def test_scroll_to_bottom(self):
        """Test scroll_to_bottom delegates to gestures.scroll_to_bottom."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll_to_bottom', wraps=element.gestures.scroll_to_bottom) as mock_stb:
            mock_stb.return_value = element
            result = element.scroll_to_bottom(percent=0.8, speed=9000)

            mock_stb.assert_called_once_with(0.8, 9000, GestureStrategy.AUTO)
            assert result == element

    def test_scroll_to_top(self):
        """Test scroll_to_top delegates to gestures.scroll_to_top."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'scroll_to_top', wraps=element.gestures.scroll_to_top) as mock_stt:
            mock_stt.return_value = element
            result = element.scroll_to_top(percent=0.7, speed=8000)

            mock_stt.assert_called_once_with(0.7, 8000, GestureStrategy.AUTO)
            assert result == element

    def test_scroll_to_element(self):
        """Test scroll_to_element delegates to gestures.scroll_to_element."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        target_element = Mock(spec=Element)
        
        with patch.object(element.gestures, 'scroll_to_element', wraps=element.gestures.scroll_to_element) as mock_ste:
            mock_ste.return_value = target_element
            target_locator = ("id", "target")
            result = element.scroll_to_element(target_locator, max_swipes=20)

            mock_ste.assert_called_once_with(target_locator, 20, 0.7, 5000, GestureStrategy.AUTO)
            assert result == target_element

    def test_zoom(self):
        """Test zoom delegates to gestures.zoom."""
        mock_shadowstep = Mock()
        element = Element(("id", "image"), mock_shadowstep)
        
        with patch.object(element.gestures, 'zoom', wraps=element.gestures.zoom) as mock_zoom:
            mock_zoom.return_value = element
            result = element.zoom(percent=0.8, speed=3000)

            mock_zoom.assert_called_once_with(0.8, 3000, GestureStrategy.AUTO)
            assert result == element

    def test_unzoom(self):
        """Test unzoom delegates to gestures.unzoom."""
        mock_shadowstep = Mock()
        element = Element(("id", "image"), mock_shadowstep)
        
        with patch.object(element.gestures, 'unzoom', wraps=element.gestures.unzoom) as mock_unzoom:
            mock_unzoom.return_value = element
            result = element.unzoom(percent=0.75, speed=2500)

            mock_unzoom.assert_called_once_with(0.75, 2500, GestureStrategy.AUTO)
            assert result == element

    def test_swipe_up(self):
        """Test swipe_up calls swipe with up direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'swipe', wraps=element.gestures.swipe) as mock_swipe:
            mock_swipe.return_value = element
            result = element.swipe_up(percent=0.8, speed=6000)

            mock_swipe.assert_called_once_with("up", 0.8, 6000, GestureStrategy.AUTO)
            assert result == element

    def test_swipe_down(self):
        """Test swipe_down calls swipe with down direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'swipe', wraps=element.gestures.swipe) as mock_swipe:
            mock_swipe.return_value = element
            result = element.swipe_down(percent=0.75, speed=5000)

            mock_swipe.assert_called_once_with("down", 0.75, 5000, GestureStrategy.AUTO)
            assert result == element

    def test_swipe_left(self):
        """Test swipe_left calls swipe with left direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'swipe', wraps=element.gestures.swipe) as mock_swipe:
            mock_swipe.return_value = element
            result = element.swipe_left(percent=0.7, speed=4000)

            mock_swipe.assert_called_once_with("left", 0.7, 4000, GestureStrategy.AUTO)
            assert result == element

    def test_swipe_right(self):
        """Test swipe_right calls swipe with right direction."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'swipe', wraps=element.gestures.swipe) as mock_swipe:
            mock_swipe.return_value = element
            result = element.swipe_right(percent=0.65, speed=3500)

            mock_swipe.assert_called_once_with("right", 0.65, 3500, GestureStrategy.AUTO)
            assert result == element

    def test_swipe(self):
        """Test swipe delegates to gestures.swipe."""
        mock_shadowstep = Mock()
        element = Element(("id", "scrollable"), mock_shadowstep)
        
        with patch.object(element.gestures, 'swipe', wraps=element.gestures.swipe) as mock_swipe:
            mock_swipe.return_value = element
            result = element.swipe(direction="up", percent=0.75, speed=5000)

            mock_swipe.assert_called_once_with("up", 0.75, 5000, GestureStrategy.AUTO)
            assert result == element


class TestElementProperties:
    """Test Element property methods."""

    def test_get_attribute(self):
        """Test get_attribute delegates to properties.get_attribute."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.get_attribute = Mock(return_value="test_value")

        result = element.get_attribute("attr_name")

        element.properties.get_attribute.assert_called_once_with("attr_name")
        assert result == "test_value"

    def test_get_attributes(self):
        """Test get_attributes delegates to properties.get_attributes."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_attrs = {"attr1": "value1", "attr2": "value2"}
        element.properties.get_attributes = Mock(return_value=expected_attrs)

        result = element.get_attributes()

        element.properties.get_attributes.assert_called_once()
        assert result == expected_attrs

    def test_get_property(self):
        """Test get_property delegates to properties.get_property."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.get_property = Mock(return_value="prop_value")

        result = element.get_property("prop_name")

        element.properties.get_property.assert_called_once_with("prop_name")
        assert result == "prop_value"

    def test_get_dom_attribute(self):
        """Test get_dom_attribute delegates to properties.get_dom_attribute."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.get_dom_attribute = Mock(return_value="dom_value")

        result = element.get_dom_attribute("dom_attr")

        element.properties.get_dom_attribute.assert_called_once_with("dom_attr")
        assert result == "dom_value"

    def test_is_displayed(self):
        """Test is_displayed delegates to properties.is_displayed."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.is_displayed = Mock(return_value=True)

        result = element.is_displayed()

        element.properties.is_displayed.assert_called_once()
        assert result is True

    def test_is_visible(self):
        """Test is_visible delegates to properties.is_visible."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.is_visible = Mock(return_value=False)

        result = element.is_visible()

        element.properties.is_visible.assert_called_once()
        assert result is False

    def test_is_selected(self):
        """Test is_selected delegates to properties.is_selected."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.is_selected = Mock(return_value=True)

        result = element.is_selected()

        element.properties.is_selected.assert_called_once()
        assert result is True

    def test_is_enabled(self):
        """Test is_enabled delegates to properties.is_enabled."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.is_enabled = Mock(return_value=True)

        result = element.is_enabled()

        element.properties.is_enabled.assert_called_once()
        assert result is True

    def test_is_contains(self):
        """Test is_contains delegates to properties.is_contains."""
        mock_shadowstep = Mock()
        element = Element(("id", "parent"), mock_shadowstep)
        element.properties.is_contains = Mock(return_value=True)

        child_locator = ("id", "child")
        result = element.is_contains(child_locator)

        element.properties.is_contains.assert_called_once_with(child_locator)
        assert result is True

    def test_tag_name_property(self):
        """Test tag_name property delegates to properties.tag_name."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.tag_name = Mock(return_value="div")

        result = element.tag_name

        element.properties.tag_name.assert_called_once()
        assert result == "div"

    def test_attributes_property(self):
        """Test attributes property calls get_attributes."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_attrs = {"attr1": "value1"}
        element.properties.get_attributes = Mock(return_value=expected_attrs)

        result = element.attributes

        element.properties.get_attributes.assert_called_once()
        assert result == expected_attrs

    def test_text_property(self):
        """Test text property delegates to properties.text."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.text = Mock(return_value="sample text")

        result = element.text

        element.properties.text.assert_called_once()
        assert result == "sample text"

    def test_resource_id_property(self):
        """Test resource_id property delegates to properties.resource_id."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.resource_id = Mock(return_value="com.app:id/button")

        result = element.resource_id

        element.properties.resource_id.assert_called_once()
        assert result == "com.app:id/button"

    def test_class_property(self):
        """Test class_ property delegates to properties.class_."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.class_ = Mock(return_value="android.widget.Button")

        result = element.class_

        element.properties.class_.assert_called_once()
        assert result == "android.widget.Button"

    def test_class_name_property(self):
        """Test class_name property delegates to properties.class_name."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.class_name = Mock(return_value="android.widget.TextView")

        result = element.class_name

        element.properties.class_name.assert_called_once()
        assert result == "android.widget.TextView"

    def test_index_property(self):
        """Test index property delegates to properties.index."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.index = Mock(return_value="0")

        result = element.index

        element.properties.index.assert_called_once()
        assert result == "0"

    def test_package_property(self):
        """Test package property delegates to properties.package."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.package = Mock(return_value="com.example.app")

        result = element.package

        element.properties.package.assert_called_once()
        assert result == "com.example.app"

    def test_bounds_property(self):
        """Test bounds property delegates to properties.bounds."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.bounds = Mock(return_value="[0,0][100,100]")

        result = element.bounds

        element.properties.bounds.assert_called_once()
        assert result == "[0,0][100,100]"

    def test_checked_property(self):
        """Test checked property delegates to properties.checked."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.checked = Mock(return_value="true")

        result = element.checked

        element.properties.checked.assert_called_once()
        assert result == "true"

    def test_checkable_property(self):
        """Test checkable property delegates to properties.checkable."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.checkable = Mock(return_value="false")

        result = element.checkable

        element.properties.checkable.assert_called_once()
        assert result == "false"

    def test_enabled_property(self):
        """Test enabled property delegates to properties.enabled."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.enabled = Mock(return_value="true")

        result = element.enabled

        element.properties.enabled.assert_called_once()
        assert result == "true"

    def test_focusable_property(self):
        """Test focusable property delegates to properties.focusable."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.focusable = Mock(return_value="true")

        result = element.focusable

        element.properties.focusable.assert_called_once()
        assert result == "true"

    def test_focused_property(self):
        """Test focused property delegates to properties.focused."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.focused = Mock(return_value="false")

        result = element.focused

        element.properties.focused.assert_called_once()
        assert result == "false"

    def test_long_clickable_property(self):
        """Test long_clickable property delegates to properties.long_clickable."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.long_clickable = Mock(return_value="true")

        result = element.long_clickable

        element.properties.long_clickable.assert_called_once()
        assert result == "true"

    def test_password_property(self):
        """Test password property delegates to properties.password."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.password = Mock(return_value="false")

        result = element.password

        element.properties.password.assert_called_once()
        assert result == "false"

    def test_scrollable_property(self):
        """Test scrollable property delegates to properties.scrollable."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.scrollable = Mock(return_value="true")

        result = element.scrollable

        element.properties.scrollable.assert_called_once()
        assert result == "true"

    def test_selected_property(self):
        """Test selected property delegates to properties.selected."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.selected = Mock(return_value="false")

        result = element.selected

        element.properties.selected.assert_called_once()
        assert result == "false"

    def test_displayed_property(self):
        """Test displayed property delegates to properties.displayed."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.displayed = Mock(return_value="true")

        result = element.displayed

        element.properties.displayed.assert_called_once()
        assert result == "true"

    def test_shadow_root_property(self):
        """Test shadow_root property delegates to properties.shadow_root."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        mock_shadow_root = Mock()
        element.properties.shadow_root = Mock(return_value=mock_shadow_root)

        result = element.shadow_root

        element.properties.shadow_root.assert_called_once()
        assert result == mock_shadow_root

    def test_size_property(self):
        """Test size property delegates to properties.size."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_size = {"width": 100, "height": 200}
        element.properties.size = Mock(return_value=expected_size)

        result = element.size

        element.properties.size.assert_called_once()
        assert result == expected_size

    def test_value_of_css_property(self):
        """Test value_of_css_property delegates to properties.value_of_css_property."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.value_of_css_property = Mock(return_value="red")

        result = element.value_of_css_property("color")

        element.properties.value_of_css_property.assert_called_once_with("color")
        assert result == "red"

    def test_location_property(self):
        """Test location property delegates to properties.location."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_location = {"x": 10, "y": 20}
        element.properties.location = Mock(return_value=expected_location)

        result = element.location

        element.properties.location.assert_called_once()
        assert result == expected_location

    def test_rect_property(self):
        """Test rect property delegates to properties.rect."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_rect = {"x": 10, "y": 20, "width": 100, "height": 200}
        element.properties.rect = Mock(return_value=expected_rect)

        result = element.rect

        element.properties.rect.assert_called_once()
        assert result == expected_rect

    def test_aria_role_property(self):
        """Test aria_role property delegates to properties.aria_role."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.aria_role = Mock(return_value="button")

        result = element.aria_role

        element.properties.aria_role.assert_called_once()
        assert result == "button"

    def test_accessible_name_property(self):
        """Test accessible_name property delegates to properties.accessible_name."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.properties.accessible_name = Mock(return_value="Submit Button")

        result = element.accessible_name

        element.properties.accessible_name.assert_called_once()
        assert result == "Submit Button"


class TestElementCoordinates:
    """Test Element coordinate methods."""

    def test_get_coordinates(self):
        """Test get_coordinates delegates to coordinates.get_coordinates."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.coordinates.get_coordinates = Mock(return_value=(10, 20, 100, 200))

        result = element.get_coordinates()

        element.coordinates.get_coordinates.assert_called_once()
        assert result == (10, 20, 100, 200)

    def test_get_center(self):
        """Test get_center delegates to coordinates.get_center."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.coordinates.get_center = Mock(return_value=(50, 100))

        result = element.get_center()

        element.coordinates.get_center.assert_called_once()
        assert result == (50, 100)

    def test_location_in_view_property(self):
        """Test location_in_view property delegates to coordinates.location_in_view."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_location = {"x": 15, "y": 25}
        element.coordinates.location_in_view = Mock(return_value=expected_location)

        result = element.location_in_view

        element.coordinates.location_in_view.assert_called_once()
        assert result == expected_location

    def test_location_once_scrolled_into_view_property(self):
        """Test location_once_scrolled_into_view property delegates to coordinates."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        expected_location = {"x": 20, "y": 30}
        element.coordinates.location_once_scrolled_into_view = Mock(return_value=expected_location)

        result = element.location_once_scrolled_into_view

        element.coordinates.location_once_scrolled_into_view.assert_called_once()
        assert result == expected_location


class TestElementScreenshots:
    """Test Element screenshot methods."""

    def test_screenshot_as_base64_property(self):
        """Test screenshot_as_base64 property delegates to screenshots.screenshot_as_base64."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.screenshots.screenshot_as_base64 = Mock(return_value="base64_string")

        result = element.screenshot_as_base64

        element.screenshots.screenshot_as_base64.assert_called_once()
        assert result == "base64_string"

    def test_screenshot_as_png_property(self):
        """Test screenshot_as_png property delegates to screenshots.screenshot_as_png."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.screenshots.screenshot_as_png = Mock(return_value=b"png_bytes")

        result = element.screenshot_as_png

        element.screenshots.screenshot_as_png.assert_called_once()
        assert result == b"png_bytes"

    def test_save_screenshot(self):
        """Test save_screenshot delegates to screenshots.save_screenshot."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.screenshots.save_screenshot = Mock(return_value=True)

        result = element.save_screenshot("/path/to/screenshot.png")

        element.screenshots.save_screenshot.assert_called_once_with("/path/to/screenshot.png")
        assert result is True


class TestElementWaiting:
    """Test Element waiting methods."""

    def test_wait(self):
        """Test wait delegates to waiting.wait."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait = Mock(return_value=element)

        result = element.wait(timeout=15, poll_frequency=1.0, return_bool=False)

        element.waiting.wait.assert_called_once_with(15, poll_frequency=1.0, return_bool=False)
        assert result == element

    def test_wait_return_bool(self):
        """Test wait with return_bool=True."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait = Mock(return_value=True)

        result = element.wait(timeout=10, return_bool=True)

        element.waiting.wait.assert_called_once_with(10, poll_frequency=0.5, return_bool=True)
        assert result is True

    def test_wait_visible(self):
        """Test wait_visible delegates to waiting.wait_visible."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait_visible = Mock(return_value=element)

        result = element.wait_visible(timeout=10, poll_frequency=0.5, return_bool=False)

        element.waiting.wait_visible.assert_called_once_with(10, poll_frequency=0.5, return_bool=False)
        assert result == element

    def test_wait_clickable(self):
        """Test wait_clickable delegates to waiting.wait_clickable."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait_clickable = Mock(return_value=element)

        result = element.wait_clickable(timeout=10, poll_frequency=0.5, return_bool=False)

        element.waiting.wait_clickable.assert_called_once_with(10, 0.5, False)
        assert result == element

    def test_wait_for_not(self):
        """Test wait_for_not delegates to waiting.wait_for_not."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait_for_not = Mock(return_value=element)

        result = element.wait_for_not(timeout=10, poll_frequency=0.5, return_bool=False)

        element.waiting.wait_for_not.assert_called_once_with(10, poll_frequency=0.5, return_bool=False)
        assert result == element

    def test_wait_for_not_visible(self):
        """Test wait_for_not_visible delegates to waiting.wait_for_not_visible."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait_for_not_visible = Mock(return_value=element)

        result = element.wait_for_not_visible(timeout=10, poll_frequency=0.5, return_bool=False)

        element.waiting.wait_for_not_visible.assert_called_once_with(10, 0.5, False)
        assert result == element

    def test_wait_for_not_clickable(self):
        """Test wait_for_not_clickable delegates to waiting.wait_for_not_clickable."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)
        element.waiting.wait_for_not_clickable = Mock(return_value=element)

        result = element.wait_for_not_clickable(timeout=10, poll_frequency=0.5, return_bool=False)

        element.waiting.wait_for_not_clickable.assert_called_once_with(10, 0.5, False)
        assert result == element


class TestElementOther:
    """Test other Element methods."""

    def test_should_property(self):
        """Test should property returns Should instance."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep)

        result = element.should

        assert result is not None
        # The Should instance should have the element
        assert result.element == element

    def test_get_native_with_native_provided(self):
        """Test get_native returns provided native element."""
        mock_shadowstep = Mock()
        mock_native = Mock(spec=WebElement)
        element = Element(("id", "elem"), mock_shadowstep, native=mock_native)

        result = element.get_native()

        assert result == mock_native

    def test_get_native_without_native(self):
        """Test get_native calls _get_web_element when native is None."""
        mock_shadowstep = Mock()
        element = Element(("id", "elem"), mock_shadowstep, timeout=15, poll_frequency=1.0)
        mock_web_element = Mock(spec=WebElement)
        element._get_web_element = Mock(return_value=mock_web_element)

        result = element.get_native()

        element._get_web_element.assert_called_once_with(
            locator=("id", "elem"),
            timeout=15,
            poll_frequency=1.0,
            ignored_exceptions=None
        )
        assert result == mock_web_element

    def test_get_native_with_element_locator(self):
        """Test get_native converts Element locator correctly."""
        mock_shadowstep = Mock()
        base_locator = ("xpath", "//div")
        base_element = Element(base_locator, mock_shadowstep)
        element = Element(base_element, mock_shadowstep)

        mock_web_element = Mock(spec=WebElement)
        element._get_web_element = Mock(return_value=mock_web_element)

        result = element.get_native()

        # Should use the base_locator, not the Element
        element._get_web_element.assert_called_once()
        call_args = element._get_web_element.call_args
        assert call_args[1]["locator"] == base_locator
