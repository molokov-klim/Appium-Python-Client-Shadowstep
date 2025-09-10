import time

import pytest
from icecream import ic  # noqa: F401

from shadowstep.element.element import Element
from shadowstep.locator import UiSelector
from shadowstep.shadowstep import Shadowstep


class TestGetElement:

    @pytest.mark.parametrize(
        "locator, expected_package, expected_class_, expected_resource_id",  # noqa: PT006
        [
            # dict
            (
                    {"text": "Network & internet"},
                    "com.android.settings", "android.widget.TextView", "android:id/title"),

            # xpath
            (
                    ("xpath", '//*[@text="Network & internet"]'),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),

            # uiselector
            (
                    UiSelector().text("Network & internet"),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),
        ]
    )
    def test_get_element_positive(self,
                                  app: Shadowstep, stability: None,
                                  android_settings_open_close: None,
                                  android_settings_recycler: Element,
                                  locator,
                                  expected_package, expected_class_, expected_resource_id):
        inner_element = android_settings_recycler.get_element(locator=locator)
        assert isinstance(inner_element, Element)  # noqa: S101
        assert inner_element.package == expected_package  # noqa: S101
        assert inner_element.class_ == expected_class_  # noqa: S101
        assert inner_element.resource_id == expected_resource_id  # noqa: S101

    @pytest.mark.parametrize(
        "locator, expected_package, expected_class_, expected_resource_id",  # noqa: PT006
        [
            # dict
            (
                    {"textContains": "ork & int"},
                    "com.android.settings", "android.widget.TextView", "android:id/title"),

            # xpath
            (
                    ("xpath", '//*[contains(@text,"ork & int")]'),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),

            # uiselector
            (
                    UiSelector().textContains("ork & int"),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),
        ]
    )
    def test_get_element_contains(self,
                                  app: Shadowstep, stability: None,
                                  android_settings_open_close: None,
                                  android_settings_recycler: Element,
                                  locator,
                                  expected_package, expected_class_, expected_resource_id):
        inner_element = android_settings_recycler.get_element(locator=locator)
        assert isinstance(inner_element, Element)  # noqa: S101
        assert inner_element.package == expected_package  # noqa: S101
        assert inner_element.class_ == expected_class_  # noqa: S101
        assert inner_element.resource_id == expected_resource_id  # noqa: S101

    @pytest.mark.parametrize(
        "locator, expected_package, expected_class_, expected_resource_id",  # noqa: PT006
        [
            # dict
            (
                    {"textStartsWith": "Netwo"},
                    "com.android.settings", "android.widget.TextView", "android:id/title"),

            # xpath
            (
                    ("xpath", '//*[starts-with(@text,"Netwo")]'),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),

            # uiselector
            (
                    UiSelector().textStartsWith("Netwo"),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),
        ]
    )
    def test_get_element_starts_with(self,
                                     app: Shadowstep, stability: None,
                                     android_settings_open_close: None,
                                     android_settings_recycler: Element,
                                     locator,
                                     expected_package, expected_class_, expected_resource_id):
        inner_element = android_settings_recycler.get_element(locator=locator)
        assert isinstance(inner_element, Element)  # noqa: S101
        assert inner_element.package == expected_package  # noqa: S101
        assert inner_element.class_ == expected_class_  # noqa: S101
        assert inner_element.resource_id == expected_resource_id  # noqa: S101

    @pytest.mark.parametrize(
        "locator, expected_package, expected_class_, expected_resource_id",  # noqa: PT006
        [
            # dict
            (
                    {"classMatches": "TextView"},
                    "com.android.settings", "android.widget.TextView", "com.android.settings:id/homepage_title"
            ),

            # xpath
            (
                    ("xpath", '//*[matches(@class,".*Text.*")]'),
                    "com.android.settings", "android.widget.TextView", "com.android.settings:id/homepage_title"
            ),

            # uiselector
            (
                    UiSelector().textMatches(".*Settings"),
                    "com.android.settings", "android.widget.TextView", "com.android.settings:id/homepage_title"
            ),
        ]
    )
    def test_get_element_matches(self,
                                 app: Shadowstep, stability: None,
                                 android_settings_open_close: None,
                                 android_settings_recycler: Element,
                                 locator,
                                 expected_package, expected_class_, expected_resource_id):
        inner_element = android_settings_recycler.get_element(locator=locator)
        assert isinstance(inner_element, Element)  # noqa: S101
        assert inner_element.package == expected_package  # noqa: S101
        assert inner_element.class_ == expected_class_  # noqa: S101
        assert inner_element.resource_id == expected_resource_id  # noqa: S101

    def test_get_element_repeated_search(self,
                                         app: Shadowstep, stability: None,
                                         android_settings_open_close: None,
                                         android_settings_recycler: Element):
        element1 = app.get_element(locator={"text": "Network & internet"})
        element2 = app.get_element(locator={"text": "Network & internet"})
        assert element1 is not None  # noqa: S101  # noqa: S101
        assert element2 is not None  # noqa: S101  # noqa: S101
        assert element1.locator == element2.locator  # noqa: S101  # noqa: S101

    def test_get_element_disconnected(self,
                                      app: Shadowstep, stability: None,
                                      android_settings_open_close: None,
                                      android_settings_recycler: Element):
        app.disconnect()
        assert not app.is_connected()  # noqa: S101  # noqa: S101
        element = app.get_element(locator={"text": "Network & internet"})
        app.reconnect()
        assert app.is_connected()  # noqa: S101  # noqa: S101
        assert isinstance(element, Element)  # noqa: S101  # noqa: S101
        assert element.locator == {"text": "Network & internet"}  # noqa: S101  # noqa: S101


