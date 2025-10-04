"""Tests for page_object_generator module."""

import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepFailedToNormalizeScreenNameError,
    ShadowstepNameCannotBeEmptyError,
    ShadowstepPageClassNameCannotBeEmptyError,
    ShadowstepTitleNodeNoUsableNameError,
    ShadowstepTitleNotFoundError,
)


class TestPageObjectGenerator:
    """Test cases for PageObjectGenerator class."""

    @pytest.mark.unit
    def test_init(self):
        """Test PageObjectGenerator initialization."""
        generator = PageObjectGenerator()
        assert generator.logger is not None  # noqa: S101
        assert generator.translator is None  # noqa: S101
        assert generator.BLACKLIST_NO_TEXT_CLASSES is not None  # noqa: S101

    @pytest.mark.unit
    def test_init_with_translator(self):
        """Test PageObjectGenerator initialization with translator."""
        translator = Mock()
        generator = PageObjectGenerator(translator)
        assert generator.translator == translator  # noqa: S101

    @pytest.mark.unit
    def test_normilize_to_camel_case(self):
        """Test _normilize_to_camel_case method."""
        generator = PageObjectGenerator()
        
        result = generator._normilize_to_camel_case("test class")
        assert result == "PageTestClass"  # noqa: S101
        
        result = generator._normilize_to_camel_case("test_class")
        assert result == "PageTest_class"  # noqa: S101
        
        result = generator._normilize_to_camel_case("test-class")
        assert result == "PageTestclass"  # noqa: S101

    @pytest.mark.unit
    def test_translate(self):
        """Test _translate method."""
        generator = PageObjectGenerator()
        
        result = generator._translate("test text")
        assert result == "test text"  # noqa: S101
        
        # Test with translator
        translator = Mock()
        translator.translate.return_value = "translated text"
        generator_with_translator = PageObjectGenerator(translator)
        
        result = generator_with_translator._translate("test text")
        assert result == "translated text"  # noqa: S101

    @pytest.mark.unit
    def test_generate_simple_tree(self):
        """Test generate method with simple tree."""
        generator = PageObjectGenerator()
        
        # Create a simple tree with title
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"class": "android.widget.TextView", "text": "Test Page", "displayed": "true"},
            parent=root
        )
        
        button = UiElementNode(
            id="button",
            tag="node",
            attrs={"class": "android.widget.Button", "text": "Click me"},
            parent=root
        )
        
        root.children = [title, button]
        
        with tempfile.TemporaryDirectory() as temp_dir, \
             patch("builtins.open", mock_open()):
            result = generator.generate(root, output_dir=temp_dir)
            
            assert result is not None  # noqa: S101
            assert len(result) == 2  # noqa: S101

    @pytest.mark.unit
    def test_get_title_property_with_text(self):
        """Test _get_title_property with text attribute."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "Test Page", "displayed": "true"},
            parent=root
        )
        
        root.children = [title]
        
        result = generator._get_title_property(root)
        assert result == title  # noqa: S101

    @pytest.mark.unit
    def test_get_title_property_with_content_desc(self):
        """Test _get_title_property with content-desc attribute."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        title = UiElementNode(
            id="title",
            tag="android.widget.FrameLayout",
            attrs={"content-desc": "Test Page", "displayed": "true"},
            parent=root
        )
        
        root.children = [title]
        
        result = generator._get_title_property(root)
        assert result == title  # noqa: S101

    @pytest.mark.unit
    def test_get_title_property_no_title(self):
        """Test _get_title_property when no title found."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        result = generator._get_title_property(root)
        assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_get_name_property_with_text(self):
        """Test _get_name_property with text attribute."""
        generator = PageObjectGenerator()
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "Test Page"},
            parent=None
        )
        
        result = generator._get_name_property(title)
        assert result == "Test Page"  # noqa: S101

    @pytest.mark.unit
    def test_get_name_property_with_content_desc(self):
        """Test _get_name_property with content-desc attribute."""
        generator = PageObjectGenerator()
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"content-desc": "Test Page"},
            parent=None
        )
        
        result = generator._get_name_property(title)
        assert result == "Test Page"  # noqa: S101

    @pytest.mark.unit
    def test_get_name_property_empty_name(self):
        """Test _get_name_property with empty name."""
        generator = PageObjectGenerator()
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={},
            parent=None
        )
        
        with pytest.raises(ShadowstepTitleNodeNoUsableNameError):
            generator._get_name_property(title)

    @pytest.mark.unit
    def test_get_name_property_keyword_name(self):
        """Test _get_name_property with Python keyword."""
        generator = PageObjectGenerator()
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "class"},
            parent=None
        )
        
        result = generator._get_name_property(title)
        assert result == "class_"  # noqa: S101

    @pytest.mark.unit
    def test_get_recycler_property_with_scrollable(self):
        """Test _get_recycler_property with scrollable parent."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        recycler = UiElementNode(
            id="recycler",
            tag="androidx.recyclerview.widget.RecyclerView",
            attrs={},
            parent=root
        )
        
        child = UiElementNode(
            id="child",
            tag="android.widget.TextView",
            attrs={},
            parent=recycler,
            scrollable_parents=["recycler"]
        )
        
        root.children = [recycler]
        recycler.children = [child]
        
        result = generator._get_recycler_property(root)
        assert result == recycler  # noqa: S101

    @pytest.mark.unit
    def test_get_recycler_property_no_scrollable(self):
        """Test _get_recycler_property with no scrollable parent."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        result = generator._get_recycler_property(root)
        assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_get_anchor_pairs_with_switches(self):
        """Test _get_anchor_pairs with switch elements."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        switch = UiElementNode(
            id="switch",
            tag="android.widget.Switch",
            attrs={"class": "android.widget.Switch"},
            parent=root
        )
        
        anchor = UiElementNode(
            id="anchor",
            tag="android.widget.TextView",
            attrs={"text": "Switch Label"},
            parent=root
        )
        
        root.children = [switch, anchor]
        
        with patch.object(generator, '_find_anchor_for_target', return_value=anchor):
            result = generator._get_anchor_pairs(root, {"class": "android.widget.Switch"})
            assert len(result) == 1  # noqa: S101
            assert result[0] == (anchor, switch)  # noqa: S101

    @pytest.mark.unit
    def test_get_anchor_pairs_no_targets(self):
        """Test _get_anchor_pairs with no matching targets."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        result = generator._get_anchor_pairs(root, {"class": "android.widget.Switch"})
        assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_find_anchor_for_target(self):
        """Test _find_anchor_for_target method."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        target = UiElementNode(
            id="target",
            tag="android.widget.Switch",
            attrs={},
            parent=root
        )
        
        anchor = UiElementNode(
            id="anchor",
            tag="android.widget.TextView",
            attrs={"text": "Label"},
            parent=root
        )
        
        root.children = [target, anchor]
        
        with patch.object(generator, '_get_ancestor', return_value=root), \
             patch.object(generator, '_get_siblings_or_cousins', return_value=[anchor]), \
             patch.object(generator, '_is_anchor_like', return_value=True):
            
            result = generator._find_anchor_for_target(target, 1)
            assert result == anchor  # noqa: S101

    @pytest.mark.unit
    def test_get_ancestor(self):
        """Test _get_ancestor method."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        child = UiElementNode(
            id="child",
            tag="node",
            attrs={},
            parent=root
        )
        
        grandchild = UiElementNode(
            id="grandchild",
            tag="node",
            attrs={},
            parent=child
        )
        
        root.children = [child]
        child.children = [grandchild]
        
        result = generator._get_ancestor(grandchild, 1)
        assert result == root  # noqa: S101

    @pytest.mark.unit
    def test_get_ancestor_no_parent(self):
        """Test _get_ancestor when no parent exists."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        result = generator._get_ancestor(root, 1)
        assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_get_siblings_or_cousins(self):
        """Test _get_siblings_or_cousins method."""
        generator = PageObjectGenerator()
        
        ancestor = UiElementNode(
            id="ancestor",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        child1 = UiElementNode(
            id="child1",
            tag="node",
            attrs={},
            parent=ancestor,
            depth=1
        )
        
        child2 = UiElementNode(
            id="child2",
            tag="node",
            attrs={},
            parent=ancestor,
            depth=1
        )
        
        target = UiElementNode(
            id="target",
            tag="node",
            attrs={},
            parent=ancestor,
            depth=1
        )
        
        ancestor.children = [child1, child2, target]
        
        result = generator._get_siblings_or_cousins(ancestor, target)
        assert len(result) == 2  # noqa: S101
        assert child1 in result  # noqa: S101
        assert child2 in result  # noqa: S101
        assert target not in result  # noqa: S101

    @pytest.mark.unit
    def test_is_same_depth(self):
        """Test _is_same_depth method."""
        generator = PageObjectGenerator()
        
        node1 = UiElementNode(
            id="node1",
            tag="node",
            attrs={},
            parent=None,
            depth=1
        )
        
        node2 = UiElementNode(
            id="node2",
            tag="node",
            attrs={},
            parent=None,
            depth=1
        )
        
        node3 = UiElementNode(
            id="node3",
            tag="node",
            attrs={},
            parent=None,
            depth=2
        )
        
        assert generator._is_same_depth(node1, node2) is True  # noqa: S101
        assert generator._is_same_depth(node1, node3) is False  # noqa: S101

    @pytest.mark.unit
    def test_is_anchor_like_with_text(self):
        """Test _is_anchor_like with text attribute."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.TextView",
            attrs={"text": "Label"},
            parent=None
        )
        
        result = generator._is_anchor_like(node)
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_is_anchor_like_with_content_desc(self):
        """Test _is_anchor_like with content-desc attribute."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.TextView",
            attrs={"content-desc": "Label"},
            parent=None
        )
        
        result = generator._is_anchor_like(node)
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_is_anchor_like_no_anchor_attrs(self):
        """Test _is_anchor_like with no anchor attributes."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.TextView",
            attrs={},
            parent=None
        )
        
        result = generator._is_anchor_like(node)
        assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_get_summary_pairs(self):
        """Test _get_summary_pairs method."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        summary = UiElementNode(
            id="summary",
            tag="android.widget.TextView",
            attrs={"text": "Summary text"},
            parent=root
        )
        
        anchor = UiElementNode(
            id="anchor",
            tag="android.widget.TextView",
            attrs={"text": "Anchor text"},
            parent=root
        )
        
        root.children = [summary, anchor]
        
        with patch.object(generator, '_find_anchor_for_target', return_value=anchor):
            result = generator._get_summary_pairs(root)
            assert len(result) == 1  # noqa: S101
            assert result[0] == (anchor, summary)  # noqa: S101

    @pytest.mark.unit
    def test_get_regular_properties(self):
        """Test _get_regular_properties method."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        element1 = UiElementNode(
            id="element1",
            tag="android.widget.Button",
            attrs={"text": "Button 1"},
            parent=root
        )
        
        element2 = UiElementNode(
            id="element2",
            tag="android.widget.Button",
            attrs={"text": "Button 2"},
            parent=root
        )
        
        root.children = [element1, element2]
        
        used_elements = [(element1, element1)]  # element1 is already used
        
        result = generator._get_regular_properties(root, used_elements)
        # The method returns all elements that are not in used_elements
        # It includes root and element2 (element1 is filtered out)
        assert len(result) == 2  # noqa: S101
        assert root in result  # noqa: S101
        assert element2 in result  # noqa: S101

    @pytest.mark.unit
    def test_remove_text_from_non_text_elements(self):
        """Test _remove_text_from_non_text_elements method."""
        generator = PageObjectGenerator()
        
        element = UiElementNode(
            id="element",
            tag="android.widget.SeekBar",
            attrs={"text": "SeekBar text"},
            parent=None
        )
        
        generator._remove_text_from_non_text_elements([element])
        assert "text" not in element.attrs  # noqa: S101

    @pytest.mark.unit
    def test_prepare_template_data(self):
        """Test _prepare_template_data method."""
        generator = PageObjectGenerator()
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "Test Page"},
            parent=None
        )
        
        recycler = UiElementNode(
            id="recycler",
            tag="androidx.recyclerview.widget.RecyclerView",
            attrs={},
            parent=None
        )
        
        properties = [{"name": "button1", "locator": {"text": "Button 1"}}]
        
        result = generator._prepare_template_data(title, recycler, properties, True)
        
        assert result["class_name"] == "PageTestPage"  # noqa: S101
        assert result["raw_title"] == "Test Page"  # noqa: S101
        assert result["need_recycler"] is True  # noqa: S101
        assert result["properties"] == properties  # noqa: S101

    @pytest.mark.unit
    def test_node_to_locator_with_only_id(self):
        """Test _node_to_locator with only_id=True."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.Button",
            attrs={"resource-id": "com.test:id/button", "text": "Button"},
            parent=None
        )
        
        result = generator._node_to_locator(node, only_id=True)
        assert result == {"resource-id": "com.test:id/button"}  # noqa: S101

    @pytest.mark.unit
    def test_node_to_locator_full(self):
        """Test _node_to_locator with full locator."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.Button",
            attrs={"resource-id": "com.test:id/button", "text": "Button"},
            parent=None
        )
        
        result = generator._node_to_locator(node)
        assert result["resource-id"] == "com.test:id/button"  # noqa: S101
        assert result["text"] == "Button"  # noqa: S101
        assert result["class"] == "android.widget.Button"  # noqa: S101

    @pytest.mark.unit
    def test_is_scrollable_by(self):
        """Test _is_scrollable_by method."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.TextView",
            attrs={},
            parent=None,
            scrollable_parents=["recycler1", "recycler2"]
        )
        
        result = generator._is_scrollable_by(node, "recycler1")
        assert result is True  # noqa: S101
        
        result = generator._is_scrollable_by(node, "recycler3")
        assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_calculate_depth(self):
        """Test _calculate_depth method."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        child = UiElementNode(
            id="child",
            tag="node",
            attrs={},
            parent=root
        )
        
        grandchild = UiElementNode(
            id="grandchild",
            tag="node",
            attrs={},
            parent=child
        )
        
        root.children = [child]
        child.children = [grandchild]
        
        result = generator._calculate_depth(child, grandchild)
        assert result == 1  # noqa: S101

    @pytest.mark.unit
    def test_generate_property_name(self):
        """Test _generate_property_name method."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.Button",
            attrs={"text": "Test Button"},
            parent=None
        )
        
        used_names = set()
        result = generator._generate_property_name(node, used_names)
        assert result == "test_button"  # noqa: S101

    @pytest.mark.unit
    def test_generate_property_name_with_suffix(self):
        """Test _generate_property_name with suffix."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.Switch",
            attrs={"text": "Test Switch"},
            parent=None
        )
        
        used_names = set()
        result = generator._generate_property_name(node, used_names, "_switch")
        assert result == "test_switch_switch"  # noqa: S101

    @pytest.mark.unit
    def test_generate_property_name_with_anchor_base(self):
        """Test _generate_property_name with anchor base."""
        generator = PageObjectGenerator()
        
        node = UiElementNode(
            id="node",
            tag="android.widget.Switch",
            attrs={"text": "Test Switch"},
            parent=None
        )
        
        used_names = set()
        result = generator._generate_property_name(node, used_names, "_switch", "anchor_name")
        assert result == "anchor_name_switch"  # noqa: S101

    @pytest.mark.unit
    def test_slug_words(self):
        """Test _slug_words method."""
        generator = PageObjectGenerator()
        
        result = generator._slug_words("Test String With Spaces")
        assert result == ["test", "string", "with", "spaces"]  # noqa: S101

    @pytest.mark.unit
    def test_slug_words_with_special_chars(self):
        """Test _slug_words with special characters."""
        generator = PageObjectGenerator()
        
        result = generator._slug_words("Test-String_With.Special@Chars!")
        assert result == ["test", "string_with", "special", "chars"]  # noqa: S101

    @pytest.mark.unit
    def test_strip_package_prefix(self):
        """Test _strip_package_prefix method."""
        generator = PageObjectGenerator()
        
        result = generator._strip_package_prefix("com.test:id/button")
        assert result == "button"  # noqa: S101

    @pytest.mark.unit
    def test_strip_package_prefix_no_slash(self):
        """Test _strip_package_prefix with no slash."""
        generator = PageObjectGenerator()
        
        result = generator._strip_package_prefix("button")
        assert result == "button"  # noqa: S101

    @pytest.mark.unit
    def test_sanitize_name(self):
        """Test _sanitize_name method."""
        generator = PageObjectGenerator()
        
        result = generator._sanitize_name("test-name_with.special@chars")
        assert result == "test_name_with_special_chars"  # noqa: S101

    @pytest.mark.unit
    def test_sanitize_name_starts_with_digit(self):
        """Test _sanitize_name with name starting with digit."""
        generator = PageObjectGenerator()
        
        result = generator._sanitize_name("123test")
        assert result == "num_123test"  # noqa: S101

    @pytest.mark.unit
    def test_class_name_to_file_name(self):
        """Test _class_name_to_file_name method."""
        generator = PageObjectGenerator()
        
        result = generator._class_name_to_file_name("PageTestClass")
        assert result == "page_test_class.py"  # noqa: S101

    @pytest.mark.unit
    def test_is_need_recycler_true(self):
        """Test _is_need_recycler when recycler is needed."""
        generator = PageObjectGenerator()
        
        recycler = UiElementNode(
            id="recycler",
            tag="androidx.recyclerview.widget.RecyclerView",
            attrs={},
            parent=None
        )
        
        element = UiElementNode(
            id="element",
            tag="android.widget.TextView",
            attrs={},
            parent=None,
            scrollable_parents=["recycler"]
        )
        
        result = generator._is_need_recycler(recycler, [element])
        assert result is True  # noqa: S101

    @pytest.mark.unit
    def test_is_need_recycler_false(self):
        """Test _is_need_recycler when recycler is not needed."""
        generator = PageObjectGenerator()
        
        recycler = UiElementNode(
            id="recycler",
            tag="androidx.recyclerview.widget.RecyclerView",
            attrs={},
            parent=None
        )
        
        element = UiElementNode(
            id="element",
            tag="android.widget.TextView",
            attrs={},
            parent=None,
            scrollable_parents=[]
        )
        
        result = generator._is_need_recycler(recycler, [element])
        assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_is_need_recycler_no_recycler(self):
        """Test _is_need_recycler when no recycler provided."""
        generator = PageObjectGenerator()
        
        element = UiElementNode(
            id="element",
            tag="android.widget.TextView",
            attrs={},
            parent=None
        )
        
        result = generator._is_need_recycler(None, [element])
        assert result is False  # noqa: S101

    @pytest.mark.unit
    def test_filter_properties(self):
        """Test _filter_properties method."""
        generator = PageObjectGenerator()
        
        properties = [
            {"name": "button1", "element_id": "button1", "locator": {"text": "Button 1"}},
            {"name": "button2", "element_id": "button2", "locator": {"class": "android.widget.Button"}},
        ]
        
        result = generator._filter_properties(properties, "button1", None)
        # button2 gets filtered out because it only has class in locator
        assert len(result) == 1  # noqa: S101
        assert result[0]["name"] == "button1"  # noqa: S101

    @pytest.mark.unit
    def test_filter_class_only_properties(self):
        """Test _filter_class_only_properties method."""
        generator = PageObjectGenerator()
        
        properties = [
            {"name": "button1", "locator": {"text": "Button 1", "class": "android.widget.Button"}},
            {"name": "button2", "locator": {"class": "android.widget.Button"}},
        ]
        
        result = generator._filter_class_only_properties(properties)
        assert len(result) == 1  # noqa: S101
        assert result[0]["name"] == "button1"  # noqa: S101

    @pytest.mark.unit
    def test_filter_structural_containers(self):
        """Test _filter_structural_containers method."""
        generator = PageObjectGenerator()
        
        properties = [
            {"name": "button1", "locator": {"text": "Button 1", "class": "android.widget.Button"}},
            {"name": "layout1", "locator": {"class": "android.widget.LinearLayout"}},
        ]
        
        result = generator._filter_structural_containers(properties)
        assert len(result) == 1  # noqa: S101
        assert result[0]["name"] == "button1"  # noqa: S101

    @pytest.mark.unit
    def test_normilize_to_camel_case_empty_string(self):
        """Test _normilize_to_camel_case with empty string."""
        generator = PageObjectGenerator()
        
        with pytest.raises(ShadowstepFailedToNormalizeScreenNameError):
            generator._normilize_to_camel_case("")

    @pytest.mark.unit
    def test_normilize_to_camel_case_special_chars_only(self):
        """Test _normilize_to_camel_case with only special characters."""
        generator = PageObjectGenerator()
        
        with pytest.raises(ShadowstepFailedToNormalizeScreenNameError):
            generator._normilize_to_camel_case("!@#$%^&*()")

    @pytest.mark.unit
    def test_normilize_to_camel_case_already_starts_with_page(self):
        """Test _normilize_to_camel_case when already starts with Page."""
        generator = PageObjectGenerator()
        
        result = generator._normilize_to_camel_case("PageTest")
        assert result == "Pagetest"  # noqa: S101

    @pytest.mark.unit
    def test_generate_with_title_not_found(self):
        """Test generate method when title is not found."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        with pytest.raises(ShadowstepTitleNotFoundError):
            generator.generate(root, output_dir="/tmp")

    @pytest.mark.unit
    def test_generate_with_empty_name(self):
        """Test generate method when name is empty."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "Test Page", "displayed": "true"},
            parent=root
        )
        
        root.children = [title]
        
        # Mock _get_name_property to return empty string
        with patch.object(generator, '_get_name_property', return_value=""):
            with pytest.raises(ShadowstepNameCannotBeEmptyError):
                generator.generate(root, output_dir="/tmp")

    @pytest.mark.unit
    def test_generate_with_empty_class_name(self):
        """Test generate method when class name is empty."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "!@#$%^&*()", "displayed": "true"},
            parent=root
        )
        
        root.children = [title]
        
        with pytest.raises(ShadowstepFailedToNormalizeScreenNameError):
            generator.generate(root, output_dir="/tmp")

    @pytest.mark.unit
    def test_generate_with_filename_prefix(self):
        """Test generate method with filename prefix."""
        generator = PageObjectGenerator()
        
        root = UiElementNode(
            id="root",
            tag="hierarchy",
            attrs={},
            parent=None
        )
        
        title = UiElementNode(
            id="title",
            tag="android.widget.TextView",
            attrs={"text": "Test Page", "displayed": "true"},
            parent=root
        )
        
        root.children = [title]
        
        with tempfile.TemporaryDirectory() as temp_dir, \
             patch("builtins.open", mock_open()):
            result = generator.generate(root, output_dir=temp_dir, filename_prefix="prefix_")
            
            assert result is not None  # noqa: S101
            assert len(result) == 2  # noqa: S101
            assert result[0].name.endswith("prefix_page_test_page.py")  # noqa: S101

    @pytest.mark.unit
    def test_pretty_dict_function(self):
        """Test _pretty_dict function."""
        from shadowstep.page_object.page_object_generator import _pretty_dict
        
        test_dict = {"key1": "value1", "key2": "value2"}
        result = _pretty_dict(test_dict, base_indent=4)
        
        expected = "{\n    'key1': 'value1',\n    'key2': 'value2'\n}"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_pretty_dict_empty(self):
        """Test _pretty_dict with empty dictionary."""
        from shadowstep.page_object.page_object_generator import _pretty_dict
        
        result = _pretty_dict({}, base_indent=4)
        expected = "{\n}"
        assert result == expected  # noqa: S101

