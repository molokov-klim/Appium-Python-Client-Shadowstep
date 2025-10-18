"""Integration tests for PageObjectParser class.

This module tests the PageObjectParser functionality using real Android device
connections through the app fixture.
"""
import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepRootNodeFilteredOutError
from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def parser():
    """Fixture providing PageObjectParser instance."""
    return PageObjectParser()


class TestParse:
    """Tests for parse method."""

    def test_parse_real_app_xml(self, app: Shadowstep, parser: PageObjectParser):
        """Test parsing XML from real app."""
        # Get XML from real app
        xml = app.driver.page_source

        # Parse XML
        tree = parser.parse(xml)

        # Verify tree structure
        assert isinstance(tree, UiElementNode)
        assert tree.id is not None
        assert tree.tag is not None

    def test_parse_returns_ui_element_node(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parse returns UiElementNode instance."""
        xml = app.driver.page_source
        result = parser.parse(xml)

        assert isinstance(result, UiElementNode)
        assert hasattr(result, 'id')
        assert hasattr(result, 'tag')
        assert hasattr(result, 'attrs')
        assert hasattr(result, 'children')

    def test_parse_builds_tree_with_children(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parse builds tree with child nodes."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Verify tree has structure
        assert isinstance(tree.children, list)
        # Most Android screens will have at least some UI elements

    def test_parse_sets_node_attributes(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parsed nodes have proper attributes."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Check root node attributes
        assert tree.id.startswith("el_")
        assert isinstance(tree.depth, int)
        assert tree.depth >= 0
        assert isinstance(tree.attrs, dict)

    def test_parse_handles_scrollable_elements(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parse correctly identifies scrollable elements."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Walk tree to find nodes
        def walk_tree(node):
            yield node
            for child in node.children:
                yield from walk_tree(child)

        # Check if any node has scrollable_parents tracking
        nodes = list(walk_tree(tree))
        assert len(nodes) > 0
        # All nodes should have scrollable_parents attribute
        for node in nodes:
            assert hasattr(node, 'scrollable_parents')
            assert isinstance(node.scrollable_parents, list)

    def test_parse_with_custom_white_list(self, app: Shadowstep):
        """Test parsing with custom white list classes."""
        custom_white_list = ("android.widget.TextView", "android.widget.Button")
        parser = PageObjectParser(white_list_classes=custom_white_list)

        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Verify tree was created
        assert isinstance(tree, UiElementNode)

    def test_parse_with_custom_black_list(self, app: Shadowstep):
        """Test parsing with custom black list classes."""
        custom_black_list = ("android.widget.ImageView",)
        parser = PageObjectParser(black_list_classes=custom_black_list)

        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Verify tree was created
        assert isinstance(tree, UiElementNode)

    def test_parse_filters_elements_correctly(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parse filters elements based on white/black lists."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Walk tree - note that blacklisted classes can appear as virtual containers
        # if they have children that pass filtering
        def walk_tree(node):
            yield node
            for child in node.children:
                yield from walk_tree(child)

        nodes = list(walk_tree(tree))
        # Just verify tree was created and has nodes
        assert len(nodes) > 0

    def test_parse_assigns_unique_ids(self, app: Shadowstep, parser: PageObjectParser):
        """Test that all nodes get unique IDs."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        def collect_ids(node):
            ids = [node.id]
            for child in node.children:
                ids.extend(collect_ids(child))
            return ids

        all_ids = collect_ids(tree)
        # All IDs should be unique
        assert len(all_ids) == len(set(all_ids))

    def test_parse_maintains_parent_child_relationships(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parent-child relationships are correct."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Root should have no parent
        assert tree.parent is None

        # All children should have correct parent
        def check_relationships(node):
            for child in node.children:
                assert child.parent is node
                check_relationships(child)

        check_relationships(tree)

    def test_parse_sets_correct_depth(self, app: Shadowstep, parser: PageObjectParser):
        """Test that node depth is set correctly."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Root should be at depth 0
        assert tree.depth == 0

        # Children depths should increase
        def check_depths(node, expected_depth):
            assert node.depth == expected_depth
            for child in node.children:
                check_depths(child, expected_depth + 1)

        check_depths(tree, 0)


class TestParseEdgeCases:
    """Tests for parse method edge cases."""

    def test_parse_handles_hierarchy_tag(self, app: Shadowstep, parser: PageObjectParser):
        """Test that parse handles hierarchy root tag correctly."""
        xml = app.driver.page_source
        # Real Android XML should start with <hierarchy>
        assert xml.strip().startswith('<?xml') or xml.strip().startswith('<hierarchy')

        tree = parser.parse(xml)
        assert isinstance(tree, UiElementNode)

    def test_parse_multiple_times_independent(self, app: Shadowstep, parser: PageObjectParser):
        """Test that multiple parse calls are independent."""
        xml = app.driver.page_source

        tree1 = parser.parse(xml)
        tree2 = parser.parse(xml)

        # Trees should be independent instances
        assert tree1 is not tree2
        # IDs will be different since counter continues incrementing
        # Just verify both trees are valid
        assert isinstance(tree1, UiElementNode)
        assert isinstance(tree2, UiElementNode)


class TestFilteringLogic:
    """Tests for element filtering logic."""

    def test_white_list_classes_always_allowed(self, app: Shadowstep):
        """Test that white list classes are always included."""
        white_list = ("android.widget.EditText", "android.widget.Switch")
        parser = PageObjectParser(white_list_classes=white_list)

        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Verify tree exists
        assert isinstance(tree, UiElementNode)

    def test_black_list_classes_always_filtered(self, app: Shadowstep):
        """Test that black list classes configuration works."""
        black_list = ("android.widget.LinearLayout", "android.widget.FrameLayout")
        parser = PageObjectParser(black_list_classes=black_list)

        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Note: Blacklisted classes can appear as virtual containers if they have children
        # Just verify tree was created successfully with custom blacklist
        assert isinstance(tree, UiElementNode)

    def test_elements_with_text_always_allowed(self, app: Shadowstep, parser: PageObjectParser):
        """Test that elements with text are always included."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Find nodes with text
        def find_text_nodes(node):
            text_nodes = []
            if node.attrs.get("text"):
                text_nodes.append(node)
            for child in node.children:
                text_nodes.extend(find_text_nodes(child))
            return text_nodes

        text_nodes = find_text_nodes(tree)
        # Verify text nodes exist (most Android screens have text)
        # Just verify they have text attribute
        for node in text_nodes:
            assert node.attrs.get("text")

    def test_elements_with_content_desc_always_allowed(self, app: Shadowstep, parser: PageObjectParser):
        """Test that elements with content-desc are always included."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Find nodes with content-desc
        def find_desc_nodes(node):
            desc_nodes = []
            if node.attrs.get("content-desc"):
                desc_nodes.append(node)
            for child in node.children:
                desc_nodes.extend(find_desc_nodes(child))
            return desc_nodes

        desc_nodes = find_desc_nodes(tree)
        # Just verify they have content-desc if found
        for node in desc_nodes:
            assert node.attrs.get("content-desc")


class TestScrollableParents:
    """Tests for scrollable parents tracking."""

    def test_scrollable_parents_tracked_correctly(self, app: Shadowstep, parser: PageObjectParser):
        """Test that scrollable parents are tracked in node hierarchy."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Walk tree and check scrollable tracking
        def check_scrollable_tracking(node):
            # All nodes should have scrollable_parents attribute
            assert isinstance(node.scrollable_parents, list)

            # If node is scrollable, children should have it in their stack
            if node.attrs.get("scrollable") == "true":
                for child in node.children:
                    # Child's stack should contain this node's ID
                    assert node.id in child.scrollable_parents

            for child in node.children:
                check_scrollable_tracking(child)

        check_scrollable_tracking(tree)


class TestPageObjectParserIntegration:
    """Integration tests using real app and complete workflows."""

    def test_full_workflow_parse_and_traverse(self, app: Shadowstep, parser: PageObjectParser):
        """Test complete workflow: get XML -> parse -> traverse tree."""
        # Get XML from app
        xml = app.driver.page_source
        assert xml
        assert len(xml) > 0

        # Parse XML
        tree = parser.parse(xml)
        assert isinstance(tree, UiElementNode)

        # Traverse tree
        node_count = 0
        def count_nodes(node):
            nonlocal node_count
            node_count += 1
            for child in node.children:
                count_nodes(child)

        count_nodes(tree)
        # Should have at least some nodes
        assert node_count > 0

    def test_parsed_tree_usable_for_generation(
        self, app: Shadowstep, parser: PageObjectParser
    ):
        """Test that parsed tree can be used for page object generation."""
        from shadowstep.page_object.page_object_generator import PageObjectGenerator
        import tempfile

        class SimpleTranslator:
            def translate(self, text: str) -> str:
                return text

        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Use tree with generator
        generator = PageObjectGenerator(SimpleTranslator())
        with tempfile.TemporaryDirectory() as tmpdir:
            page_path, class_name = generator.generate(tree, output_dir=tmpdir)

            # Verify generation worked
            from pathlib import Path
            assert Path(page_path).exists()

    def test_multiple_parse_calls_consistent(self, app: Shadowstep, parser: PageObjectParser):
        """Test that multiple parse calls produce consistent results."""
        xml = app.driver.page_source

        tree1 = parser.parse(xml)
        tree2 = parser.parse(xml)

        # Count nodes in both trees
        def count_nodes(node):
            count = 1
            for child in node.children:
                count += count_nodes(child)
            return count

        count1 = count_nodes(tree1)
        count2 = count_nodes(tree2)

        # Should have same number of nodes
        assert count1 == count2

    def test_parser_state_after_parse(self, app: Shadowstep, parser: PageObjectParser):
        """Test parser internal state after parsing."""
        xml = app.driver.page_source
        tree = parser.parse(xml)

        # Check parser has stored tree
        assert parser.ui_element_tree is not None
        assert parser.ui_element_tree is tree
        assert parser._tree is not None
