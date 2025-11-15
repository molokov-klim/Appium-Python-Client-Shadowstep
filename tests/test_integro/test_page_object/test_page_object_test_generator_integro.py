# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Smoke integration tests for PageObjectTestGenerator class.

This module contains minimal smoke tests that verify PageObjectTestGenerator works
with real generated page objects. Detailed logic testing is in unit tests.
"""
import tempfile
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_test_generator import PageObjectTestGenerator
from shadowstep.shadowstep import Shadowstep


def test_test_generator_works_with_real_page_object(
    app: Shadowstep,
    android_settings_open_close: None
):
    """Smoke test: verify test generator works with real page object."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Arrange - Generate real page object
        parser = PageObjectParser()
        generator = PageObjectGenerator(translator=None)
        test_generator = PageObjectTestGenerator()
        
        # Get real page source and generate page object
        xml = app.driver.page_source
        tree = parser.parse(xml)
        page_path, page_class_name = generator.generate(tree, output_dir=tmpdir)
        
        # Act - Generate test from page object
        test_path, test_class_name = test_generator.generate_test(
            input_path=str(page_path),
            class_name=page_class_name,
            output_dir=tmpdir
        )
        
        # Assert - Test file created with correct structure
        assert Path(test_path).exists()
        assert test_class_name.startswith("Test")
        assert test_class_name == f"Test{page_class_name}"
        
        # Verify test has correct structure
        test_content = Path(test_path).read_text()
        assert "import pytest" in test_content
        assert f"class {test_class_name}:" in test_content
        assert "def test_" in test_content
        
        # Verify test is valid Python
        import ast
        ast.parse(test_content)  # Should not raise SyntaxError
