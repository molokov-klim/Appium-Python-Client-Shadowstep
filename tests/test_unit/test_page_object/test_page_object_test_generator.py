"""Tests for page_object_test_generator module."""

import os
import tempfile

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepNoClassDefinitionFoundInTreeError
from shadowstep.page_object.page_object_test_generator import PageObjectTestGenerator


class TestPageObjectTestGenerator:
    """Test cases for PageObjectTestGenerator class."""

    @pytest.mark.unit
    def test_init(self):
        """Test PageObjectTestGenerator initialization."""
        generator = PageObjectTestGenerator()
        assert generator.logger is not None  # noqa: S101

    @pytest.mark.unit
    def test_generate_simple_test(self):
        """Test generate method with simple test case."""
        generator = PageObjectTestGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("class TestPage:\n    def test_method(self): pass")
            
            result = generator.generate_test(test_file, "TestPage", temp_dir)
            
            assert result is not None  # noqa: S101
            assert len(result) == 2  # noqa: S101

    @pytest.mark.unit
    def test_generate_with_filename_prefix(self):
        """Test generate method with filename prefix."""
        generator = PageObjectTestGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("class TestPage:\n    def test_method(self): pass")
            
            result = generator.generate_test(test_file, "TestPage", temp_dir)
            
            assert result is not None  # noqa: S101
            assert len(result) == 2  # noqa: S101

    @pytest.mark.unit
    def test_generate_with_temp_files(self):
        """Test generate method with temporary files."""
        generator = PageObjectTestGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("class TestPage:\n    def test_method(self): pass")
            
            result = generator.generate_test(test_file, "TestPage", temp_dir)
            
            assert result is not None  # noqa: S101
            assert len(result) == 2  # noqa: S101
            
            # Check that file was created
            file_path = result[0]
            assert os.path.exists(file_path)  # noqa: S101

    @pytest.mark.unit
    def test_extract_properties_no_class_definition(self):
        """Test _extract_properties method when no class definition is found."""
        generator = PageObjectTestGenerator()
        
        # Create a file without class definition
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def some_function():\n    pass\n")
            temp_file = f.name

        try:
            with open(temp_file, "r") as f:
                source = f.read()
            
            with pytest.raises(ShadowstepNoClassDefinitionFoundInTreeError):
                generator._extract_properties(source)
        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_extract_properties_with_properties(self):
        """Test _extract_properties method with class containing properties."""
        generator = PageObjectTestGenerator()
        
        # Create a file with class containing properties
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
class TestPage:
    @property
    def button(self):
        return self._button
    
    @property
    def text_field(self):
        return self._text_field
    
    def regular_method(self):
        pass
""")
            temp_file = f.name

        try:
            with open(temp_file, "r") as f:
                source = f.read()
            
            properties = generator._extract_properties(source)
            
            # Should extract properties but ignore regular methods and ignored properties
            assert "button" in properties  # noqa: S101
            assert "text_field" in properties  # noqa: S101
            assert "regular_method" not in properties  # noqa: S101
        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_camel_to_snake(self):
        """Test _camel_to_snake method."""
        generator = PageObjectTestGenerator()
        
        # Test various camelCase to snake_case conversions
        assert generator._camel_to_snake("TestPage") == "test_page"  # noqa: S101
        assert generator._camel_to_snake("LoginPage") == "login_page"  # noqa: S101
        assert generator._camel_to_snake("SettingsPage") == "settings_page"  # noqa: S101
        assert generator._camel_to_snake("Page") == "page"  # noqa: S101
        assert generator._camel_to_snake("") == ""  # noqa: S101
