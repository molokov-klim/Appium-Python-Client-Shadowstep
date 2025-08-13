# shadowstep/utils/tests/test_locator_converter.py

import inspect

import pytest
import logging
logger = logging.getLogger(__name__)

from shadowstep.utils.locator_converter import LocatorConverter

converter = LocatorConverter()

@pytest.mark.parametrize("test_data", [
    {"data": {"text": "Экран"},
        "expected_result": ('xpath', ".//*[@text='Экран']"),},

    {"data": {"textContains": "Экра"},
     "expected_result": ('xpath', ".//*[@textContains='Экра']")},

    {"data": {"resource-id": "android:id/title", "class": "android.widget.TextView"},
     "expected_result": ('xpath',
                         ".//*[@resource-id='android:id/title' and "
                         "@class='android.widget.TextView']")},

    {"data": {"enabled": True, "scrollable": False},
     "expected_result": ('xpath', './/*[@enabled=true and @scrollable=false]')},

    {"data": {"package": "com.android.settings", "class": "android.widget.FrameLayout"},
     "expected_result": ('xpath',
                         ".//*[@package='com.android.settings' and "
                         "@class='android.widget.FrameLayout']")},
])
def test_dict_to_xpath(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data.get("data")
    expected_result = test_data.get("expected_result")
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    actual_result = converter._dict_to_xpath(data)
    logger.info(f"{actual_result=}")
    assert actual_result == expected_result


@pytest.mark.parametrize("test_data", [
    {"data": ("xpath", "//*[@text='Экран']"),
     "expected_result": {"text": "Экран"}},

    {"data": ("xpath", "//*[@resource-id='android:id/title' and @text='Экран']"),
     "expected_result": {"resource-id": "android:id/title", "text": "Экран"}},

    {"data": ("xpath", "//*[@text='Экран']/following-sibling::*[@class='android.widget.TextView'][2]"),
     "expected_result": {"text": "Экран"}},

    {"data": ("xpath", "//*[@text='Адаптивная регулировка'][@resource-id='android:id/title']/../..//*[@resource-id='android:id/switch_widget']"),
     "expected_result": {"text": "Адаптивная регулировка", "resource-id": "android:id/title"}},
])
def test_xpath_to_dict(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]
    actual_result = converter._xpath_to_dict(data)
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    logger.info(f"{actual_result=}")
    assert actual_result == expected_result


@pytest.mark.parametrize("test_data", [
    {"data": 'new UiSelector().text("Экран")',
     "expected_result": {"text": "Экран"}},

    {"data": 'new UiSelector().resourceId("android:id/title").instance(0)',
     "expected_result": {"resource-id": "android:id/title", "instance": 0}},

    {"data": 'new UiSelector().text("Экран").fromParent(new UiSelector().text("Яркость"))',
     "expected_result": {"text": "Экран", "parentSelector": {"text": "Яркость"}}}
])
def test_uiselector_to_dict(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]
    actual_result = converter._uiselector_to_dict(data)
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    logger.info(f"{actual_result=}")
    assert actual_result == expected_result


@pytest.mark.parametrize("test_data", [
    {"data": {"text": "Экран"},
     "expected_result": {"text": "Экран"}},

    {"data": ("xpath", "//*[@text='Экран']"),
     "expected_result": {"text": "Экран"}},

    {"data": 'new UiSelector().text("Экран")',
     "expected_result": {"text": "Экран"}}
])
def test_to_dict(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]
    actual_result = converter.to_dict(data)
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    logger.info(f"{actual_result=}")
    assert actual_result == expected_result


@pytest.mark.parametrize("test_data", [
    {"data": {"text": "Экран", "resource-id": "android:id/title"},
     "expected_result":'new UiSelector().text("Экран").resourceId("android:id/title")'},

    {"data": {"text": "Экран", "parentSelector": {"text": "Яркость"}},
     "expected_result": 'new UiSelector().text("Яркость").childSelector(new UiSelector().text("Экран"))'}
])
def test_dict_to_uiselector(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]
    actual_result = converter._dict_to_uiselector(data)
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    logger.info(f"{actual_result=}")
    assert actual_result == expected_result


@pytest.mark.parametrize("test_data", [
    {"data": {"text": "Экран"},
     "expected_result": 'new UiSelector().text("Экран")'},

    {"data": ("xpath", "//*[@text='Экран']"),
     "expected_result": 'new UiSelector().text("Экран")'},

    {"data": 'new UiSelector().text("Экран")',
     "expected_result": 'new UiSelector().text("Экран")'}
])
def test_to_uiselector(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]
    actual_result = converter.to_uiselector(data)
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    logger.info(f"{actual_result=}")
    assert expected_result == actual_result


@pytest.mark.parametrize("test_data", [
    {"data": {"text": "Экран"},
     "expected_result": ('xpath', ".//*[@text='Экран']")},

    {"data": 'new UiSelector().text("Экран")',
     "expected_result": ('xpath', ".//*[@text='Экран']")},

    {"data": ("xpath", "//*[@text='Экран']"),
     "expected_result": ('xpath', "//*[@text='Экран']")},
])
def test_to_xpath(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]
    actual_result = converter.to_xpath(data)
    logger.info(f"{data=}")
    logger.info(f"{expected_result=}")
    logger.info(f"{actual_result=}")
    assert expected_result == actual_result

@pytest.mark.parametrize("test_data", [
    {
        "data": {
            "text": "Экран",
            "childSelector": {
                "class": "android.widget.TextView",
                "text": "Яркость"
            }
        },
        "expected_result": {
            "text": "Экран",
            "childSelector": {
                "class": "android.widget.TextView",
                "text": "Яркость"
            }
        }
    },
    {
        "data": {
            "class": "android.widget.LinearLayout",
            "resource-id": "android:id/content",
            "childSelector": {
                "textContains": "Настройки",
                "childSelector": {
                    "textStartsWith": "Wi-"
                }
            }
        },
        "expected_result": {
            "class": "android.widget.LinearLayout",
            "resource-id": "android:id/content",
            "childSelector": {
                "textContains": "Настройки",
                "childSelector": {
                    "textStartsWith": "Wi-"
                }
            }
        }
    }
])
def test_dict_to_xpath_to_dict_childselector_roundtrip(test_data):
    logger.info(f"{inspect.currentframe().f_code.co_name}")
    data = test_data["data"]
    expected_result = test_data["expected_result"]

    logger.info(f"{data=}")
    xpath = converter.to_xpath(data)[1]
    logger.info(f"{xpath=}")
    actual_result = converter.to_dict(("xpath", xpath))
    logger.info(f"{actual_result=}")
    logger.info(f"{expected_result=}")
    assert actual_result == expected_result

@pytest.mark.parametrize("test_data", [
    {
        "data": {
            "text": "A",
            "fromParent": {
                "text": "B",
                "class": "android.widget.TextView"
            }
        },
        "expected_xpath": "//*[@text='A']/following-sibling::*[@text='B' and @class='android.widget.TextView']"
    }
])
def test_dict_to_xpath_from_parent(test_data):
    data = test_data["data"]
    expected = ("xpath", test_data["expected_xpath"])
    result = converter.to_xpath(data)
    assert result == expected

@pytest.mark.parametrize("test_data", [
    {
        'name': 'sibling_from_parent_xpath',
        'dict': {
            'text': 'Настройки Wi-Fi',
            'fromParent': {
                'text': 'Яркость экрана',
                'class': 'android.widget.TextView',
                'resource-id': 'android:id/title'
            }
        },
        'expected_xpath': "//*[@text='Настройки Wi-Fi']/following-sibling::*[@text='Яркость экрана' and @class='android.widget.TextView' and @resource-id='android:id/title']",
        'expected_uiselector': 'new UiSelector().text("Настройки Wi-Fi").fromParent(new UiSelector().text("Яркость экрана").className("android.widget.TextView").resourceId("android:id/title"))'
    },
    {
        'name': 'deep_sibling_inside_parent',
        'dict': {
            'text': 'Bluetooth',
            'parentSelector': {
                'class': 'androidx.recyclerview.widget.RecyclerView',
                'childSelector': {
                    'text': 'Wi-Fi',
                    'fromParent': {
                        'class': 'android.widget.TextView',
                        'textContains': 'Дополнительно'
                    }
                }
            }
        },
        'expected_xpath': "//*[@class='androidx.recyclerview.widget.RecyclerView']/*[@text='Wi-Fi']/following-sibling::*[contains(@text, 'Дополнительно') and @class='android.widget.TextView']/*[@text='Bluetooth']",
        'expected_uiselector': 'new UiSelector().className("androidx.recyclerview.widget.RecyclerView").childSelector(new UiSelector().text("Wi-Fi").fromParent(new UiSelector().className("android.widget.TextView").textContains("Дополнительно"))).childSelector(new UiSelector().text("Bluetooth"))'
    },
{
    'name': 'complex_nested_all_selectors',
    'dict': {
        'text': 'Настройки',
        'instance': 0,
        'childSelector': {
            'textStartsWith': 'Wi-',
            'fromParent': {
                'text': 'Дополнительно',
                'class': 'android.widget.TextView',
                'childSelector': {
                    'text': 'Bluetooth',
                    'enabled': True
                }
            }
        }
    },
    'expected_xpath': (
        "//*[@text='Настройки' and @instance=0]"
        "/following-sibling::*[starts-with(@text, 'Wi-')]"
        "/following-sibling::*[@text='Дополнительно' and @class='android.widget.TextView']"
        "/*[@text='Bluetooth' and @enabled=true]"
    ),
    'expected_uiselector': (
        'new UiSelector().text("Настройки").instance(0).childSelector('
        'new UiSelector().textStartsWith("Wi-").fromParent('
        'new UiSelector().text("Дополнительно").className("android.widget.TextView").childSelector('
        'new UiSelector().text("Bluetooth").enabled(true)'
        ')))'
    )
},
{
    'name': 'contains_in_deep_branch',
    'dict': {
        'class': 'android.view.ViewGroup',
        'childSelector': {
            'textContains': 'Батарея',
            'fromParent': {
                'text': 'Экран',
                'resource-id': 'android:id/title'
            }
        }
    },
    'expected_xpath': (
        "//*[@class='android.view.ViewGroup']"
        "/*[contains(@text, 'Батарея')]"
        "/following-sibling::*[@text='Экран' and @resource-id='android:id/title']"
    ),
    'expected_uiselector': (
        'new UiSelector().className("android.view.ViewGroup").childSelector('
        'new UiSelector().textContains("Батарея").fromParent('
        'new UiSelector().text("Экран").resourceId("android:id/title")'
        '))'
    )
},
{
    'name': 'multi_level_parent_chain',
    'dict': {
        'text': 'Bluetooth',
        'parentSelector': {
            'text': 'Wi-Fi',
            'parentSelector': {
                'text': 'Подключения',
                'class': 'android.view.ViewGroup'
            }
        }
    },
    'expected_xpath': (
        "//*[@text='Подключения' and @class='android.view.ViewGroup']"
        "/*[@text='Wi-Fi']"
        "/*[@text='Bluetooth']"
    ),
    'expected_uiselector': (
        'new UiSelector().text("Подключения").className("android.view.ViewGroup").childSelector('
        'new UiSelector().text("Wi-Fi").childSelector('
        'new UiSelector().text("Bluetooth"))'
        ')'
    )
},
{
    'name': 'from_parent_with_boolean_and_index',
    'dict': {
        'text': 'Сеть',
        'fromParent': {
            'text': 'Мобильные данные',
            'checked': False,
            'index': 3
        }
    },
    'expected_xpath': (
        "//*[@text='Сеть']"
        "/following-sibling::*[@text='Мобильные данные' and @checked=false and @index=3]"
    ),
    'expected_uiselector': (
        'new UiSelector().text("Сеть").fromParent('
        'new UiSelector().text("Мобильные данные").checked(false).index(3))'
    )
},
{
    'name': 'full_xpath_branch_with_all_types',
    'dict': {
        'class': 'android.widget.FrameLayout',
        'childSelector': {
            'resource-id': 'com.example:id/container',
            'childSelector': {
                'text': 'Активация',
                'scrollable': False,
                'fromParent': {
                    'textStartsWith': 'Безопасность'
                }
            }
        }
    },
    'expected_xpath': (
        "//*[@class='android.widget.FrameLayout']"
        "/*[@resource-id='com.example:id/container']"
        "/*[@text='Активация' and @scrollable=false]"
        "/following-sibling::*[starts-with(@text, 'Безопасность')]"
    ),
    'expected_uiselector': (
        'new UiSelector().className("android.widget.FrameLayout").childSelector('
        'new UiSelector().resourceId("com.example:id/container").childSelector('
        'new UiSelector().text("Активация").scrollable(false).fromParent('
        'new UiSelector().textStartsWith("Безопасность")'
        ')'
        '))'
    )
}

])
def test_complex_locator_cases(test_data):
    logger.info(f"Running complex test: {test_data['name']}")
    data = test_data["dict"]
    expected_xpath = ("xpath", test_data["expected_xpath"])
    expected_uiselector = test_data["expected_uiselector"]

    xpath_result = converter.to_xpath(data)
    logger.info(f"dict → xpath: {xpath_result}")
    assert xpath_result == expected_xpath

    uiselector_result = converter._dict_to_uiselector(data)
    logger.info(f"dict → UiSelector: {uiselector_result}")
    assert uiselector_result == expected_uiselector

