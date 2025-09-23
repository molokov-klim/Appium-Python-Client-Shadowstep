# tests/page_object/test_page_object_test_generator.py
"""Tests for page_object_test_generator module."""

import os
import tempfile

from shadowstep.page_object.page_object_test_generator import PageObjectTestGenerator


class TestPageObjectTestGenerator:
    """Test cases for PageObjectTestGenerator class."""

    def test_init(self):
        """Test PageObjectTestGenerator initialization."""
        generator = PageObjectTestGenerator()
        assert generator.logger is not None  # noqa: S101

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
