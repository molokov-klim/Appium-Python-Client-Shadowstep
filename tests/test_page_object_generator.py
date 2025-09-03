"""Tests for page_object_generator module."""

import tempfile
from unittest.mock import Mock, mock_open, patch

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_generator import PageObjectGenerator


class TestPageObjectGenerator:
    """Test cases for PageObjectGenerator class."""

    def test_init(self):
        """Test PageObjectGenerator initialization."""
        generator = PageObjectGenerator()
        assert generator.logger is not None  # noqa: S101
        assert generator.translator is None  # noqa: S101
        assert generator.BLACKLIST_NO_TEXT_CLASSES is not None  # noqa: S101

    def test_init_with_translator(self):
        """Test PageObjectGenerator initialization with translator."""
        translator = Mock()
        generator = PageObjectGenerator(translator)
        assert generator.translator == translator  # noqa: S101

    def test_normilize_to_camel_case(self):
        """Test _normilize_to_camel_case method."""
        generator = PageObjectGenerator()
        
        result = generator._normilize_to_camel_case("test class")
        assert result == "PageTestClass"  # noqa: S101
        
        result = generator._normilize_to_camel_case("test_class")
        assert result == "PageTest_class"  # noqa: S101
        
        result = generator._normilize_to_camel_case("test-class")
        assert result == "PageTestclass"  # noqa: S101

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
