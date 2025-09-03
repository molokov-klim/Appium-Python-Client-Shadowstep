"""Tests for page_object_merger module."""

import os
import tempfile
from unittest.mock import patch

import pytest

from shadowstep.page_object.page_object_merger import PageObjectMerger


class TestPageObjectMerger:
    """Test cases for PageObjectMerger class."""

    def test_init(self):
        """Test PageObjectMerger initialization."""
        merger = PageObjectMerger()
        assert merger.logger is not None  # noqa: S101

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
            
            with patch("builtins.open", side_effect=OSError("File not found")), \
                 pytest.raises(OSError, match="File not found"):
                merger.merge(file1_path, file2_path, output_path)

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
