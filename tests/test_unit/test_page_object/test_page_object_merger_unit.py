# ruff: noqa
# pyright: ignore
"""Tests for page_object_merger module."""

import os
import tempfile
from unittest.mock import patch

import pytest

from shadowstep.page_object.page_object_merger import PageObjectMerger


class TestPageObjectMerger:
    """Test cases for PageObjectMerger class."""

    @pytest.mark.unit
    def test_init(self):
        """Test PageObjectMerger initialization."""
        merger = PageObjectMerger()
        assert merger.logger is not None  # noqa: S101

    @pytest.mark.unit
    def test_merge_success(self):
        """Test merge method with successful merge."""
        merger = PageObjectMerger()

        # Mock file contents
        file1_content = "class Page1:\n    def method1(self): pass"
        file2_content = "class Page2:\n    def method2(self): pass"

        with tempfile.TemporaryDirectory() as temp_dir:
            file1_path = os.path.join(temp_dir, "file1.py")
            file2_path = os.path.join(temp_dir, "file2.py")
            output_path = os.path.join(temp_dir, "output.py")

            with open(file1_path, "w") as f:
                f.write(file1_content)
            with open(file2_path, "w") as f:
                f.write(file2_content)

            result = merger.merge(file1_path, file2_path, output_path)

            assert result == output_path  # noqa: S101
            assert os.path.exists(output_path)  # noqa: S101

    @pytest.mark.unit
    def test_merge_file_not_found(self):
        """Test merge method when file is not found."""
        merger = PageObjectMerger()

        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = os.path.join(temp_dir, "nonexistent.py")
            file2_path = os.path.join(temp_dir, "file2.py")
            output_path = os.path.join(temp_dir, "output.py")

            with open(file2_path, "w") as f:
                f.write("class Page2:\n    def method2(self): pass")

            with pytest.raises(FileNotFoundError):
                merger.merge(nonexistent_path, file2_path, output_path)

    @pytest.mark.unit
    def test_merge_io_error(self):
        """Test merge method with IO error."""
        merger = PageObjectMerger()

        with tempfile.TemporaryDirectory() as temp_dir:
            file1_path = os.path.join(temp_dir, "file1.py")
            file2_path = os.path.join(temp_dir, "file2.py")
            output_path = os.path.join(temp_dir, "output.py")

            with open(file1_path, "w") as f:
                f.write("class Page1:\n    def method1(self): pass")
            with open(file2_path, "w") as f:
                f.write("class Page2:\n    def method2(self): pass")

            with patch("pathlib.Path.open", side_effect=OSError("File not found")), \
                    pytest.raises(OSError, match="File not found"):
                merger.merge(file1_path, file2_path, output_path)

    @pytest.mark.unit
    def test_merge_with_temp_files(self):
        """Test merge method with temporary files."""
        merger = PageObjectMerger()

        with tempfile.TemporaryDirectory() as temp_dir:
            file1_path = os.path.join(temp_dir, "file1.py")
            file2_path = os.path.join(temp_dir, "file2.py")
            output_path = os.path.join(temp_dir, "output.py")

            # Create test files
            with open(file1_path, "w") as f:
                f.write("class Page1:\n    def method1(self): pass")

            with open(file2_path, "w") as f:
                f.write("class Page2:\n    def method2(self): pass")

            result = merger.merge(file1_path, file2_path, output_path)

            assert result == output_path  # noqa: S101
            assert os.path.exists(output_path)  # noqa: S101

    @pytest.mark.unit
    def test_parse_success(self):
        """Test parse method with successful file reading."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.py")
            content = "class TestClass:\n    def test_method(self): pass"
            
            with open(file_path, "w") as f:
                f.write(content)
            
            result = merger.parse(file_path)
            assert result == content  # noqa: S101

    @pytest.mark.unit
    def test_parse_file_not_found(self):
        """Test parse method when file is not found."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = os.path.join(temp_dir, "nonexistent.py")
            
            with pytest.raises(FileNotFoundError):
                merger.parse(nonexistent_path)

    @pytest.mark.unit
    def test_parse_io_error(self):
        """Test parse method with IO error."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.py")
            
            with open(file_path, "w") as f:
                f.write("class TestClass:\n    def test_method(self): pass")
            
            with patch("pathlib.Path.open", side_effect=OSError("IO Error")):
                with pytest.raises(OSError, match="IO Error"):
                    merger.parse(file_path)

    @pytest.mark.unit
    def test_get_imports_with_imports(self):
        """Test get_imports method with import statements."""
        merger = PageObjectMerger()
        
        page_content = """import os
