import subprocess
import time
from typing import Generator
import pytest
from selenium.common import NoSuchElementException

from shadowstep.element.element import Element, GeneralElementException
from shadowstep.elements.elements import Elements
from shadowstep.shadowstep import Shadowstep


class TestElement:

    def test_get_element_positive(self, app: Shadowstep, android_settings, android_settings_recycler):
        inner_element = android_settings_recycler.get_element(locator={'text': 'Network & internet'})
        assert isinstance(inner_element, Element)
        assert inner_element.get_attribute('package') == 'com.android.settings'
        assert inner_element.get_attribute('class') == 'android.widget.TextView'
        assert inner_element.get_attribute('resource-id') == 'android:id/title'

    def test_get_element_contains(self, app: Shadowstep, android_settings, android_settings_recycler):
        inner_element = android_settings_recycler.get_element(locator={'text': 'ork & int'},
                                                   contains=True)
        assert inner_element.contains
        assert inner_element.get_attribute('text') == 'Network & internet'

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

    def test_get_elements(self, app: Shadowstep, android_settings, android_settings_recycler):
        inner_elements = android_settings_recycler.get_elements(locator={'resource-id': 'android:id/title'})
        assert isinstance(inner_elements, Elements)
        for inner_element in inner_elements:
            assert isinstance(inner_element, Element)
            assert inner_element.get_attribute('resource-id') == 'android:id/title'


    def test_get_attributes(self, app: Shadowstep):
        element = app.get_element(locator={'package': 'com.android.launcher3',
                                           'class': 'android.view.ViewGroup',
                                           'resource-id': 'com.android.launcher3:id/hotseat',
                                           })
        attrs = element.get_attributes()
        assert isinstance(attrs, dict)
        assert 'bounds' in attrs.keys()

    def test_get_parent(self, app: Shadowstep):
        child = app.get_element(locator={'content-desc': 'Phone'})
        parent = child.get_parent()
        assert isinstance(parent, Element)
        assert 'ViewGroup' in parent.get_attribute('class')
        child = app.get_element(locator={'resource-id': 'com.android.launcher3:id/drag_layer'})
        parent = child.get_parent()
        assert 'com.android.launcher3:id/launcher' in parent.get_attribute('resource-id')

    def test_get_parents(self, app: Shadowstep):
        element = app.get_element(locator={'content-desc': 'Phone'})
        parents = element.get_parents()
        assert isinstance(parents, Generator)
        count = 0
        for parent in parents:
            assert isinstance(parent, Element)
            count += 1
        assert count > 0
        app.adb.press_home()

    def test_get_sibling(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        sibling = el.get_sibling({'content-desc': 'WebView Browser Tester'})
        assert isinstance(sibling, Element)
        assert 'WebView Browser Tester' in sibling.get_attribute('text')
        el = app.get_element({'content-desc': 'Phone'})
        sibling_element = app.get_element({'content-desc': 'WebView Browser Tester'})
        sibling = el.get_sibling(sibling_element)
        assert isinstance(sibling, Element)
        assert 'WebView Browser Tester' in sibling.get_attribute('text')

    def test_get_siblings(self, app: Shadowstep, android_settings, android_settings_recycler):
        el = android_settings_recycler.get_element({'resource-id': 'com.android.settings:id/recycler_view'}).get_element({'class': 'android.widget.LinearLayout'})
        siblings = el.get_siblings()
        assert isinstance(siblings, Generator)
        count = 0
        bounds = []
        for sibling in siblings:
            assert isinstance(sibling, Element)
            assert sibling.get_attribute('bounds') is not None
            bounds.append(sibling.get_attribute('bounds'))
            count += 1
        bounds = set(bounds)
        assert len(bounds) > 3
        assert count > 0

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
        phone_info_title = app.get_element(locator={'content-desc': 'App info'})
        phone_info_storage = app.get_element(locator={'text': 'Storage & cache'})
        assert phone_info_title.get_attribute('content-desc') == 'App info'
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

    # FIXME почему-то один проходит а в связке - нет
    def test_click(self, app: Shadowstep):
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.click()
        time.sleep(5)
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
        phone_info_title = app.get_element(locator={'content-desc': 'App info'})
        phone_info_storage = app.get_element(locator={'text': 'Storage & cache',
                                                      'resource-id': 'android:id/title'})
        assert phone_info_title.get_attribute('content-desc') == 'App info'
        assert phone_info_storage.get_attribute('text') == 'Storage & cache'

    def test_click_double(self, app: Shadowstep):
        search = app.get_element(locator={'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        search.click_double()
        time.sleep(5)
        search_src_text = app.get_element(locator={'resource-id': 'com.android.quicksearchbox:id/search_src_text'})
        app.terminal.past_text(text="some_text")
        assert 'some_text' in search_src_text.get_attribute('text')

    def test_drag(self, app: Shadowstep):
        app.terminal.press_home()
        time.sleep(10)
        dev_settings = app.get_element(locator={"content-desc": "Appium Settings"})
        search = app.get_element(locator={'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        assert 'com.android.quicksearchbox' in search.get_attribute('package')
        end_x, end_y = search.get_center()
        app.get_element(locator={"content-desc": "Phone"}).tap_and_move(x=100, y=500)
        time.sleep(1)
        dev_settings.drag(end_x=100, end_y=500)
        time.sleep(1)
        dev_settings.drag(end_x=end_x, end_y=end_y)
        dev_settings.timeout = 5
        time.sleep(1)
        assert not dev_settings.is_visible()

    def test_is_within_screen(self, app: Shadowstep):
        phone = app.get_element(locator={"content-desc": "Phone"}, timeout=5)
        search = app.get_element(locator={'resource-id': 'com.android.quicksearchbox:id/search_widget_text'}, timeout=5)
        assert search.is_visible() is True
        assert phone.is_visible() is True
        phone.tap()
        time.sleep(3)
        assert phone.is_visible() is False
        assert search.is_visible() is False

    def test_fling(self, app: Shadowstep):
        element = app.get_element(locator={"content-desc": "Phone"})
        target_element = app.get_element(locator={'content-desc': 'Do Not Disturb.'})
        element.fling_up(speed=2000)
        time.sleep(5)
        assert 'Off' in target_element.get_attribute(name='text')
        assert isinstance(element, Element)

    def test_scroll(self, app: Shadowstep):
        settings_recycler = app.get_element(
            locator={'resource-id': 'com.android.settings:id/main_content_scrollable_container'})
        settings_network = app.get_element(locator={'text': 'Network & internet',
                                                    'resource-id': 'android:id/title'})
        settings_about_phone = app.get_element(locator={'text': 'About phone',
                                                        'resource-id': 'android:id/title'})
        app.terminal.start_activity(package='com.android.settings', activity='com.android.settings.Settings')
        time.sleep(3)
        assert 'Network & internet' in settings_network.get_attribute('text')
        settings_recycler.scroll_down(percent=10, speed=2000)
        time.sleep(3)
        assert 'About phone' in settings_about_phone.get_attribute('text')
        app.terminal.close_app(package='com.android.settings')

    def test_scroll_to_bottom(self, app: Shadowstep):
        settings_recycler = app.get_element(
            locator={'resource-id': 'com.android.settings:id/main_content_scrollable_container'})
        settings_network = app.get_element(locator={'text': 'Network & internet',
                                                    'resource-id': 'android:id/title'})
        settings_about_phone = app.get_element(locator={'text': 'About phone',
                                                        'resource-id': 'android:id/title'})
        app.terminal.start_activity(package='com.android.settings', activity='com.android.settings.Settings')
        time.sleep(3)
        assert 'Network & internet' in settings_network.get_attribute('text')
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert 'About phone' in settings_about_phone.get_attribute('text')
        app.terminal.close_app(package='com.android.settings')

    def test_scroll_to_top(self, app: Shadowstep):
        settings_recycler = app.get_element(
            locator={'resource-id': 'com.android.settings:id/main_content_scrollable_container'})
        settings_network = app.get_element(locator={'text': 'Network & internet',
                                                    'resource-id': 'android:id/title'})
        settings_about_phone = app.get_element(locator={'text': 'About phone',
                                                        'resource-id': 'android:id/title'})
        app.terminal.start_activity(package='com.android.settings', activity='com.android.settings.Settings')
        time.sleep(3)
        assert 'Network & internet' in settings_network.get_attribute('text')
        settings_recycler.scroll_to_bottom()
        time.sleep(3)
        assert 'About phone' in settings_about_phone.get_attribute('text')
        settings_recycler.scroll_to_top()
        time.sleep(3)
        assert 'Network & internet' in settings_network.get_attribute('text')
        app.terminal.close_app(package='com.android.settings')

    def test_scroll_to_element(self, app: Shadowstep):
        settings_recycler = app.get_element(
            locator={'resource-id': 'com.android.settings:id/main_content_scrollable_container'})
        settings_network = app.get_element(locator={'text': 'Network & internet',
                                                    'resource-id': 'android:id/title'})
        settings_about_phone = app.get_element(locator={'text': 'About phone',
                                                        'resource-id': 'android:id/title'})
        app.terminal.start_activity(package='com.android.settings', activity='com.android.settings.Settings')
        time.sleep(3)
        assert 'Network & internet' in settings_network.get_attribute('text')
        settings_recycler.scroll_to_element(locator=settings_about_phone.locator)
        time.sleep(3)
        assert 'About phone' in settings_about_phone.get_attribute('text')
        settings_recycler.scroll_to_element(locator=settings_network)
        time.sleep(3)
        assert 'Network & internet' in settings_network.get_attribute('text')
        app.terminal.close_app(package='com.android.settings')

    def test_get_center(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        center = el.get_center()
        assert isinstance(center, tuple) and len(center) == 2
        assert center == (126, 2184)

    def test_get_coordinates(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        coords = el.get_coordinates()
        assert isinstance(coords, tuple) and len(coords) == 4
        assert coords == (23, 2100, 230, 2269)

    def test_get_attribute(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert el.get_attribute('content-desc') == 'Phone'

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_get_property(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        prop = el.get_property('enabled')
        assert isinstance(prop, (str, bool, dict, type(None)))

    def test_get_dom_attribute(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert el.get_dom_attribute('class') == 'android.widget.TextView'

    def test_is_displayed(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert isinstance(el.is_displayed(), bool)
        assert el.is_displayed()

    def test_is_selected(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert isinstance(el.is_selected(), bool)
        assert not el.is_selected()

    def test_is_enabled(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert isinstance(el.is_enabled(), bool)
        assert el.is_enabled()

    def test_is_contains(self, app: Shadowstep):
        el = app.get_element({'resource-id': 'com.android.launcher3:id/hotseat'})
        assert el.is_contains({'content-desc': 'Phone'}) is True

    def test_tag_name(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert isinstance(el.tag_name, str)
        assert el.tag_name == 'Phone'

    def test_text(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert isinstance(el.text, str)
        assert el.text == 'Phone'

    # FIXME почему-то один проходит а в связке - нет
    def test_clear(self, app: Shadowstep):
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        el.tap()
        app.terminal.past_text('some_text')
        time.sleep(3)
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_src_text'})
        assert el.text == 'some_text'
        el.clear()
        assert el.text == ''

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_set_value(self, app: Shadowstep):
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        el.tap()
        time.sleep(3)
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_src_text'})
        el.set_value("test123")
        assert "test123" in el.text
        el.clear()

    def test_send_keys(self, app: Shadowstep):
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        el.tap()
        time.sleep(3)
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_src_text'})
        el.send_keys("abc")
        assert "abc" in el.text
        el.clear()

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_submit(self, app: Shadowstep):
        el = app.get_element({'resource-id': 'com.android.quicksearchbox:id/search_widget_text'})
        el.submit()  # Не всегда валидно, но для теста вызова достаточно

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_shadow_root(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        try:
            sr = el.shadow_root
            assert sr is not None
        except Exception as e:
            assert isinstance(e, (NoSuchElementException, AttributeError))

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_location_once_scrolled_into_view(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        loc = el.location_once_scrolled_into_view
        assert 'x' in loc and 'y' in loc

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_size_location_rect(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        assert 'width' in el.size and 'height' in el.size
        assert 'x' in el.location and 'y' in el.location
        assert all(k in el.rect for k in ('x', 'y', 'width', 'height'))

    @pytest.mark.xfail(reason="Method is not implemented in UiAutomator2")
    def test_value_of_css_property(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        value = el.value_of_css_property("display")
        assert isinstance(value, str)

    def test_screenshot_as_base64(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        ss = el.screenshot_as_base64
        assert isinstance(ss, str)

    def test_screenshot_as_png(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        ss = el.screenshot_as_png
        assert isinstance(ss, bytes)

    def test_save_screenshot(self, tmp_path, app: Shadowstep):
        el = app.get_element({'content-desc': 'Phone'})
        filepath = tmp_path / "test_element.png"
        assert el.save_screenshot(str(filepath)) is True
        assert filepath.exists()
        filepath.unlink()
        assert not filepath.exists()

    def test_shadow_root_error(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'non_existing'})
        with pytest.raises(GeneralElementException):
            _ = el.shadow_root

    def test_get_attribute_no_such_element(self, app: Shadowstep):
        el = app.get_element({'content-desc': 'non_existing'})
        with pytest.raises(NoSuchElementException):
            el.get_attribute("text")

    def test_scroll_to_element_not_found(self, app):
        app.terminal.start_activity(package="com.android.settings", activity=".Settings")
        container = app.get_element({'resource-id': 'com.android.settings:id/main_content_scrollable_container'})
        with pytest.raises(GeneralElementException):
            container.scroll_to_element(locator={'text': 'Element That Does Not Exist'})


