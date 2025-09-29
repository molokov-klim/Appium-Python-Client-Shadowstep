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

    def test_is_element_allowed_blacklist_class(self):
        """Test _is_element_allowed method with blacklisted class."""
        parser = PageObjectParser()
        
        # Element with blacklisted class should not be allowed
        attrib = {"class": "hierarchy"}
        assert parser._is_element_allowed(attrib) is False  # noqa: S101

    def test_is_element_allowed_blacklist_resource_id(self):
        """Test _is_element_allowed method with blacklisted resource ID."""
        parser = PageObjectParser()
        
        # Element with blacklisted resource ID should not be allowed
        attrib = {"class": "android.widget.View", "resource-id": "decor"}
        assert parser._is_element_allowed(attrib) is False  # noqa: S101

    def test_is_element_allowed_whitelist_resource_id(self):
        """Test _is_element_allowed method with whitelisted resource ID."""
        parser = PageObjectParser()
        
        # Element with whitelisted resource ID should be allowed
        attrib = {"class": "android.widget.View", "resource-id": "button"}
        assert parser._is_element_allowed(attrib) is True  # noqa: S101

    def test_build_tree_simple_hierarchy(self):
        """Test _build_tree method with simple hierarchy."""
        parser = PageObjectParser()
        
        # Create a mock XML element
        mock_element = Mock()
        mock_element.tag = "node"
        mock_element.attrib = {"class": "android.widget.Button", "text": "Click me"}
        mock_element.__iter__ = Mock(return_value=iter([]))  # No children
        
        with patch.object(parser, "_is_element_allowed", return_value=True):
            result = parser._build_tree(mock_element)
            
            assert result is not None  # noqa: S101
            assert result.tag == "node"  # noqa: S101
            assert result.attrs == {"class": "android.widget.Button", "text": "Click me"}  # noqa: S101

    def test_build_tree_hierarchy_root(self):
        """Test _build_tree method with hierarchy root."""
        parser = PageObjectParser()
        
        # Create a mock hierarchy element
        mock_hierarchy = Mock()
        mock_hierarchy.tag = "hierarchy"
        
        mock_child = Mock()
        mock_child.tag = "node"
        mock_child.attrib = {"class": "android.widget.Button", "text": "Click me"}
        mock_child.__iter__ = Mock(return_value=iter([]))  # No children
        
        mock_hierarchy.__iter__ = Mock(return_value=iter([mock_child]))
        
        with patch.object(parser, "_is_element_allowed", return_value=True):
            result = parser._build_tree(mock_hierarchy)
            
            assert result is not None  # noqa: S101
            assert result.tag == "node"  # noqa: S101

    def test_build_tree_with_children(self):
        """Test _build_tree method with children elements."""
        parser = PageObjectParser()
        
        # Create a mock parent element
        mock_parent = Mock()
        mock_parent.tag = "parent"
        mock_parent.attrib = {"class": "android.widget.LinearLayout"}
        
        # Create mock child elements
        mock_child1 = Mock()
        mock_child1.tag = "child1"
        mock_child1.attrib = {"class": "android.widget.Button", "text": "Button 1"}
        mock_child1.__iter__ = Mock(return_value=iter([]))
        
        mock_child2 = Mock()
        mock_child2.tag = "child2"
        mock_child2.attrib = {"class": "android.widget.TextView", "text": "Text 1"}
        mock_child2.__iter__ = Mock(return_value=iter([]))
        
        mock_parent.__iter__ = Mock(return_value=iter([mock_child1, mock_child2]))
        
        with patch.object(parser, "_is_element_allowed", return_value=True):
            result = parser._build_tree(mock_parent)
            
            assert result is not None  # noqa: S101
            assert len(result.children) == 2  # noqa: S101
            assert result.children[0].tag == "child1"  # noqa: S101
            assert result.children[1].tag == "child2"  # noqa: S101

    def test_build_tree_filtered_parent_with_children(self):
        """Test _build_tree method with filtered parent but allowed children."""
        parser = PageObjectParser()
        
        # Create a mock parent element that will be filtered out
        mock_parent = Mock()
        mock_parent.tag = "parent"
        mock_parent.attrib = {"class": "hierarchy"}  # This will be filtered out
        
        # Create mock child elements that will be allowed
        mock_child = Mock()
        mock_child.tag = "child"
        mock_child.attrib = {"class": "android.widget.Button", "text": "Button 1"}
        mock_child.__iter__ = Mock(return_value=iter([]))
        
        mock_parent.__iter__ = Mock(return_value=iter([mock_child]))
        
        def mock_is_element_allowed(attrib):
            # Parent is filtered out, child is allowed
            return attrib.get("class") != "hierarchy"
        
        with patch.object(parser, "_is_element_allowed", side_effect=mock_is_element_allowed):
            result = parser._build_tree(mock_parent)
            
            assert result is not None  # noqa: S101
            assert result.tag == "parent"  # Virtual container
            assert len(result.children) == 1  # noqa: S101
            assert result.children[0].tag == "child"  # noqa: S101

    def test_build_tree_filtered_parent_no_children(self):
        """Test _build_tree method with filtered parent and no children."""
        parser = PageObjectParser()
        
        # Create a mock parent element that will be filtered out
        mock_parent = Mock()
        mock_parent.tag = "parent"
        mock_parent.attrib = {"class": "hierarchy"}  # This will be filtered out
        mock_parent.__iter__ = Mock(return_value=iter([]))  # No children
        
        with patch.object(parser, "_is_element_allowed", return_value=False):
            from shadowstep.exceptions.shadowstep_exceptions import ShadowstepRootNodeFilteredOutError
            with pytest.raises(ShadowstepRootNodeFilteredOutError):
                parser._build_tree(mock_parent)

    def test_build_tree_root_node_filtered_out_error(self):
        """Test _build_tree method when root node is filtered out."""
        parser = PageObjectParser()
        
        # Create a mock root element that will be filtered out
        mock_root = Mock()
        mock_root.tag = "node"
        mock_root.attrib = {"class": "hierarchy"}  # This will be filtered out
        mock_root.__iter__ = Mock(return_value=iter([]))  # No children
        
        with patch.object(parser, "_is_element_allowed", return_value=False):
            from shadowstep.exceptions.shadowstep_exceptions import ShadowstepRootNodeFilteredOutError
            with pytest.raises(ShadowstepRootNodeFilteredOutError):
                parser._build_tree(mock_root)

    def test_build_tree_with_scrollable_parents(self):
        """Test _build_tree method with scrollable parents."""
        parser = PageObjectParser()
        
        # Create a mock scrollable parent element
        mock_parent = Mock()
        mock_parent.tag = "parent"
        mock_parent.attrib = {"class": "android.widget.ScrollView", "scrollable": "true"}
        
        # Create mock child element
        mock_child = Mock()
        mock_child.tag = "child"
        mock_child.attrib = {"class": "android.widget.Button", "text": "Button 1"}
        mock_child.__iter__ = Mock(return_value=iter([]))
        
        mock_parent.__iter__ = Mock(return_value=iter([mock_child]))
        
        with patch.object(parser, "_is_element_allowed", return_value=True):
            result = parser._build_tree(mock_parent)
            
            assert result is not None  # noqa: S101
            assert result.scrollable_parents == ["el_0"]  # Parent's ID should be in scrollable_parents
            assert result.children[0].scrollable_parents == ["el_0"]  # Child should inherit scrollable parents

    def test_parse_successful_parsing(self):
        """Test parse method with successful parsing."""
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

    def test_init_with_all_parameters(self):
        """Test PageObjectParser initialization with all parameters."""
        whitelist_classes = ("android.widget.Button", "android.widget.TextView")
        blacklist_classes = ("android.widget.LinearLayout",)
        whitelist_resource_id = ("button", "text")
        blacklist_resource_id = ("decor",)
        container_whitelist = ("main", "dialog")
        
        parser = PageObjectParser(
            white_list_classes=whitelist_classes,
            black_list_classes=blacklist_classes,
            white_list_resource_id=whitelist_resource_id,
            black_list_resource_id=blacklist_resource_id,
            container_whitelist=container_whitelist
        )
        
        assert parser.WHITE_LIST_CLASSES == whitelist_classes  # noqa: S101
        assert parser.BLACK_LIST_CLASSES == blacklist_classes  # noqa: S101
        assert parser.WHITE_LIST_RESOURCE_ID == whitelist_resource_id  # noqa: S101
        assert parser.BLACK_LIST_RESOURCE_ID == blacklist_resource_id  # noqa: S101
        assert parser.CONTAINER_WHITELIST == container_whitelist  # noqa: S101
