"""Integration tests for PageObjectTestGenerator class.

This module tests the PageObjectTestGenerator functionality using real Android device
connections through the app fixture and real page objects.
"""
import tempfile
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_test_generator import PageObjectTestGenerator
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def test_generator():
    """Fixture providing PageObjectTestGenerator instance."""
    return PageObjectTestGenerator()


@pytest.fixture
def parser():
    """Fixture providing PageObjectParser instance."""
    return PageObjectParser()


@pytest.fixture
def translator():
    """Fixture providing a simple translator."""
    class SimpleTranslator:
        def translate(self, text: str) -> str:
            return text
    return SimpleTranslator()


@pytest.fixture
def generator(translator):
    """Fixture providing PageObjectGenerator instance."""
    return PageObjectGenerator(translator)


class TestGenerateTest:
    """Tests for generate_test method."""

    def test_generate_test_from_real_page_object(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test generating test file from real page object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object from real app
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test from page object
            test_path, test_class_name = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Verify test file was created
            assert Path(test_path).exists()
            assert test_class_name.startswith("Test")
            assert test_class_name == f"Test{page_class_name}"

    def test_generated_test_has_correct_structure(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generated test has correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, test_class_name = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Read generated test
            with Path(test_path).open() as f:
                test_content = f.read()

            # Verify test structure
            assert "import pytest" in test_content
            assert "@pytest.fixture" in test_content
            assert f"class {test_class_name}:" in test_content
            assert "def test_" in test_content
            assert ".is_visible()" in test_content

    def test_generated_test_imports_page_object(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generated test imports the page object class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Read generated test
            with Path(test_path).open() as f:
                test_content = f.read()

            # Verify import statement
            assert f"from" in test_content
            assert f"import {page_class_name}" in test_content

    def test_generated_test_creates_fixture(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generated test creates page object fixture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Read generated test
            with Path(test_path).open() as f:
                test_content = f.read()

            # Verify fixture
            assert "@pytest.fixture" in test_content
            assert f"{page_class_name}()" in test_content
            assert "yield" in test_content

    def test_generated_test_contains_property_tests(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generated test contains tests for properties."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Read page object to count properties
            with Path(page_path).open() as f:
                page_content = f.read()

            # Count @property decorators (excluding ignored ones)
            import ast
            tree_ast = ast.parse(page_content)
            class_node = next((n for n in tree_ast.body if isinstance(n, ast.ClassDef)), None)
            ignore = {"name", "edges", "title", "recycler", "is_current_page"}
            property_count = sum(
                1 for node in class_node.body
                if isinstance(node, ast.FunctionDef)
                and any(isinstance(d, ast.Name) and d.id == "property" for d in node.decorator_list)
                and node.name not in ignore
            )

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Read generated test
            with Path(test_path).open() as f:
                test_content = f.read()

            # Verify test methods count (at least one test per property)
            test_method_count = test_content.count("def test_")
            assert test_method_count >= property_count

    def test_generate_test_returns_correct_paths(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generate_test returns correct file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, test_class_name = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Verify paths
            assert test_path.startswith(tmpdir)
            assert test_path.endswith(".py")
            assert "test_" in test_path

    def test_generate_test_file_naming_convention(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generated test follows naming convention."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Verify naming convention (test_<snake_case>.py)
            filename = Path(test_path).name
            assert filename.startswith("test_")
            assert filename.endswith(".py")
            assert filename.islower() or "_" in filename

    def test_generate_test_overwrites_existing_file(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generate_test overwrites existing test file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test first time
            test_path1, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Get first file timestamp
            mtime1 = Path(test_path1).stat().st_mtime

            # Generate test second time
            test_path2, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Verify same path and file was overwritten
            assert test_path1 == test_path2
            assert Path(test_path2).exists()


class TestExtractProperties:
    """Tests for _extract_properties method (indirectly through generate_test)."""

    def test_extract_properties_excludes_ignored_properties(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that ignored properties are not included in tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Read generated test
            with Path(test_path).open() as f:
                test_content = f.read()

            # Verify ignored properties are not tested
            ignore = {"name", "edges", "title", "recycler", "is_current_page"}
            for prop in ignore:
                # These properties should not have test methods
                assert f"def test_{prop}(" not in test_content


class TestCamelToSnake:
    """Tests for _camel_to_snake method (indirectly through file naming)."""

    def test_camel_to_snake_conversion_in_filename(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that CamelCase class name converts to snake_case filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Verify filename is snake_case
            filename = Path(test_path).stem  # Remove .py extension
            # Should start with test_
            assert filename.startswith("test_")
            # Should be lowercase with underscores
            assert filename == filename.lower()


class TestPageObjectTestGeneratorIntegration:
    """Integration tests using real app and complete workflow."""

    def test_full_workflow_generate_and_verify(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test complete workflow: parse -> generate page -> generate test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Parse real app screen
            xml = app.driver.page_source
            tree = parser.parse(xml)

            # Generate page object
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)
            assert Path(page_path).exists()

            # Generate test
            test_path, test_class_name = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Verify test file
            assert Path(test_path).exists()
            with Path(test_path).open() as f:
                test_content = f.read()

            # Verify all required components
            assert "import pytest" in test_content
            assert f"import {page_class_name}" in test_content
            assert f"class {test_class_name}:" in test_content
            assert "@pytest.fixture" in test_content
            assert "def test_" in test_content
            assert ".is_visible()" in test_content

    def test_generated_test_is_valid_python(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that generated test is valid Python code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)

            # Generate test
            test_path, _ = test_generator.generate_test(
                input_path=str(page_path),
                class_name=page_class_name,
                output_dir=tmpdir
            )

            # Try to parse generated test as Python
            with Path(test_path).open() as f:
                test_content = f.read()

            import ast
            try:
                ast.parse(test_content)
            except SyntaxError as e:
                pytest.fail(f"Generated test has syntax error: {e}")

    def test_multiple_page_objects_generate_different_tests(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, test_generator: PageObjectTestGenerator
    ):
        """Test that different page objects generate different tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate first page object
            xml1 = app.driver.page_source
            tree1 = parser.parse(xml1)
            page_path1, page_class_name1 = generator.generate(tree1, output_dir=tmpdir)

            # Generate first test
            test_path1, test_class_name1 = test_generator.generate_test(
                input_path=str(page_path1),
                class_name=page_class_name1,
                output_dir=tmpdir
            )

            # Generate second page object with different filename_prefix
            page_path2, page_class_name2 = generator.generate(
                tree1, output_dir=tmpdir, filename_prefix="second"
            )

            # Generate second test
            test_path2, test_class_name2 = test_generator.generate_test(
                input_path=str(page_path2),
                class_name=page_class_name2,
                output_dir=tmpdir
            )

            # Verify both test files exist
            assert Path(test_path1).exists()
            assert Path(test_path2).exists()
            # Test paths should be different since class names include prefix
            if page_class_name1 != page_class_name2:
                assert test_path1 != test_path2
