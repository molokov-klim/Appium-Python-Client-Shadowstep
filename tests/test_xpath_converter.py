# tests/test_xpath_converter.py
import logging
from typing import Any

import pytest

from shadowstep.locator_converter.types.xpath import XPathAttribute

logger = logging.getLogger(__name__)


class TestXpathConverter:

    @pytest.mark.parametrize(
        "method_name, arg, expected",
        [
            # --- text-based ---
            (XPathAttribute.TEXT, "Привет", {"text": "Привет"}),
            (XPathAttribute.TEXT_CONTAINS, "Hello", {"textContains": "Hello"}),
            (XPathAttribute.TEXT_STARTS_WITH, "Оплат", {"textStartsWith": "Оплат"}),
            (XPathAttribute.TEXT_MATCHES, ".*Тест.*", {"textMatches": ".*Тест.*"}),

            # --- description ---
            (XPathAttribute.DESCRIPTION, "desc", {"content-desc": "desc"}),
            (XPathAttribute.DESCRIPTION_CONTAINS, "part", {"content-descContains": "part"}),
            (XPathAttribute.DESCRIPTION_STARTS_WITH, "start", {"content-descStartsWith": "start"}),
            (XPathAttribute.DESCRIPTION_MATCHES, "regex.*", {"content-descMatches": "regex.*"}),

            # --- resource id / package ---
            (XPathAttribute.RESOURCE_ID, "resId", {"resource-id": "resId"}),
            (XPathAttribute.RESOURCE_ID_MATCHES, "res.*", {"resource-idMatches": "res.*"}),
            (XPathAttribute.PACKAGE_NAME, "pkg.name", {"package": "pkg.name"}),
            (XPathAttribute.PACKAGE_NAME_MATCHES, "pkg.name", {"packageMatches": "pkg.name"}),

            # --- class ---
            (XPathAttribute.CLASS_NAME, "android.widget.Button", {"class": "android.widget.Button"}),
            (XPathAttribute.CLASS_NAME_MATCHES, ".*Button", {"classNameMatches": ".*Button"}),

            # --- bool props ---
            (XPathAttribute.CHECKABLE, True, {"checkable": True}),
            (XPathAttribute.CHECKED, False, {"checked": False}),
            (XPathAttribute.CLICKABLE, True, {"clickable": True}),
            (XPathAttribute.ENABLED, False, {"enabled": False}),
            (XPathAttribute.FOCUSABLE, True, {"focusable": True}),
            (XPathAttribute.FOCUSED, False, {"focused": False}),
            (XPathAttribute.LONG_CLICKABLE, True, {"longClickable": True}),
            (XPathAttribute.SCROLLABLE, False, {"scrollable": False}),
            (XPathAttribute.SELECTED, True, {"selected": True}),

            # --- numeric ---
            (XPathAttribute.INDEX, 2, {"index": 2}),
            (XPathAttribute.INSTANCE, 0, {"instance": 0}),
        ]
    )
    def test_xpath_to_dict_attributes(self, method_name: str, arg: Any, expected: dict[str, Any]):
        ...

    @pytest.mark.parametrize(
        "xpath, expected",
        [
            # 1. text + class + instance
            (
                    '//*[@text="OK"][@class="android.widget.Button"][position()=1]',
                    {"text": "OK", "class": "android.widget.Button", "instance": 0},
            ),
            # 2. contains text + clickable
            (
                    '//*[contains(@text, "Подтвердить")][@clickable="true"]',
                    {"textContains": "Подтвердить", "clickable": True},
            ),
            # 3. resource-id + enabled
            (
                    '//*[@resource-id="ru.app:id/btn"][@enabled="false"]',
                    {"resource-id": "ru.app:id/btn", "enabled": False},
            ),
            # 4. textStartsWith + package + focusable
            (
                    '//*[starts-with(@text, "Нач")][@package="ru.app"][@focusable="true"]',
                    {"textStartsWith": "Нач", "packageName": "ru.app", "focusable": True},
            ),
            # 5. descriptionContains + longClickable + class
            (
                    '//*[contains(@content-desc, "icon")][@long-clickable="true"][@class="android.widget.ImageView"]',
                    {"descriptionContains": "icon", "longClickable": True, "class": "android.widget.ImageView"},
            ),
            # 6. regex text + scrollable
            (
                    '//*[matches(@text, ".*Тест.*")][@scrollable="false"]',
                    {"textMatches": ".*Тест.*", "scrollable": False},
            ),
            # 7. description + checked + index
            (
                    '//*[@content-desc="switch"][@checked="true"][@index="2"]',
                    {"description": "switch", "checked": True, "index": 2},
            ),
            # 8. package + enabled + selected
            (
                    '//*[@package="ru.pkg"][@enabled="true"][@selected="false"]',
                    {"packageName": "ru.pkg", "enabled": True, "selected": False},
            ),
            # 9. classNameMatches + focusable + instance
            (
                    '//*[matches(@class, ".*EditText")][@focusable="true"][position()=3]',
                    {"classNameMatches": ".*EditText", "focusable": True, "instance": 2},
            ),
            # 10. text + descriptionMatches + clickable
            (
                    '//*[@text="Save"][matches(@content-desc, ".*save.*")][@clickable="true"]',
                    {"text": "Save", "descriptionMatches": ".*save.*", "clickable": True},
            ),
            # 11. resource-idMatches + textContains + enabled
            (
                    '//*[matches(@resource-id, ".*btn.*")][contains(@text, "Отправить")][@enabled="true"]',
                    {"resourceIdMatches": ".*btn.*", "textContains": "Отправить", "enabled": True},
            ),
            # 12. class + descriptionStartsWith + longClickable
            (
                    '//*[@class="android.widget.TextView"][starts-with(@content-desc, "hint")][@long-clickable="false"]',
                    {"class": "android.widget.TextView", "descriptionStartsWith": "hint", "longClickable": False},
            ),
            # 13. text + packageMatches + checked
            (
                    '//*[@text="OK"][matches(@package, "com.example.*")][@checked="true"]',
                    {"text": "OK", "packageNameMatches": "com.example.*", "checked": True},
            ),
            # 14. descriptionContains + index + instance
            (
                    '//*[contains(@content-desc, "item")][@index="5"][position()=2]',
                    {"descriptionContains": "item", "index": 5, "instance": 1},
            ),
            # 15. textMatches + class + selected
            (
                    '//*[matches(@text, ".*done.*")][@class="android.widget.CheckBox"][@selected="true"]',
                    {"textMatches": ".*done.*", "class": "android.widget.CheckBox", "selected": True},
            ),
            # 16. resource-id + text + focusable + focused
            (
                    '//*[@resource-id="ru.app:id/input"][@text="Login"][@focusable="true"][@focused="false"]',
                    {"resource-id": "ru.app:id/input", "text": "Login", "focusable": True, "focused": False},
            ),
            # 17. description + package + enabled + clickable
            (
                    '//*[@content-desc="menu"][@package="ru.app"][@enabled="true"][@clickable="true"]',
                    {"description": "menu", "packageName": "ru.app", "enabled": True, "clickable": True},
            ),
            # 18. textStartsWith + classNameMatches + scrollable
            (
                    '//*[starts-with(@text, "File")][matches(@class, ".*ListView")][@scrollable="true"]',
                    {"textStartsWith": "File", "classNameMatches": ".*ListView", "scrollable": True},
            ),
            # 19. resource-idMatches + descriptionMatches + longClickable
            (
                    '//*[matches(@resource-id, ".*toolbar")][matches(@content-desc, ".*tool.*")][@long-clickable="true"]',
                    {"resourceIdMatches": ".*toolbar", "descriptionMatches": ".*tool.*", "longClickable": True},
            ),
            # 20. combo монстр
            (
                    '//*[@text="Submit"][contains(@content-desc, "send")][@class="android.widget.Button"][@enabled="true"][@clickable="true"][@index="1"][position()=4]',
                    {
                        "text": "Submit",
                        "descriptionContains": "send",
                        "class": "android.widget.Button",
                        "enabled": True,
                        "clickable": True,
                        "index": 1,
                        "instance": 3,
                    },
            ),
            (
                    '//*[@text="Оплатить"]/*[@class="android.widget.ImageView"]',
                    {
                        "text": "Оплатить",
                        "childSelector": {"class": "android.widget.ImageView"},
                    },
            ),
            # 22. class + childSelector с textContains
            (
                    '//*[@class="android.widget.LinearLayout"]/*[contains(@text, "Email")]',
                    {
                        "class": "android.widget.LinearLayout",
                        "childSelector": {"textContains": "Email"},
                    },
            ),
            # 23. resource-id + parent
            (
                    '//*[@resource-id="ru.app:id/input"]/..[@class="android.widget.ScrollView"]',
                    {
                        "resource-id": "ru.app:id/input",
                        "fromParent": {"class": "android.widget.ScrollView"},
                    },
            ),
            # 24. combo: class + textStartsWith + childSelector с description
            (
                    '//*[@class="android.widget.Button"][starts-with(@text,"Дал")]'
                    '/*[@content-desc="icon"]',
                    {
                        "class": "android.widget.Button",
                        "textStartsWith": "Дал",
                        "childSelector": {"description": "icon"},
                    },
            ),
            # 25. вложенность: parent + child
            (
                    '//*[@text="Settings"]/..[@class="android.widget.FrameLayout"]'
                    '/*[@resource-id="ru.app:id/switch"]',
                    {
                        "text": "Settings",
                        "fromParent": {"class": "android.widget.FrameLayout"},
                        "childSelector": {"resource-id": "ru.app:id/switch"},
                    },
            ),
        ]
    )
    def test_xpath_to_dict(self, xpath: str, expected: dict[str, Any]):
        ...

    def test_xpath_to_dict_negative(self):
        ...

    def test_xpath_to_ui_attributes(self):
        ...

    def test_xpath_to_ui(self):
        ...

    def test_xpath_to_ui_negative(self):
        ...
