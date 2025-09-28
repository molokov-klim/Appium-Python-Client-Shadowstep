"""Tests for page_object_recycler_explorer module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepTerminalNotInitializedError
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer


class TestPageObjectRecyclerExplorer:
    """Test cases for PageObjectRecyclerExplorer class."""

    def test_init(self):
        """Test PageObjectRecyclerExplorer initialization."""
        base = Mock()
        translator = Mock()

        explorer = PageObjectRecyclerExplorer(base, translator)

        assert explorer.base == base  # noqa: S101
        assert explorer.logger is not None  # noqa: S101
        assert explorer.parser is not None  # noqa: S101
        assert explorer.generator is not None  # noqa: S101
        assert explorer.merger is not None  # noqa: S101

    def test_explore_without_terminal(self):
        """Test explore method when terminal is None."""
        base = Mock()
        base.terminal = None
        translator = Mock()

        explorer = PageObjectRecyclerExplorer(base, translator)

        with pytest.raises(ShadowstepTerminalNotInitializedError, match="Terminal is not initialized"):
            explorer.explore("output_dir")

    def test_explore_with_terminal(self):
        """Test explore method with terminal available."""
        base = Mock()
        base.terminal = Mock()
        base.terminal.get_screen_resolution.return_value = (1080, 1920)
        base.terminal.adb_shell = Mock()
        base.driver = Mock()
        base.driver.page_source = "<hierarchy><node class='test' /></hierarchy>"
        base.swipe = Mock()

        translator = Mock()

        explorer = PageObjectRecyclerExplorer(base, translator)

        # Mock the parser
        mock_tree = Mock()
        explorer.parser.parse = Mock(return_value=mock_tree)

        # Mock the generator
        mock_generator_result = (Path("test_page.py"), "TestPage")
        explorer.generator.generate = Mock(return_value=mock_generator_result)

        # Mock the merger
        explorer.merger.merge = Mock(return_value=True)

        # Mock the _load_class_from_file method
        mock_class = Mock()
        mock_class.return_value = Mock()
        mock_class.return_value.recycler = Mock()
        mock_class.return_value.recycler.scroll_down = Mock(return_value=False)
        explorer._load_class_from_file = Mock(return_value=mock_class)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = explorer.explore(temp_dir)

            assert result is not None  # noqa: S101
            assert result.parent.name == "merged_pages"  # noqa: S101
            base.terminal.get_screen_resolution.assert_called()
            base.terminal.adb_shell.assert_called()
            base.swipe.assert_called()

    def test_load_class_from_file_success(self):
        """Test _load_class_from_file method with successful loading."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())

        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
class TestPage:
    def __init__(self):
        pass
    
    def test_method(self):
        return "test"
""")    # don't change intend!
            temp_file = f.name

        try:
            result = explorer._load_class_from_file(temp_file, "TestPage")

            assert result is not None  # noqa: S101
            assert result.__name__ == "TestPage"  # noqa: S101

            # Test that we can instantiate the class
            instance = result()
            assert instance.test_method() == "test"  # noqa: S101
        finally:
            os.unlink(temp_file)

    def test_load_class_from_file_nonexistent_file(self):
        """Test _load_class_from_file method with nonexistent file."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())

        with pytest.raises(FileNotFoundError):
            explorer._load_class_from_file("nonexistent.py", "TestPage")
