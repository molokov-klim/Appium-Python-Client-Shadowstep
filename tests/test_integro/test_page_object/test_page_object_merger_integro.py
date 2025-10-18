"""Smoke integration tests for PageObjectMerger class.

This module contains minimal smoke tests that verify PageObjectMerger works
with real generated page objects. Detailed logic testing is in unit tests.
"""
import tempfile
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_merger import PageObjectMerger
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.shadowstep import Shadowstep


def test_merger_works_with_real_page_objects(
    app: Shadowstep,
    android_settings_open_close: None
):
    """Smoke test: verify merger works with real generated page objects."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Arrange - Generate two real page objects
        parser = PageObjectParser()
        generator = PageObjectGenerator(translator=None)
        merger = PageObjectMerger()
        
        # Get real page source
        xml = app.driver.page_source
        tree = parser.parse(xml)
        
        # Generate two page objects
        page_path1, _ = generator.generate(tree, output_dir=tmpdir)
        page_path2, _ = generator.generate(tree, output_dir=tmpdir, filename_prefix="second_")
        
        # Act - Merge them
        output_path = str(Path(tmpdir) / "merged_page.py")
        result_path = merger.merge(str(page_path1), str(page_path2), output_path)
        
        # Assert - Merge succeeded and creates valid Python
        assert result_path == output_path
        assert Path(output_path).exists()
        
        # Verify merged file is valid Python
        content = Path(output_path).read_text()
        import ast
        ast.parse(content)  # Should not raise SyntaxError
