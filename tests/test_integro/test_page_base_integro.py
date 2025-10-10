# ruff: noqa
# pyright: ignore
"""
Integration tests for page_base.py module.

uv run pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_integro/test_page_base.py
"""

import sys
from pathlib import Path

import pytest

# Add test_integro directory to path for importing pages
test_integro_dir = Path(__file__).parent
if str(test_integro_dir) not in sys.path:
    sys.path.insert(0, str(test_integro_dir))

from shadowstep.page_base import PageBaseShadowstep
from shadowstep.shadowstep import Shadowstep



class TestPageBaseShadowstep:
    """Integration tests for PageBaseShadowstep class."""

    def test_singleton_pattern_returns_same_instance(self, app: Shadowstep):
        """Test that PageBaseShadowstep implements singleton pattern correctly.

        Steps:
        1. Get instance of a page class.
        2. Get instance again.
        3. Verify both are the same instance.
        """
        # Import a real page class
        from _pages.page_settings import PageSettings

        # Get first instance
        instance1 = PageSettings()

        # Get second instance
        instance2 = PageSettings()

        # Verify singleton pattern
        assert instance1 is instance2, "Both instances should be the same (singleton)"

    def test_get_instance_class_method(self, app: Shadowstep):
        """Test get_instance class method returns singleton instance.

        Steps:
        1. Call get_instance() class method.
        2. Create instance using constructor.
        3. Verify both are the same instance.
        """
        from _pages.page_settings import PageSettings

        # Get instance using class method
        instance1 = PageSettings.get_instance()

        # Get instance using constructor
        instance2 = PageSettings()

        # Verify both are same instance
        assert instance1 is instance2, "get_instance() should return singleton instance"

    def test_clear_instance_removes_stored_instance(self, app: Shadowstep):
        """Test clear_instance removes the stored singleton instance.

        Steps:
        1. Create page instance.
        2. Store reference.
        3. Call clear_instance().
        4. Create new instance.
        5. Verify new instance is different from original.
        """
        from _pages.page_settings import PageSettings

        # Create first instance
        instance1 = PageSettings()
        id1 = id(instance1)

        # Clear instance
        PageSettings.clear_instance()

        # Create new instance
        instance2 = PageSettings()
        id2 = id(instance2)

        # Verify new instance was created
        assert id1 != id2, "After clear_instance, new instance should be created"

    def test_shadowstep_property_is_set(self, app: Shadowstep):
        """Test that shadowstep property is set to Shadowstep instance.

        Steps:
        1. Create page instance.
        2. Verify shadowstep property is set.
        3. Verify it's a Shadowstep instance.
        """
        from _pages.page_settings import PageSettings

        # Create instance
        page = PageSettings()

        # Verify shadowstep property
        assert hasattr(page, "shadowstep"), "Page should have shadowstep property"
        assert isinstance(page.shadowstep, Shadowstep), "shadowstep should be Shadowstep instance"
        assert page.shadowstep is app, "shadowstep should be the same as app fixture"

    def test_edges_property_returns_dict(self, app: Shadowstep):
        """Test that edges property returns a dictionary.

        Steps:
        1. Create page instance.
        2. Access edges property.
        3. Verify it returns a dictionary.
        """
        from _pages.page_settings import PageSettings

        # Create instance
        page = PageSettings()

        # Get edges
        edges = page.edges

        # Verify edges is a dictionary
        assert isinstance(edges, dict), "edges should return a dictionary"

    def test_edges_property_contains_callable_values(self, app: Shadowstep):
        """Test that edges property dictionary contains callable values.

        Steps:
        1. Create page instance.
        2. Access edges property.
        3. Verify all values are callable.
        """
        from _pages.page_settings import PageSettings

        # Create instance
        page = PageSettings()

        # Get edges
        edges = page.edges

        # Verify all values are callable
        for page_name, navigation_func in edges.items():
            assert callable(navigation_func), f"Edge '{page_name}' should be callable"

    def test_multiple_page_classes_have_independent_singletons(self, app: Shadowstep):
        """Test that different page classes have independent singleton instances.

        Steps:
        1. Create instance of first page class.
        2. Create instance of second page class.
        3. Verify they are different instances.
        4. Verify each maintains singleton behavior.
        """
        from _pages.page_settings import PageSettings
        from _pages.page_about_phone.page_about_phone import PageAboutPhone

        # Create instances of different page classes
        settings_page1 = PageSettings()
        about_page1 = PageAboutPhone()

        # Verify they are different instances
        assert settings_page1 is not about_page1, "Different page classes should be different instances"

        # Verify each maintains singleton
        settings_page2 = PageSettings()
        about_page2 = PageAboutPhone()

        assert settings_page1 is settings_page2, "Settings page should maintain singleton"
        assert about_page1 is about_page2, "About page should maintain singleton"

    def test_instance_persists_across_multiple_calls(self, app: Shadowstep):
        """Test that page instance persists across multiple constructor calls.

        Steps:
        1. Create instance.
        2. Call constructor multiple times.
        3. Verify all return same instance.
        """
        from _pages.page_settings import PageSettings

        # Create multiple instances
        instances = [PageSettings() for _ in range(5)]

        # Verify all are the same
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance, "All instances should be the same"

    def test_clear_instance_does_not_affect_other_pages(self, app: Shadowstep):
        """Test that clear_instance only affects the specific page class.

        Steps:
        1. Create instances of two different page classes.
        2. Clear one page's instance.
        3. Verify only that page's instance is cleared.
        """
        from _pages.page_settings import PageSettings
        from _pages.page_about_phone.page_about_phone import PageAboutPhone

        # Create instances
        settings_page = PageSettings()
        about_page1 = PageAboutPhone()
        about_id1 = id(about_page1)

        # Clear settings instance
        PageSettings.clear_instance()

        # Create new settings instance
        new_settings = PageSettings()

        # Verify settings is new
        assert new_settings is not settings_page, "Settings should be new instance"

        # Verify about page is still the same
        about_page2 = PageAboutPhone()
        about_id2 = id(about_page2)
        assert about_id1 == about_id2, "About page should still be same instance"

    def test_page_has_access_to_shadowstep_methods(self, app: Shadowstep):
        """Test that page instance can access Shadowstep methods through shadowstep property.

        Steps:
        1. Create page instance.
        2. Access Shadowstep methods through shadowstep property.
        3. Verify methods are accessible and functional.
        """
        from _pages.page_settings import PageSettings

        # Create instance
        page = PageSettings()

        # Verify access to Shadowstep methods
        assert hasattr(page.shadowstep, "get_element"), "Should have access to get_element"
        assert hasattr(page.shadowstep, "get_page"), "Should have access to get_page"
        assert hasattr(page.shadowstep, "driver"), "Should have access to driver"
        assert callable(page.shadowstep.get_element), "get_element should be callable"

    def test_get_instance_returns_correct_type(self, app: Shadowstep):
        """Test that get_instance returns instance of correct page class.

        Steps:
        1. Call get_instance on a page class.
        2. Verify returned instance is of that class.
        """
        from _pages.page_settings import PageSettings

        # Get instance
        instance = PageSettings.get_instance()

        # Verify type
        assert isinstance(instance, PageSettings), "get_instance should return PageSettings instance"
        assert isinstance(instance, PageBaseShadowstep), "Should be instance of PageBaseShadowstep"

    def test_instance_storage_in_class_variable(self, app: Shadowstep):
        """Test that instances are stored in _instances class variable.

        Steps:
        1. Create page instance.
        2. Check _instances class variable.
        3. Verify instance is stored there.
        """
        from _pages.page_settings import PageSettings

        # Clear first to ensure clean state
        PageSettings.clear_instance()

        # Create instance
        instance = PageSettings()

        # Verify storage in _instances
        assert PageSettings in PageBaseShadowstep._instances, "Page class should be in _instances"
        assert PageBaseShadowstep._instances[PageSettings] is instance, "Stored instance should match created instance"

    def test_shadowstep_instance_is_singleton(self, app: Shadowstep):
        """Test that all pages share the same Shadowstep instance.

        Steps:
        1. Create multiple page instances.
        2. Verify all have the same shadowstep instance.
        """
        from _pages.page_settings import PageSettings
        from _pages.page_about_phone.page_about_phone import PageAboutPhone

        # Create page instances
        settings_page = PageSettings()
        about_page = PageAboutPhone()

        # Verify both use same Shadowstep instance
        assert settings_page.shadowstep is about_page.shadowstep, "All pages should share same Shadowstep instance"
        assert settings_page.shadowstep is app, "Pages should use app Shadowstep instance"

    def test_clear_instance_with_no_existing_instance(self, app: Shadowstep):
        """Test that clear_instance works even when no instance exists.

        Steps:
        1. Ensure no instance exists.
        2. Call clear_instance.
        3. Verify no errors occur.
        """
        from _pages.page_settings import PageSettings

        # Clear instance
        PageSettings.clear_instance()

        # Clear again (should not raise error)
        PageSettings.clear_instance()

        # Create new instance (should work)
        instance = PageSettings()
        assert instance is not None, "Should be able to create instance after multiple clears"

    def test_edges_property_keys_are_strings(self, app: Shadowstep):
        """Test that edges property dictionary has string keys.

        Steps:
        1. Create page instance.
        2. Access edges property.
        3. Verify all keys are strings.
        """
        from _pages.page_settings import PageSettings

        # Create instance
        page = PageSettings()

        # Get edges
        edges = page.edges

        # Verify all keys are strings (page class names)
        for page_name in edges.keys():
            assert isinstance(page_name, str), f"Edge key '{page_name}' should be a string"

    def test_page_instance_creation_uses_shadowstep_singleton(self, app: Shadowstep):
        """Test that page creation uses Shadowstep.get_instance().

        Steps:
        1. Create page instance.
        2. Verify it uses the Shadowstep singleton.
        3. Verify it's the same as app fixture.
        """
        from _pages.page_settings import PageSettings

        # Create page
        page = PageSettings()

        # Verify Shadowstep instance
        shadowstep_singleton = Shadowstep.get_instance()
        assert page.shadowstep is shadowstep_singleton, "Should use Shadowstep singleton"
        assert page.shadowstep is app, "Should use app fixture Shadowstep instance"

    def test_multiple_clear_and_recreate_cycles(self, app: Shadowstep):
        """Test multiple cycles of clear and recreate instances.

        Steps:
        1. Create, clear, and recreate instance multiple times.
        2. Verify each recreation creates new instance.
        3. Verify singleton behavior within each cycle.
        """
        from _pages.page_settings import PageSettings

        previous_id = None

        for cycle in range(3):
            # Create instance
            instance1 = PageSettings()
            current_id = id(instance1)

            # Verify singleton within cycle
            instance2 = PageSettings()
            assert id(instance2) == current_id, f"Singleton should work in cycle {cycle}"

            # Verify different from previous cycle
            if previous_id is not None:
                assert current_id != previous_id, f"New instance should be created in cycle {cycle}"

            previous_id = current_id

            # Clear for next cycle
            PageSettings.clear_instance()

    def test_page_base_is_abstract(self, app: Shadowstep):
        """Test that PageBaseShadowstep is an abstract base class.

        Steps:
        1. Verify PageBaseShadowstep has ABC as base.
        2. Verify edges is abstract property.
        """
        from abc import ABC

        # Verify PageBaseShadowstep inherits from ABC
        assert issubclass(PageBaseShadowstep, ABC), "PageBaseShadowstep should inherit from ABC"

    def test_concrete_page_implements_edges(self, app: Shadowstep):
        """Test that concrete page classes implement edges property.

        Steps:
        1. Create concrete page instance.
        2. Verify edges property is implemented.
        3. Verify it's not None.
        """
        from _pages.page_settings import PageSettings

        # Create instance
        page = PageSettings()

        # Verify edges is implemented
        edges = page.edges
        assert edges is not None, "Concrete page should implement edges"
        assert isinstance(edges, dict), "edges should be a dictionary"
