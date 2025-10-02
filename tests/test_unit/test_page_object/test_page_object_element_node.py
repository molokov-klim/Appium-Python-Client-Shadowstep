"""Tests for page_object_element_node module."""

from unittest.mock import Mock, patch
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_element_node import (
    Jinja2Renderer, 
    UiElementNode, 
    PropertyModel, 
    PageObjectModel, 
    TemplateRenderer, 
    PageObjectRendererFactory, 
    ModelBuilder, 
    PageObjectRenderer
)


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
        renderer = Jinja2Renderer(templates_dir="page_object/templates")
        assert renderer.env is not None  # noqa: S101
        assert renderer.env.loader is not None  # noqa: S101

    @patch("shadowstep.page_object.page_object_element_node.get_current_func_name")
    def test_render(self, mock_get_func_name: Mock):
        """Test render method."""
        mock_get_func_name.return_value = "test_function"
        
        renderer = Jinja2Renderer(templates_dir="page_object/templates")
        
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

    def test_walk_tree(self):
        """Test walk method with tree of nodes."""
        root = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={},
            parent=None
        )
        
        child1 = UiElementNode(
            id="child1",
            tag="child1_tag",
            attrs={},
            parent=root
        )
        
        child2 = UiElementNode(
            id="child2",
            tag="child2_tag",
            attrs={},
            parent=root
        )
        
        grandchild = UiElementNode(
            id="grandchild",
            tag="grandchild_tag",
            attrs={},
            parent=child1
        )
        
        root.children = [child1, child2]
        child1.children = [grandchild]
        
        nodes = list(root.walk())
        assert len(nodes) == 4  # noqa: S101
        assert nodes[0] == root  # noqa: S101
        assert nodes[1] == child1  # noqa: S101
        assert nodes[2] == grandchild  # noqa: S101
        assert nodes[3] == child2  # noqa: S101

    def test_get_attr_with_none_attrs(self):
        """Test get_attr method when attrs is None."""
        node = UiElementNode(
            id="test_id",
            tag="test_tag",
            attrs=None,
            parent=None
        )
        
        assert node.get_attr("any_key") == ""  # noqa: S101

    def test_repr(self):
        """Test __repr__ method."""
        root = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={"text": "Root", "resource-id": "root_id"},
            parent=None,
            depth=0,
            scrollable_parents=["parent1"]
        )
        
        child = UiElementNode(
            id="child",
            tag="child_tag",
            attrs={"text": "Child", "resource-id": "child_id"},
            parent=root,
            depth=1,
            scrollable_parents=["parent1", "parent2"]
        )
        
        root.children = [child]
        
        repr_str = repr(root)
        assert "id=root" in repr_str  # noqa: S101
        assert "tag='root_tag'" in repr_str  # noqa: S101
        assert "text='Root'" in repr_str  # noqa: S101
        assert "resource-id='root_id'" in repr_str  # noqa: S101
        assert "parent_id='None'" in repr_str  # noqa: S101
        assert "depth='0'" in repr_str  # noqa: S101
        assert "scrollable_parents='['parent1']'" in repr_str  # noqa: S101
        assert "id=child" in repr_str  # noqa: S101
        assert "parent_id='root'" in repr_str  # noqa: S101

    def test_find_no_matches(self):
        """Test find method with no matches."""
        root = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={"class": "android.widget.LinearLayout"},
            parent=None
        )
        
        found = root.find(**{"class": "android.widget.Button"})
        assert len(found) == 0  # noqa: S101

    def test_find_multiple_matches(self):
        """Test find method with multiple matches."""
        root = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={"class": "android.widget.LinearLayout"},
            parent=None
        )
        
        button1 = UiElementNode(
            id="button1",
            tag="button_tag",
            attrs={"class": "android.widget.Button", "text": "Button 1"},
            parent=root
        )
        
        button2 = UiElementNode(
            id="button2",
            tag="button_tag",
            attrs={"class": "android.widget.Button", "text": "Button 2"},
            parent=root
        )
        
        root.children = [button1, button2]
        
        found = root.find(**{"class": "android.widget.Button"})
        assert len(found) == 2  # noqa: S101
        assert button1 in found  # noqa: S101
        assert button2 in found  # noqa: S101


