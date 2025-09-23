# tests/page_object/test_page_object_element_node.py
"""Tests for page_object_element_node module."""

from unittest.mock import Mock, patch

from shadowstep.page_object.page_object_element_node import Jinja2Renderer, UiElementNode


class TestUiElementNode:
    """Test cases for UiElementNode class."""

    def test_init(self):
        """Test UiElementNode initialization."""
        node = UiElementNode(
            id="test_id",
            tag="test_tag",
            attrs={"class": "test_class"},
            parent=None
        )
        
        assert node.id == "test_id"  # noqa: S101
        assert node.tag == "test_tag"  # noqa: S101
        assert node.attrs == {"class": "test_class"}  # noqa: S101
        assert node.parent is None  # noqa: S101
        assert node.children == []  # noqa: S101
        assert node.depth == 0  # noqa: S101
        assert node.scrollable_parents == []  # noqa: S101

    def test_walk_single_node(self):
        """Test walk method with single node."""
        node = UiElementNode(
            id="test_id",
            tag="test_tag",
            attrs={},
            parent=None
        )
        
        nodes = list(node.walk())
        assert len(nodes) == 1  # noqa: S101
        assert nodes[0] == node  # noqa: S101

    def test_find(self):
        """Test find method."""
        root = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={},
            parent=None
        )
        
        button = UiElementNode(
            id="button",
            tag="button_tag",
            attrs={"class": "android.widget.Button", "text": "Click me"},
            parent=root
        )
        
        root.children = [button]
        
        found = root.find(**{"class": "android.widget.Button"})
        assert len(found) == 1  # noqa: S101
        assert found[0] == button  # noqa: S101

    def test_get_attr(self):
        """Test get_attr method."""
        node = UiElementNode(
            id="test_id",
            tag="test_tag",
            attrs={
                "resource-id": "com.test:id/button",
                "text": "Click me",
                "class": "android.widget.Button"
            },
            parent=None
        )
        
        assert node.get_attr("resource-id") == "com.test:id/button"  # noqa: S101
        assert node.get_attr("text") == "Click me"  # noqa: S101
        assert node.get_attr("class") == "android.widget.Button"  # noqa: S101
        assert node.get_attr("nonexistent") == ""  # noqa: S101


class TestJinja2Renderer:
    """Test cases for Jinja2Renderer class."""

    def test_init(self):
        """Test Jinja2Renderer initialization."""
        renderer = Jinja2Renderer(templates_dir="templates")
        assert renderer.env is not None  # noqa: S101
        assert renderer.env.loader is not None  # noqa: S101

    @patch("shadowstep.page_object.page_object_element_node.get_current_func_name")
    def test_render(self, mock_get_func_name: Mock):
        """Test render method."""
        mock_get_func_name.return_value = "test_function"
        
        renderer = Jinja2Renderer(templates_dir="templates")
        
        # Create a mock model
        from shadowstep.page_object.page_object_element_node import PageObjectModel
        model = PageObjectModel(
            class_name="TestPage",
            raw_title="Test Page",
            title_locator={"text": "Test Page"},
            recycler_locator=None,
            properties=[]
        )
        
        # Mock the template
        with patch.object(renderer.env, "get_template") as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "rendered_content"
            mock_get_template.return_value = mock_template
            
            result = renderer.render(model, "page_object.py.j2")
            
            assert result == "rendered_content"  # noqa: S101
            mock_get_template.assert_called_once_with("page_object.py.j2")
            mock_template.render.assert_called_once()
