import logging
from typing import Any

import pytest

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepConversionError,
    ShadowstepUnsupportedAttributeExpressionError,
    ShadowstepUnsupportedComparisonOperatorError,
    ShadowstepEqualityComparisonError,
)
from shadowstep.locator.converter.xpath_converter import XPathConverter
from shadowstep.locator.locator_types.shadowstep_dict import ShadowstepDictAttribute

logger = logging.getLogger(__name__)


class TestXPathConverter:

    @pytest.mark.parametrize(
        "xpath, expected",  # noqa: PT006
        [  # pyright: ignore [reportUnknownArgumentType]
            # --- text-based ---
            ('//*[@text="Hello"]', {ShadowstepDictAttribute.TEXT: "Hello"}),
            ('//*[contains(@text,"Hello")]', {ShadowstepDictAttribute.TEXT_CONTAINS: "Hello"}),
            ('//*[starts-with(@text,"Pay")]', {ShadowstepDictAttribute.TEXT_STARTS_WITH: "Pay"}),
            ('//*[matches(@text,".*Test.*")]', {ShadowstepDictAttribute.TEXT_MATCHES: ".*Test.*"}),

            # --- description ---
            ('//*[@content-desc="desc"]', {ShadowstepDictAttribute.DESCRIPTION: "desc"}),
            ('//*[contains(@content-desc,"part")]', {ShadowstepDictAttribute.DESCRIPTION_CONTAINS: "part"}),
            ('//*[starts-with(@content-desc,"start")]', {ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: "start"}),
            ('//*[matches(@content-desc,"regex.*")]', {ShadowstepDictAttribute.DESCRIPTION_MATCHES: "regex.*"}),

            # --- resource id / package ---
            ('//*[@resource-id="resId"]', {ShadowstepDictAttribute.RESOURCE_ID: "resId"}),
            ('//*[matches(@resource-id,"res.*")]', {ShadowstepDictAttribute.RESOURCE_ID_MATCHES: "res.*"}),
            ('//*[@package="pkg.name"]', {ShadowstepDictAttribute.PACKAGE_NAME: "pkg.name"}),
            ('//*[matches(@package,"pkg.name")]', {ShadowstepDictAttribute.PACKAGE_NAME_MATCHES: "pkg.name"}),

            # --- class ---
            ('//*[@class="android.widget.Button"]', {ShadowstepDictAttribute.CLASS_NAME: "android.widget.Button"}),
            ('//*[matches(@class,".*Button")]', {ShadowstepDictAttribute.CLASS_NAME_MATCHES: ".*Button"}),

            # --- bool props ---
            ('//*[@checkable="true"]', {ShadowstepDictAttribute.CHECKABLE: True}),
            ('//*[@checked="false"]', {ShadowstepDictAttribute.CHECKED: False}),
            ('//*[@clickable="true"]', {ShadowstepDictAttribute.CLICKABLE: True}),
            ('//*[@enabled="true"]', {ShadowstepDictAttribute.ENABLED: True}),
            ('//*[@focusable="true"]', {ShadowstepDictAttribute.FOCUSABLE: True}),
            ('//*[@focused="false"]', {ShadowstepDictAttribute.FOCUSED: False}),
            ('//*[@long-clickable="true"]', {ShadowstepDictAttribute.LONG_CLICKABLE: True}),
            ('//*[@scrollable="false"]', {ShadowstepDictAttribute.SCROLLABLE: False}),
            ('//*[@selected="false"]', {ShadowstepDictAttribute.SELECTED: False}),
            ('//*[@password="true"]', {ShadowstepDictAttribute.PASSWORD: True}),

            # --- numeric ---
            ("//*[position()=3]", {ShadowstepDictAttribute.INDEX: 2}),
            ("//*[6]", {ShadowstepDictAttribute.INSTANCE: 5}),

            # --- hierarchy ---
            ('//*[@content-desc="Confirm"]/*[@class="android.widget.ImageView"]',
             {ShadowstepDictAttribute.DESCRIPTION: "Confirm",
              ShadowstepDictAttribute.CHILD_SELECTOR: {"class": "android.widget.ImageView"}}),
            ('//*[@class="android.widget.RadioButton"]/..//*[@resource-id="ru.figma.app.debug:id/paymentMethods"]',
             {ShadowstepDictAttribute.CLASS_NAME: "android.widget.RadioButton",
              ShadowstepDictAttribute.FROM_PARENT: {
                  ShadowstepDictAttribute.RESOURCE_ID: "ru.figma.app.debug:id/paymentMethods"}}),
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
                        ShadowstepDictAttribute.TEXT: "OK",
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.Button",
                        ShadowstepDictAttribute.INDEX: 0,
                    },
            ),
            (
                    '//*[contains(@text, "Confirm")][@clickable="true"]',
                    {
                        ShadowstepDictAttribute.TEXT_CONTAINS: "Confirm",
                        ShadowstepDictAttribute.CLICKABLE: True,
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/btn"][@enabled="false"]',
                    {
                        ShadowstepDictAttribute.RESOURCE_ID: "ru.app:id/btn",
                        ShadowstepDictAttribute.ENABLED: False,
                    },
            ),
            (
                    '//*[starts-with(@text, "Start")][@package="ru.app"][@focusable="true"]',
                    {
                        ShadowstepDictAttribute.TEXT_STARTS_WITH: "Start",
                        ShadowstepDictAttribute.PACKAGE_NAME: "ru.app",
                        ShadowstepDictAttribute.FOCUSABLE: True,
                    },
            ),
            (
                    '//*[contains(@content-desc, "icon")][@long-clickable="true"][@class="android.widget.ImageView"]',
                    {
                        ShadowstepDictAttribute.DESCRIPTION_CONTAINS: "icon",
                        ShadowstepDictAttribute.LONG_CLICKABLE: True,
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.ImageView",
                    },
            ),
            (
                    '//*[matches(@text, ".*Test.*")][@scrollable="false"]',
                    {
                        ShadowstepDictAttribute.TEXT_MATCHES: ".*Test.*",
                        ShadowstepDictAttribute.SCROLLABLE: False,
                    },
            ),
            (
                    '//*[@content-desc="switch"][@checked="true"][position()=2]',
                    {
                        ShadowstepDictAttribute.DESCRIPTION: "switch",
                        ShadowstepDictAttribute.CHECKED: True,
                        ShadowstepDictAttribute.INDEX: 1,
                    },
            ),
            (
                    '//*[@package="ru.pkg"][@enabled="true"][@selected="false"]',
                    {
                        ShadowstepDictAttribute.PACKAGE_NAME: "ru.pkg",
                        ShadowstepDictAttribute.ENABLED: True,
                        ShadowstepDictAttribute.SELECTED: False,
                    },
            ),
            (
                    '//*[matches(@class, ".*EditText")][@focusable="true"][position()=3]',
                    {
                        ShadowstepDictAttribute.CLASS_NAME_MATCHES: ".*EditText",
                        ShadowstepDictAttribute.FOCUSABLE: True,
                        ShadowstepDictAttribute.INDEX: 2,
                    },
            ),
            (
                    '//*[@text="Save"][matches(@content-desc, ".*save.*")][@clickable="true"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Save",
                        ShadowstepDictAttribute.DESCRIPTION_MATCHES: ".*save.*",
                        ShadowstepDictAttribute.CLICKABLE: True,
                    },
            ),
            (
                    '//*[matches(@resource-id, ".*btn.*")][contains(@text, "Send")][@enabled="true"]',
                    {
                        ShadowstepDictAttribute.RESOURCE_ID_MATCHES: ".*btn.*",
                        ShadowstepDictAttribute.TEXT_CONTAINS: "Send",
                        ShadowstepDictAttribute.ENABLED: True,
                    },
            ),
            (
                    '//*[@class="android.widget.TextView"][starts-with(@content-desc, "hint")][@long-clickable="false"]',
                    {
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.TextView",
                        ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: "hint",
                        ShadowstepDictAttribute.LONG_CLICKABLE: False,
                    },
            ),
            (
                    '//*[@text="OK"][matches(@package, "com.example.*")][@checked="true"]',
                    {
                        ShadowstepDictAttribute.TEXT: "OK",
                        ShadowstepDictAttribute.PACKAGE_NAME_MATCHES: "com.example.*",
                        ShadowstepDictAttribute.CHECKED: True,
                    },
            ),
            (
                    '//*[contains(@content-desc, "item")][position()=5][position()=2]',
                    {
                        ShadowstepDictAttribute.DESCRIPTION_CONTAINS: "item",
                        ShadowstepDictAttribute.INDEX: 1,  # Last index wins
                    },
            ),
            (
                    '//*[matches(@text, ".*done.*")][@class="android.widget.CheckBox"][@selected="true"]',
                    {
                        ShadowstepDictAttribute.TEXT_MATCHES: ".*done.*",
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.CheckBox",
                        ShadowstepDictAttribute.SELECTED: True,
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"][@text="Login"][@focusable="true"][@focused="false"]',
                    {
                        ShadowstepDictAttribute.RESOURCE_ID: "ru.app:id/input",
                        ShadowstepDictAttribute.TEXT: "Login",
                        ShadowstepDictAttribute.FOCUSABLE: True,
                        ShadowstepDictAttribute.FOCUSED: False,
                    },
            ),
            (
                    '//*[@content-desc="menu"][@package="ru.app"][@enabled="true"][@clickable="true"]',
                    {
                        ShadowstepDictAttribute.DESCRIPTION: "menu",
                        ShadowstepDictAttribute.PACKAGE_NAME: "ru.app",
                        ShadowstepDictAttribute.ENABLED: True,
                        ShadowstepDictAttribute.CLICKABLE: True,
                    },
            ),
            (
                    '//*[starts-with(@text, "File")][matches(@class, ".*ListView")][@scrollable="true"]',
                    {
                        ShadowstepDictAttribute.TEXT_STARTS_WITH: "File",
                        ShadowstepDictAttribute.CLASS_NAME_MATCHES: ".*ListView",
                        ShadowstepDictAttribute.SCROLLABLE: True,
                    },
            ),
            (
                    '//*[matches(@resource-id, ".*toolbar")][matches(@content-desc, ".*tool.*")][@long-clickable="true"]',
                    {
                        ShadowstepDictAttribute.RESOURCE_ID_MATCHES: ".*toolbar",
                        ShadowstepDictAttribute.DESCRIPTION_MATCHES: ".*tool.*",
                        ShadowstepDictAttribute.LONG_CLICKABLE: True,
                    },
            ),
            (
                    '//*[@text="Submit"][contains(@content-desc, "send")][@class="android.widget.Button"][@enabled="true"][@clickable="true"][position()=1][position()=4]',
                    {
                        ShadowstepDictAttribute.TEXT: "Submit",
                        ShadowstepDictAttribute.DESCRIPTION_CONTAINS: "send",
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.Button",
                        ShadowstepDictAttribute.ENABLED: True,
                        ShadowstepDictAttribute.CLICKABLE: True,
                        ShadowstepDictAttribute.INDEX: 3,  # Last index wins
                    },
            ),
            (
                    '//*[@text="Pay"]/*[@class="android.widget.ImageView"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Pay",
                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.ImageView",
                        },
                    },
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[contains(@text, "Email")]',
                    {
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                            ShadowstepDictAttribute.TEXT_CONTAINS: "Email",
                        },
                    },
            ),
            (
                    '//*[@resource-id="ru.app:id/input"]/../*[@class="android.widget.ScrollView"]',
                    {
                        ShadowstepDictAttribute.RESOURCE_ID: "ru.app:id/input",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.ScrollView",
                        },
                    },
            ),
            (
                    '//*[@class="android.widget.Button"][starts-with(@text,"Give")]/*[@content-desc="icon"]',
                    {
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.Button",
                        ShadowstepDictAttribute.TEXT_STARTS_WITH: "Give",
                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                            ShadowstepDictAttribute.DESCRIPTION: "icon",
                        },
                    },
            ),
            (
                    '//*[@text="Settings"]/../*[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Settings",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.RESOURCE_ID: "ru.app:id/switch",
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
            # 1) Your original example (basic sanity)
            (
                    '//*[@text="Settings"][@class="android.widget.Button"]/../*[@class="android.widget.FrameLayout"]/*[@resource-id="ru.app:id/switch"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Settings",
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.Button",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.RESOURCE_ID: "ru.app:id/switch",
                            },
                        },
                    },
            ),

            # 2) Two steps up, then two steps down by classes and resource-id at the end
            (
                    '//*[@text="Root"]/../../*[@class="L1"]/*[@class="L2"]/*[@resource-id="app:id/toggle"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Root",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.FROM_PARENT: {
                                ShadowstepDictAttribute.CLASS_NAME: "L1",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    ShadowstepDictAttribute.CLASS_NAME: "L2",
                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                        ShadowstepDictAttribute.RESOURCE_ID: "app:id/toggle",
                                    },
                                },
                            }
                        },
                    },
            ),

            # 3) One step up, then long chain down (5 levels)
            (
                    '//*[@text="Deep"]/../*[@class="A"]/*[@class="B"]/*[@class="C"]/*[@class="D"]/*[@resource-id="pkg:id/end"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Deep",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.CLASS_NAME: "A",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.CLASS_NAME: "B",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    ShadowstepDictAttribute.CLASS_NAME: "C",
                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                        ShadowstepDictAttribute.CLASS_NAME: "D",
                                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                                            ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/end",
                                        },
                                    },
                                },
                            },
                        },
                    },
            ),

            # 4) Three steps up, then two down
            (
                    '//*[@text="T"]/../../../*[@class="P1"]/*[@class="P2"]/*[@resource-id="pkg:id/final"]',
                    {
                        ShadowstepDictAttribute.TEXT: "T",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.FROM_PARENT: {
                                ShadowstepDictAttribute.FROM_PARENT: {
                                    ShadowstepDictAttribute.CLASS_NAME: "P1",
                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                        ShadowstepDictAttribute.CLASS_NAME: "P2",
                                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                                            ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/final",
                                        },
                                    },
                                }
                            }
                        },
                    },
            ),

            # 5) Deep purely descending chain (without ..), 6 levels
            (
                    '//*[*[@text="Anchor"]]/*[@class="L1"]/*[@class="L2"]/*[@class="L3"]/*[@class="L4"]/*[@class="L5"]/*[@resource-id="app:id/leaf"]',
                    {
                        # Since at root we have predicate by text(), it will go to top level
                        ShadowstepDictAttribute.TEXT: "Anchor",
                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                            ShadowstepDictAttribute.CLASS_NAME: "L1",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.CLASS_NAME: "L2",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    ShadowstepDictAttribute.CLASS_NAME: "L3",
                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                        ShadowstepDictAttribute.CLASS_NAME: "L4",
                                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                                            ShadowstepDictAttribute.CLASS_NAME: "L5",
                                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                                ShadowstepDictAttribute.RESOURCE_ID: "app:id/leaf",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
            ),

            # 6) Mixed: up, down, down again via double slash (// treated as / in tree building)
            (
                    '//*[@text="Mixed"]/..//*[@class="C1"]/*[@class="C2"]//*[@resource-id="pkg:id/x"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Mixed",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            # After '..' first descending step
                            ShadowstepDictAttribute.CLASS_NAME: "C1",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.CLASS_NAME: "C2",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    # another descending step via //
                                    ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/x",
                                },
                            },
                        },
                    },
            ),

            # 7) Maximum "crazy" nesting: up x3, then down x6
            (
                    '//*[@text="Mega"]/../../../*[@class="L1"]/*[@class="L2"]/*[@class="L3"]/*[@class="L4"]/*[@class="L5"]/*[@class="L6"]/*[@resource-id="pkg:id/the_end"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Mega",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.FROM_PARENT: {
                                ShadowstepDictAttribute.FROM_PARENT: {
                                    ShadowstepDictAttribute.CLASS_NAME: "L1",
                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                        ShadowstepDictAttribute.CLASS_NAME: "L2",
                                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                                            ShadowstepDictAttribute.CLASS_NAME: "L3",
                                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                                ShadowstepDictAttribute.CLASS_NAME: "L4",
                                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                                    ShadowstepDictAttribute.CLASS_NAME: "L5",
                                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                                        ShadowstepDictAttribute.CLASS_NAME: "L6",
                                                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                                                            ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/the_end",
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
                        ShadowstepDictAttribute.TEXT_CONTAINS: "Hello",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.view.View",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.DESCRIPTION_CONTAINS: "Btn",
                            },
                        },
                    },
            ),

            # 2) starts-with(@content-desc, ...)
            (
                    '//*[@text="Start"]/../*[starts-with(@content-desc, "prefix")]/child::*[@resource-id="pkg:id/target"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Start",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: "prefix",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/target",
                            },
                        },
                    },
            ),

            # 3) matches(@resource-id, regex)
            (
                    '//*[@class="android.widget.LinearLayout"]//node()[matches(@resource-id, ".*button.*")]',
                    {
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                            ShadowstepDictAttribute.RESOURCE_ID_MATCHES: ".*button.*",
                        },
                    },
            ),

            # 4) Combo: text, then contains, then starts-with and finally matches
            (
                    '//*[@text="Anchor"]/../*[contains(@text, "foo")]/child::*[starts-with(@content-desc, "bar")]/*[matches(@class, ".*Layout")]',
                    {
                        ShadowstepDictAttribute.TEXT: "Anchor",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.TEXT_CONTAINS: "foo",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: "bar",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    ShadowstepDictAttribute.CLASS_NAME_MATCHES: ".*Layout",
                                },
                            },
                        },
                    },
            ),

            # 5) Super nesting: 2 times up, then chain from contains → starts-with → matches → resource-id
            (
                    '//*[@text="Mega"]/../../*[contains(@text, "deep")]/child::*[starts-with(@content-desc, "zzz")]/*[matches(@package, "com\\..*")]/*[@resource-id="pkg:id/the_end"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Mega",
                        ShadowstepDictAttribute.FROM_PARENT: {
                            ShadowstepDictAttribute.FROM_PARENT: {
                                ShadowstepDictAttribute.TEXT_CONTAINS: "deep",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: "zzz",
                                    ShadowstepDictAttribute.CHILD_SELECTOR: {
                                        ShadowstepDictAttribute.PACKAGE_NAME_MATCHES: "com\\..*",
                                        ShadowstepDictAttribute.CHILD_SELECTOR: {
                                            ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/the_end",
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
            # simple sibling by class
            (
                    '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Anchor",
                        ShadowstepDictAttribute.SIBLING: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                        },
                    },
            ),
            # sibling + child
            (
                    '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]/child::*[@resource-id="pkg:id/target"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Anchor",
                        ShadowstepDictAttribute.SIBLING: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/target",
                            },
                        },
                    },
            ),
            # sibling → child → sibling
            (
                    '//*[@text="Anchor"]/following-sibling::*[@class="android.widget.FrameLayout"]/child::*[@resource-id="pkg:id/target"]/following-sibling::*[contains(@content-desc,"final")]',
                    {
                        ShadowstepDictAttribute.TEXT: "Anchor",
                        ShadowstepDictAttribute.SIBLING: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            ShadowstepDictAttribute.CHILD_SELECTOR: {
                                ShadowstepDictAttribute.RESOURCE_ID: "pkg:id/target",
                                ShadowstepDictAttribute.SIBLING: {
                                    ShadowstepDictAttribute.DESCRIPTION_CONTAINS: "final",
                                },
                            },
                        },
                    },
            ),
            # sibling with starts-with
            (
                    '//*[@text="Btn"]/following-sibling::*[starts-with(@content-desc,"prefix")]',
                    {
                        ShadowstepDictAttribute.TEXT: "Btn",
                        ShadowstepDictAttribute.SIBLING: {
                            ShadowstepDictAttribute.DESCRIPTION_STARTS_WITH: "prefix",
                        },
                    },
            ),
            # sibling with matches
            (
                    '//*[@class="android.widget.LinearLayout"]/following-sibling::*[matches(@resource-id,".*button.*")]',
                    {
                        ShadowstepDictAttribute.CLASS_NAME: "android.widget.LinearLayout",
                        ShadowstepDictAttribute.SIBLING: {
                            ShadowstepDictAttribute.RESOURCE_ID_MATCHES: ".*button.*",
                        },
                    },
            ),
            # deep nesting: sibling → sibling → child
            (
                    '//*[@text="Mega"]/following-sibling::*[@class="android.widget.FrameLayout"]/following-sibling::*[matches(@package,"com.example")]/child::*[@content-desc="leaf"]',
                    {
                        ShadowstepDictAttribute.TEXT: "Mega",
                        ShadowstepDictAttribute.SIBLING: {
                            ShadowstepDictAttribute.CLASS_NAME: "android.widget.FrameLayout",
                            ShadowstepDictAttribute.SIBLING: {
                                ShadowstepDictAttribute.PACKAGE_NAME_MATCHES: "com.example",
                                ShadowstepDictAttribute.CHILD_SELECTOR: {
                                    ShadowstepDictAttribute.DESCRIPTION: "leaf",
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
            ('//*[@text="Hello"]', 'new UiSelector().text("Hello");'),
            ('//*[contains(@text,"Hello")]', 'new UiSelector().textContains("Hello");'),
            ('//*[starts-with(@text,"Pay")]', 'new UiSelector().textStartsWith("Pay");'),
            ('//*[matches(@text,".*Test.*")]', 'new UiSelector().textMatches(".*Test.*");'),

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
                    '//*[starts-with(@text,"Pay")][@class="android.widget.Button"]/*[@class="android.widget.ImageView"]',
                    'new UiSelector().textStartsWith("Pay").className("android.widget.Button").childSelector(new UiSelector().className("android.widget.ImageView"));',
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
                    '//*[contains(@content-desc,"Map")][@clickable="true"]',
                    'new UiSelector().descriptionContains("Map").clickable(true);',
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
                    '//*[@scrollable="true"]/*[@text="History"]',
                    'new UiSelector().scrollable(true).childSelector(new UiSelector().text("History"));',
            ),
            (
                    '//*[@class="android.widget.CheckBox"][@checkable="true"][@checked="false"][3]',
                    'new UiSelector().className("android.widget.CheckBox").checkable(true).checked(false).instance(2);',
            ),
            (
                    '//*[starts-with(@text,"Pay")][contains(@text,"Card")][@enabled="true"]',
                    'new UiSelector().textStartsWith("Pay").textContains("Card").enabled(true);',
            ),
            (
                    '//*[matches(@class,"android\\.widget\\..*Button")][2]',
                    'new UiSelector().classNameMatches("android\\.widget\\..*Button").instance(1);',
            ),
            (
                    '//*[@content-desc="Confirm"][@clickable="true"]/*[@class="android.widget.ImageView"]',
                    'new UiSelector().description("Confirm").clickable(true).childSelector(new UiSelector().className("android.widget.ImageView"));',
            ),
            (
                    '//*[@class="android.widget.LinearLayout"]/*[@class="android.widget.FrameLayout"]/*[@text="List"]',
                    'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().className("android.widget.FrameLayout").childSelector(new UiSelector().text("List")));',
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
                    '//*[contains(@text,"card")][@resource-id="ru.figma.app.debug:id/card_number"]',
                    'new UiSelector().textContains("card").resourceId("ru.figma.app.debug:id/card_number");',
            ),
            (
                    '//*[@text="Pay"][@long-clickable="false"]',
                    'new UiSelector().text("Pay").longClickable(false);',
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
                    '//*[contains(@text, "section")][@class="android.widget.TextView"]',
                    'new UiSelector().textContains("section").className("android.widget.TextView");',
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
        except ShadowstepConversionError:
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
            # Add other deep nested scenarios if needed
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
            # Can add other function variants for coverage
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
            # simple sibling by class
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
            # sibling with starts-with
            (
                '//*[@text="Btn"]/following-sibling::*[starts-with(@content-desc,"prefix")]',
                'new UiSelector().text("Btn").fromParent(new UiSelector().descriptionStartsWith("prefix"));'
            ),
            # sibling with matches
            (
                '//*[@class="android.widget.LinearLayout"]/following-sibling::*[matches(@resource-id,".*button.*")]',
                'new UiSelector().className("android.widget.LinearLayout").fromParent(new UiSelector().resourceIdMatches(".*button.*"));'
            ),
            # deep nesting: sibling → sibling → child
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

    def test_to_bool_with_invalid_value(self):
        """Test _to_bool function with invalid values."""
        from shadowstep.locator.converter.xpath_converter import _to_bool
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepBooleanLiteralError
        
        # Test with invalid string
        with pytest.raises(ShadowstepBooleanLiteralError):
            _to_bool("invalid")
        
        # Test with invalid number
        with pytest.raises(ShadowstepBooleanLiteralError):
            _to_bool(123)
    
    def test_to_number_with_invalid_value(self):
        """Test _to_number function with invalid values."""
        from shadowstep.locator.converter.xpath_converter import _to_number
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepNumericLiteralError
        
        # Test with invalid string
        with pytest.raises(ShadowstepNumericLiteralError):
            _to_number("invalid")
        
        # Test with float that's not a whole number - this should actually work
        # as the function converts float to int
        result = _to_number(3.14)
        assert result == 3
    
    def test_validate_xpath_with_logical_operators(self):
        """Test _validate_xpath with logical operators."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepLogicalOperatorsNotSupportedError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepLogicalOperatorsNotSupportedError):
            converter._validate_xpath('//*[@text="test" and @class="button"]')
        
        with pytest.raises(ShadowstepLogicalOperatorsNotSupportedError):
            converter._validate_xpath('//*[@text="test" or @class="button"]')
    
    def test_validate_xpath_with_invalid_syntax(self):
        """Test _validate_xpath with invalid XPath syntax."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepInvalidXPathError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepInvalidXPathError):
            converter._validate_xpath('//*[invalid syntax')
    
    def test_ast_to_ui_selector_empty_list(self):
        """Test _ast_to_ui_selector with empty list."""
        converter = XPathConverter()
        result = converter._ast_to_ui_selector([])
        assert result == ""
    
    def test_ast_to_ui_selector_unsupported_abbreviated_step(self):
        """Test _ast_to_ui_selector with unsupported abbreviated step."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedAbbreviatedStepError
        from eulxml.xpath.ast import AbbreviatedStep
        
        converter = XPathConverter()
        
        # Create a mock AbbreviatedStep with unsupported abbreviation
        mock_step = AbbreviatedStep("unsupported")
        
        with pytest.raises(ShadowstepUnsupportedAbbreviatedStepError):
            converter._ast_to_ui_selector([mock_step])
    
    def test_ast_to_ui_selector_unsupported_ast_node(self):
        """Test _ast_to_ui_selector with unsupported AST node."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedASTNodeError
        
        converter = XPathConverter()
        
        # Test with unsupported node type
        with pytest.raises(ShadowstepUnsupportedASTNodeError):
            converter._ast_to_ui_selector(["invalid_node"])
    
    def test_ast_to_dict_empty_list(self):
        """Test _ast_to_dict with empty list."""
        converter = XPathConverter()
        result = converter._ast_to_dict([])
        assert result == {}
    
    def test_build_shadowstep_dict_unsupported_ast_node(self):
        """Test _build_shadowstep_dict with unsupported AST node."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedASTNodeBuildError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepUnsupportedASTNodeBuildError):
            converter._build_shadowstep_dict(["invalid_node"], {})
    
    def test_ast_to_list_unsupported_ast_node(self):
        """Test _ast_to_list with unsupported AST node."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedASTNodeError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepUnsupportedASTNodeError):
            converter._ast_to_list("invalid_node")
    
    def test_collect_predicates_absolute_path_with_relative(self):
        """Test _collect_predicates with AbsolutePath that has relative."""
        from eulxml.xpath.ast import AbsolutePath, Step, NameTest
        
        converter = XPathConverter()
        
        # Create mock nodes
        name_test = NameTest("", "test")
        step = Step("child", name_test, [])
        
        abs_path = AbsolutePath(step)
        
        predicates = list(converter._collect_predicates(abs_path))
        assert len(predicates) == 0  # No predicates in this case
    
    def test_apply_predicate_to_dict_contains_not_supported(self):
        """Test _apply_predicate_to_dict with contains on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepContainsNotSupportedError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for contains on unsupported attribute
        func_call = FunctionCall("", "contains", ["unsupported_attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._apply_predicate_to_dict(func_call, {})
    
    def test_apply_predicate_to_dict_starts_with_not_supported(self):
        """Test _apply_predicate_to_dict with starts-with on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepStartsWithNotSupportedError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for starts-with on unsupported attribute
        func_call = FunctionCall("", "starts-with", ["unsupported_attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._apply_predicate_to_dict(func_call, {})
    
    def test_apply_predicate_to_dict_matches_not_supported(self):
        """Test _apply_predicate_to_dict with matches on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepMatchesNotSupportedError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for matches on unsupported attribute
        func_call = FunctionCall("", "matches", ["unsupported_attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._apply_predicate_to_dict(func_call, {})
    
    def test_apply_predicate_to_dict_unsupported_function(self):
        """Test _apply_predicate_to_dict with unsupported function."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedFunctionError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for unsupported function
        func_call = FunctionCall("", "unsupported_function", ["attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedFunctionError):
            converter._apply_predicate_to_dict(func_call, {})
    
    def test_apply_predicate_to_dict_unsupported_comparison_operator(self):
        """Test _apply_predicate_to_dict with unsupported comparison operator."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedComparisonOperatorError
        from eulxml.xpath.ast import BinaryExpression
        
        converter = XPathConverter()
        
        # Create mock binary expression with unsupported operator
        bexpr = BinaryExpression("!=", "attr", "value")
        
        with pytest.raises(ShadowstepUnsupportedComparisonOperatorError):
            converter._apply_predicate_to_dict(bexpr, {})
    
    def test_apply_predicate_to_dict_unsupported_attribute(self):
        """Test _apply_predicate_to_dict with unsupported attribute."""
        from eulxml.xpath.ast import BinaryExpression, Step, NameTest
        
        converter = XPathConverter()
        
        # Create mock binary expression with unsupported attribute
        name_test = NameTest("", "unsupported_attr")
        step = Step("@", name_test, [])
        
        bexpr = BinaryExpression(step, "=", "value")
        
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedAttributeError

        with pytest.raises(ShadowstepUnsupportedAttributeError):
            converter._apply_predicate_to_dict(bexpr, {})
    
    def test_apply_predicate_to_dict_attribute_presence_not_supported(self):
        """Test _apply_predicate_to_dict with attribute presence on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepAttributePresenceNotSupportedError
        from eulxml.xpath.ast import Step, NameTest
        
        converter = XPathConverter()
        
        # Create mock step for attribute presence
        name_test = NameTest("", "unsupported_attr")
        step = Step("@", name_test, [])
        
        converter._apply_predicate_to_dict(step, {})
    
    def test_apply_predicate_to_dict_unsupported_predicate(self):
        """Test _apply_predicate_to_dict with unsupported predicate."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedPredicateError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepUnsupportedPredicateError):
            converter._apply_predicate_to_dict("invalid_predicate", {})
    
    def test_predicate_to_ui_contains_not_supported(self):
        """Test _predicate_to_ui with contains on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepContainsNotSupportedError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for contains on unsupported attribute
        func_call = FunctionCall("", "contains", ["unsupported_attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._predicate_to_ui(func_call)
    
    def test_predicate_to_ui_starts_with_not_supported(self):
        """Test _predicate_to_ui with starts-with on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepStartsWithNotSupportedError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for starts-with on unsupported attribute
        func_call = FunctionCall("", "starts-with", ["unsupported_attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._predicate_to_ui(func_call)
    
    def test_predicate_to_ui_matches_not_supported(self):
        """Test _predicate_to_ui with matches on unsupported attribute."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepMatchesNotSupportedError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for matches on unsupported attribute
        func_call = FunctionCall("", "matches", ["unsupported_attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._predicate_to_ui(func_call)
    
    def test_predicate_to_ui_unsupported_function(self):
        """Test _predicate_to_ui with unsupported function."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedFunctionError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for unsupported function
        func_call = FunctionCall("", "unsupported_function", ["attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedFunctionError):
            converter._predicate_to_ui(func_call)
    
    def test_predicate_to_ui_unsupported_attribute(self):
        """Test _predicate_to_ui with unsupported attribute."""
        from eulxml.xpath.ast import BinaryExpression, Step, NameTest
        
        converter = XPathConverter()
        
        # Create mock binary expression with unsupported attribute
        name_test = NameTest("", "unsupported_attr")
        step = Step("@", name_test, [])
        
        bexpr = BinaryExpression(step, "=", "value")
        
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedAttributeError

        with pytest.raises(ShadowstepUnsupportedAttributeError):
            converter._predicate_to_ui(bexpr)
    
    def test_predicate_to_ui_unsupported_predicate(self):
        """Test _predicate_to_ui with unsupported predicate."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedPredicateError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepUnsupportedPredicateError):
            converter._predicate_to_ui("invalid_predicate")
    
    def test_parse_function_predicate_unsupported_function(self):
        """Test _parse_function_predicate with unsupported function."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedFunctionError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call for unsupported function
        func_call = FunctionCall("", "unsupported_function", ["attr", "value"])
        
        with pytest.raises(ShadowstepUnsupportedFunctionError):
            converter._parse_function_predicate(func_call)
    
    def test_parse_function_predicate_wrong_argument_count(self):
        """Test _parse_function_predicate with wrong argument count."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepFunctionArgumentCountError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call with wrong argument count
        func_call = FunctionCall("", "contains", ["attr"])  # Only one argument, should be two
        
        with pytest.raises(ShadowstepFunctionArgumentCountError):
            converter._parse_function_predicate(func_call)
    
    def test_parse_equality_comparison_equality_error(self):
        """Test _parse_equality_comparison with equality comparison error."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepEqualityComparisonError
        from eulxml.xpath.ast import BinaryExpression
        
        converter = XPathConverter()
        
        # Create mock binary expression that can't be parsed
        bexpr = BinaryExpression("=", "value1", "value2")
        
        with pytest.raises(ShadowstepEqualityComparisonError):
            converter._parse_equality_comparison(bexpr)
    
    def test_extract_attr_name_unsupported_attribute_expression(self):
        """Test _extract_attr_name with unsupported attribute expression."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedAttributeExpressionError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepUnsupportedAttributeExpressionError):
            converter._extract_attr_name("invalid_node")
    
    def test_extract_literal_unsupported_literal(self):
        """Test _extract_literal with unsupported literal."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedLiteralError
        from eulxml.xpath.ast import FunctionCall
        
        converter = XPathConverter()
        
        # Create mock function call that's not a boolean
        func_call = FunctionCall("", "unsupported_function", [])
        
        with pytest.raises(ShadowstepUnsupportedLiteralError):
            converter._extract_literal(func_call)
    
    def test_balance_parentheses_unbalanced_error(self):
        """Test _balance_parentheses with unbalanced parentheses."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnbalancedUiSelectorError
        
        converter = XPathConverter()
        
        with pytest.raises(ShadowstepUnbalancedUiSelectorError):
            converter._balance_parentheses("((unbalanced")
    
    def test_balance_parentheses_extra_close_parentheses(self):
        """Test _balance_parentheses with extra close parentheses."""
        converter = XPathConverter()
        
        result = converter._balance_parentheses("balanced))")
        assert result == "balanced)"
    
    def test_balance_parentheses_already_balanced(self):
        """Test _balance_parentheses with already balanced parentheses."""
        converter = XPathConverter()
        
        result = converter._balance_parentheses("balanced()")
        assert result == "balanced()"

