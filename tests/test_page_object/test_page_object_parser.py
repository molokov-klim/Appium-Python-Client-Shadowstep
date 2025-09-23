# tests/page_object/test_page_object_parser.py
"""Tests for page_object_parser module."""

from unittest.mock import Mock, patch

import pytest
from lxml import etree

from shadowstep.page_object.page_object_parser import PageObjectParser


class TestPageObjectParser:
    """Test cases for PageObjectParser class."""

    def test_init(self):
        """Test PageObjectParser initialization."""
        parser = PageObjectParser()
        assert parser.ui_element_tree is None  # noqa: S101
        assert parser.logger is not None  # noqa: S101

    def test_init_with_whitelist(self):
        """Test PageObjectParser initialization with whitelist."""
        whitelist = ("android.widget.Button", "android.widget.TextView")
        parser = PageObjectParser(white_list_classes=whitelist)
        assert whitelist == parser.WHITE_LIST_CLASSES  # noqa: S101

    def test_parse_valid_xml(self):
        """Test parse method with valid XML."""
        parser = PageObjectParser()
        
        xml_content = """
        <hierarchy>
            <node class="android.widget.Button" text="Click me" resource-id="com.test:id/button">
                <node class="android.widget.TextView" text="Hello World" />
            </node>
        </hierarchy>
        """
        
        with patch("lxml.etree.fromstring") as mock_fromstring:
            mock_root = Mock()
            mock_fromstring.return_value = mock_root
            
            with patch.object(parser, "_build_tree") as mock_build_tree:
                mock_node = Mock()
                mock_build_tree.return_value = mock_node
                
                result = parser.parse(xml_content)
                
                assert result == mock_node  # noqa: S101
                mock_fromstring.assert_called_once_with(xml_content.encode("utf-8"))
                mock_build_tree.assert_called_once_with(mock_root)

    def test_parse_invalid_xml(self):
        """Test parse method with invalid XML."""
        parser = PageObjectParser()
        
        invalid_xml = "<invalid>xml</invalid>"
        
        with patch("lxml.etree.fromstring", side_effect=etree.XMLSyntaxError("Invalid XML", 0, 0, 0)), \
             pytest.raises(etree.XMLSyntaxError):  # type: ignore
            parser.parse(invalid_xml)

    def test_is_element_allowed_with_whitelist(self):
        """Test _is_element_allowed method with whitelist."""
        parser = PageObjectParser()
        
        # Test allowed class (EditText is in whitelist)
        attrib = {"class": "android.widget.EditText"}
        assert parser._is_element_allowed(attrib) is True  # noqa: S101
        
        # Test disallowed class (Button is not in whitelist and has no text)
        attrib = {"class": "android.widget.Button"}
        assert parser._is_element_allowed(attrib) is False  # noqa: S101

    def test_is_element_allowed_with_text(self):
        """Test _is_element_allowed method with text content."""
        parser = PageObjectParser()
        
        # Element with text should be allowed
        attrib = {"class": "android.widget.TextView", "text": "Hello World"}
        assert parser._is_element_allowed(attrib) is True  # noqa: S101

    def test_is_element_allowed_with_content_desc(self):
        """Test _is_element_allowed method with content description."""
        parser = PageObjectParser()
        
        # Element with content description should be allowed (use a class not in blacklist)
        attrib = {"class": "android.widget.TextView", "content-desc": "Text description"}
        assert parser._is_element_allowed(attrib) is True  # noqa: S101

    def test_is_element_allowed_clickable(self):
        """Test _is_element_allowed method with clickable attribute."""
        parser = PageObjectParser()
        
        # Clickable element should be allowed (has text)
        attrib = {"class": "android.widget.View", "clickable": "true", "text": "Click me"}
        assert parser._is_element_allowed(attrib) is True  # noqa: S101

    def test_is_element_allowed_none_of_above(self):
        """Test _is_element_allowed method with none of the special attributes."""
        parser = PageObjectParser()
        
        # Element without special attributes should not be allowed
        attrib = {"class": "android.widget.View"}
        assert parser._is_element_allowed(attrib) is False  # noqa: S101
