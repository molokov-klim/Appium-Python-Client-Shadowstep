# ruff: noqa
# pyright: ignore
"""Tests for page_object_recycler_explorer module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepTerminalNotInitializedError
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer

"""
uv run pytest -svl --log-cli-level INFO --tb=short --setup-show  tests/test_unit/test_page_object/test_page_object_recycler_explorer.py
"""

class TestPageObjectRecyclerExplorer:
    """Test cases for PageObjectRecyclerExplorer class."""

    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_explore_without_terminal(self):
        """Test explore method when terminal is None."""
        base = Mock()
        base.terminal = None
        translator = Mock()

        explorer = PageObjectRecyclerExplorer(base, translator)

        with pytest.raises(ShadowstepTerminalNotInitializedError, match="Terminal is not initialized"):
            explorer.explore("output_dir", timeout=10)

    @pytest.mark.unit
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
            result = explorer.explore(temp_dir, timeout=10)

            assert result is not None  # noqa: S101
            assert result.parent.name == "merged_pages"  # noqa: S101
            base.terminal.get_screen_resolution.assert_called()
            base.terminal.adb_shell.assert_called()
            base.swipe.assert_called()

    @pytest.mark.unit
    def test_load_class_from_file_success(self):
        """Test _load_class_from_file method with successful loading."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())

        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
import pytest

class TestPage:
    def __init__(self):
        pass
    
    @pytest.mark.unit
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

    @pytest.mark.unit
    def test_load_class_from_file_nonexistent_file(self):
        """Test _load_class_from_file method with nonexistent file."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())

        with pytest.raises(FileNotFoundError):
            explorer._load_class_from_file("nonexistent.py", "TestPage")

    @pytest.mark.unit
    def test_explore_failed_to_load_class(self):
        """Test explore method when class loading fails."""
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

        # Mock _load_class_from_file to return None
        explorer._load_class_from_file = Mock(return_value=None)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = explorer.explore(temp_dir, timeout=10)

            assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_explore_no_recycler_property(self):
        """Test explore method when page has no recycler property."""
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

        # Mock the _load_class_from_file method to return a class without recycler
        class PageWithoutRecycler:
            def __init__(self) -> None:
                pass

        explorer._load_class_from_file = Mock(return_value=PageWithoutRecycler)

        result = explorer.explore("temp_dir", timeout=5)

        assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_explore_recycler_no_scroll_down(self):
        """Test explore method when recycler has no scroll_down method."""
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

        # Mock the _load_class_from_file method
        class RecyclerWithoutScroll:
            def __init__(self) -> None:
                pass

        class PageWithRecyclerNoScroll:
            def __init__(self) -> None:
                self.recycler = RecyclerWithoutScroll()

        explorer._load_class_from_file = Mock(return_value=PageWithRecyclerNoScroll)

        result = explorer.explore("temp_dir", timeout=10)

        assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_explore_with_scroll_down_loop(self):
        """Test explore method with scroll_down loop."""
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
        mock_instance = Mock()
        mock_recycler = Mock()
        # scroll_down returns True twice, then False
        mock_recycler.scroll_down = Mock(side_effect=[True, True, False])
        mock_instance.recycler = mock_recycler
        mock_class.return_value = mock_instance
        explorer._load_class_from_file = Mock(return_value=mock_class)

        # Mock Path operations to avoid file system operations
        with tempfile.TemporaryDirectory() as temp_dir:
            current_dir = os.getcwd()
            os.chdir(temp_dir)
            try:
                result = explorer.explore(temp_dir, timeout=10)
            finally:
                os.chdir(current_dir)

            assert result is not None  # noqa: S101
            assert result.parent.name == "merged_pages"  # noqa: S101
        # Should call scroll_down 3 times (2 True + 1 False)
        assert mock_recycler.scroll_down.call_count == 3  # noqa: S101

    @pytest.mark.unit
    def test_load_class_from_file_invalid_spec(self):
        """Test _load_class_from_file method with invalid spec."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())

        # Create a temporary file that will cause importlib.util.spec_from_file_location to return None
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("invalid python syntax {")
            temp_file = f.name

        try:
            with pytest.raises(SyntaxError):
                explorer._load_class_from_file(temp_file, "TestPage")
        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_load_class_from_file_class_not_found(self):
        """Test _load_class_from_file method when class is not found in module."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())

        # Create a temporary Python file without the expected class
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
class OtherClass:
    def __init__(self):
        pass
""")
            temp_file = f.name

        try:
            result = explorer._load_class_from_file(temp_file, "TestPage")

            assert result is None  # noqa: S101
        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_load_class_from_file_spec_is_none(self):
        """Test _load_class_from_file when spec_from_file_location returns None."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())
        
        with patch("importlib.util.spec_from_file_location", return_value=None):
            result = explorer._load_class_from_file("/test/path.py", "TestClass")
            assert result is None  # noqa: S101

    @pytest.mark.unit
    def test_load_class_from_file_loader_is_none(self):
        """Test _load_class_from_file when spec.loader is None."""
        explorer = PageObjectRecyclerExplorer(Mock(), Mock())
        
        mock_spec = Mock()
        mock_spec.loader = None
        
        with patch("importlib.util.spec_from_file_location", return_value=mock_spec):
            result = explorer._load_class_from_file("/test/path.py", "TestClass")
            assert result is None  # noqa: S101
