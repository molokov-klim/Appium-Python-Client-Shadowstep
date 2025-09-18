import logging
import time

import pytest

from shadowstep.element.element import Element
from shadowstep.locator import UiSelector
from shadowstep.shadowstep import Shadowstep

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/element/test_element_dom.py
"""

logger = logging.getLogger(__name__)

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
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),

            # xpath
            (
                    ("xpath", '//*[matches(@class,".*Text.*")]'),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
            ),

            # uiselector
            (
                    UiSelector().classNameMatches(".*Text"),
                    "com.android.settings", "android.widget.TextView", "android:id/title"
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
        logger.info(inner_element.package)
        logger.info(inner_element.class_)
        logger.info(inner_element.resource_id)
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

        assert isinstance(inner_elements, list)  # noqa: S101
        for inner_element in inner_elements:
            actual_text_list.append(inner_element.text)

        assert actual_text_list == expected_text_list  # noqa: S101

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
                    ("xpath", "//*[@text='Network & internet']")
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

        expected_parent_locator = ("xpath", "//*[@text='Network & internet']/..")
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
        assert len(parents) == 12  # noqa: S101
        assert isinstance(parents, list) and parents, "Список родителей пуст"  # noqa: S101, PT018
        assert all(isinstance(p, Element) for p in parents)  # noqa: S101

        brokens = []

        for parent in parents:
            parent.timeout = 1
            try:
                assert parent.package == "com.android.settings"  # noqa: S101
            except Exception:
                brokens.append(parent)

        nearest_parent = parents[-1]
        expected_parent_class = "android.widget.RelativeLayout"
        expected_parent_resource_id = "com.android.settings:id/text_frame"

        assert nearest_parent.resource_id == expected_parent_resource_id  # noqa: S101
        assert nearest_parent.class_ == expected_parent_class  # noqa: S101


class TestGetSibling:
    @pytest.mark.parametrize(
        "locator, sibling_locator, expected_text, expected_class, expected_resource_id",  # noqa: PT006
        [
            # dict
            (
                    {"text": "Network & internet"},
                    {"class": "android.widget.TextView"},
                    "Mobile, Wi‑Fi, hotspot", "android.widget.TextView", "android:id/summary"
            ),
            # xpath
            (
                    ("xpath", '//*[@text="Network & internet"]'),
                    ("xpath", '//*[@class="android.widget.TextView"]'),
                    "Mobile, Wi‑Fi, hotspot", "android.widget.TextView", "android:id/summary"
            ),
            # uiselector
            (
                    UiSelector().text("Network & internet"),
                    UiSelector().className("android.widget.TextView"),
                    "Mobile, Wi‑Fi, hotspot", "android.widget.TextView", "android:id/summary"
            ),
        ]
    )
    def test_get_sibling(self,
                         app: Shadowstep, stability: None,
                         android_settings_open_close: None,
                         android_settings_recycler: Element,
                         locator, sibling_locator, expected_text, expected_class, expected_resource_id):
        element = android_settings_recycler.get_element(locator=locator)
        sibling = element.get_sibling(sibling_locator)
        assert isinstance(sibling, Element)  # noqa: S101
        assert sibling.text == expected_text  # noqa: S101
        assert sibling.class_ == expected_class  # noqa: S101
        assert sibling.resource_id == expected_resource_id  # noqa: S101

    @pytest.mark.parametrize(
        "locator, siblings_locator, expected_texts",  # noqa: PT006
        [
            # dict
            (
                    {"text": "Network & internet"},
                    {"class": "android.widget.TextView"},
                    ["Mobile, Wi‑Fi, hotspot"]
            ),
            # xpath
            (
                    ("xpath", '//*[@text="Network & internet"]'),
                    ("xpath", '//*[contains(@class,"TextView")]'),
                    ["Mobile, Wi‑Fi, hotspot"]
            ),
            # uiselector
            (
                    UiSelector().text("Network & internet"),
                    UiSelector().className("android.widget.TextView"),
                    ["Mobile, Wi‑Fi, hotspot"]
            ),
        ]
    )
    def test_get_siblings(self,
                          app: Shadowstep, stability: None,
                          android_settings_open_close: None,
                          android_settings_recycler: Element,
                          locator, siblings_locator, expected_texts):
        element = android_settings_recycler.get_element(locator=locator)
        siblings = element.get_siblings(siblings_locator)
        assert isinstance(siblings, list) and siblings  # noqa: S101, PT018
        actual_texts = [e.text for e in siblings]
        assert actual_texts == expected_texts  # noqa: S101
        assert all(isinstance(e, Element) for e in siblings)  # noqa: S101


class TestGetCousin:
    @pytest.mark.parametrize(
        "locator, cousin_locator, expected_text, expected_class, expected_resource_id",  # noqa: PT006
        [
            # dict
            (
                    {"text": "Bluetooth, pairing"},
                    {"resource-id": "android:id/summary"},
                    "Mobile, Wi‑Fi, hotspot", "android.widget.TextView", "android:id/summary"
            ),
            # xpath
            (
                    ("xpath", '//*[@text="Bluetooth, pairing"]'),
                    ("xpath", '//*[@resource-id="android:id/summary"]'),
                    "Mobile, Wi‑Fi, hotspot", "android.widget.TextView", "android:id/summary"
            ),
            # uiselector
            (
                    UiSelector().text("Bluetooth, pairing"),
                    UiSelector().resourceId("android:id/summary"),
                    "Mobile, Wi‑Fi, hotspot", "android.widget.TextView", "android:id/summary"
            ),
        ]
    )
    def test_get_cousin(self,
                        app: Shadowstep, stability: None,
                        android_settings_open_close: None,
                        android_settings_recycler: Element,
                        locator, cousin_locator, expected_text, expected_class, expected_resource_id):
        element = android_settings_recycler.get_element(locator=locator)
        cousin = element.get_cousin(cousin_locator, 2)
        assert isinstance(cousin, Element)  # noqa: S101
        assert cousin.text == expected_text  # noqa: S101
        assert cousin.class_ == expected_class  # noqa: S101
        assert cousin.resource_id == expected_resource_id  # noqa: S101

    @pytest.mark.parametrize(
        "locator, cousin_locator, expected_text_list",  # noqa: PT006
        [
            # dict
            (
                    {"text": "Bluetooth, pairing"},
                    {"resource-id": "android:id/summary"},
                    ["Mobile, Wi‑Fi, hotspot",
                     "Bluetooth, pairing",
                     "Recent apps, default apps",
                     "Notification history, conversations",
                     "100%"]
            ),
            # xpath
            (
                    ("xpath", '//*[@text="Bluetooth, pairing"]'),
                    ("xpath", '//*[@resource-id="android:id/summary"]'),
                    ["Mobile, Wi‑Fi, hotspot",
                     "Bluetooth, pairing",
                     "Recent apps, default apps",
                     "Notification history, conversations",
                     "100%"]
            ),
            # uiselector
            (
                    UiSelector().text("Bluetooth, pairing"),
                    UiSelector().resourceId("android:id/summary"),
                    ["Mobile, Wi‑Fi, hotspot",
                     "Bluetooth, pairing",
                     "Recent apps, default apps",
                     "Notification history, conversations",
                     "100%"]
            ),
        ]
    )
    def test_get_cousins(self,
                         app: Shadowstep, stability: None,
                         android_settings_open_close: None,
                         android_settings_recycler: Element,
                         locator, cousin_locator, expected_text_list):
        element = android_settings_recycler.get_element(locator=locator)
        cousins = element.get_cousins(cousin_locator, 2)
        actual_text_list = []
        for cousin in cousins:
            actual_text_list.append(cousin.text)
        assert actual_text_list == expected_text_list  # noqa: S101
