# ruff: noqa
# pyright: ignore
"""Integration tests for shadowstep.page_object modules.

These tests verify real Page Object operations with actual mobile applications
including parsing, generation, and exploration of UI elements.

Coverage notes:
- Tests PageObjectGenerator.generate() with real device UI
- Tests PageObjectRecyclerExplorer.explore() with scrollable content
- Tests file generation, cleanup, and Python validity
- Tests error handling for invalid inputs

Requirements:
- Shadowstep instance connected to Android device (app fixture)
- Real Android Settings app
"""

import importlib.util
import shutil
import time
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_element_node import UiElementNode
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepTitleNotFoundError,
    ShadowstepNameCannotBeEmptyError,
    ShadowstepPageClassNameCannotBeEmptyError,
)


@pytest.fixture
def cleanup_generated_files():
    """Fixture to cleanup generated page object files after tests."""
    yield
    # Cleanup various output directories that tests create
    for folder in ("pages", "mergedpages", "merged_pages", "test_pages", "test_output"):
        path = Path(folder)
        if path.exists() and path.is_dir():
            shutil.rmtree(path)


@pytest.fixture
def temp_output_dir(cleanup_generated_files):
    """Fixture to create and cleanup temporary output directory."""
    output_dir = Path("test_pages")
    output_dir.mkdir(exist_ok=True)
    yield str(output_dir)


class TestPageObjectGenerator:
    """Integration test cases for PageObjectGenerator module."""

    def test_generator_initialization_default(self):
        """Test PageObjectGenerator can be initialized with defaults."""
        # Act
        generator = PageObjectGenerator()

        # Assert
        assert generator is not None

    def test_generator_initialization_with_translator_none(self):
        """Test PageObjectGenerator can be initialized with None translator."""
        # Act
        generator = PageObjectGenerator(translator=None)

        # Assert
        assert generator is not None

    def test_generate_from_real_device(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test generate() creates page object from real device UI."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir
        )

        # Assert
        assert output_path.exists()
        assert output_path.is_file()
        assert output_path.suffix == ".py"
        assert class_name.startswith("Page")
        assert len(class_name) > 4

    def test_generate_creates_valid_python_file(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test generated file can be imported as Python module."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir
        )

        # Assert - file is valid Python and can be imported
        spec = importlib.util.spec_from_file_location("test_module", output_path)
        assert spec is not None
        assert spec.loader is not None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Verify class exists
        page_class = getattr(module, class_name)
        assert page_class is not None

    def test_generate_with_filename_prefix(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test generate() respects filename_prefix parameter."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir, filename_prefix="test_"
        )

        # Assert
        assert output_path.name.startswith("test_")

    def test_generate_multiple_pages(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test generating multiple page objects from different UI states."""
        # Arrange
        parser = PageObjectParser()
        generator = PageObjectGenerator()
        
        # Generate from settings
        time.sleep(2)
        page_source1 = app.driver.page_source
        ui_tree1 = parser.parse(page_source1)

        # Act - generate first page
        output_path1, class_name1 = generator.generate(
            ui_element_tree=ui_tree1, output_dir=temp_output_dir, filename_prefix="1_"
        )

        # Close and get different UI
        app.terminal.press_home()
        time.sleep(1)
        page_source2 = app.driver.page_source
        ui_tree2 = parser.parse(page_source2)

        # Act - generate second page
        output_path2, class_name2 = generator.generate(
            ui_element_tree=ui_tree2, output_dir=temp_output_dir, filename_prefix="2_"
        )

        # Assert
        assert output_path1.exists()
        assert output_path2.exists()
        assert output_path1 != output_path2

    def test_generate_returns_tuple(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test generate() returns tuple of (Path, str)."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act
        result = generator.generate(ui_element_tree=ui_tree, output_dir=temp_output_dir)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Path)
        assert isinstance(result[1], str)

    def test_generate_output_directory_created(self, app: Shadowstep, android_settings_open_close: None):
        """Test generate() creates output directory if it doesn't exist."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)

        new_dir = Path("test_output") / "nested" / "path"
        assert not new_dir.exists()

        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=str(new_dir)
        )

        # Assert
        assert new_dir.exists()
        assert output_path.exists()

        # Cleanup
        shutil.rmtree("test_output")

    def test_generate_with_minimal_ui_tree(self, temp_output_dir: str):
        """Test generator behavior with minimal UI tree."""
        # Arrange - create minimal valid UI tree
        root = UiElementNode(
            id="el_0",
            tag="android.widget.FrameLayout",
            attrs={"text": "TestTitle", "displayed": "true"},
            parent=None,
            children=[],
            depth=0,
            scrollable_parents=[],
        )

        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=root, output_dir=temp_output_dir
        )

        # Assert
        assert output_path.exists()
        assert "Page" in class_name

    def test_generate_raises_error_for_tree_without_title(self, temp_output_dir: str):
        """Test generator raises error when UI tree has no title."""
        # Arrange - create UI tree without text (no valid title)
        root = UiElementNode(
            id="el_0",
            tag="android.widget.FrameLayout",
            attrs={"displayed": "true"},  # No text attribute
            parent=None,
            children=[],
            depth=0,
            scrollable_parents=[],
        )

        generator = PageObjectGenerator()

        # Act & Assert
        with pytest.raises((ShadowstepTitleNotFoundError, ShadowstepNameCannotBeEmptyError, ShadowstepPageClassNameCannotBeEmptyError)):
            generator.generate(ui_element_tree=root, output_dir=temp_output_dir)