class TestPropertyModel:
    """Test cases for PropertyModel class."""

    def test_init(self):
        """Test PropertyModel initialization."""
        prop = PropertyModel(
            name="test_property",
            locator={"text": "Test Button"},
            anchor_name="test_anchor",
            base_name="test_base",
            summary_id={"id": "test_id"},
            depth=2,
            sibling=True,
            via_recycler=True
        )
        
        assert prop.name == "test_property"  # noqa: S101
        assert prop.locator == {"text": "Test Button"}  # noqa: S101
        assert prop.anchor_name == "test_anchor"  # noqa: S101
        assert prop.base_name == "test_base"  # noqa: S101
        assert prop.summary_id == {"id": "test_id"}  # noqa: S101
        assert prop.depth == 2  # noqa: S101
        assert prop.sibling is True  # noqa: S101
        assert prop.via_recycler is True  # noqa: S101

    def test_init_with_defaults(self):
        """Test PropertyModel initialization with default values."""
        prop = PropertyModel(
            name="test_property",
            locator={"text": "Test Button"},
            anchor_name=None,
            base_name=None,
            summary_id=None
        )
        
        assert prop.name == "test_property"  # noqa: S101
        assert prop.locator == {"text": "Test Button"}  # noqa: S101
        assert prop.anchor_name is None  # noqa: S101
        assert prop.base_name is None  # noqa: S101
        assert prop.summary_id is None  # noqa: S101
        assert prop.depth == 0  # noqa: S101
        assert prop.sibling is False  # noqa: S101
        assert prop.via_recycler is False  # noqa: S101


class TestPageObjectModel:
    """Test cases for PageObjectModel class."""

    def test_init(self):
        """Test PageObjectModel initialization."""
        properties = [
            PropertyModel(name="button1", locator={"text": "Button 1"}, anchor_name=None, base_name=None, summary_id=None),
            PropertyModel(name="button2", locator={"text": "Button 2"}, anchor_name=None, base_name=None, summary_id=None)
        ]
        
        model = PageObjectModel(
            class_name="TestPage",
            raw_title="Test Page",
            title_locator={"text": "Test Page"},
            recycler_locator={"class": "android.widget.RecyclerView"},
            properties=properties,
            need_recycler=True
        )
        
        assert model.class_name == "TestPage"  # noqa: S101
        assert model.raw_title == "Test Page"  # noqa: S101
        assert model.title_locator == {"text": "Test Page"}  # noqa: S101
        assert model.recycler_locator == {"class": "android.widget.RecyclerView"}  # noqa: S101
        assert model.properties == properties  # noqa: S101
        assert model.need_recycler is True  # noqa: S101

    def test_init_with_defaults(self):
        """Test PageObjectModel initialization with default values."""
        model = PageObjectModel(
            class_name="TestPage",
            raw_title="Test Page",
            title_locator={"text": "Test Page"},
            recycler_locator=None
        )
        
        assert model.class_name == "TestPage"  # noqa: S101
        assert model.raw_title == "Test Page"  # noqa: S101
        assert model.title_locator == {"text": "Test Page"}  # noqa: S101
        assert model.recycler_locator is None  # noqa: S101
        assert model.properties == []  # noqa: S101
        assert model.need_recycler is False  # noqa: S101