class TestGetElements:
    @pytest.mark.parametrize(
        "locator",  # noqa: PT006
        [
            # dict
            (
                    {"resource-id": "android:id/title"}
            ),
            # xpath
            (
                    ("xpath", '//*[@resource-id="android:id/title"]')
            ),

            # uiselector
            (
                    UiSelector().resourceId("android:id/title")
            ),
        ]
    )
    def test_get_elements(self,
                          app: Shadowstep, stability: None,
                          android_settings_open_close: None,
                          android_settings_recycler: Element,
                          locator):
        start = time.perf_counter()
        inner_elements = android_settings_recycler.get_elements(locator=locator)
        elapsed = time.perf_counter() - start

        app.logger.info(f"Время выполнения get_elements: {elapsed:.4f} сек")
        actual_text_list = []
        expected_text_list = ["Network & internet", "Connected devices", "Apps", "Notifications", "Battery"]

        assert isinstance(inner_elements, list)  # noqa: S101  # noqa: S101
        for inner_element in inner_elements:
            actual_text_list.append(inner_element.text)

        assert actual_text_list == expected_text_list

        app.logger.info(f"Время выполнения get_elements: {elapsed:.4f} сек")


class TestGetParent:
    @pytest.mark.parametrize(
        "child",  # noqa: PT006
        [
            # dict
            (
                    {"text": "Network & internet"}
            ),
            # xpath
            (
                    ("xpath", '//*[@text="Network & internet"]')
            ),

            # uiselector
            (
                    UiSelector().text("Network & internet")
            ),
        ]
    )
    def test_get_parent(self,
                        app: Shadowstep, stability: None,
                        android_settings_open_close: None,
                        android_settings_recycler: Element,
                        child):
        actual_parent = app.get_element(child).get_parent()
        assert isinstance(actual_parent, Element)  # noqa: S101

        expected_parent_locator = ("xpath", '//*[@text="Network & internet"]/..')
        expected_parent_class = "android.widget.RelativeLayout"
        expected_parent_resource_id = "com.android.settings:id/text_frame"

        assert actual_parent.locator == expected_parent_locator  # noqa: S101
        assert actual_parent.class_ == expected_parent_class  # noqa: S101
        assert actual_parent.resource_id == expected_parent_resource_id  # noqa: S101

    @pytest.mark.parametrize(
        "child",  # noqa: PT006
        [
            (
                    {"text": "Network & internet"}
            ),
            (
                    ("xpath", '//*[@text="Network & internet"]')
            ),
            (
                    UiSelector().text("Network & internet")
            ),
        ]
    )
    def test_get_parents(self,
                         app: Shadowstep, stability: None,
                         android_settings_open_close: None,
                         android_settings_recycler: Element,
                         child):
        parents = app.get_element(child).get_parents()
        assert len(parents) == 12   # noqa: S101
        assert isinstance(parents, list) and parents, "Список родителей пуст"  # noqa: S101, PT018
        assert all(isinstance(p, Element) for p in parents)  # noqa: S101

        brokens = []

        for parent in parents:
            parent.timeout = 1
            ic()
            ic(parent)
            ic(parent.locator)
            ic(parent)
            try:
                ic(parent.package)
                assert parent.package == "com.android.settings"  # noqa: S101
            except Exception as error:
                ic("::::::::::::::::::::::::::::::::::")
                from loguru import logger
                logger.exception(error)
                brokens.append(parent)
                
        ic(")))))))))))))))(((((((((((((")
        ic(len(brokens))
            
        for broken in brokens:
            ic()
            ic("___")
            ic(broken)
            ic(app.driver.page_source)


        nearest_parent = parents[-1]
        expected_parent_class = "android.widget.RelativeLayout"
        expected_parent_resource_id = "com.android.settings:id/text_frame"

        assert nearest_parent.resource_id == expected_parent_resource_id  # noqa: S101
        assert nearest_parent.class_ == expected_parent_class  # noqa: S101
