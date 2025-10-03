import logging
from typing import Any
from unittest.mock import patch

import pytest

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepInvalidUiSelectorStringError,
    ShadowstepMethodRequiresArgumentError,
    ShadowstepSelectorToXPathError,
    ShadowstepUiSelectorConversionError,
    ShadowstepUiSelectorMethodArgumentError,
    ShadowstepUnsupportedNestedSelectorError,
)
from shadowstep.locator.converter.ui_selector_converter import UiSelectorConverter
from shadowstep.locator.locator_types.ui_selector import UiAttribute

logger = logging.getLogger(__name__)


class TestUiSelectorConverter:

    @pytest.mark.parametrize(
        "method_name, arg, expected_xpath_part",  # noqa: PT006
        [
            # --- text-based ---
            (UiAttribute.TEXT, "Hello", "@text='Hello'"),
            (UiAttribute.TEXT_CONTAINS, "Hello", "contains(@text, 'Hello')"),
            (UiAttribute.TEXT_STARTS_WITH, "Pay", "starts-with(@text, 'Pay')"),
            (UiAttribute.TEXT_MATCHES, ".*Test.*", "matches(@text, '.*Test.*')"),

            # --- description ---
            (UiAttribute.DESCRIPTION, "desc", "@content-desc='desc'"),
            (UiAttribute.DESCRIPTION_CONTAINS, "part", "contains(@content-desc, 'part')"),
            (UiAttribute.DESCRIPTION_STARTS_WITH, "start", "starts-with(@content-desc, 'start')"),
            (UiAttribute.DESCRIPTION_MATCHES, "regex.*", "matches(@content-desc, 'regex.*')"),

            # --- resource id / package ---
            (UiAttribute.RESOURCE_ID, "resId", "@resource-id='resId'"),
            (UiAttribute.RESOURCE_ID_MATCHES, "res.*", "matches(@resource-id, 'res.*')"),
            (UiAttribute.PACKAGE_NAME, "pkg.name", "@package='pkg.name'"),
            (UiAttribute.PACKAGE_NAME_MATCHES, "pkg.name", "matches(@package, 'pkg.name')"),

            # --- class ---
            (UiAttribute.CLASS_NAME, "android.widget.Button", "@class='android.widget.Button'"),
            (UiAttribute.CLASS_NAME_MATCHES, ".*Button", "matches(@class, '.*Button')"),

            # --- bool props ---
            (UiAttribute.CHECKABLE, True, "@checkable='true'"),
            (UiAttribute.CHECKED, False, "@checked='false'"),
            (UiAttribute.CLICKABLE, True, "@clickable='true'"),
            (UiAttribute.ENABLED, False, "@enabled='false'"),
            (UiAttribute.FOCUSABLE, True, "@focusable='true'"),
            (UiAttribute.FOCUSED, False, "@focused='false'"),
            (UiAttribute.LONG_CLICKABLE, True, "@long-clickable='true'"),
            (UiAttribute.SCROLLABLE, False, "@scrollable='false'"),
            (UiAttribute.SELECTED, True, "@selected='true'"),

            # --- numeric ---
            (UiAttribute.INDEX, 2, "position()=3"),
            (UiAttribute.INSTANCE, 0, "//*[1]"),
        ]
    )
    @pytest.mark.unit
    def test_ui_to_xpath_attributes(self, method_name: str, arg: Any, expected_xpath_part: str):
        converter = UiSelectorConverter()
        selector_str = f"new UiSelector().{method_name}({repr(arg)});"
        parsed = converter.parse_selector_string(selector_str)
        xpath = converter._selector_to_xpath(parsed)

        logger.info(f"{method_name=}")
        logger.info(f"{arg=}")
        logger.info(f"{expected_xpath_part=}")
        logger.info(f"{parsed=}")
        logger.info(f"{xpath=}")

        method_in_dict = parsed["methods"][0]
        assert method_in_dict["name"] == method_name  # noqa: S101
        assert method_in_dict["args"][0] == arg  # noqa: S101
        assert expected_xpath_part in xpath  # noqa: S101

    @pytest.mark.parametrize(
        "selector_str, expected_xpath",  # noqa: PT006
        [
            (
                    'new UiSelector().textStartsWith("Pay").className("android.widget.Button")'
                    '.childSelector(new UiSelector().className("android.widget.ImageView"));',
                    "//*[starts-with(@text,'Pay')][@class='android.widget.Button']/*[@class='android.widget.ImageView']"
            ),
            (
                    'new UiSelector().className("android.widget.EditText").focused(true).instance(0);',
                    "//*[@class='android.widget.EditText'][@focused='true'][1]"
            ),
            (
                    'new UiSelector().packageName("ru.figma.app.debug").resourceIdMatches(".*:id/btn.*");',
                    "//*[@package='ru.figma.app.debug'][matches(@resource-id,'.*:id/btn.*')]"
            ),
            (
                    'new UiSelector().descriptionContains("Map").clickable(true);',
                    "//*[contains(@content-desc,'Map')][@clickable='true']"
            ),
            (
                    'new UiSelector().className("androidx.appcompat.app.ActionBar$Tab").index(2);',
                    "//*[@class='androidx.appcompat.app.ActionBar$Tab'][position()=3]"
            ),
            (
                    'new UiSelector().className("android.widget.RadioButton").fromParent(new UiSelector().resourceId("ru.figma.app.debug:id/paymentMethods"));',
                    "//*[@class='android.widget.RadioButton']/..//*[@resource-id='ru.figma.app.debug:id/paymentMethods']"
            ),
            (
                    'new UiSelector().className("android.widget.EditText").textStartsWith("+7").enabled(true);',
                    "//*[@class='android.widget.EditText'][starts-with(@text,'+7')][@enabled='true']"
            ),
            (
                    'new UiSelector().descriptionMatches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");',
                    "//*[matches(@content-desc,'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')]"
            ),
            (
                    'new UiSelector().scrollable(true).childSelector(new UiSelector().text("History"));',
                    "//*[@scrollable='true']/*[@text='History']"
            ),
            (
                    'new UiSelector().className("android.widget.CheckBox").checkable(true).checked(false).instance(2);',
                    "//*[@class='android.widget.CheckBox'][@checkable='true'][@checked='false'][3]"
            ),
            (
                    'new UiSelector().textStartsWith("Pay").textContains("Card").enabled(true);',
                    "//*[starts-with(@text,'Pay')][contains(@text,'Card')][@enabled='true']"
            ),
            (
                    'new UiSelector().classNameMatches("android\\.widget\\..*Button").instance(1);',
                    "//*[matches(@class,'android\\.widget\\..*Button')][2]"
            ),
            (
                    'new UiSelector().description("Confirm").clickable(true)'
                    '.childSelector(new UiSelector().className("android.widget.ImageView"));',
                    "//*[@content-desc='Confirm'][@clickable='true']/*[@class='android.widget.ImageView']"
            ),
            (
                    'new UiSelector().className("android.widget.LinearLayout")'
                    '.childSelector(new UiSelector().className("android.widget.FrameLayout")'
                    '.childSelector(new UiSelector().text("List")))',
                    "//*[@class='android.widget.LinearLayout']/*[@class='android.widget.FrameLayout']/*[@text='List']"
            ),
            (
                    'new UiSelector().className("android.widget.TextView").fromParent('
                    'new UiSelector().className("android.widget.LinearLayout").enabled(true).index(0));',
                    "//*[@class='android.widget.TextView']/..//*[@class='android.widget.LinearLayout'][@enabled='true'][position()=1]"
            ),
            (
                    "new UiSelector().scrollable(false).clickable(false).instance(2);",
                    "//*[@scrollable='false'][@clickable='false'][3]"
            ),
            (
                    'new UiSelector().textContains("card").resourceId("ru.figma.app.debug:id/card_number");',
                    "//*[contains(@text,'card')][@resource-id='ru.figma.app.debug:id/card_number']"
            ),
            (
                    'new UiSelector().text("Pay").longClickable(false);',
                    "//*[@text='Pay'][@long-clickable='false']"
            ),
            (
                    'new UiSelector().className("android.widget.Button").selected(true);',
                    "//*[@class='android.widget.Button'][@selected='true']"
            ),
            (
                    'new UiSelector().className("Button").longClickable(true).packageName("com.example.app");',
                    "//*[@class='Button'][@long-clickable='true'][@package='com.example.app']"
            ),
            (
                    'new UiSelector().childSelector(new UiSelector().className("ListView").childSelector(new UiSelector().text("Item")));',
                    "//*/*[@class='ListView']/*[@text='Item']"
            ),
            (
                    'new UiSelector().fromParent(new UiSelector().className("Container").childSelector(new UiSelector().text("Title")));',
                    "//*/..//*[@class='Container']/*[@text='Title']"
            ),
            (
                    'new UiSelector().text("C:\\Windows\\Path");',
                    "//*[@text='C:\\Windows\\Path']"
            ),
            (
                    'new UiSelector().descriptionMatches(".*\\d+.*");',
                    "//*[matches(@content-desc,'.*\\d+.*')]"
            ),
            (
                    'new UiSelector().resourceId("");',
                    "//*[@resource-id='']"
            ),
            (
                    "new UiSelector().index(0);",
                    "//*[position()=1]"
            ),
            (
                    "new UiSelector().instance(5);",
                    "//*[6]"
            ),
            (
                    "new UiSelector().focusable(true).password(true);",
                    "//*[@focusable='true'][@password='true']"
            ),
            (
                    'new UiSelector().textContains("section").className("android.widget.TextView");',
                    "//*[contains(@text,'section')][@class='android.widget.TextView']"
            ),
            (
                    'new UiSelector().textMatches("\\\\d{3}-\\\\d{2}-\\\\d{4}");',
                    "//*[matches(@text,'\\d{3}-\\d{2}-\\d{4}')]"
            ),
            (
                    'new UiSelector().className("android.widget.LinearLayout")'
                    '.childSelector(new UiSelector().className("android.widget.FrameLayout")'
                    '.childSelector(new UiSelector().className("android.widget.TextView")));',
                    "//*[@class='android.widget.LinearLayout']/*[@class='android.widget.FrameLayout']/*[@class='android.widget.TextView']"
            ),
            (
                    'new UiSelector().className("android.widget.Button").enabled(true).clickable(true);',
                    "//*[@class='android.widget.Button'][@enabled='true'][@clickable='true']"
            ),
            (
                    'new UiSelector().className("android.widget.ImageView");',
                    "//*[@class='android.widget.ImageView']"
            ),
        ]
    )
    @pytest.mark.unit
    def test_ui_to_xpath(self, selector_str: str, expected_xpath: str):
        converter = UiSelectorConverter()
        xpath = converter.selector_to_xpath(selector_str)
        logger.info(f"{selector_str=}")
        logger.info(f"{expected_xpath=}")
        logger.info(f"{xpath=}")
        assert expected_xpath.replace(" ", "") == xpath.replace(" ", ""), \
            f"Expected '{expected_xpath}' got: {xpath}"  # noqa: S101

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "selector_str, expected_xpath",  # noqa: PT006
        [
            (
                    'new UiSelector().unknownProperty("value");',
                    ""
            )

        ]
    )
    @pytest.mark.unit
    def test_ui_to_xpath_negative(self, selector_str: str, expected_xpath: str):
        converter = UiSelectorConverter()
        xpath = converter.selector_to_xpath(selector_str)
        # logger.info(f"{selector_str=}")
        # logger.info(f"{expected_xpath=}")
        # logger.info(f"{parsed=}")
        # logger.info(f"{xpath=}")
        assert expected_xpath.replace(" ", "") == xpath.replace(" ", ""), f"Expected '{expected_xpath}' got: {xpath}"  # noqa: S101  # noqa: S101

    @pytest.mark.parametrize(
        "method, value, expected",  # noqa: PT006
        [
            # --- text-based ---
            (UiAttribute.TEXT, "OK", {"text": "OK"}),
            (UiAttribute.TEXT_CONTAINS, "abc", {"textContains": "abc"}),
            (UiAttribute.TEXT_STARTS_WITH, "Op", {"textStartsWith": "Op"}),
            (UiAttribute.TEXT_MATCHES, r"\d+", {"textMatches": r"\d+"}),

            # --- description ---
            (UiAttribute.DESCRIPTION, "Next", {"content-desc": "Next"}),
            (UiAttribute.DESCRIPTION_CONTAINS, "Btn", {"content-descContains": "Btn"}),
            (UiAttribute.DESCRIPTION_STARTS_WITH, "Pre", {"content-descStartsWith": "Pre"}),
            (UiAttribute.DESCRIPTION_MATCHES, ".*", {"content-descMatches": ".*"}),

            # --- resource id / package ---
            (UiAttribute.RESOURCE_ID, "my.id", {"resource-id": "my.id"}),
            (UiAttribute.RESOURCE_ID_MATCHES, ".*id", {"resource-idMatches": ".*id"}),
            (UiAttribute.PACKAGE_NAME, "com.app", {"package": "com.app"}),
            (UiAttribute.PACKAGE_NAME_MATCHES, ".*app", {"packageMatches": ".*app"}),

            # --- class ---
            (UiAttribute.CLASS_NAME, "android.widget.TextView", {"class": "android.widget.TextView"}),
            (UiAttribute.CLASS_NAME_MATCHES, ".*View", {"classMatches": ".*View"}),

            # --- bool props ---
            (UiAttribute.CHECKABLE, True, {"checkable": True}),
            (UiAttribute.CHECKED, False, {"checked": False}),
            (UiAttribute.CLICKABLE, True, {"clickable": True}),
            (UiAttribute.LONG_CLICKABLE, False, {"long-clickable": False}),
            (UiAttribute.ENABLED, True, {"enabled": True}),
            (UiAttribute.FOCUSABLE, True, {"focusable": True}),
            (UiAttribute.FOCUSED, False, {"focused": False}),
            (UiAttribute.SCROLLABLE, True, {"scrollable": True}),
            (UiAttribute.SELECTED, False, {"selected": False}),
            (UiAttribute.PASSWORD, True, {"password": True}),

            # --- numeric ---
            (UiAttribute.INDEX, 3, {"index": 3}),
            (UiAttribute.INSTANCE, 1, {"instance": 1}),

            # --- hierarchy ---
            (UiAttribute.CHILD_SELECTOR, "child", {"childSelector": "child"}),
            (UiAttribute.FROM_PARENT, "parent", {"fromParent": "parent"}),
        ]
    )
    @pytest.mark.unit
    def test_ui_to_dict_attributes(self, method: UiAttribute, value: Any, expected: dict[str, Any]):
        converter = UiSelectorConverter()
        selector_str = f"new UiSelector().{method.value}({repr(value)});"

        shadowstep_dict = converter.selector_to_dict(selector_str)

        logger.info(f"method={method}")
        logger.info(f"value={value}")
        logger.info(f"expected={expected}")
        logger.info(f"shadowstep_dict={shadowstep_dict}")

        assert shadowstep_dict == expected  # noqa: S101  # noqa: S101

    @pytest.mark.parametrize(
        "selector_str, expected_dict",  # noqa: PT006
        [
            (
                    'new UiSelector().text("OK").clickable(true);',
                    {"text": "OK", "clickable": True}
            ),
            (
                    'new UiSelector().className("android.widget.Button").enabled(false).instance(1);',
                    {"class": "android.widget.Button", "enabled": False, "instance": 1}
            ),
            (
                    'new UiSelector().descriptionContains("Map").scrollable(true);',
                    {"content-descContains": "Map", "scrollable": True}
            ),
            (
                    'new UiSelector().packageName("com.example.app").resourceIdMatches(".*btn.*");',
                    {"package": "com.example.app", "resource-idMatches": ".*btn.*"}
            ),
            (
                    'new UiSelector().className("android.widget.LinearLayout")'
                    '.childSelector(new UiSelector().text("Item"));',
                    {"class": "android.widget.LinearLayout", "childSelector": {"text": "Item"}}
            ),
            (
                    'new UiSelector().fromParent(new UiSelector().className("Container").enabled(true));',
                    {"fromParent": {"class": "Container", "enabled": True}}
            ),
            (
                    'new UiSelector().textMatches("\\d{3}-\\d{2}-\\d{4}");',
                    {"textMatches": "\\d{3}-\\d{2}-\\d{4}"}
            ),
            (
                    "new UiSelector().scrollable(false).clickable(false).instance(2);",
                    {"scrollable": False, "clickable": False, "instance": 2}
            ),
        ]
    )
    @pytest.mark.unit
    def test_ui_to_dict(self, selector_str: str, expected_dict: dict[str, Any]):
        converter = UiSelectorConverter()
        shadowstep_dict = converter.selector_to_dict(selector_str)

        logger.info(f"{selector_str=}")
        logger.info(f"{expected_dict=}")
        logger.info(f"{shadowstep_dict=}")

        assert shadowstep_dict == expected_dict, f"Expected {expected_dict} got: {shadowstep_dict}"  # noqa: S101  # noqa: S101

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "selector_str, expected_dict",  # noqa: PT006
        [
            (
                    'new UiSelector().textStartsWith("Pay").textContains("Card").enabled(true);',
                    {"textStartsWith": "Pay", "textContains": "Card", "enabled": True}
            ),
        ]
    )
    @pytest.mark.unit
    def test_ui_to_dict_negative(self, selector_str: str, expected_dict: dict[str, Any]):
        converter = UiSelectorConverter()
        shadowstep_dict = converter.selector_to_dict(selector_str)

        logger.info(f"{selector_str=}")
        logger.info(f"{expected_dict=}")
        logger.info(f"{shadowstep_dict=}")

        assert shadowstep_dict == expected_dict, f"Expected {expected_dict} got: {shadowstep_dict}"  # noqa: S101  # noqa: S101

    @pytest.mark.unit
    def test_selector_to_xpath_invalid_selector_error(self):
        """Test selector_to_xpath with invalid selector string."""
        converter = UiSelectorConverter()
        
        result = converter.selector_to_xpath("invalid selector")
        assert result == "//*"

    @pytest.mark.unit
    def test_selector_to_xpath_conversion_error(self):
        """Test selector_to_xpath with conversion error."""
        converter = UiSelectorConverter()
        
        # Mock parse_selector_string to raise a different exception
        with patch.object(converter, 'parse_selector_string', side_effect=ValueError("Test error")):
            with pytest.raises(ShadowstepUiSelectorConversionError) as exc_info:
                converter.selector_to_xpath('new UiSelector().text("test");')
            assert "Test error" in str(exc_info.value)

    @pytest.mark.unit
    def test_selector_to_dict_invalid_selector_error(self):
        """Test selector_to_dict with invalid selector string."""
        converter = UiSelectorConverter()
        
        result = converter.selector_to_dict("invalid selector")
        assert result == {}

    @pytest.mark.unit
    def test_selector_to_dict_conversion_error(self):
        """Test selector_to_dict with conversion error."""
        converter = UiSelectorConverter()
        
        # Mock parse_selector_string to raise a different exception
        with patch.object(converter, 'parse_selector_string', side_effect=ValueError("Test error")):
            with pytest.raises(ShadowstepUiSelectorConversionError) as exc_info:
                converter.selector_to_dict('new UiSelector().text("test");')
            assert "Test error" in str(exc_info.value)

    @pytest.mark.unit
    def test_parse_selector_string_with_quotes(self):
        """Test parse_selector_string with quoted string."""
        converter = UiSelectorConverter()
        
        # Test with string wrapped in quotes
        result = converter.parse_selector_string("'new UiSelector().text(\"test\");'")
        expected = {
            "methods": [
                {"name": "text", "args": ["test"]}
            ]
        }
        assert result == expected

    @pytest.mark.unit
    def test_parse_selector_string_parsing_error(self):
        """Test parse_selector_string with parsing error."""
        converter = UiSelectorConverter()
        
        result = converter.parse_selector_string("invalid syntax")
        assert result == {"methods": []}

    @pytest.mark.unit
    def test_selector_to_xpath_no_args_method(self):
        """Test _selector_to_xpath with method that has no arguments."""
        converter = UiSelectorConverter()
        
        # Test with a method that doesn't require arguments
        selector_dict = {
            "methods": [
                {"name": "clickable", "args": []}
            ]
        }
        
        result = converter._selector_to_xpath(selector_dict)
        assert "clickable" in result

    @pytest.mark.unit
    def test_selector_to_xpath_unsupported_method(self):
        """Test _selector_to_xpath with unsupported method."""
        converter = UiSelectorConverter()
        
        # Mock logger to capture warning
        with patch.object(converter.logger, 'warning') as mock_warning:
            selector_dict = {
                "methods": [
                    {"name": "unknownMethod", "args": ["test"]}
                ]
            }
            
            result = converter._selector_to_xpath(selector_dict)
            mock_warning.assert_called_once()
            assert mock_warning.call_args[0][1] == "unknownMethod"
            assert isinstance(mock_warning.call_args[0][2], ValueError)

    @pytest.mark.unit
    def test_selector_to_xpath_from_parent_with_double_slash(self):
        """Test _selector_to_xpath with fromParent that starts with //."""
        converter = UiSelectorConverter()
        
        # Mock _convert_nested_selector to return xpath starting with //
        with patch.object(converter, '_convert_nested_selector', return_value="//*[@class='test']"):
            selector_dict = {
                "methods": [
                    {"name": "fromParent", "args": [{"methods": [{"name": "className", "args": ["test"]}]}]}
                ]
            }
            
            result = converter._selector_to_xpath(selector_dict)
            assert "/..//*[@class='test']" in result

    @pytest.mark.unit
    def test_selector_to_dict_empty_methods(self):
        """Test _selector_to_dict with empty methods list."""
        converter = UiSelectorConverter()
        
        selector_dict = {"methods": []}
        result = converter._selector_to_dict(selector_dict)
        assert result == {}

    @pytest.mark.unit
    def test_selector_to_dict_unsupported_method(self):
        """Test _selector_to_dict with unsupported method."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "unknownMethod", "args": ["test"]}
            ]
        }
        
        with pytest.raises(NotImplementedError) as exc_info:
            converter._selector_to_dict(selector_dict)
        assert "unknownMethod" in str(exc_info.value)

    @pytest.mark.unit
    def test_selector_to_dict_method_requires_argument(self):
        """Test _selector_to_dict with method that requires argument but has none."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "text", "args": []}
            ]
        }
        
        with pytest.raises(ShadowstepMethodRequiresArgumentError) as exc_info:
            converter._selector_to_dict(selector_dict)
        assert "text" in str(exc_info.value)

    @pytest.mark.unit
    def test_convert_nested_selector_with_selector_object(self):
        """Test _convert_nested_selector with Selector AST object."""
        converter = UiSelectorConverter()
        
        # Create a mock Selector object
        class MockSelector:
            def __init__(self):
                self.methods = [MockMethod()]
        
        class MockMethod:
            def __init__(self):
                self.name = "text"
                self.args = ["test"]
        
        mock_selector = MockSelector()
        
        with patch.object(converter, '_selector_to_parsed_dict', return_value={"methods": [{"name": "text", "args": ["test"]}]}):
            with patch.object(converter, '_selector_to_xpath', return_value="*[@text='test']"):
                result = converter._convert_nested_selector(mock_selector)
                assert result == "*[@text='test']"

    @pytest.mark.unit
    def test_convert_nested_selector_unsupported_type(self):
        """Test _convert_nested_selector with unsupported type."""
        converter = UiSelectorConverter()
        
        with pytest.raises(ShadowstepUnsupportedNestedSelectorError) as exc_info:
            converter._convert_nested_selector("unsupported")
        assert "str" in str(exc_info.value)

    @pytest.mark.unit
    def test_parsed_dict_to_selector_with_nested_dict(self):
        """Test _parsed_dict_to_selector with nested dictionary."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {
                    "name": "childSelector",
                    "args": [{"methods": [{"name": "text", "args": ["child"]}]}]
                }
            ]
        }
        
        result = converter._parsed_dict_to_selector(selector_dict, top_level=True)
        assert 'new UiSelector().childSelector(new UiSelector().text("child"));' == result

    @pytest.mark.unit
    def test_parsed_dict_to_selector_with_bool_arg(self):
        """Test _parsed_dict_to_selector with boolean argument."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "clickable", "args": [True]},
                {"name": "enabled", "args": [False]}
            ]
        }
        
        result = converter._parsed_dict_to_selector(selector_dict, top_level=True)
        assert 'new UiSelector().clickable(true).enabled(false);' == result

    @pytest.mark.unit
    def test_parsed_dict_to_selector_with_int_arg(self):
        """Test _parsed_dict_to_selector with integer argument."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "index", "args": [5]}
            ]
        }
        
        result = converter._parsed_dict_to_selector(selector_dict, top_level=True)
        assert 'new UiSelector().index(5);' == result

    @pytest.mark.unit
    def test_parsed_dict_to_selector_with_string_arg_escaping(self):
        """Test _parsed_dict_to_selector with string argument that needs escaping."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "text", "args": ['test"with"quotes']},
                {"name": "description", "args": ['test\\with\\backslashes']}
            ]
        }
        
        result = converter._parsed_dict_to_selector(selector_dict, top_level=True)
        assert 'new UiSelector().text("test\\"with\\"quotes").description("test\\\\with\\\\backslashes");' == result

    @pytest.mark.unit
    def test_parsed_dict_to_selector_multiple_args_error(self):
        """Test _parsed_dict_to_selector with method that has multiple arguments."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "text", "args": ["arg1", "arg2"]}
            ]
        }
        
        with pytest.raises(ShadowstepUiSelectorMethodArgumentError) as exc_info:
            converter._parsed_dict_to_selector(selector_dict, top_level=True)
        assert "2" in str(exc_info.value)

    @pytest.mark.unit
    def test_parsed_dict_to_selector_no_top_level_semicolon(self):
        """Test _parsed_dict_to_selector without top-level semicolon."""
        converter = UiSelectorConverter()
        
        selector_dict = {
            "methods": [
                {"name": "text", "args": ["test"]}
            ]
        }
        
        result = converter._parsed_dict_to_selector(selector_dict, top_level=False)
        assert result == 'new UiSelector().text("test")'
        assert not result.endswith(';')