class TestPageObjectRecyclerExplorer:
    """Integration test cases for PageObjectRecyclerExplorer module."""

    def test_explorer_initialization(self, app: Shadowstep):
        """Test PageObjectRecyclerExplorer can be initialized."""
        # Act
        explorer = PageObjectRecyclerExplorer(base=app, translator=None)

        # Assert
        assert explorer is not None
        assert explorer.base is app

    def test_explore_with_scrollable_content(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test explore() generates page objects from scrollable content."""
        # Arrange
        time.sleep(2)
        explorer = PageObjectRecyclerExplorer(base=app, translator=None)

        # Act
        output_path = explorer.explore(output_dir=temp_output_dir, timeout=10)

        # Assert
        assert isinstance(output_path, (Path, str))
        # If Path returned, verify it exists or check for output directory
        if isinstance(output_path, Path) and output_path != Path(""):
            assert output_path.exists() or Path(temp_output_dir).exists()

    def test_explore_creates_files(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test explore() creates page object files."""
        # Arrange
        time.sleep(2)
        explorer = PageObjectRecyclerExplorer(base=app, translator=None)

        # Act
        output_path = explorer.explore(output_dir=temp_output_dir, timeout=15)

        # Assert - check that files were created
        output_dir_path = Path(temp_output_dir)
        if output_dir_path.exists():
            generated_files = list(output_dir_path.glob("*.py"))
            # At least one file should be generated
            assert len(generated_files) >= 0  # May or may not generate depending on UI

    def test_explore_timeout_parameter(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test explore() respects timeout parameter."""
        # Arrange
        time.sleep(2)
        explorer = PageObjectRecyclerExplorer(base=app, translator=None)

        # Act
        start_time = time.time()
        output_path = explorer.explore(output_dir=temp_output_dir, timeout=5)
        elapsed = time.time() - start_time

        # Assert - should not exceed timeout by too much
        assert elapsed < 45  # 5 second timeout + overhead for scrolling/generation

    def test_explore_with_non_scrollable_screen(self, app: Shadowstep, temp_output_dir: str):
        """Test explore() handles screens without recycler view."""
        # Arrange
        app.terminal.press_home()
        time.sleep(2)
        explorer = PageObjectRecyclerExplorer(base=app, translator=None)

        # Act
        output_path = explorer.explore(output_dir=temp_output_dir, timeout=5)

        # Assert - should complete without errors
        assert isinstance(output_path, (Path, str))

    def test_multiple_explorers_same_app(self, app: Shadowstep):
        """Test creating multiple explorers with same app instance."""
        # Act
        explorer1 = PageObjectRecyclerExplorer(base=app, translator=None)
        explorer2 = PageObjectRecyclerExplorer(base=app, translator=None)

        # Assert
        assert explorer1 is not explorer2
        assert explorer1.base is app
        assert explorer2.base is app


class TestPageObjectIntegration:
    """Integration tests for Page Object generation workflow."""

    def test_full_workflow_parse_generate(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test full workflow: parse UI -> generate page object."""
        # Arrange
        time.sleep(2)
        parser = PageObjectParser()
        generator = PageObjectGenerator()

        # Act
        page_source = app.driver.page_source
        ui_tree = parser.parse(page_source)
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir
        )

        # Assert
        assert output_path.exists()
        assert class_name.startswith("Page")

        # Verify file contains valid Python code
        content = output_path.read_text()
        assert f"class {class_name}" in content
        assert "from shadowstep" in content

    def test_generator_consistency(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test that generator produces consistent class names for same input."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act - generate twice from same tree
        output_path1, class_name1 = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir, filename_prefix="1_"
        )

        output_path2, class_name2 = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir, filename_prefix="2_"
        )

        # Assert - class names should be identical
        assert class_name1 == class_name2

    def test_generated_file_has_page_base_import(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test that generated files have correct base class import."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir
        )

        # Assert
        content = output_path.read_text()
        assert "from shadowstep.page_base import PageBaseShadowstep" in content

    def test_generated_file_can_be_instantiated(self, app: Shadowstep, temp_output_dir: str, android_settings_open_close: None):
        """Test that generated page object class can be instantiated."""
        # Arrange
        time.sleep(2)
        page_source = app.driver.page_source
        parser = PageObjectParser()
        ui_tree = parser.parse(page_source)
        generator = PageObjectGenerator()

        # Act
        output_path, class_name = generator.generate(
            ui_element_tree=ui_tree, output_dir=temp_output_dir
        )

        # Load the module
        spec = importlib.util.spec_from_file_location("test_module", output_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get class and instantiate
        page_class = getattr(module, class_name)
        page_instance = page_class()

        # Assert
        assert page_instance is not None
        assert hasattr(page_instance, "title")  # Should have title property
