# tests/test_converter_xpath.py
import logging
from typing import Any

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ConversionError
from shadowstep.locator.converter.xpath_converter import XPathConverter
from shadowstep.locator.types.shadowstep_dict import DictAttribute

logger = logging.getLogger(__name__)


class TestXPathConverter:

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # --- text-based ---
            ('//*[@text="Привет"]', {DictAttribute.TEXT: "Привет"}),
            ('//*[contains(@text,"Hello")]', {DictAttribute.TEXT_CONTAINS: "Hello"}),
            ('//*[starts-with(@text,"Оплат")]', {DictAttribute.TEXT_STARTS_WITH: "Оплат"}),
            ('//*[matches(@text,".*Тест.*")]', {DictAttribute.TEXT_MATCHES: ".*Тест.*"}),

            # --- description ---
            ('//*[@content-desc="desc"]', {DictAttribute.DESCRIPTION: "desc"}),
            ('//*[contains(@content-desc,"part")]', {DictAttribute.DESCRIPTION_CONTAINS: "part"}),
            ('//*[starts-with(@content-desc,"start")]', {DictAttribute.DESCRIPTION_STARTS_WITH: "start"}),
            ('//*[matches(@content-desc,"regex.*")]', {DictAttribute.DESCRIPTION_MATCHES: "regex.*"}),

            # --- resource id / package ---
            ('//*[@resource-id="resId"]', {DictAttribute.RESOURCE_ID: "resId"}),
            ('//*[matches(@resource-id,"res.*")]', {DictAttribute.RESOURCE_ID_MATCHES: "res.*"}),
            ('//*[@package="pkg.name"]', {DictAttribute.PACKAGE_NAME: "pkg.name"}),
            ('//*[matches(@package,"pkg.name")]', {DictAttribute.PACKAGE_NAME_MATCHES: "pkg.name"}),

            # --- class ---
            ('//*[@class="android.widget.Button"]', {DictAttribute.CLASS_NAME: "android.widget.Button"}),
            ('//*[matches(@class,".*Button")]', {DictAttribute.CLASS_NAME_MATCHES: ".*Button"}),

            # --- bool props ---
            ('//*[@checkable="true"]', {DictAttribute.CHECKABLE: True}),
            ('//*[@checked="false"]', {DictAttribute.CHECKED: False}),
            ('//*[@clickable="true"]', {DictAttribute.CLICKABLE: True}),
            ('//*[@enabled="true"]', {DictAttribute.ENABLED: True}),
            ('//*[@focusable="true"]', {DictAttribute.FOCUSABLE: True}),
            ('//*[@focused="false"]', {DictAttribute.FOCUSED: False}),
            ('//*[@long-clickable="true"]', {DictAttribute.LONG_CLICKABLE: True}),
            ('//*[@scrollable="false"]', {DictAttribute.SCROLLABLE: False}),
            ('//*[@selected="false"]', {DictAttribute.SELECTED: False}),
            ('//*[@password="true"]', {DictAttribute.PASSWORD: True}),

            # --- numeric ---
            ("//*[position()=3]", {DictAttribute.INDEX: 2}),
            ("//*[6]", {DictAttribute.INSTANCE: 5}),

            # --- hierarchy ---
            ('//*[@content-desc="Подтвердить"]/*[@class="android.widget.ImageView"]',
             {DictAttribute.DESCRIPTION: "Подтвердить",
              DictAttribute.CHILD_SELECTOR: {"class": "android.widget.ImageView"}}),
            ('//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.figma.app.debug:id/paymentMethods"]',
             {DictAttribute.CLASS_NAME: "android.widget.RadioButton",
              DictAttribute.FROM_PARENT: {
                  DictAttribute.RESOURCE_ID: "ru.figma.app.debug:id/paymentMethods"}}),
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
        assert expected == shadowstep_dict  # noqa: S101  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            (
                    '//*[@text="OK"][@class="android.widget.Button"][position()=1]',
                    {
                        DictAttribute.TEXT: "OK",
                        DictAttribute.CLASS_NAME: "android.widget.Button",
                        DictAttribute.INDEX: 0,
                    },
            ),
            (
                    '//*[contains(@text, "Подтвердить")][@clickable="true"]',
                    {
                        DictAttribute.TEXT_CONTAINS: "Подтвердить",
                        DictAttribute.CLICKABLE: True,
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/btn"][@enabled="false"]',
                    {
                        DictAttribute.RESOURCE_ID: "ru.app:id/btn",
                        DictAttribute.ENABLED: False,
                    },
            ),
            (
                    '//*[starts-with(@text, "Нач")][@package="ru.app"][@focusable="true"]',
                    {
                        DictAttribute.TEXT_STARTS_WITH: "Нач",
                        DictAttribute.PACKAGE_NAME: "ru.app",
                        DictAttribute.FOCUSABLE: True,
                    },
            ),
            (
                    '//*[contains(@content-desc, "icon")][@long-clickable="true"][@class="android.widget.ImageView"]',
                    {
                        DictAttribute.DESCRIPTION_CONTAINS: "icon",
                        DictAttribute.LONG_CLICKABLE: True,
                        DictAttribute.CLASS_NAME: "android.widget.ImageView",
                    },
            ),
            (
                    '//*[matches(@text, ".*Тест.*")][@scrollable="false"]',
                    {
                        DictAttribute.TEXT_MATCHES: ".*Тест.*",
                        DictAttribute.SCROLLABLE: False,
                    },
            ),
            (
                    '//*[@content-desc="switch"][@checked="true"][position()=2]',
                    {
                        DictAttribute.DESCRIPTION: "switch",
                        DictAttribute.CHECKED: True,
                        DictAttribute.INDEX: 1,
                    },
            ),
            (
                    '//*[@package="ru.pkg"][@enabled="true"][@selected="false"]',
                    {
                        DictAttribute.PACKAGE_NAME: "ru.pkg",
                        DictAttribute.ENABLED: True,
                        DictAttribute.SELECTED: False,
                    },
            ),
            (
                    '//*[matches(@class, ".*EditText")][@focusable="true"][position()=3]',
                    {
                        DictAttribute.CLASS_NAME_MATCHES: ".*EditText",
                        DictAttribute.FOCUSABLE: True,
                        DictAttribute.INDEX: 2,
                    },
            ),
            (
                    '//*[@text="Save"][matches(@content-desc, ".*save.*")][@clickable="true"]',
                    {
                        DictAttribute.TEXT: "Save",
                        DictAttribute.DESCRIPTION_MATCHES: ".*save.*",
                        DictAttribute.CLICKABLE: True,
                    },
            ),
            (
                    '//*[matches(@resource-id, ".*btn.*")][contains(@text, "Отправить")][@enabled="true"]',
                    {
                        DictAttribute.RESOURCE_ID_MATCHES: ".*btn.*",
                        DictAttribute.TEXT_CONTAINS: "Отправить",
                        DictAttribute.ENABLED: True,
                    },
            ),
            (
                    '//*[@class="android.widget.TextView"][starts-with(@content-desc, "hint")][@long-clickable="false"]',
                    {
                        DictAttribute.CLASS_NAME: "android.widget.TextView",
                        DictAttribute.DESCRIPTION_STARTS_WITH: "hint",
                        DictAttribute.LONG_CLICKABLE: False,
                    },
            ),
            (
                    '//*[@text="OK"][matches(@package, "com.example.*")][@checked="true"]',
                    {
                        DictAttribute.TEXT: "OK",
                        DictAttribute.PACKAGE_NAME_MATCHES: "com.example.*",
                        DictAttribute.CHECKED: True,
                    },
            ),
            (
                    '//*[contains(@content-desc, "item")][position()=5][position()=2]',
                    {
                        DictAttribute.DESCRIPTION_CONTAINS: "item",
                        DictAttribute.INDEX: 1,  # Last index wins
                    },
            ),
            (
                    '//*[matches(@text, ".*done.*")][@class="android.widget.CheckBox"][@selected="true"]',
                    {
                        DictAttribute.TEXT_MATCHES: ".*done.*",
                        DictAttribute.CLASS_NAME: "android.widget.CheckBox",
                        DictAttribute.SELECTED: True,
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"][@text="Login"][@focusable="true"][@focused="false"]',
                    {
                        DictAttribute.RESOURCE_ID: "ru.app:id/input",
                        DictAttribute.TEXT: "Login",
                        DictAttribute.FOCUSABLE: True,
                        DictAttribute.FOCUSED: False,
                    },
            ),
            (
                    '//*[@content-desc="menu"][@package="ru.app"][@enabled="true"][@clickable="true"]',
                    {
                        DictAttribute.DESCRIPTION: "menu",
                        DictAttribute.PACKAGE_NAME: "ru.app",
                        DictAttribute.ENABLED: True,
                        DictAttribute.CLICKABLE: True,
                    },
            ),
            (
                    '//*[starts-with(@text, "File")][matches(@class, ".*ListView")][@scrollable="true"]',
                    {
                        DictAttribute.TEXT_STARTS_WITH: "File",
                        DictAttribute.CLASS_NAME_MATCHES: ".*ListView",
                        DictAttribute.SCROLLABLE: True,
                    },
            ),
            (
                    '//*[matches(@resource-id, ".*toolbar")][matches(@content-desc, ".*tool.*")][@long-clickable="true"]',
                    {
                        DictAttribute.RESOURCE_ID_MATCHES: ".*toolbar",
                        DictAttribute.DESCRIPTION_MATCHES: ".*tool.*",
                        DictAttribute.LONG_CLICKABLE: True,
                    },
            ),
            (
                    '//*[@text="Submit"][contains(@content-desc, "send")][@class="android.widget.Button"][@enabled="true"][@clickable="true"][position()=1][position()=4]',
                    {
                        DictAttribute.TEXT: "Submit",
                        DictAttribute.DESCRIPTION_CONTAINS: "send",
                        DictAttribute.CLASS_NAME: "android.widget.Button",
                        DictAttribute.ENABLED: True,
                        DictAttribute.CLICKABLE: True,
                        DictAttribute.INDEX: 3,  # Last index wins
                    },
            ),
            (
                    '//*[@text="Оплатить"]/*[@class="android.widget.ImageView"]',
                    {
                        DictAttribute.TEXT: "Оплатить",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.CLASS_NAME: "android.widget.ImageView",
                        },
                    },
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[contains(@text, "Email")]',
                    {
                        DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.TEXT_CONTAINS: "Email",
                        },
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"]/../*[@class="android.widget.ScrollView"]',
                    {
                        DictAttribute.RESOURCE_ID: "ru.app:id/input",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.CLASS_NAME: "android.widget.ScrollView",
                        },
                    },
            ),
            (
                    '//*[@class="android.widget.Button"][starts-with(@text,"Дал")]/*[@content-desc="icon"]',
                    {
                        DictAttribute.CLASS_NAME: "android.widget.Button",
                        DictAttribute.TEXT_STARTS_WITH: "Дал",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.DESCRIPTION: "icon",
                        },
                    },
            ),
            (
                    '//*[@text="Settings"]/../*[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        DictAttribute.TEXT: "Settings",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.RESOURCE_ID: "ru.app:id/switch",
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
        assert expected == shadowstep_dict  # noqa: S101  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # 1) Твой исходный пример (базовый sanity)
            (
                    '//*[@text="Settings"][@class="android.widget.Button"]/../*[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        DictAttribute.TEXT: "Settings",
                        DictAttribute.CLASS_NAME: "android.widget.Button",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.RESOURCE_ID: "ru.app:id/switch",
                            },
                        },
                    },
            ),

            # 2) Два шага вверх, затем два шага вниз по классам и ресурс-id в конце
            (
                    '//*[@text="Root"]/../../*[@class="L1"]/*[@class="L2"]/*[@resource-id="app:id/toggle"]',
                    {
                        DictAttribute.TEXT: "Root",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.FROM_PARENT: {
                                DictAttribute.CLASS_NAME: "L1",
                                DictAttribute.CHILD_SELECTOR: {
                                    DictAttribute.CLASS_NAME: "L2",
                                    DictAttribute.CHILD_SELECTOR: {
                                        DictAttribute.RESOURCE_ID: "app:id/toggle",
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
                        DictAttribute.TEXT: "Deep",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.CLASS_NAME: "A",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.CLASS_NAME: "B",
                                DictAttribute.CHILD_SELECTOR: {
                                    DictAttribute.CLASS_NAME: "C",
                                    DictAttribute.CHILD_SELECTOR: {
                                        DictAttribute.CLASS_NAME: "D",
                                        DictAttribute.CHILD_SELECTOR: {
                                            DictAttribute.RESOURCE_ID: "pkg:id/end",
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
                        DictAttribute.TEXT: "T",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.FROM_PARENT: {
                                DictAttribute.FROM_PARENT: {
                                    DictAttribute.CLASS_NAME: "P1",
                                    DictAttribute.CHILD_SELECTOR: {
                                        DictAttribute.CLASS_NAME: "P2",
                                        DictAttribute.CHILD_SELECTOR: {
                                            DictAttribute.RESOURCE_ID: "pkg:id/final",
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
                        DictAttribute.TEXT: "Anchor",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.CLASS_NAME: "L1",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.CLASS_NAME: "L2",
                                DictAttribute.CHILD_SELECTOR: {
                                    DictAttribute.CLASS_NAME: "L3",
                                    DictAttribute.CHILD_SELECTOR: {
                                        DictAttribute.CLASS_NAME: "L4",
                                        DictAttribute.CHILD_SELECTOR: {
                                            DictAttribute.CLASS_NAME: "L5",
                                            DictAttribute.CHILD_SELECTOR: {
                                                DictAttribute.RESOURCE_ID: "app:id/leaf",
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
                        DictAttribute.TEXT: "Mixed",
                        DictAttribute.FROM_PARENT: {
                            # После '..' первый нисходящий шаг
                            DictAttribute.CLASS_NAME: "C1",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.CLASS_NAME: "C2",
                                DictAttribute.CHILD_SELECTOR: {
                                    # ещё один нисходящий шаг через //
                                    DictAttribute.RESOURCE_ID: "pkg:id/x",
                                },
                            },
                        },
                    },
            ),

            # 7) Максимально «сумасшедшая» матрёшка: вверх x3, затем вниз x6
            (
                    '//*[@text="Mega"]/../../../*[@class="L1"]/*[@class="L2"]/*[@class="L3"]/*[@class="L4"]/*[@class="L5"]/*[@class="L6"]/*[@resource-id="pkg:id/the_end"]',
                    {
                        DictAttribute.TEXT: "Mega",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.FROM_PARENT: {
                                DictAttribute.FROM_PARENT: {
                                    DictAttribute.CLASS_NAME: "L1",
                                    DictAttribute.CHILD_SELECTOR: {
                                        DictAttribute.CLASS_NAME: "L2",
                                        DictAttribute.CHILD_SELECTOR: {
                                            DictAttribute.CLASS_NAME: "L3",
                                            DictAttribute.CHILD_SELECTOR: {
                                                DictAttribute.CLASS_NAME: "L4",
                                                DictAttribute.CHILD_SELECTOR: {
                                                    DictAttribute.CLASS_NAME: "L5",
                                                    DictAttribute.CHILD_SELECTOR: {
                                                        DictAttribute.CLASS_NAME: "L6",
                                                        DictAttribute.CHILD_SELECTOR: {
                                                            DictAttribute.RESOURCE_ID: "pkg:id/the_end",
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
    def test_xpath_to_dict_deep_nesting(self, xpath: Any, expected: Any):
        converter = XPathConverter()
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {shadowstep_dict=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert shadowstep_dict == expected  # noqa: S101  # noqa: S101

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # 1) contains(@text, ...)
            (
                    '//*[contains(@text, "Hello")]/../*[@class="android.view.View"]/*[contains(@content-desc, "Btn")]',
                    {
                        DictAttribute.TEXT_CONTAINS: "Hello",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.CLASS_NAME: "android.view.View",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.DESCRIPTION_CONTAINS: "Btn",
                            },
                        },
                    },
            ),

            # 2) starts-with(@content-desc, ...)
            (
                    '//*[@text="Start"]/../*[starts-with(@content-desc, "prefix")]/child::*[@resource-id="pkg:id/target"]',
                    {
                        DictAttribute.TEXT: "Start",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.DESCRIPTION_STARTS_WITH: "prefix",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.RESOURCE_ID: "pkg:id/target",
                            },
                        },
                    },
            ),

            # 3) matches(@resource-id, regex)
            (
                    '//*[@class="android.widget.LinearLayout"]//node()[matches(@resource-id, ".*button.*")]',
                    {
                        DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                        DictAttribute.CHILD_SELECTOR: {
                            DictAttribute.RESOURCE_ID_MATCHES: ".*button.*",
                        },
                    },
            ),

            # 4) Комбо: text, затем contains, потом starts-with и в конце matches
            (
                    '//*[@text="Anchor"]/../*[contains(@text, "foo")]/child::*[starts-with(@content-desc, "bar")]/*[matches(@class, ".*Layout")]',
                    {
                        DictAttribute.TEXT: "Anchor",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.TEXT_CONTAINS: "foo",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.DESCRIPTION_STARTS_WITH: "bar",
                                DictAttribute.CHILD_SELECTOR: {
                                    DictAttribute.CLASS_NAME_MATCHES: ".*Layout",
                                },
                            },
                        },
                    },
            ),

            # 5) Супер-вложенность: 2 раза вверх, потом цепочка из contains → starts-with → matches → resource-id
            (
                    '//*[@text="Mega"]/../../*[contains(@text, "deep")]/child::*[starts-with(@content-desc, "zzz")]/*[matches(@package, "com\\..*")]/*[@resource-id="pkg:id/the_end"]',
                    {
                        DictAttribute.TEXT: "Mega",
                        DictAttribute.FROM_PARENT: {
                            DictAttribute.FROM_PARENT: {
                                DictAttribute.TEXT_CONTAINS: "deep",
                                DictAttribute.CHILD_SELECTOR: {
                                    DictAttribute.DESCRIPTION_STARTS_WITH: "zzz",
                                    DictAttribute.CHILD_SELECTOR: {
                                        DictAttribute.PACKAGE_NAME_MATCHES: "com\\..*",
                                        DictAttribute.CHILD_SELECTOR: {
                                            DictAttribute.RESOURCE_ID: "pkg:id/the_end",
                                        },
                                    },
                                },
                            }
                        },
                    },
            ),
        ],
    )
    def test_xpath_to_dict_with_functions(self, xpath: Any, expected: Any):
        converter = XPathConverter()
        shadowstep_dict = converter.xpath_to_dict(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {shadowstep_dict=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert shadowstep_dict == expected  # noqa: S101  # noqa: S101


    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # простой sibling по классу
            (
                    '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]',
                    {
                        DictAttribute.TEXT: "Anchor",
                        DictAttribute.SIBLING: {
                            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                        },
                    },
            ),
            # sibling + child
            (
                    '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]/child::*[@resource-id="pkg:id/target"]',
                    {
                        DictAttribute.TEXT: "Anchor",
                        DictAttribute.SIBLING: {
                            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.RESOURCE_ID: "pkg:id/target",
                            },
                        },
                    },
            ),
            # sibling → child → sibling
            (
                    '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]/child::*[@resource-id="pkg:id/target"]/following-sibling::*[contains(@content-desc,"final")]',
                    {
                        DictAttribute.TEXT: "Anchor",
                        DictAttribute.SIBLING: {
                            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            DictAttribute.CHILD_SELECTOR: {
                                DictAttribute.RESOURCE_ID: "pkg:id/target",
                                DictAttribute.SIBLING: {
                                    DictAttribute.DESCRIPTION_CONTAINS: "final",
                                },
                            },
                        },
                    },
            ),
            # sibling со starts-with
            (
                    '//*[@text="Btn"]/following-sibling::*[starts-with(@content-desc,"prefix")]',
                    {
                        DictAttribute.TEXT: "Btn",
                        DictAttribute.SIBLING: {
                            DictAttribute.DESCRIPTION_STARTS_WITH: "prefix",
                        },
                    },
            ),
            # sibling с matches
            (
                    '//*[@class="android.widget.LinearLayout"]/following-sibling::*[matches(@resource-id,".*button.*")]',
                    {
                        DictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                        DictAttribute.SIBLING: {
                            DictAttribute.RESOURCE_ID_MATCHES: ".*button.*",
                        },
                    },
            ),
            # глубокая вложенность: sibling → sibling → child
            (
                    '//*[@text="Mega"]/following-sibling::*[@class="android.widget.FrameLayout"]/following-sibling::*[matches(@package,"com.example")]/child::*[@content-desc="leaf"]',
                    {
                        DictAttribute.TEXT: "Mega",
                        DictAttribute.SIBLING: {
                            DictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            DictAttribute.SIBLING: {
                                DictAttribute.PACKAGE_NAME_MATCHES: "com.example",
                                DictAttribute.CHILD_SELECTOR: {
                                    DictAttribute.DESCRIPTION: "leaf",
                                },
                            },
                        },
                    },
            ),
        ],
    )
    def test_xpath_to_dict_with_following_sibling(self, xpath: str, expected: dict[str, Any]):
        converter = XPathConverter()
        result = converter.xpath_to_dict(xpath)
        assert result == expected  # noqa: S101  # noqa: S101

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
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {ui_selector=}")
        logger.info(f"\n {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == ui_selector  # noqa: S101  # noqa: S101

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
                    'new UiSelector().textMatches("\\d{3}-\\d{2}-\\d{4}");',
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
        ui_selector = converter.xpath_to_ui_selector(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {ui_selector=}")
        logger.info(f"\n    {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == ui_selector  # noqa: S101  # noqa: S101

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
            ui_selector = converter.xpath_to_ui_selector(xpath)
            # If conversion succeeds, it should not match expected empty string
            assert ui_selector != expected  # noqa: S101  # noqa: S101
        except ConversionError:
            # Expected behavior for invalid XPath
            pass
    
    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            (
                '//*[@text="Root"]/../../*[@class="L1"]/*[@class="L2"]/*[@resource-id="app:id/toggle"]',
                'new UiSelector().text("Root").fromParent(new UiSelector().fromParent(new UiSelector().className("L1").childSelector(new UiSelector().className("L2").childSelector(new UiSelector().resourceId("app:id/toggle")))));'
            ),
            (
                '//*[@text="Deep"]/../*[@class="A"]/*[@class="B"]/*[@class="C"]/*[@class="D"]/*[@resource-id="pkg:id/end"]',
                'new UiSelector().text("Deep").fromParent(new UiSelector().className("A").childSelector(new UiSelector().className("B").childSelector(new UiSelector().className("C").childSelector(new UiSelector().className("D").childSelector(new UiSelector().resourceId("pkg:id/end"))))));'
            ),
            (
                '//*[@text="T"]/../../../*[@class="P1"]/*[@class="P2"]/*[@resource-id="pkg:id/final"]',
                'new UiSelector().text("T").fromParent(new UiSelector().fromParent(new UiSelector().fromParent(new UiSelector().className("P1").childSelector(new UiSelector().className("P2").childSelector(new UiSelector().resourceId("pkg:id/final"))))));'
            ),
            # Добавьте другие глубокие вложенные сценарии если нужно
        ],
    )
    def test_xpath_to_ui_deep_nesting(self, xpath: str, expected: str):
        converter = XPathConverter()
        ui_selector = converter.xpath_to_ui_selector(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {ui_selector=}")
        logger.info(f"\n    {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == ui_selector  # noqa: S101  # noqa: S101
    
    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            (
                '//*[contains(@text, "Hello")]/../*[@class="android.view.View"]/*[contains(@content-desc, "Btn")]',
                'new UiSelector().textContains("Hello").fromParent(new UiSelector().className("android.view.View").childSelector(new UiSelector().descriptionContains("Btn")));'
            ),
            (
                '//*[@text="Start"]/../*[starts-with(@content-desc, "prefix")]/child::*[@resource-id="pkg:id/target"]',
                'new UiSelector().text("Start").fromParent(new UiSelector().descriptionStartsWith("prefix").childSelector(new UiSelector().resourceId("pkg:id/target")));'
            ),
            (
                '//*[@class="android.widget.LinearLayout"]//node()[matches(@resource-id, ".*button.*")]',
                'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().resourceIdMatches(".*button.*"));'
            ),
            (
                '//*[@text="Anchor"]/../*[contains(@text, "foo")]/child::*[starts-with(@content-desc, "bar")]/*[matches(@class, ".*Layout")]',
                'new UiSelector().text("Anchor").fromParent(new UiSelector().textContains("foo").childSelector(new UiSelector().descriptionStartsWith("bar").childSelector(new UiSelector().classNameMatches(".*Layout"))));'
            ),
            (
                '//*[@text="Mega"]/../../*[contains(@text, "deep")]/child::*[starts-with(@content-desc, "zzz")]/*[matches(@package, "com\\..*")]/*[@resource-id="pkg:id/the_end"]',
                'new UiSelector().text("Mega").fromParent(new UiSelector().fromParent(new UiSelector().textContains("deep").childSelector(new UiSelector().descriptionStartsWith("zzz").childSelector(new UiSelector().packageNameMatches("com\\..*").childSelector(new UiSelector().resourceId("pkg:id/the_end"))))));'
            ),
            # Можно добавить другие варианты функций для покрытия
        ],
    )
    def test_xpath_to_ui_with_functions(self, xpath: str, expected: str):
        converter = XPathConverter()
        ui_selector = converter.xpath_to_ui_selector(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {ui_selector=}")
        logger.info(f"\n    {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == ui_selector  # noqa: S101  # noqa: S101
    
    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [
            # простой sibling по классу
            (
                '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]',
                'new UiSelector().text("Anchor").fromParent(new UiSelector().className("android.widget.FrameLayout"));'
            ),
            # sibling + child
            (
                '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]/child::*[@resource-id="pkg:id/target"]',
                'new UiSelector().text("Anchor").fromParent(new UiSelector().className("android.widget.FrameLayout").childSelector(new UiSelector().resourceId("pkg:id/target")));'
            ),
            # sibling → child → sibling
            (
                '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]/child::*[@resource-id="pkg:id/target"]/following-sibling::*[contains(@content-desc,"final")]',
                'new UiSelector().text("Anchor").fromParent(new UiSelector().className("android.widget.FrameLayout").childSelector(new UiSelector().resourceId("pkg:id/target").fromParent(new UiSelector().descriptionContains("final"))));'
            ),
            # sibling со starts-with
            (
                '//*[@text="Btn"]/following-sibling::*[starts-with(@content-desc,"prefix")]',
                'new UiSelector().text("Btn").fromParent(new UiSelector().descriptionStartsWith("prefix"));'
            ),
            # sibling с matches
            (
                '//*[@class="android.widget.LinearLayout"]/following-sibling::*[matches(@resource-id,".*button.*")]',
                'new UiSelector().className("android.widget.LinearLayout").fromParent(new UiSelector().resourceIdMatches(".*button.*"));'
            ),
            # глубокая вложенность: sibling → sibling → child
            (
                '//*[@text="Mega"]/following-sibling::*[@class="android.widget.FrameLayout"]/following-sibling::*[matches(@package,"com.example")]/child::*[@content-desc="leaf"]',
                'new UiSelector().text("Mega").fromParent(new UiSelector().className("android.widget.FrameLayout").fromParent(new UiSelector().packageNameMatches("com.example").childSelector(new UiSelector().description("leaf"))));'
            ),
        ],
    )
    def test_xpath_to_ui_with_following_sibling(self, xpath: str, expected: str):
        converter = XPathConverter()
        ui_selector = converter.xpath_to_ui_selector(xpath)
        logger.info("+++++++++++++++++++++++++++++++++")
        logger.info(f"\n {xpath=}")
        logger.info(f"\n {ui_selector=}")
        logger.info(f"\n    {expected=}")
        logger.info("+++++++++++++++++++++++++++++++++")
        assert expected == ui_selector  # noqa: S101  # noqa: S101