from pathlib import Path
# This is a comment

class TestClass:
    def test_method(self): pass"""
        
        result = merger.get_imports(page_content)
        expected = "import os\nfrom pathlib import Path"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_get_imports_with_empty_lines_and_comments(self):
        """Test get_imports method with empty lines and comments."""
        merger = PageObjectMerger()
        
        page_content = """import os
# This is a comment

from pathlib import Path

class TestClass:
    def test_method(self): pass"""
        
        result = merger.get_imports(page_content)
        expected = "import os\nfrom pathlib import Path"
        assert result == expected  # noqa: S101

    @pytest.mark.unit
    def test_get_imports_no_imports(self):
        """Test get_imports method with no import statements."""
        merger = PageObjectMerger()
        
        page_content = """class TestClass:
    def test_method(self): pass"""
        
        result = merger.get_imports(page_content)
        assert result == ""  # noqa: S101

    @pytest.mark.unit
    def test_get_class_name_success(self):
        """Test get_class_name method with successful class finding."""
        merger = PageObjectMerger()
        
        page_content = """import os

class TestClass:
    def test_method(self): pass"""
        
        result = merger.get_class_name(page_content)
        assert result == "class TestClass:"  # noqa: S101

    @pytest.mark.unit
    def test_get_class_name_not_found(self):
        """Test get_class_name method when no class is found."""
        merger = PageObjectMerger()
        
        page_content = """import os

def test_function():
    pass"""
        
        from shadowstep.exceptions.shadowstep_exceptions import ShadowstepNoClassDefinitionFoundError
        with pytest.raises(ShadowstepNoClassDefinitionFoundError):
            merger.get_class_name(page_content)

    @pytest.mark.unit
    def test_get_methods_with_def_methods(self):
        """Test get_methods method with def methods."""
        merger = PageObjectMerger()
        
        page_content = """class TestClass:

    def method1(self):
        return "test1"

    def method2(self):
        return "test2"
"""
        
        result = merger.get_methods(page_content)
        assert "method1" in result  # noqa: S101
        assert "method2" in result  # noqa: S101
        assert "def method1(self):" in result["method1"]  # noqa: S101
        assert "def method2(self):" in result["method2"]  # noqa: S101

    @pytest.mark.unit
    def test_get_methods_with_property_methods(self):
        """Test get_methods method with @property methods."""
        merger = PageObjectMerger()
        
        page_content = """class TestClass:

    @property
    def property1(self):
        return "test1"

    @property
    def property2(self):
        return "test2"
"""
        
        result = merger.get_methods(page_content)
        assert "property1" in result  # noqa: S101
        assert "property2" in result  # noqa: S101

    @pytest.mark.unit
    def test_get_methods_with_current_page_methods(self):
        """Test get_methods method with @current_page methods."""
        merger = PageObjectMerger()
        
        page_content = """class TestClass:

    @current_page
    def current_page_method(self):
        return "test1"
