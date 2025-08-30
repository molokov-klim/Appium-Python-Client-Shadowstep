# shadowstep/utils/tests/test_ui_selector_converter.py
import logging
from typing import Any

import pytest

from shadowstep.locator_converter.map.ui_to_dict import UI_TO_SHADOWSTEP_DICT
from shadowstep.locator_converter.types.ui_selector import UiMethod
from shadowstep.locator_converter.ui_selector_converter import UiSelectorConverter

logger = logging.getLogger(__name__)


class TestUiSelectorParser:

    @pytest.mark.parametrize(
        "selector_str, expected_xpath",
        [
            (
                    'new UiSelector().textStartsWith("Оплат").className("android.widget.Button")'
                    '.childSelector(new UiSelector().className("android.widget.ImageView"));',
                    '//*[starts-with(@text, "Оплат")][@class="android.widget.Button"]/*[@class="android.widget.ImageView"]'
            ),
            (
                    'new UiSelector().className("android.widget.EditText").focused(true).instance(0);',
                    '//*[@class="android.widget.EditText"][@focused="true"][1]'
            ),
            (
                    'new UiSelector().packageName("ru.sigma.app.debug").resourceIdMatches(".*:id/btn.*");',
                    '//*[@package="ru.sigma.app.debug"][matches(@resource-id, ".*:id/btn.*")]'
            ),
            (
                    'new UiSelector().descriptionContains("Карта").clickable(true);',
                    '//*[contains(@content-desc,"Карта")][@clickable="true"]'
            ),
            (
                    'new UiSelector().className("androidx.appcompat.app.ActionBar$Tab").index(2);',
                    '//*[@class="androidx.appcompat.app.ActionBar$Tab"][position()=3]'
            ),
            (
                    'new UiSelector().className("android.widget.RadioButton").fromParent(new UiSelector().resourceId("ru.sigma.app.debug:id/paymentMethods"));',
                    '//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.sigma.app.debug:id/paymentMethods"]'
            ),
            (
                    'new UiSelector().className("android.widget.EditText").textStartsWith("+7").enabled(true);',
                    '//*[@class="android.widget.EditText"][starts-with(@text,"+7")][@enabled="true"]'
            ),
            (
                    'new UiSelector().descriptionMatches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");',
                    '//*[matches(@content-desc,"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")]'
            ),
            (
                    'new UiSelector().scrollable(true).childSelector(new UiSelector().text("История"));',
                    '//*[@scrollable="true"]/*[@text="История"]'
            ),
            (
                    'new UiSelector().className("android.widget.CheckBox").checkable(true).checked(false).instance(2);',
                    '//*[@class="android.widget.CheckBox"][@checkable="true"][@checked="false"][3]'
            ),
            # 1️⃣ Комбинация нескольких текстовых фильтров + enabled
            (
                    'new UiSelector().textStartsWith("Оплат").textContains("Карт").enabled(true);',
                    '//*[starts-with(@text,"Оплат")][contains(@text,"Карт")][@enabled="true"]'
            ),
            # 2️⃣ Regex для className + instance
            (
                    'new UiSelector().classNameMatches("android\\.widget\\..*Button").instance(1);',
                    '//*[matches(@class,"android\\.widget\\..*Button")][2]'
            ),
            # 3️⃣ Точное описание + clickable + childSelector
            (
                    'new UiSelector().description("Подтвердить").clickable(true)'
                    '.childSelector(new UiSelector().className("android.widget.ImageView"));',
                    '//*[@content-desc="Подтвердить"][@clickable="true"]/*[@class="android.widget.ImageView"]'
            ),
            # 4️⃣ Глубокая вложенность childSelector (2 уровня)
            (
                    'new UiSelector().className("android.widget.LinearLayout")'
                    '.childSelector(new UiSelector().className("android.widget.FrameLayout")'
                    '.childSelector(new UiSelector().text("Список")))',
                    '//*[@class="android.widget.LinearLayout"]/*[@class="android.widget.FrameLayout"]/*[@text="Список"]'
            ),
            # 5️⃣ fromParent с несколькими атрибутами
            (
                    'new UiSelector().className("android.widget.TextView").fromParent('
                    'new UiSelector().className("android.widget.LinearLayout").enabled(true).index(0));',
                    '//*[@class="android.widget.TextView"]/..//*[@class="android.widget.LinearLayout"][@enabled="true"][position()=1]'
            ),
            # 6️⃣ Булевые отрицательные значения + scrollable + instance
            (
                    'new UiSelector().scrollable(false).clickable(false).instance(2);',
                    '//*[@scrollable="false"][@clickable="false"][3]'
            ),
            (
                    'new UiSelector().textStartsWith("Оплат").className("android.widget.Button")'
                    '.childSelector(new UiSelector().className("android.widget.ImageView"));',
                    '//*[starts-with(@text, "Оплат")][@class="android.widget.Button"]/*[@class="android.widget.ImageView"]'
            ),
            (
                    'new UiSelector().className("android.widget.EditText").focused(true).instance(0);',
                    '//*[@class="android.widget.EditText"][@focused="true"][1]'
            ),
            (
                    'new UiSelector().packageName("ru.sigma.app.debug").resourceIdMatches(".*:id/btn.*");',
                    '//*[@package="ru.sigma.app.debug"][matches(@resource-id, ".*:id/btn.*")]'
            ),
            (
                    'new UiSelector().descriptionContains("Карта").clickable(true);',
                    '//*[contains(@content-desc,"Карта")][@clickable="true"]'
            ),
            (
                    'new UiSelector().className("androidx.appcompat.app.ActionBar$Tab").index(2);',
                    '//*[@class="androidx.appcompat.app.ActionBar$Tab"][position()=3]'
            ),
            (
                    'new UiSelector().className("android.widget.RadioButton").fromParent(new UiSelector().resourceId("ru.sigma.app.debug:id/paymentMethods"));',
                    '//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.sigma.app.debug:id/paymentMethods"]'
            ),
            (
                    'new UiSelector().className("android.widget.EditText").textStartsWith("+7").enabled(true);',
                    '//*[@class="android.widget.EditText"][starts-with(@text,"+7")][@enabled="true"]'
            ),
            (
                    'new UiSelector().descriptionMatches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");',
                    '//*[matches(@content-desc,"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")]'
            ),
            (
                    'new UiSelector().scrollable(true).childSelector(new UiSelector().text("История"));',
                    '//*[@scrollable="true"]/*[@text="История"]'
            ),
            (
                    'new UiSelector().className("android.widget.CheckBox").checkable(true).checked(false).instance(2);',
                    '//*[@class="android.widget.CheckBox"][@checkable="true"][@checked="false"][3]'
            ),
            # Добавленные тест кейсы для полного покрытия
            (
                    'new UiSelector().textContains("карт").resourceId("ru.sigma.app.debug:id/card_number");',
                    '//*[contains(@text,"карт")][@resource-id="ru.sigma.app.debug:id/card_number"]'
            ),
            (
                    'new UiSelector().text("Оплатить").longClickable(false);',
                    '//*[@text="Оплатить"][@long-clickable="false"]'
            ),
            (
                    'new UiSelector().className("android.widget.Button").selected(true);',
                    '//*[@class="android.widget.Button"][@selected="true"]'
            ),
            (
                    'new UiSelector().text("OK").or(new UiSelector().text("Confirm"));',
                    '//*[@text="OK"] | //*[@text="Confirm"]'
            ),
            (
                    'new UiSelector().className("Button").longClickable(true).packageName("com.example.app");',
                    '//*[@class="Button"][@long-clickable="true"][@package="com.example.app"]'
            ),
            (
                    'new UiSelector().childSelector(new UiSelector().className("ListView").childSelector(new UiSelector().text("Item")));',
                    '//*/*[@class="ListView"]/*[@text="Item"]'
            ),
            (
                    'new UiSelector().fromParent(new UiSelector().className("Container").childSelector(new UiSelector().text("Title")));',
                    '//*/..//*[@class="Container"]/*[@text="Title"]'
            ),
            (
                    'new UiSelector().text("C:\\Windows\\Path");',
                    '//*[@text="C:\\Windows\\Path"]'
            ),
            (
                    'new UiSelector().descriptionMatches(".*\\d+.*");',
                    '//*[matches(@content-desc,".*\\d+.*")]'
            ),
            (
                    'new UiSelector().resourceId("");',
                    '//*[@resource-id=""]'
            ),
            (
                    'new UiSelector().index(0);',
                    '//*[position()=1]'
            ),
            (
                    'new UiSelector().instance(5);',
                    '//*[6]'
            ),
            (
                    'new UiSelector().focusable(true).password(true);',
                    '//*[@focusable="true"][@password="true"]'
            ),
            (
                    'new UiSelector().textContains("секция").className("android.widget.TextView");',
                    '//*[contains(@text, "секция")][@class="android.widget.TextView"]'
            ),
            # Новый вариант: textMatches (регулярное выражение)
            (
                    'new UiSelector().textMatches("\\\\d{3}-\\\\d{2}-\\\\d{4}");',
                    '//*[matches(@text, "\\d{3}-\\d{2}-\\d{4}")]'  # type: ignore
            ),
            # Вложенный childSelector несколько уровней
            (
                    'new UiSelector().className("android.widget.LinearLayout")'
                    '.childSelector(new UiSelector().className("android.widget.FrameLayout")'
                    '.childSelector(new UiSelector().className("android.widget.TextView")));',
                    '//*[@class="android.widget.LinearLayout"]/*[@class="android.widget.FrameLayout"]/*[@class="android.widget.TextView"]'
            ),
            # Комбинация enabled и clickable
            (
                    'new UiSelector().className("android.widget.Button").enabled(true).clickable(true);',
                    '//*[@class="android.widget.Button"][@enabled="true"][@clickable="true"]'
            ),
            # Минимальный селектор с классом
            (
                    'new UiSelector().className("android.widget.ImageView");',
                    '//*[@class="android.widget.ImageView"]'
            )
        ]
    )
    def test_ui_selector_parsing_and_xpath(self, selector_str: str, expected_xpath: str):
        converter = UiSelectorConverter()
        xpath = converter.selector_to_xpath(selector_str)
        # logger.info(f"{selector_str=}")
        # logger.info(f"{expected_xpath=}")
        # logger.info(f"{parsed=}")
        # logger.info(f"{xpath=}")
        assert expected_xpath.replace(" ", "") == xpath.replace(" ", ""), f"Expected '{expected_xpath}' got: {xpath}"

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "selector_str, expected_xpath",
        [
            # Ошибочный селектор (имитация, ожидается пустой XPath или исключение)
            (
                    'new UiSelector().unknownProperty("value");',
                    ''
            )

        ]
    )
    def test_ui_selector_parsing_and_xpath_negative(self, selector_str: str, expected_xpath: str):
        converter = UiSelectorConverter()
        xpath = converter.selector_to_xpath(selector_str)
        # logger.info(f"{selector_str=}")
        # logger.info(f"{expected_xpath=}")
        # logger.info(f"{parsed=}")
        # logger.info(f"{xpath=}")
        assert expected_xpath.replace(" ", "") == xpath.replace(" ", ""), f"Expected '{expected_xpath}' got: {xpath}"

    @pytest.mark.parametrize(
        "method_name, arg, expected_xpath_part",
        [
            # --- text-based ---
            ("text", "Привет", '@text="Привет"'),
            ("textContains", "Hello", 'contains(@text, "Hello")'),
            ("textStartsWith", "Оплат", 'starts-with(@text, "Оплат")'),
            ("textMatches", ".*Тест.*", 'matches(@text, ".*Тест.*")'),

            # --- description ---
            ("description", "desc", '@content-desc="desc"'),
            ("descriptionContains", "part", 'contains(@content-desc, "part")'),
            ("descriptionStartsWith", "start", 'starts-with(@content-desc, "start")'),
            ("descriptionMatches", "regex.*", 'matches(@content-desc, "regex.*")'),

            # --- resource id / package ---
            ("resourceId", "resId", '@resource-id="resId"'),
            ("resourceIdMatches", "res.*", 'matches(@resource-id, "res.*")'),
            ("packageName", "pkg.name", '@package="pkg.name"'),

            # --- class ---
            ("className", "android.widget.Button", '@class="android.widget.Button"'),
            ("classNameMatches", ".*Button", 'matches(@class, ".*Button")'),

            # --- bool props ---
            ("checkable", True, '@checkable="true"'),
            ("checked", False, '@checked="false"'),
            ("clickable", True, '@clickable="true"'),
            ("enabled", False, '@enabled="false"'),
            ("focusable", True, '@focusable="true"'),
            ("focused", False, '@focused="false"'),
            ("longClickable", True, '@long-clickable="true"'),
            ("scrollable", False, '@scrollable="false"'),
            ("selected", True, '@selected="true"'),

            # --- numeric ---
            ("index", 2, 'position()=3'),
            ("instance", 0, '//*[1]'),
        ]
    )
    def test_all_ui_methods(self, method_name: str, arg: Any, expected_xpath_part: str):
        converter = UiSelectorConverter()
        selector_str = f'new UiSelector().{method_name}({repr(arg)});'
        parsed = converter.parse_selector_string(selector_str)
        xpath = converter._selector_to_xpath(parsed)

        logger.info(f"{method_name=}")
        logger.info(f"{arg=}")
        logger.info(f"{expected_xpath_part=}")
        logger.info(f"{parsed=}")
        logger.info(f"{xpath=}")

        # Проверяем, что метод распарсился правильно
        method_in_dict = parsed['methods'][0]
        assert method_in_dict['name'] == method_name
        assert method_in_dict['args'][0] == arg

        # Проверяем, что XPath содержит ожидаемый фрагмент
        assert expected_xpath_part in xpath

    @pytest.mark.parametrize(
        "method, value, expected",
        [
            # --- text-based ---
            (UiMethod.TEXT, "OK", {"text": "OK"}),
            (UiMethod.TEXT_CONTAINS, "abc", {"textContains": "abc"}),
            (UiMethod.TEXT_STARTS_WITH, "Op", {"textStartsWith": "Op"}),
            (UiMethod.TEXT_MATCHES, r"\d+", {"textMatches": r"\d+"}),

            # --- description ---
            (UiMethod.DESCRIPTION, "Next", {"content-desc": "Next"}),
            (UiMethod.DESCRIPTION_CONTAINS, "Btn", {"content-descContains": "Btn"}),
            (UiMethod.DESCRIPTION_STARTS_WITH, "Pre", {"content-descStartsWith": "Pre"}),
            (UiMethod.DESCRIPTION_MATCHES, ".*", {"content-descMatches": ".*"}),

            # --- resource id / package ---
            (UiMethod.RESOURCE_ID, "my.id", {"resource-id": "my.id"}),
            (UiMethod.RESOURCE_ID_MATCHES, ".*id", {"resource-idMatches": ".*id"}),
            (UiMethod.PACKAGE_NAME, "com.app", {"package": "com.app"}),
            (UiMethod.PACKAGE_NAME_MATCHES, ".*app", {"packageMatches": ".*app"}),

            # --- class ---
            (UiMethod.CLASS_NAME, "android.widget.TextView", {"class": "android.widget.TextView"}),
            (UiMethod.CLASS_NAME_MATCHES, ".*View", {"classNameMatches": ".*View"}),

            # --- bool props ---
            (UiMethod.CHECKABLE, True, {"checkable": True}),
            (UiMethod.CHECKED, False, {"checked": False}),
            (UiMethod.CLICKABLE, True, {"clickable": True}),
            (UiMethod.LONG_CLICKABLE, False, {"long-clickable": False}),
            (UiMethod.ENABLED, True, {"enabled": True}),
            (UiMethod.FOCUSABLE, True, {"focusable": True}),
            (UiMethod.FOCUSED, False, {"focused": False}),
            (UiMethod.SCROLLABLE, True, {"scrollable": True}),
            (UiMethod.SELECTED, False, {"selected": False}),
            (UiMethod.PASSWORD, True, {"password": True}),

            # --- numeric ---
            (UiMethod.INDEX, 3, {"index": 3}),
            (UiMethod.INSTANCE, 1, {"instance": 1}),

            # --- hierarchy ---
            (UiMethod.CHILD_SELECTOR, "child", {"instance": "child"}),
            (UiMethod.FROM_PARENT, "parent", {"instance": "parent"}),
        ]
    )
    def test_ui_to_shadowstep_dict(self, method: UiMethod, value: Any, expected: dict[str, Any]):
        converter = UiSelectorConverter()
        # собираем строку вида new UiSelector().text("OK");
        # repr() нужен, чтобы для строк были кавычки, для bool — True/False, для int — число
        selector_str = f'new UiSelector().{method.value}({repr(value)});'

        shadowstep_dict = converter.selector_to_dict(selector_str)

        logger.info(f"method={method}")
        logger.info(f"value={value}")
        logger.info(f"expected={expected}")
        logger.info(f"shadowstep_dict={shadowstep_dict}")

        assert shadowstep_dict == expected

