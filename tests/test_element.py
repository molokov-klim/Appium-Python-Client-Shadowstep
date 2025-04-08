import os
import subprocess
import time

import pytest
from appium.webdriver import WebElement
from icecream import ic
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException

from shadowstep.element.element import Element
from shadowstep.shadowstep import Shadowstep


class TestElement:

    def test_get_element_positive(self, app: Shadowstep):
        parent_element = app.get_element(locator={'package': 'com.android.launcher3',
                                                  'class': 'android.view.ViewGroup',
                                                  'resource-id': 'com.android.launcher3:id/hotseat',
                                                  })
        inner_element = parent_element.get_element(locator={'package': 'com.android.launcher3',
                                                            'class': 'android.widget.TextView',
                                                            'content-desc': 'Phone'})
        assert isinstance(inner_element, Element)
        assert inner_element.get_attribute('package') == 'com.android.launcher3'
        assert inner_element.get_attribute('class') == 'android.widget.TextView'
        assert inner_element.get_attribute('content-desc') == 'Phone'
        app.adb.press_home()

    def test_get_element_contains(self, app: Shadowstep):
        parent_element = app.get_element(locator={'package': 'com.android.launcher3',
                                                  'class': 'android.view.ViewGroup',
                                                  'resource-id': 'com.android.launcher3:id/hotseat',
                                                  })
        inner_element = parent_element.get_element(locator={'package': 'com.android.launcher3',
                                                            'class': 'android.widget.TextView',
                                                            'content-desc': 'Phone'},
                                                   contains=True)
        assert inner_element.contains
        app.adb.press_home()

    def test_get_element_repeated_search(self, app: Shadowstep):
        element1 = app.get_element(locator={'content-desc': 'Phone'})
        element2 = app.get_element(locator={'content-desc': 'Phone'})
        assert element1 is not None
        assert element2 is not None
        assert element1.locator == element2.locator

    def test_get_element_disconnected(self, app: Shadowstep):
        app.disconnect()
        assert not app.is_connected()
        element = app.get_element(locator={'content-desc': 'Phone'})
        app.reconnect()
        assert app.is_connected()
        assert isinstance(element, Element)
        assert element.locator == {'content-desc': 'Phone'}

    def test_tap(self, app: Shadowstep) -> None:
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response

    def test_tap_duration(self, app: Shadowstep):
        phone = app.get_element(locator={'content-desc': 'Phone'})
        phone.tap(duration=3000)
        bubble = app.get_element(locator={'package': 'com.android.launcher3',
                                          'class': 'android.widget.TextView',
                                          'text': 'App info',
                                          'resource-id': 'com.android.launcher3:id/bubble_text'})
        bubble.tap()
        time.sleep(3)
        phone_info_title = app.get_element(locator={'package': 'com.android.settings',
                                                    'class': 'android.widget.TextView',
                                                    'text': 'App info'})
        phone_info_storage = app.get_element(locator={'package': 'com.android.settings',
                                                      'class': 'android.widget.TextView',
                                                      'text': 'Storage & cache',
                                                      'resource-id': 'android:id/title'})
        assert phone_info_title.get_attribute('text') == 'App info'
        assert phone_info_storage.get_attribute('text') == 'Storage & cache'

    def test_tap_no_such_driver_exception(self, app: Shadowstep):
        app.disconnect()
        assert not app.is_connected()
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        assert app.is_connected()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response

    def test_tap_invalid_session_id_exception(self, app: Shadowstep):
        app.driver.session_id = '12345'
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
        assert app.is_connected()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response

    def test_tap_no_such_element_exception(self, app: Shadowstep):
        try:
            element = app.get_element(locator={'content-desc': 'no_such_element'})
            element.tap()
        except Exception as error:
            assert isinstance(error, NoSuchElementException)

    def test_tap_stale_element_reference_exception(self, app: Shadowstep):
        pass  # don't know how to catch

    def test_tap_invalid_element_state_exception(self, app: Shadowstep):
        pass  # don't know how to catch

    def test_get_elements(self, app: Shadowstep):
        parent_element = app.get_element(locator={'package': 'com.android.launcher3',
                                                  'class': 'android.view.ViewGroup',
                                                  'resource-id': 'com.android.launcher3:id/hotseat',
                                                  })
        inner_elements = parent_element.get_elements(locator={'package': 'com.android.launcher3',
                                                              'class': 'android.widget.TextView'})
        assert isinstance(inner_elements, list)
        for inner_element in inner_elements:
            assert isinstance(inner_element, Element)
            assert inner_element.get_attribute('package') == 'com.android.launcher3'
            assert inner_element.get_attribute('class') == 'android.widget.TextView'
        app.adb.press_home()

    def test_get_attributes(self, app: Shadowstep):
        element = app.get_element(locator={'package': 'com.android.launcher3',
                                           'class': 'android.view.ViewGroup',
                                           'resource-id': 'com.android.launcher3:id/hotseat',
                                           })
        attrs = element.get_attributes()
        assert isinstance(attrs, dict)
        assert 'bounds' in attrs.keys()

    @pytest.mark.parametrize("params", [
        {"x": 100, "y": 500},  # Прямые координаты
        {"locator": {"package": "com.android.quicksearchbox",
                     'class': 'android.widget.TextView',
                     'resource-id': 'com.android.quicksearchbox:id/search_widget_text'}},  # Локатор
        {"direction": 0, "distance": 1000},  # Вверх
    ])
    def test_tap_and_move(self, app: Shadowstep, params):
        element = app.get_element(locator={"content-desc": "Phone"})
        target_element = app.get_element(locator={'resource-id': 'com.android.launcher3:id/search_container_all_apps'})
        element.tap_and_move(**params)
        time.sleep(5)
        assert 'Search apps' in target_element.get_attribute(name='text')
        assert isinstance(element, Element)

    def test_click(self, app: Shadowstep):
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.click()
        time.sleep(3)
        response = str(subprocess.check_output('adb shell "dumpsys window windows | grep -E \'mSurface\'"'))
        assert "com.android.dialer" in response

    def test_click_duration(self, app: Shadowstep):
        phone = app.get_element(locator={'content-desc': 'Phone'})
        phone.click(duration=3000)
        bubble = app.get_element(locator={'package': 'com.android.launcher3',
                                          'class': 'android.widget.TextView',
                                          'text': 'App info',
                                          'resource-id': 'com.android.launcher3:id/bubble_text'})
        bubble.click()
        time.sleep(3)
        phone_info_title = app.get_element(locator={'package': 'com.android.settings',
                                                    'class': 'android.widget.TextView',
                                                    'text': 'App info'})
        phone_info_storage = app.get_element(locator={'package': 'com.android.settings',
                                                      'class': 'android.widget.TextView',
                                                      'text': 'Storage & cache',
                                                      'resource-id': 'android:id/title'})
        assert phone_info_title.get_attribute('text') == 'App info'
        assert phone_info_storage.get_attribute('text') == 'Storage & cache'

    def test_click_double(self, app: Shadowstep):
        search = app.get_element(locator={'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        search.click_double()
        time.sleep(5)
        search_src_text = app.get_element(locator={'resource-id': 'com.android.quicksearchbox:id/search_src_text'})
        app.terminal.past_text(text="some_text")
        assert 'some_text' in search_src_text.get_attribute('text')

    @pytest.mark.skip(reason="Not implemented yet")
    def test_click_and_move(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_scroll_down(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_scroll_up(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_scroll_to_bottom(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_scroll_to_top(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_scroll_and_get(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_parent(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_parents(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_sibling(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_siblings(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_cousin(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_cousins(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_is_contains(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_zoom(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_unzoom(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_center(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_coordinates(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_attribute(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_is_displayed(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_clear(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_set_text(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_location_in_view(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_set_value(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_send_keys(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_tag_name(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_text(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_submit(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_property(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_dom_attribute(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_is_selected(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_is_enabled(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_shadow_root(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_location_once_scrolled_into_view(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_size(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_value_of_css_property(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_location(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_rect(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_aria_role(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_accessible_name(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_screenshot_as_base64(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_screenshot_as_png(self, app: Shadowstep):
        ...

    @pytest.mark.skip(reason="Not implemented yet")
    def test_screenshot(self, app: Shadowstep):
        ...

# """
# NoSuchDriverException
# InvalidSessionIdException
#
# NoSuchElementException
# StaleElementReferenceException
# InvalidElementStateException
# """
