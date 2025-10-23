# ruff: noqa
# pyright: ignore
"""Smoke integration tests for shadowstep.page_object modules.

This module contains minimal smoke tests that verify PageObject functionality
works with real Appium/Android device. Detailed logic testing is in unit tests.

Requirements:
- Shadowstep instance connected to Android device (app fixture)
- Real Android Settings app
"""

import importlib.util
import shutil
import time
from pathlib import Path

import pytest

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.shadowstep import Shadowstep


@pytest.fixture
def cleanup_generated_files():
    """Fixture to cleanup generated page object files after tests."""
    yield
    # Cleanup output directories
    for folder in ("test_pages",):
        path = Path(folder)
        if path.exists() and path.is_dir():
            shutil.rmtree(path)


@pytest.fixture
def temp_output_dir(cleanup_generated_files):
    """Fixture to create and cleanup temporary output directory."""
    output_dir = Path("test_pages")
    output_dir.mkdir(exist_ok=True)
    yield str(output_dir)


def test_page_object_generation_from_real_device(
    app: Shadowstep, 
    temp_output_dir: str, 
    android_settings_open_close: None
):
    """Smoke test: verify page object generation works with real device."""
    # Arrange
    time.sleep(2)
    parser = PageObjectParser()
    generator = PageObjectGenerator()
    
    # Act - Get real page source and generate page object
    page_source = app.driver.page_source
    ui_tree = parser.parse(page_source)
    output_path, class_name = generator.generate(
        ui_element_tree=ui_tree, output_dir=temp_output_dir
    )
    
    # Assert - File created and can be imported
    assert output_path.exists()
    assert output_path.is_file()
    assert output_path.suffix == ".py"
    assert class_name.startswith("Page")
    
    # Verify generated file is valid Python
    spec = importlib.util.spec_from_file_location("test_module", output_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Verify class exists and has required attributes
    page_class = getattr(module, class_name)
    page_instance = page_class()
    assert page_instance is not None
    assert hasattr(page_instance, "title")
