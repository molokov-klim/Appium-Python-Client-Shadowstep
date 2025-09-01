# tests/test_xpath_converter.py
import logging
from typing import Any

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator_converter.xpath_converter import XPathConverter

logger = logging.getLogger(__name__)


class TestXPathConverter:

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            # --- text-based ---
            ('//*[@text="Привет"]', {"text": "Привет"}),
            ('//*[contains(@text,"Hello")]', {"textContains": "Hello"}),
            ('//*[starts-with(@text,"Оплат")]', {"textStartsWith": "Оплат"}),
            ('//*[matches(@text,".*Тест.*")]', {"textMatches": ".*Тест.*"}),

            # --- description ---
            ('//*[@content-desc="desc"]', {"description": "desc"}),
            ('//*[contains(@content-desc,"part")]', {"descriptionContains": "part"}),
            ('//*[starts-with(@content-desc,"start")]', {"descriptionStartsWith": "start"}),
            ('//*[matches(@content-desc,"regex.*")]', {"descriptionMatches": "regex.*"}),

            # --- resource id / package ---
            ('//*[@resource-id="resId"]', {"resource-id": "resId"}),
            ('//*[matches(@resource-id,"res.*")]', {"resource-idMatches": "res.*"}),
            ('//*[@package="pkg.name"]', {"package": "pkg.name"}),
            ('//*[matches(@package,"pkg.name")]', {"packageMatches": "pkg.name"}),

            # --- class ---
            ('//*[@class="android.widget.Button"]', {"class": "android.widget.Button"}),
            ('//*[matches(@class,".*Button")]', {"classMatches": ".*Button"}),

            # --- bool props ---
            ('//*[@checkable="true"]', {"checkable": True}),
            ('//*[@checked="false"]', {"checked": False}),
            ('//*[@clickable="true"]', {"clickable": True}),
            ('//*[@enabled="true"]', {"enabled": True}),
            ('//*[@focusable="true"]', {"focusable": True}),
            ('//*[@focused="false"]', {"focused": False}),
            ('//*[@long-clickable="true"]', {"long-clickable": True}),
            ('//*[@scrollable="false"]', {"scrollable": False}),
            ('//*[@selected="false"]', {"selected": False}),
            ('//*[@password="true"]', {"password": True}),

            # --- numeric ---
            ("//*[position()=3]", {"index": 2}),
            ("//*[6]", {"instance": 5}),
        ]
    )
    def test_xpath_to_dict_attributes(self, xpath: str, expected: dict[str, Any]):
        """Test conversion of XPath attributes to dictionary format."""
        converter = XPathConverter()
        logger.info(f"{xpath=}")
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info(f"{shadowstep_dict=}")
        logger.info(f"{expected=}")
        assert expected == shadowstep_dict  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            (
                    '//*[@text="OK"][@class="android.widget.Button"][position()=1]',
                    {"text": "OK", "class": "android.widget.Button", "index": 0},
            ),
            (
                    '//*[contains(@text, "Подтвердить")][@clickable="true"]',
                    {"textContains": "Подтвердить", "clickable": True},
            ),
            (
                    '//*[@resource-id="ru.app:id/btn"][@enabled="false"]',
                    {"resource-id": "ru.app:id/btn", "enabled": False},
            ),
            (
                    '//*[starts-with(@text, "Нач")][@package="ru.app"][@focusable="true"]',
                    {"textStartsWith": "Нач", "package": "ru.app", "focusable": True},
            ),
            (
                    '//*[contains(@content-desc, "icon")][@long-clickable="true"][@class="android.widget.ImageView"]',
                    {"descriptionContains": "icon", "long-clickable": True, "class": "android.widget.ImageView"},
            ),
            (
                    '//*[matches(@text, ".*Тест.*")][@scrollable="false"]',
                    {"textMatches": ".*Тест.*", "scrollable": False},
            ),
            (
                    '//*[@content-desc="switch"][@checked="true"][position()=2]',
                    {"description": "switch", "checked": True, "index": 1},
            ),
            (
                    '//*[@package="ru.pkg"][@enabled="true"][@selected="false"]',
                    {"package": "ru.pkg", "enabled": True, "selected": False},
            ),
            (
                    '//*[matches(@class, ".*EditText")][@focusable="true"][position()=3]',
                    {"classMatches": ".*EditText", "focusable": True, "index": 2},
            ),
            (
                    '//*[@text="Save"][matches(@content-desc, ".*save.*")][@clickable="true"]',
                    {"text": "Save", "descriptionMatches": ".*save.*", "clickable": True},
            ),
            (
                    '//*[matches(@resource-id, ".*btn.*")][contains(@text, "Отправить")][@enabled="true"]',
                    {"resource-idMatches": ".*btn.*", "textContains": "Отправить", "enabled": True},
            ),
            (
                    '//*[@class="android.widget.TextView"][starts-with(@content-desc, "hint")][@long-clickable="false"]',
                    {"class": "android.widget.TextView", "descriptionStartsWith": "hint", "long-clickable": False},
            ),
            (
                    '//*[@text="OK"][matches(@package, "com.example.*")][@checked="true"]',
                    {"text": "OK", "packageMatches": "com.example.*", "checked": True},
            ),
            (
                    '//*[contains(@content-desc, "item")][position()=5][position()=2]',
                    {"descriptionContains": "item", "index": 1},  # Last index wins
            ),
            (
                    '//*[matches(@text, ".*done.*")][@class="android.widget.CheckBox"][@selected="true"]',
                    {"textMatches": ".*done.*", "class": "android.widget.CheckBox", "selected": True},
            ),
            (
                    '//*[@resource-id="ru.app:id/input"][@text="Login"][@focusable="true"][@focused="false"]',
                    {"resource-id": "ru.app:id/input", "text": "Login", "focusable": True, "focused": False},
            ),
            (
                    '//*[@content-desc="menu"][@package="ru.app"][@enabled="true"][@clickable="true"]',
                    {"description": "menu", "package": "ru.app", "enabled": True, "clickable": True},
            ),
            (
                    '//*[starts-with(@text, "File")][matches(@class, ".*ListView")][@scrollable="true"]',
                    {"textStartsWith": "File", "classMatches": ".*ListView", "scrollable": True},
            ),
            (
                    '//*[matches(@resource-id, ".*toolbar")][matches(@content-desc, ".*tool.*")][@long-clickable="true"]',
                    {"resource-idMatches": ".*toolbar", "descriptionMatches": ".*tool.*", "long-clickable": True},
            ),
            (
                    '//*[@text="Submit"][contains(@content-desc, "send")][@class="android.widget.Button"][@enabled="true"][@clickable="true"][position()=1][position()=4]',
                    {
                        "text": "Submit",
                        "descriptionContains": "send",
                        "class": "android.widget.Button",
                        "enabled": True,
                        "clickable": True,
                        "index": 3,  # Last index wins
                    },
            ),
            (
                    '//*[@text="Оплатить"]/*[@class="android.widget.ImageView"]',
                    {
                        "text": "Оплатить",
                        "childSelector": {"class": "android.widget.ImageView"},
                    },
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[contains(@text, "Email")]',
                    {
                        "class": "android.widget.LinearLayout",
                        "childSelector": {"textContains": "Email"},
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"]/..[@class="android.widget.ScrollView"]',
                    {
                        "resource-id": "ru.app:id/input",
                        "fromParent": {"class": "android.widget.ScrollView"},
                    },
            ),
            (
                    '//*[@class="android.widget.Button"][starts-with(@text,"Дал")]/*[@content-desc="icon"]',
                    {
                        "class": "android.widget.Button",
                        "textStartsWith": "Дал",
                        "childSelector": {"description": "icon"},
                    },
            ),
            (
                    '//*[@text="Settings"]/..[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        "text": "Settings",
                        "fromParent": {"class": "android.widget.FrameLayout"},
                        "childSelector": {"resource-id": "ru.app:id/switch"},
                    },
            ),
        ]
    )
    def test_xpath_to_dict(self, xpath: str, expected: dict[str, Any]):
        """Test conversion of complex XPath expressions to dictionary format."""
        converter = XPathConverter()
        shadowstep_dict = converter.xpath_to_dict(xpath)
        assert expected == shadowstep_dict  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            # --- text-based ---
            ('//*[@text="Привет"]', 'new UiSelector().text("Привет");'),
            ('//*[contains(@text,"Hello")]', 'new UiSelector().textContains("Hello");'),
            ('//*[starts-with(@text,"Оплат")]', 'new UiSelector().textStartsWith("Оплат");'),
            ('//*[matches(@text,".*Тест.*")]', 'new UiSelector().textMatches(".*Тест.*");'),

            # --- description ---
            ('//*[@content-desc="desc"]', 'new UiSelector().description("desc");'),
            ('//*[contains(@content-desc,"part")]', 'new UiSelector().descriptionContains("part");'),
            ('//*[starts-with(@content-desc,"start")]', 'new UiSelector().descriptionStartsWith("start");'),
            ('//*[matches(@content-desc,"regex.*")]', 'new UiSelector().descriptionMatches("regex.*");'),

            # --- resource id / package ---
            ('//*[@resource-id="resId"]', 'new UiSelector().resourceId("resId");'),
            ('//*[matches(@resource-id,"res.*")]', 'new UiSelector().resourceIdMatches("res.*");'),
            ('//*[@package="pkg.name"]', 'new UiSelector().packageName("pkg.name");'),
            ('//*[matches(@package,"pkg.name")]', 'new UiSelector().packageNameMatches("pkg.name");'),

            # --- class ---
            ('//*[@class="android.widget.Button"]', 'new UiSelector().className("android.widget.Button");'),
            ('//*[matches(@class,".*Button")]', 'new UiSelector().classNameMatches(".*Button");'),

            # --- bool props ---
            ('//*[@checkable="true"]', "new UiSelector().checkable(true);"),
            ('//*[@checked="false"]', "new UiSelector().checked(false);"),
            ('//*[@clickable="true"]', "new UiSelector().clickable(true);"),
            ('//*[@enabled="true"]', "new UiSelector().enabled(true);"),
            ('//*[@focusable="true"]', "new UiSelector().focusable(true);"),
            ('//*[@focused="false"]', "new UiSelector().focused(false);"),
            ('//*[@long-clickable="true"]', "new UiSelector().longClickable(true);"),
            ('//*[@scrollable="false"]', "new UiSelector().scrollable(false);"),
            ('//*[@selected="false"]', "new UiSelector().selected(false);"),
            ('//*[@password="true"]', "new UiSelector().password(true);"),

            # --- numeric ---
            ("//*[position()=3]", "new UiSelector().index(2);"),
            ("//*[6]", "new UiSelector().instance(5);"),
        ]
    )
    def test_xpath_to_ui_attributes(self, xpath: str, expected: str):
        """Test conversion of XPath attributes to UiSelector format."""
        converter = XPathConverter()
        ui_selector = converter.xpath_to_ui(xpath)
        assert expected == ui_selector  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            (
                    '//*[starts-with(@text,"Оплат")][@class="android.widget.Button"]/*[@class="android.widget.ImageView"]',
                    'new UiSelector().textStartsWith("Оплат").className("android.widget.Button").childSelector(new UiSelector().className("android.widget.ImageView"));',
            ),
            (
                    '//*[@class="android.widget.EditText"][@focused="true"][1]',
                    'new UiSelector().className("android.widget.EditText").focused(true).instance(0);',
            ),
            (
                    '//*[@package="ru.sigma.app.debug"][matches(@resource-id, ".*:id/btn.*")]',
                    'new UiSelector().packageName("ru.sigma.app.debug").resourceIdMatches(".*:id/btn.*");',
            ),
            (
                    '//*[contains(@content-desc,"Карта")][@clickable="true"]',
                    'new UiSelector().descriptionContains("Карта").clickable(true);',
            ),
            (
                    '//*[@class="androidx.appcompat.app.ActionBar$Tab"][position()=3]',
                    'new UiSelector().className("androidx.appcompat.app.ActionBar$Tab").index(2);',
            ),
            (
                    '//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.sigma.app.debug:id/paymentMethods"]',
                    'new UiSelector().className("android.widget.RadioButton").fromParent(new UiSelector().resourceId("ru.sigma.app.debug:id/paymentMethods"));',
            ),
            (
                    '//*[@class="android.widget.EditText"][starts-with(@text,"+7")][@enabled="true"]',
                    'new UiSelector().className("android.widget.EditText").textStartsWith("+7").enabled(true);',
            ),
            (
                    '//*[matches(@content-desc,"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")]',
                    'new UiSelector().descriptionMatches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");',
            ),
            (
                    '//*[@scrollable="true"]/*[@text="История"]',
                    'new UiSelector().scrollable(true).childSelector(new UiSelector().text("История"));',
            ),
            (
                    '//*[@class="android.widget.CheckBox"][@checkable="true"][@checked="false"][3]',
                    'new UiSelector().className("android.widget.CheckBox").checkable(true).checked(false).instance(2);',
            ),
            (
                    '//*[starts-with(@text,"Оплат")][contains(@text,"Карт")][@enabled="true"]',
                    'new UiSelector().textStartsWith("Оплат").textContains("Карт").enabled(true);',
            ),
            (
                    '//*[matches(@class,"android\\.widget\\..*Button")][2]',
                    'new UiSelector().classNameMatches("android\\.widget\\..*Button").instance(1);',
            ),
            (
                    '//*[@content-desc="Подтвердить"][@clickable="true"]/*[@class="android.widget.ImageView"]',
                    'new UiSelector().description("Подтвердить").clickable(true).childSelector(new UiSelector().className("android.widget.ImageView"));',
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[@class="android.widget.FrameLayout"]/*[@text="Список"]',
                    'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().className("android.widget.FrameLayout").childSelector(new UiSelector().text("Список")));',
            ),
            (
                    '//*[@class="android.widget.TextView"]/..//*[@class="android.widget.LinearLayout"][@enabled="true"][position()=1]',
                    'new UiSelector().className("android.widget.TextView").fromParent(new UiSelector().className("android.widget.LinearLayout").enabled(true).index(0));',
            ),
            (
                    '//*[@scrollable="false"][@clickable="false"][3]',
                    "new UiSelector().scrollable(false).clickable(false).instance(2);",
            ),
            (
                    '//*[contains(@text,"карт")][@resource-id="ru.sigma.app.debug:id/card_number"]',
                    'new UiSelector().textContains("карт").resourceId("ru.sigma.app.debug:id/card_number");',
            ),
            (
                    '//*[@text="Оплатить"][@long-clickable="false"]',
                    'new UiSelector().text("Оплатить").longClickable(false);',
            ),
            (
                    '//*[@class="android.widget.Button"][@selected="true"]',
                    'new UiSelector().className("android.widget.Button").selected(true);',
            ),
            (
                    '//*[@class="Button"][@long-clickable="true"][@package="com.example.app"]',
                    'new UiSelector().className("Button").longClickable(true).packageName("com.example.app");',
            ),
            (
                    '//*/*[@class="ListView"]/*[@text="Item"]',
                    'new UiSelector().childSelector(new UiSelector().className("ListView").childSelector(new UiSelector().text("Item")));',
            ),
            (
                    '//*/..//*[@class="Container"]/*[@text="Title"]',
                    'new UiSelector().fromParent(new UiSelector().className("Container").childSelector(new UiSelector().text("Title")));',
            ),
            (
                    '//*[@text="C:\\Windows\\Path"]',
                    'new UiSelector().text("C:\\Windows\\Path");',
            ),
            (
                    '//*[matches(@content-desc,".*\\d+.*")]',
                    'new UiSelector().descriptionMatches(".*\\d+.*");',
            ),
            (
                    '//*[@resource-id=""]',
                    'new UiSelector().resourceId("");',
            ),
            (
                    "//*[position()=1]",
                    "new UiSelector().index(0);",
            ),
            (
                    "//*[6]",
                    "new UiSelector().instance(5);",
            ),
            (
                    '//*[@focusable="true"][@password="true"]',
                    "new UiSelector().focusable(true).password(true);",
            ),
            (
                    '//*[contains(@text, "секция")][@class="android.widget.TextView"]',
                    'new UiSelector().textContains("секция").className("android.widget.TextView");',
            ),
            (
                    '//*[matches(@text, "\\d{3}-\\d{2}-\\d{4}")]',
                    'new UiSelector().textMatches("\\\\d{3}-\\\\d{2}-\\\\d{4}");',
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[@class="android.widget.FrameLayout"]/*[@class="android.widget.TextView"]',
                    'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().className("android.widget.FrameLayout").childSelector(new UiSelector().className("android.widget.TextView")));',
            ),
            (
                    '//*[@class="android.widget.Button"][@enabled="true"][@clickable="true"]',
                    'new UiSelector().className("android.widget.Button").enabled(true).clickable(true);',
            ),
            (
                    '//*[@class="android.widget.ImageView"]',
                    'new UiSelector().className("android.widget.ImageView");',
            ),
        ]
    )
    def test_xpath_to_ui(self, xpath: str, expected: str):
        """Test conversion of complex XPath expressions to UiSelector format."""
        converter = XPathConverter()
        ui_selector = converter.xpath_to_ui(xpath)
        assert expected == ui_selector  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            ("//[@class]", ""),
            ("//*invalid(expr)", ""),
            ('//*[@unknown-attr="xxx"]', ""),
            ('//*[contains(@nonexistent,"value")]', ""),
        ]
    )
    def test_xpath_to_ui_negative(self, xpath: str, expected: str):
        """Test conversion of invalid XPath expressions."""
        converter = XPathConverter()
        try:
            ui_selector = converter.xpath_to_ui(xpath)
            # If conversion succeeds, it should not match expected empty string
            assert ui_selector != expected  # noqa: S101
        except ConversionError:
            # Expected behavior for invalid XPath
            pass