"""
        
        result = merger.get_methods(page_content)
        assert "current_page_method" in result  # noqa: S101

    @pytest.mark.unit
    def test_get_methods_no_methods(self):
        """Test get_methods method with no methods."""
        merger = PageObjectMerger()
        
        page_content = """class TestClass:
    pass"""
        
        result = merger.get_methods(page_content)
        assert result == {}  # noqa: S101

    @pytest.mark.unit
    def test_remove_duplicates_no_duplicates(self):
        """Test remove_duplicates method with no duplicate methods."""
        merger = PageObjectMerger()
        
        methods1 = {"method1": "def method1(self): pass"}
        methods2 = {"method2": "def method2(self): pass"}
        
        result = merger.remove_duplicates(methods1, methods2)
        assert len(result) == 2  # noqa: S101
        assert "method1" in result  # noqa: S101
        assert "method2" in result  # noqa: S101

    @pytest.mark.unit
    def test_remove_duplicates_with_duplicates(self):
        """Test remove_duplicates method with duplicate methods."""
        merger = PageObjectMerger()
        
        methods1 = {"method1": "def method1(self): pass"}
        methods2 = {"method1": "def method1(self): pass"}
        
        result = merger.remove_duplicates(methods1, methods2)
        assert len(result) == 1  # noqa: S101
        assert "method1" in result  # noqa: S101

    @pytest.mark.unit
    def test_remove_duplicates_with_conflicts(self):
        """Test remove_duplicates method with conflicting methods."""
        merger = PageObjectMerger()
        
        methods1 = {"method1": "def method1(self): return 'test1'"}
        methods2 = {"method1": "def method1(self): return 'test2'"}
        
        result = merger.remove_duplicates(methods1, methods2)
        assert len(result) == 1  # noqa: S101
        assert "method1" in result  # noqa: S101
        assert result["method1"] == "def method1(self): return 'test1'"  # noqa: S101

    @pytest.mark.unit
    def test_write_to_file_success(self):
        """Test write_to_file method with successful writing."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.py")
            imports = "import os"
            class_name = "class TestClass:"
            unique_methods = {
                "method1": "def method1(self):\n    return 'test1'",
                "method2": "def method2(self):\n    return 'test2'"
            }
            
            merger.write_to_file(output_path, imports, class_name, unique_methods)
            
            assert os.path.exists(output_path)  # noqa: S101
            with open(output_path, "r") as f:
                content = f.read()
                assert "import os" in content  # noqa: S101
                assert "class TestClass:" in content  # noqa: S101
                assert "def method1(self):" in content  # noqa: S101
                assert "def method2(self):" in content  # noqa: S101

    @pytest.mark.unit
    def test_write_to_file_with_recycler_and_is_current_page(self):
        """Test write_to_file method with recycler and is_current_page methods."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.py")
            imports = "import os"
            class_name = "class TestClass:"
            unique_methods = {
                "method1": "def method1(self):\n    return 'test1'",
                "recycler": "def recycler(self):\n    return 'recycler'",
                "is_current_page": "def is_current_page(self):\n    return True"
            }
            
            merger.write_to_file(output_path, imports, class_name, unique_methods)
            
            assert os.path.exists(output_path)  # noqa: S101
            with open(output_path, "r") as f:
                content = f.read()
                assert "def method1(self):" in content  # noqa: S101
                assert "def recycler(self):" in content  # noqa: S101
                assert "def is_current_page(self):" in content  # noqa: S101

    @pytest.mark.unit
    def test_write_to_file_with_encoding(self):
        """Test write_to_file method with custom encoding."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.py")
            imports = "import os"
            class_name = "class TestClass:"
            unique_methods = {"method1": "def method1(self):\n    return 'test1'"}
            
            merger.write_to_file(output_path, imports, class_name, unique_methods, encoding="utf-8")
            
            assert os.path.exists(output_path)  # noqa: S101

    @pytest.mark.unit
    def test_write_to_file_creates_directory(self):
        """Test write_to_file method creates parent directory."""
        merger = PageObjectMerger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "subdir", "output.py")
            imports = "import os"
            class_name = "class TestClass:"
            unique_methods = {"method1": "def method1(self):\n    return 'test1'"}
            
            merger.write_to_file(output_path, imports, class_name, unique_methods)
            
            assert os.path.exists(output_path)  # noqa: S101
            assert os.path.exists(os.path.join(temp_dir, "subdir"))  # noqa: S101
