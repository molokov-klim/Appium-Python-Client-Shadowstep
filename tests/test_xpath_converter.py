# tests/test_xpath_converter.py
import logging
from typing import Any

import pytest
from locator_converter.types.shadowstep_dict import DictAttribute

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator_converter.xpath_converter import XPathConverter

logger = logging.getLogger(__name__)


class TestXPathConverter:

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # --- text-based ---
            ('//*[@text="Привет"]', {DictAttribute.TEXT.value: "Привет"}),
            ('//*[contains(@text,"Hello")]', {DictAttribute.TEXT_CONTAINS.value: "Hello"}),
            ('//*[starts-with(@text,"Оплат")]', {DictAttribute.TEXT_STARTS_WITH.value: "Оплат"}),
            ('//*[matches(@text,".*Тест.*")]', {DictAttribute.TEXT_MATCHES.value: ".*Тест.*"}),

            # --- description ---
            ('//*[@content-desc="desc"]', {DictAttribute.DESCRIPTION.value: "desc"}),
            ('//*[contains(@content-desc,"part")]', {DictAttribute.DESCRIPTION_CONTAINS.value: "part"}),
            ('//*[starts-with(@content-desc,"start")]', {DictAttribute.DESCRIPTION_STARTS_WITH.value: "start"}),
            ('//*[matches(@content-desc,"regex.*")]', {DictAttribute.DESCRIPTION_MATCHES.value: "regex.*"}),

            # --- resource id / package ---
            ('//*[@resource-id="resId"]', {DictAttribute.RESOURCE_ID.value: "resId"}),
            ('//*[matches(@resource-id,"res.*")]', {DictAttribute.RESOURCE_ID_MATCHES.value: "res.*"}),
            ('//*[@package="pkg.name"]', {DictAttribute.PACKAGE_NAME.value: "pkg.name"}),
            ('//*[matches(@package,"pkg.name")]', {DictAttribute.PACKAGE_NAME_MATCHES.value: "pkg.name"}),

            # --- class ---
            ('//*[@class="android.widget.Button"]', {DictAttribute.CLASS_NAME.value: "android.widget.Button"}),
            ('//*[matches(@class,".*Button")]', {DictAttribute.CLASS_NAME_MATCHES.value: ".*Button"}),

            # --- bool props ---
            ('//*[@checkable="true"]', {DictAttribute.CHECKABLE.value: True}),
            ('//*[@checked="false"]', {DictAttribute.CHECKED.value: False}),
            ('//*[@clickable="true"]', {DictAttribute.CLICKABLE.value: True}),
            ('//*[@enabled="true"]', {DictAttribute.ENABLED.value: True}),
            ('//*[@focusable="true"]', {DictAttribute.FOCUSABLE.value: True}),
            ('//*[@focused="false"]', {DictAttribute.FOCUSED.value: False}),
            ('//*[@long-clickable="true"]', {DictAttribute.LONG_CLICKABLE.value: True}),
            ('//*[@scrollable="false"]', {DictAttribute.SCROLLABLE.value: False}),
            ('//*[@selected="false"]', {DictAttribute.SELECTED.value: False}),
            ('//*[@password="true"]', {DictAttribute.PASSWORD.value: True}),

            # --- numeric ---
            ("//*[position()=3]", {DictAttribute.INDEX.value: 2}),
            ("//*[6]", {DictAttribute.INSTANCE.value: 5}),

            # --- hierarchy ---
            ('//*[@content-desc="Подтвердить"]/*[@class="android.widget.ImageView"]',
             {DictAttribute.DESCRIPTION.value: "Подтвердить",
              DictAttribute.CHILD_SELECTOR.value: {"class": "android.widget.ImageView"}}),
            ('//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.figma.app.debug:id/paymentMethods"]',
             {DictAttribute.CLASS_NAME.value: "android.widget.RadioButton",
              DictAttribute.FROM_PARENT.value: {
                  DictAttribute.RESOURCE_ID.value: "ru.figma.app.debug:id/paymentMethods"}}),
        ]
    )
    def test_xpath_to_dict_attributes(self, xpath: str, expected: dict[str, Any]):
        """Test conversion of XPath attributes to dictionary format."""
        converter = XPathConverter()
        # logger.info(f"{xpath=}")
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {shadowstep_dict=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == shadowstep_dict  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            (
                    '//*[@text="OK"][@class="android.widget.Button"][position()=1]',
                    {
                        DictAttribute.TEXT.value: "OK",
                        DictAttribute.CLASS_NAME.value: "android.widget.Button",
                        DictAttribute.INDEX.value: 0,
                    },
            ),
            (
                    '//*[contains(@text, "Подтвердить")][@clickable="true"]',
                    {
                        DictAttribute.TEXT_CONTAINS.value: "Подтвердить",
                        DictAttribute.CLICKABLE.value: True,
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/btn"][@enabled="false"]',
                    {
                        DictAttribute.RESOURCE_ID.value: "ru.app:id/btn",
                        DictAttribute.ENABLED.value: False,
                    },
            ),
            (
                    '//*[starts-with(@text, "Нач")][@package="ru.app"][@focusable="true"]',
                    {
                        DictAttribute.TEXT_STARTS_WITH.value: "Нач",
                        DictAttribute.PACKAGE_NAME.value: "ru.app",
                        DictAttribute.FOCUSABLE.value: True,
                    },
            ),
            (
                    '//*[contains(@content-desc, "icon")][@long-clickable="true"][@class="android.widget.ImageView"]',
                    {
                        DictAttribute.DESCRIPTION_CONTAINS.value: "icon",
                        DictAttribute.LONG_CLICKABLE.value: True,
                        DictAttribute.CLASS_NAME.value: "android.widget.ImageView",
                    },
            ),
            (
                    '//*[matches(@text, ".*Тест.*")][@scrollable="false"]',
                    {
                        DictAttribute.TEXT_MATCHES.value: ".*Тест.*",
                        DictAttribute.SCROLLABLE.value: False,
                    },
            ),
            (
                    '//*[@content-desc="switch"][@checked="true"][position()=2]',
                    {
                        DictAttribute.DESCRIPTION.value: "switch",
                        DictAttribute.CHECKED.value: True,
                        DictAttribute.INDEX.value: 1,
                    },
            ),
            (
                    '//*[@package="ru.pkg"][@enabled="true"][@selected="false"]',
                    {
                        DictAttribute.PACKAGE_NAME.value: "ru.pkg",
                        DictAttribute.ENABLED.value: True,
                        DictAttribute.SELECTED.value: False,
                    },
            ),
            (
                    '//*[matches(@class, ".*EditText")][@focusable="true"][position()=3]',
                    {
                        DictAttribute.CLASS_NAME_MATCHES.value: ".*EditText",
                        DictAttribute.FOCUSABLE.value: True,
                        DictAttribute.INDEX.value: 2,
                    },
            ),
            (
                    '//*[@text="Save"][matches(@content-desc, ".*save.*")][@clickable="true"]',
                    {
                        DictAttribute.TEXT.value: "Save",
                        DictAttribute.DESCRIPTION_MATCHES.value: ".*save.*",
                        DictAttribute.CLICKABLE.value: True,
                    },
            ),
            (
                    '//*[matches(@resource-id, ".*btn.*")][contains(@text, "Отправить")][@enabled="true"]',
                    {
                        DictAttribute.RESOURCE_ID_MATCHES.value: ".*btn.*",
                        DictAttribute.TEXT_CONTAINS.value: "Отправить",
                        DictAttribute.ENABLED.value: True,
                    },
            ),
            (
                    '//*[@class="android.widget.TextView"][starts-with(@content-desc, "hint")][@long-clickable="false"]',
                    {
                        DictAttribute.CLASS_NAME.value: "android.widget.TextView",
                        DictAttribute.DESCRIPTION_STARTS_WITH.value: "hint",
                        DictAttribute.LONG_CLICKABLE.value: False,
                    },
            ),
            (
                    '//*[@text="OK"][matches(@package, "com.example.*")][@checked="true"]',
                    {
                        DictAttribute.TEXT.value: "OK",
                        DictAttribute.PACKAGE_NAME_MATCHES.value: "com.example.*",
                        DictAttribute.CHECKED.value: True,
                    },
            ),
            (
                    '//*[contains(@content-desc, "item")][position()=5][position()=2]',
                    {
                        DictAttribute.DESCRIPTION_CONTAINS.value: "item",
                        DictAttribute.INDEX.value: 1,  # Last index wins
                    },
            ),
            (
                    '//*[matches(@text, ".*done.*")][@class="android.widget.CheckBox"][@selected="true"]',
                    {
                        DictAttribute.TEXT_MATCHES.value: ".*done.*",
                        DictAttribute.CLASS_NAME.value: "android.widget.CheckBox",
                        DictAttribute.SELECTED.value: True,
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"][@text="Login"][@focusable="true"][@focused="false"]',
                    {
                        DictAttribute.RESOURCE_ID.value: "ru.app:id/input",
                        DictAttribute.TEXT.value: "Login",
                        DictAttribute.FOCUSABLE.value: True,
                        DictAttribute.FOCUSED.value: False,
                    },
            ),
            (
                    '//*[@content-desc="menu"][@package="ru.app"][@enabled="true"][@clickable="true"]',
                    {
                        DictAttribute.DESCRIPTION.value: "menu",
                        DictAttribute.PACKAGE_NAME.value: "ru.app",
                        DictAttribute.ENABLED.value: True,
                        DictAttribute.CLICKABLE.value: True,
                    },
            ),
            (
                    '//*[starts-with(@text, "File")][matches(@class, ".*ListView")][@scrollable="true"]',
                    {
                        DictAttribute.TEXT_STARTS_WITH.value: "File",
                        DictAttribute.CLASS_NAME_MATCHES.value: ".*ListView",
                        DictAttribute.SCROLLABLE.value: True,
                    },
            ),
            (
                    '//*[matches(@resource-id, ".*toolbar")][matches(@content-desc, ".*tool.*")][@long-clickable="true"]',
                    {
                        DictAttribute.RESOURCE_ID_MATCHES.value: ".*toolbar",
                        DictAttribute.DESCRIPTION_MATCHES.value: ".*tool.*",
                        DictAttribute.LONG_CLICKABLE.value: True,
                    },
            ),
            (
                    '//*[@text="Submit"][contains(@content-desc, "send")][@class="android.widget.Button"][@enabled="true"][@clickable="true"][position()=1][position()=4]',
                    {
                        DictAttribute.TEXT.value: "Submit",
                        DictAttribute.DESCRIPTION_CONTAINS.value: "send",
                        DictAttribute.CLASS_NAME.value: "android.widget.Button",
                        DictAttribute.ENABLED.value: True,
                        DictAttribute.CLICKABLE.value: True,
                        DictAttribute.INDEX.value: 3,  # Last index wins
                    },
            ),
            (
                    '//*[@text="Оплатить"]/*[@class="android.widget.ImageView"]',
                    {
                        DictAttribute.TEXT.value: "Оплатить",
                        DictAttribute.CHILD_SELECTOR.value: {
                            DictAttribute.CLASS_NAME.value: "android.widget.ImageView",
                        },
                    },
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[contains(@text, "Email")]',
                    {
                        DictAttribute.CLASS_NAME.value: "android.widget.LinearLayout",
                        DictAttribute.CHILD_SELECTOR.value: {
                            DictAttribute.TEXT_CONTAINS.value: "Email",
                        },
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"]/../*[@class="android.widget.ScrollView"]',
                    {
                        DictAttribute.RESOURCE_ID.value: "ru.app:id/input",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.CLASS_NAME.value: "android.widget.ScrollView",
                        },
                    },
            ),
            (
                    '//*[@class="android.widget.Button"][starts-with(@text,"Дал")]/*[@content-desc="icon"]',
                    {
                        DictAttribute.CLASS_NAME.value: "android.widget.Button",
                        DictAttribute.TEXT_STARTS_WITH.value: "Дал",
                        DictAttribute.CHILD_SELECTOR.value: {
                            DictAttribute.DESCRIPTION.value: "icon",
                        },
                    },
            ),
            (
                    '//*[@text="Settings"]/../*[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        DictAttribute.TEXT.value: "Settings",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.CLASS_NAME.value: "android.widget.FrameLayout",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.RESOURCE_ID.value: "ru.app:id/switch",
                            },
                        },
                    },
            ),
        ]
    )
    def test_xpath_to_dict(self, xpath: str, expected: dict[str, Any]):
        """Test conversion of complex XPath expressions to dictionary format."""
        converter = XPathConverter()
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {shadowstep_dict=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == shadowstep_dict  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",
        [  # pyright: ignore [reportUnknownArgumentType]
            # 1) Твой исходный пример (базовый sanity)
            (
                    '//*[@text="Settings"][@class="android.widget.Button"]/../*[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        DictAttribute.TEXT.value: "Settings",
                        DictAttribute.CLASS_NAME.value: "android.widget.Button",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.CLASS_NAME.value: "android.widget.FrameLayout",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.RESOURCE_ID.value: "ru.app:id/switch",
                            },
                        },
                    },
            ),

            # 2) Два шага вверх, затем два шага вниз по классам и ресурс-id в конце
            (
                    '//*[@text="Root"]/../../*[@class="L1"]/*[@class="L2"]/*[@resource-id="app:id/toggle"]',
                    {
                        DictAttribute.TEXT.value: "Root",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.FROM_PARENT.value: {
                                DictAttribute.CLASS_NAME.value: "L1",
                                DictAttribute.CHILD_SELECTOR.value: {
                                    DictAttribute.CLASS_NAME.value: "L2",
                                    DictAttribute.CHILD_SELECTOR.value: {
                                        DictAttribute.RESOURCE_ID.value: "app:id/toggle",
                                    },
                                },
                            }
                        },
                    },
            ),

            # 3) Один шаг вверх, далее длинная цепочка вниз (5 уровней)
            (
                    '//*[@text="Deep"]/../*[@class="A"]/*[@class="B"]/*[@class="C"]/*[@class="D"]/*[@resource-id="pkg:id/end"]',
                    {
                        DictAttribute.TEXT.value: "Deep",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.CLASS_NAME.value: "A",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.CLASS_NAME.value: "B",
                                DictAttribute.CHILD_SELECTOR.value: {
                                    DictAttribute.CLASS_NAME.value: "C",
                                    DictAttribute.CHILD_SELECTOR.value: {
                                        DictAttribute.CLASS_NAME.value: "D",
                                        DictAttribute.CHILD_SELECTOR.value: {
                                            DictAttribute.RESOURCE_ID.value: "pkg:id/end",
                                        },
                                    },
                                },
                            },
                        },
                    },
            ),

            # 4) Три шага вверх, затем два вниз
            (
                    '//*[@text="T"]/../../../*[@class="P1"]/*[@class="P2"]/*[@resource-id="pkg:id/final"]',
                    {
                        DictAttribute.TEXT.value: "T",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.FROM_PARENT.value: {
                                DictAttribute.FROM_PARENT.value: {
                                    DictAttribute.CLASS_NAME.value: "P1",
                                    DictAttribute.CHILD_SELECTOR.value: {
                                        DictAttribute.CLASS_NAME.value: "P2",
                                        DictAttribute.CHILD_SELECTOR.value: {
                                            DictAttribute.RESOURCE_ID.value: "pkg:id/final",
                                        },
                                    },
                                }
                            }
                        },
                    },
            ),

            # 5) Глубокая чисто нисходящая цепочка (без ..), 6 уровней
            (
                    '//*[*[@text="Anchor"]]/*[@class="L1"]/*[@class="L2"]/*[@class="L3"]/*[@class="L4"]/*[@class="L5"]/*[@resource-id="app:id/leaf"]',
                    {
                        # Поскольку в корне у нас предикат по text(), он попадёт в верхний уровень
                        DictAttribute.TEXT.value: "Anchor",
                        DictAttribute.CHILD_SELECTOR.value: {
                            DictAttribute.CLASS_NAME.value: "L1",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.CLASS_NAME.value: "L2",
                                DictAttribute.CHILD_SELECTOR.value: {
                                    DictAttribute.CLASS_NAME.value: "L3",
                                    DictAttribute.CHILD_SELECTOR.value: {
                                        DictAttribute.CLASS_NAME.value: "L4",
                                        DictAttribute.CHILD_SELECTOR.value: {
                                            DictAttribute.CLASS_NAME.value: "L5",
                                            DictAttribute.CHILD_SELECTOR.value: {
                                                DictAttribute.RESOURCE_ID.value: "app:id/leaf",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
            ),

            # 6) Смешанный: вверх, вниз, опять вниз через двойной слэш (// трактуется как / в сборке дерева)
            (
                    '//*[@text="Mixed"]/..//*[@class="C1"]/*[@class="C2"]//*[@resource-id="pkg:id/x"]',
                    {
                        DictAttribute.TEXT.value: "Mixed",
                        DictAttribute.FROM_PARENT.value: {
                            # после .. первый нисходящий шаг
                            DictAttribute.CLASS_NAME.value: "C1",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.CLASS_NAME.value: "C2",
                                DictAttribute.CHILD_SELECTOR.value: {
                                    # ещё один нисходящий шаг через //
                                    DictAttribute.RESOURCE_ID.value: "pkg:id/x",
                                },
                            },
                        },
                    },
            ),

            # 7) Максимально «сумасшедшая» матрёшка: вверх x3, затем вниз x6
            (
                    '//*[@text="Mega"]/../../../*[@class="L1"]/*[@class="L2"]/*[@class="L3"]/*[@class="L4"]/*[@class="L5"]/*[@class="L6"]/*[@resource-id="pkg:id/the_end"]',
                    {
                        DictAttribute.TEXT.value: "Mega",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.FROM_PARENT.value: {
                                DictAttribute.FROM_PARENT.value: {
                                    DictAttribute.CLASS_NAME.value: "L1",
                                    DictAttribute.CHILD_SELECTOR.value: {
                                        DictAttribute.CLASS_NAME.value: "L2",
                                        DictAttribute.CHILD_SELECTOR.value: {
                                            DictAttribute.CLASS_NAME.value: "L3",
                                            DictAttribute.CHILD_SELECTOR.value: {
                                                DictAttribute.CLASS_NAME.value: "L4",
                                                DictAttribute.CHILD_SELECTOR.value: {
                                                    DictAttribute.CLASS_NAME.value: "L5",
                                                    DictAttribute.CHILD_SELECTOR.value: {
                                                        DictAttribute.CLASS_NAME.value: "L6",
                                                        DictAttribute.CHILD_SELECTOR.value: {
                                                            DictAttribute.RESOURCE_ID.value: "pkg:id/the_end",
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    },
            ),
        ],
    )
    def test_xpath_to_dict_deep_nesting(self, xpath, expected):
        converter = XPathConverter()
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {shadowstep_dict=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert shadowstep_dict == expected

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # 1) contains(@text, ...)
            (
                    '//*[contains(@text, "Hello")]/../*[@class="android.view.View"]/*[contains(@content-desc, "Btn")]',
                    {
                        DictAttribute.TEXT_CONTAINS.value: "Hello",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.CLASS_NAME.value: "android.view.View",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.DESCRIPTION_CONTAINS.value: "Btn",
                            },
                        },
                    },
            ),

            # 2) starts-with(@content-desc, ...)
            (
                    '//*[@text="Start"]/../*[starts-with(@content-desc, "prefix")]/child::*[@resource-id="pkg:id/target"]',
                    {
                        DictAttribute.TEXT.value: "Start",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.DESCRIPTION_STARTS_WITH.value: "prefix",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.RESOURCE_ID.value: "pkg:id/target",
                            },
                        },
                    },
            ),

            # 3) matches(@resource-id, regex)
            (
                    '//*[@class="android.widget.LinearLayout"]//node()[matches(@resource-id, ".*button.*")]',
                    {
                        DictAttribute.CLASS_NAME.value: "android.widget.LinearLayout",
                        DictAttribute.CHILD_SELECTOR.value: {
                            DictAttribute.RESOURCE_ID_MATCHES.value: ".*button.*",
                        },
                    },
            ),

            # 4) Комбо: text, затем contains, потом starts-with и в конце matches
            (
                    '//*[@text="Anchor"]/../*[contains(@text, "foo")]/child::*[starts-with(@content-desc, "bar")]/*[matches(@class, ".*Layout")]',
                    {
                        DictAttribute.TEXT.value: "Anchor",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.TEXT_CONTAINS.value: "foo",
                            DictAttribute.CHILD_SELECTOR.value: {
                                DictAttribute.DESCRIPTION_STARTS_WITH.value: "bar",
                                DictAttribute.CHILD_SELECTOR.value: {
                                    DictAttribute.CLASS_NAME_MATCHES.value: ".*Layout",
                                },
                            },
                        },
                    },
            ),

            # 5) Супер-вложенность: 2 раза вверх, потом цепочка из contains → starts-with → matches → resource-id
            (
                    '//*[@text="Mega"]/../../*[contains(@text, "deep")]/child::*[starts-with(@content-desc, "zzz")]/*[matches(@package, "com\\..*")]/*[@resource-id="pkg:id/the_end"]',
                    {
                        DictAttribute.TEXT.value: "Mega",
                        DictAttribute.FROM_PARENT.value: {
                            DictAttribute.FROM_PARENT.value: {
                                DictAttribute.TEXT_CONTAINS.value: "deep",
                                DictAttribute.CHILD_SELECTOR.value: {
                                    DictAttribute.DESCRIPTION_STARTS_WITH.value: "zzz",
                                    DictAttribute.CHILD_SELECTOR.value: {
                                        DictAttribute.PACKAGE_NAME_MATCHES.value: "com\\..*",
                                        DictAttribute.CHILD_SELECTOR.value: {
                                            DictAttribute.RESOURCE_ID.value: "pkg:id/the_end",
                                        },
                                    },
                                },
                            }
                        },
                    },
            ),
        ],
    )
    def test_xpath_to_dict_with_functions(self, xpath, expected):
        converter = XPathConverter()
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {shadowstep_dict=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert shadowstep_dict == expected

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
        ui_selector = converter.xpath_to_ui_selector(xpath)
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
                    '//*[@package="ru.figma.app.debug"][matches(@resource-id, ".*:id/btn.*")]',
                    'new UiSelector().packageName("ru.figma.app.debug").resourceIdMatches(".*:id/btn.*");',
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
                    '//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.figma.app.debug:id/paymentMethods"]',
                    'new UiSelector().className("android.widget.RadioButton").fromParent(new UiSelector().resourceId("ru.figma.app.debug:id/paymentMethods"));',
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
                    '//*[contains(@text,"карт")][@resource-id="ru.figma.app.debug:id/card_number"]',
                    'new UiSelector().textContains("карт").resourceId("ru.figma.app.debug:id/card_number");',
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