class TestTemplateRenderer:
    """Test cases for TemplateRenderer abstract class."""

    def test_cannot_instantiate(self):
        """Test that TemplateRenderer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TemplateRenderer()


class TestJinja2RendererExtended:
    """Extended test cases for Jinja2Renderer class."""

    def test_save_method_exists(self):
        """Test that save method exists and is callable."""
        renderer = Jinja2Renderer(templates_dir="page_object/templates")
        assert hasattr(renderer, 'save')  # noqa: S101
        assert callable(renderer.save)  # noqa: S101

    def test_pretty_dict(self):
        """Test _pretty_dict static method."""
        test_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
        result = Jinja2Renderer._pretty_dict(test_dict, base_indent=4)
        
        expected = "{\n    'key1': 'value1',\n    'key2': 'value2',\n    'key3': 'value3'\n}"
        assert result == expected  # noqa: S101

    def test_pretty_dict_empty(self):
        """Test _pretty_dict with empty dictionary."""
        result = Jinja2Renderer._pretty_dict({}, base_indent=4)
        expected = "{\n}"
        assert result == expected  # noqa: S101

    def test_pretty_dict_single_item(self):
        """Test _pretty_dict with single item."""
        result = Jinja2Renderer._pretty_dict({"key": "value"}, base_indent=4)
        expected = "{\n    'key': 'value'\n}"
        assert result == expected  # noqa: S101


class TestPageObjectRendererFactory:
    """Test cases for PageObjectRendererFactory class."""

    def test_create_renderer_jinja2(self):
        """Test creating Jinja2 renderer."""
        renderer = PageObjectRendererFactory.create_renderer("jinja2")
        assert isinstance(renderer, Jinja2Renderer)  # noqa: S101

    def test_create_renderer_jinja2_uppercase(self):
        """Test creating Jinja2 renderer with uppercase."""
        renderer = PageObjectRendererFactory.create_renderer("JINJA2")
        assert isinstance(renderer, Jinja2Renderer)  # noqa: S101

    def test_create_renderer_unsupported(self):
        """Test creating unsupported renderer type."""
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepUnsupportedRendererTypeError
        
        with pytest.raises(ShadowstepUnsupportedRendererTypeError):
            PageObjectRendererFactory.create_renderer("unsupported")


class TestModelBuilder:
    """Test cases for ModelBuilder class."""

    def test_build_from_ui_tree(self):
        """Test build_from_ui_tree method."""
        ui_tree = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={"text": "Test Page", "content-desc": "Test Description"},
            parent=None
        )
        
        properties = [
            {
                "name": "button1",
                "locator": {"text": "Button 1"},
                "anchor_name": "anchor1",
                "depth": 1,
                "base_name": "base1",
                "sibling": True,
                "via_recycler": False,
                "summary_id": {"id": "summary1"}
            }
        ]
        
        title_locator = {"text": "Test Page"}
        recycler_locator = {"class": "android.widget.RecyclerView"}
        
        model = ModelBuilder.build_from_ui_tree(
            ui_tree, properties, title_locator, recycler_locator
        )
        
        assert model.class_name == "PageTestPage"  # noqa: S101
        assert model.raw_title == "Test Page"  # noqa: S101
        assert model.title_locator == title_locator  # noqa: S101
        assert model.recycler_locator == recycler_locator  # noqa: S101
        assert model.need_recycler is True  # noqa: S101
        assert len(model.properties) == 1  # noqa: S101
        assert model.properties[0].name == "button1"  # noqa: S101

    def test_build_from_ui_tree_with_content_desc(self):
        """Test build_from_ui_tree with content-desc instead of text."""
        ui_tree = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={"content-desc": "Test Description"},
            parent=None
        )
        
        properties = []
        title_locator = {"text": "Test Page"}
        recycler_locator = None
        
        model = ModelBuilder.build_from_ui_tree(
            ui_tree, properties, title_locator, recycler_locator
        )
        
        assert model.class_name == "PageTestDescription"  # noqa: S101
        assert model.raw_title == "Test Description"  # noqa: S101
        assert model.need_recycler is False  # noqa: S101

    def test_build_from_ui_tree_no_title(self):
        """Test build_from_ui_tree with no title."""
        ui_tree = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={},
            parent=None
        )
        
        properties = []
        title_locator = {"text": "Test Page"}
        recycler_locator = None
        
        model = ModelBuilder.build_from_ui_tree(
            ui_tree, properties, title_locator, recycler_locator
        )
        
        assert model.class_name == "Page"  # noqa: S101
        assert model.raw_title == ""  # noqa: S101

    def test_build_from_ui_tree_with_spaces_in_title(self):
        """Test build_from_ui_tree with spaces in title."""
        ui_tree = UiElementNode(
            id="root",
            tag="root_tag",
            attrs={"text": "Test Page With Spaces"},
            parent=None
        )
        
        properties = []
        title_locator = {"text": "Test Page"}
        recycler_locator = None
        
        model = ModelBuilder.build_from_ui_tree(
            ui_tree, properties, title_locator, recycler_locator
        )
        
        assert model.class_name == "PageTestPageWithSpaces"  # noqa: S101
        assert model.raw_title == "Test Page With Spaces"  # noqa: S101


class TestPageObjectRenderer:
    """Test cases for PageObjectRenderer class."""

    def test_init_default(self):
        """Test PageObjectRenderer initialization with default renderer."""
        renderer = PageObjectRenderer()
        assert isinstance(renderer.renderer, Jinja2Renderer)  # noqa: S101

    def test_init_jinja2(self):
        """Test PageObjectRenderer initialization with jinja2 renderer."""
        renderer = PageObjectRenderer("jinja2")
        assert isinstance(renderer.renderer, Jinja2Renderer)  # noqa: S101

    @patch("shadowstep.page_object.page_object_element_node.get_current_func_name")
    def test_render_and_save(self, mock_get_func_name: Mock):
        """Test render_and_save method."""
        mock_get_func_name.return_value = "test_function"
        
        renderer = PageObjectRenderer()
        
        # Create a mock model
        model = PageObjectModel(
            class_name="TestPage",
            raw_title="Test Page",
            title_locator={"text": "Test Page"},
            recycler_locator=None,
            properties=[
                PropertyModel(name="button2", locator={"text": "Button 2"}, anchor_name=None, base_name=None, summary_id=None),
                PropertyModel(name="button1", locator={"text": "Button 1"}, anchor_name=None, base_name=None, summary_id=None)
            ]
        )
        
        with patch.object(renderer.renderer, "render") as mock_render, \
             patch.object(renderer.renderer, "save") as mock_save:
            
            mock_render.return_value = "rendered_content"
            
            result = renderer.render_and_save(model, "/test/path/file.py", "template.j2")
            
            assert result == "/test/path/file.py"  # noqa: S101
            mock_render.assert_called_once_with(model, "template.j2")
            mock_save.assert_called_once_with("rendered_content", "/test/path/file.py")
            
            # Check that properties were sorted
            assert model.properties[0].name == "button1"  # noqa: S101
            assert model.properties[1].name == "button2"  # noqa: S101

    @patch("shadowstep.page_object.page_object_element_node.get_current_func_name")
    def test_render_and_save_default_template(self, mock_get_func_name: Mock):
        """Test render_and_save method with default template."""
        mock_get_func_name.return_value = "test_function"
        
        renderer = PageObjectRenderer()
        
        model = PageObjectModel(
            class_name="TestPage",
            raw_title="Test Page",
            title_locator={"text": "Test Page"},
            recycler_locator=None,
            properties=[]
        )
        
        with patch.object(renderer.renderer, "render") as mock_render, \
             patch.object(renderer.renderer, "save") as mock_save:
            
            mock_render.return_value = "rendered_content"
            
            result = renderer.render_and_save(model, "/test/path/file.py")
            
            assert result == "/test/path/file.py"  # noqa: S101
            mock_render.assert_called_once_with(model, "page_object.py.j2")
            mock_save.assert_called_once_with("rendered_content", "/test/path/file.py")
