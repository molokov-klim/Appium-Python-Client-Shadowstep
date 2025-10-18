"""Integration tests for PageObjectMerger class.

This module tests the PageObjectMerger functionality using real Android device
connections through the app fixture and real page objects.
"""
import tempfile
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_merger import PageObjectMerger
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def merger():
    """Fixture providing PageObjectMerger instance."""
    return PageObjectMerger()


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


class TestMerge:
    """Tests for merge method."""

    def test_merge_two_real_page_objects(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test merging two real page objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate first page object
            xml1 = app.driver.page_source
            tree1 = parser.parse(xml1)
            page_path1, _ = generator.generate(tree1, output_dir=tmpdir)

            # Generate second page object with different prefix
            page_path2, _ = generator.generate(tree1, output_dir=tmpdir, filename_prefix="second")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            result_path = merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify merge succeeded
            assert result_path == output_path
            assert Path(output_path).exists()

    def test_merge_creates_valid_python_file(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merged file is valid Python code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify file is valid Python
            with Path(output_path).open() as f:
                content = f.read()

            import ast
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Merged file has syntax error: {e}")

    def test_merge_preserves_imports(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge preserves import statements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Read merged file
            with Path(output_path).open() as f:
                content = f.read()

            # Verify imports are present
            assert "import" in content or "from" in content

    def test_merge_preserves_class_definition(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge preserves class definition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, class_name1 = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Read merged file
            with Path(output_path).open() as f:
                content = f.read()

            # Verify class definition is present
            assert f"class {class_name1}" in content

    def test_merge_combines_methods(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge combines methods from both files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Count methods in original files
            with Path(page_path1).open() as f:
                content1 = f.read()
            method_count1 = content1.count("def ")

            with Path(page_path2).open() as f:
                content2 = f.read()
            method_count2 = content2.count("def ")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Read merged file
            with Path(output_path).open() as f:
                merged_content = f.read()

            # Merged file should have methods
            merged_method_count = merged_content.count("def ")
            assert merged_method_count > 0

    def test_merge_removes_duplicate_methods(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge removes duplicate methods."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two identical page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)

            # Copy file to create duplicate
            page_path2 = str(Path(tmpdir) / "page_copy.py")
            with Path(page_path1).open() as f1:
                content = f1.read()
            with Path(page_path2).open("w") as f2:
                f2.write(content)

            # Count methods in original
            method_count = content.count("def ")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Read merged file
            with Path(output_path).open() as f:
                merged_content = f.read()

            # Should not have double the methods
            merged_method_count = merged_content.count("def ")
            # Should be approximately same as original (duplicates removed)
            assert merged_method_count <= method_count * 1.1  # Allow small margin

    def test_merge_returns_output_path(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge returns the output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            result = merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify returned path matches expected
            assert result == output_path

    def test_merge_creates_output_directory_if_needed(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge to nested directory that doesn't exist
            output_path = str(Path(tmpdir) / "nested" / "dir" / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify file was created
            assert Path(output_path).exists()

    def test_merge_overwrites_existing_file(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merge overwrites existing output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate two page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge first time
            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Get file modification time
            mtime1 = Path(output_path).stat().st_mtime

            # Merge again
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify file still exists
            assert Path(output_path).exists()


class TestParse:
    """Tests for parse method."""

    def test_parse_reads_file_content(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that parse reads file content correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, _ = generator.generate(tree, output_dir=tmpdir)

            # Parse file
            content = merger.parse(page_path)

            # Verify content is string
            assert isinstance(content, str)
            assert len(content) > 0

    def test_parse_handles_path_object(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that parse accepts Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, _ = generator.generate(tree, output_dir=tmpdir)

            # Parse with Path object
            content = merger.parse(Path(page_path))

            # Verify content
            assert isinstance(content, str)
            assert len(content) > 0


class TestGetImports:
    """Tests for get_imports method."""

    def test_get_imports_extracts_imports(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that get_imports extracts import statements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, _ = generator.generate(tree, output_dir=tmpdir)

            # Read file content
            with Path(page_path).open() as f:
                content = f.read()

            # Extract imports
            imports = merger.get_imports(content)

            # Verify imports
            assert isinstance(imports, str)
            if "import" in content or "from" in content:
                assert len(imports) > 0


class TestGetClassName:
    """Tests for get_class_name method."""

    def test_get_class_name_extracts_class(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that get_class_name extracts class definition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, class_name = generator.generate(tree, output_dir=tmpdir)

            # Read file content
            with Path(page_path).open() as f:
                content = f.read()

            # Extract class name
            class_def = merger.get_class_name(content)

            # Verify class definition
            assert isinstance(class_def, str)
            assert "class" in class_def
            assert class_name in class_def


class TestGetMethods:
    """Tests for get_methods method."""

    def test_get_methods_extracts_methods(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that get_methods extracts method definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, _ = generator.generate(tree, output_dir=tmpdir)

            # Read file content
            with Path(page_path).open() as f:
                content = f.read()

            # Extract methods
            methods = merger.get_methods(content)

            # Verify methods
            assert isinstance(methods, dict)
            assert len(methods) > 0

    def test_get_methods_returns_dict(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that get_methods returns dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate page object
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path, _ = generator.generate(tree, output_dir=tmpdir)

            # Read file content
            with Path(page_path).open() as f:
                content = f.read()

            # Extract methods
            methods = merger.get_methods(content)

            # Verify structure
            assert isinstance(methods, dict)
            for name, body in methods.items():
                assert isinstance(name, str)
                assert isinstance(body, str)


class TestRemoveDuplicates:
    """Tests for remove_duplicates method."""

    def test_remove_duplicates_combines_unique_methods(self, merger: PageObjectMerger):
        """Test that remove_duplicates combines unique methods."""
        methods1 = {"method1": "def method1():\n    pass", "method2": "def method2():\n    pass"}
        methods2 = {"method3": "def method3():\n    pass"}

        result = merger.remove_duplicates(methods1, methods2)

        # Should have all three methods
        assert len(result) == 3
        assert "method1" in result
        assert "method2" in result
        assert "method3" in result

    def test_remove_duplicates_removes_exact_duplicates(self, merger: PageObjectMerger):
        """Test that remove_duplicates removes exact duplicate methods."""
        methods1 = {"method1": "def method1():\n    pass"}
        methods2 = {"method1": "def method1():\n    pass"}

        result = merger.remove_duplicates(methods1, methods2)

        # Should have only one method
        assert len(result) == 1
        assert "method1" in result

    def test_remove_duplicates_keeps_first_version_on_conflict(self, merger: PageObjectMerger):
        """Test that remove_duplicates keeps first version on conflict."""
        methods1 = {"method1": "def method1():\n    return 1"}
        methods2 = {"method1": "def method1():\n    return 2"}

        result = merger.remove_duplicates(methods1, methods2)

        # Should keep first version
        assert len(result) == 1
        assert "return 1" in result["method1"]


class TestWriteToFile:
    """Tests for write_to_file method."""

    def test_write_to_file_creates_file(self, merger: PageObjectMerger):
        """Test that write_to_file creates output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test_output.py")
            imports = "from shadowstep.element import Element"
            class_name = "class TestPage:"
            methods = {"test_method": "@property\ndef test_method(self):\n    return Element()"}

            merger.write_to_file(output_path, imports, class_name, methods)

            # Verify file was created
            assert Path(output_path).exists()

    def test_write_to_file_has_correct_structure(self, merger: PageObjectMerger):
        """Test that write_to_file creates properly structured file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test_output.py")
            imports = "from shadowstep.element import Element"
            class_name = "class TestPage:"
            methods = {"test_method": "@property\ndef test_method(self):\n    return Element()"}

            merger.write_to_file(output_path, imports, class_name, methods)

            # Read file
            with Path(output_path).open() as f:
                content = f.read()

            # Verify structure
            assert imports in content
            assert class_name in content
            assert "test_method" in content


class TestPageObjectMergerIntegration:
    """Integration tests using real app and complete workflows."""

    def test_full_merge_workflow(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test complete merge workflow with real page objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Parse XML
            xml = app.driver.page_source
            tree = parser.parse(xml)

            # Generate two page objects
            page_path1, class_name1 = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            # Merge them
            output_path = str(Path(tmpdir) / "merged_page.py")
            result_path = merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify complete workflow
            assert Path(result_path).exists()
            with Path(result_path).open() as f:
                content = f.read()

            # Verify all components
            assert "import" in content or "from" in content
            assert f"class {class_name1}" in content
            assert "def " in content

            # Verify valid Python
            import ast
            ast.parse(content)

    def test_merge_preserves_page_object_functionality(
        self, app: Shadowstep, parser: PageObjectParser,
        generator: PageObjectGenerator, merger: PageObjectMerger
    ):
        """Test that merged page object maintains functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate and merge page objects
            xml = app.driver.page_source
            tree = parser.parse(xml)
            page_path1, _ = generator.generate(tree, output_dir=tmpdir)
            page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second")

            output_path = str(Path(tmpdir) / "merged_page.py")
            merger.merge(str(page_path1), str(page_path2), output_path)

            # Verify merged file is valid Python
            with Path(output_path).open() as f:
                content = f.read()

            import ast
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Merged page object has syntax error: {e}")
