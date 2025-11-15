# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
"""Tests for PageBaseShadowstep class."""

import pytest
from shadowstep.page_base import PageBaseShadowstep


class ConcretePageBaseShadowstep(PageBaseShadowstep):
    """Concrete implementation of PageBaseShadowstep for testing."""
    
    @property
    def edges(self):
        """Concrete implementation of abstract edges property."""
        return {}


class TestPageBaseShadowstep:
    """Test cases for PageBaseShadowstep class."""

    @pytest.mark.unit
    def test_singleton_behavior(self):
        """Test that PageBaseShadowstep implements singleton pattern correctly."""
        # Clear any existing instances
        ConcretePageBaseShadowstep.clear_instance()
        
        # Create first instance
        instance1 = ConcretePageBaseShadowstep()
        assert instance1 is not None
        
        # Create second instance - should return the same instance
        instance2 = ConcretePageBaseShadowstep()
        assert instance1 is instance2

    @pytest.mark.unit
    def test_get_instance_class_method(self):
        """Test get_instance class method returns singleton instance."""
        # Clear any existing instances
        ConcretePageBaseShadowstep.clear_instance()
        
        instance1 = ConcretePageBaseShadowstep.get_instance()
        instance2 = ConcretePageBaseShadowstep.get_instance()
        
        assert instance1 is instance2
        assert isinstance(instance1, ConcretePageBaseShadowstep)

    @pytest.mark.unit
    def test_clear_instance_class_method(self):
        """Test clear_instance class method removes stored instance."""
        # Create an instance
        instance1 = ConcretePageBaseShadowstep()
        
        # Clear the instance
        ConcretePageBaseShadowstep.clear_instance()
        
        # Create new instance - should be different from previous
        instance2 = ConcretePageBaseShadowstep()
        assert instance1 is not instance2

    @pytest.mark.unit
    def test_abstract_edges_property(self):
        """Test that edges property is abstract and must be implemented."""
        # This test verifies that PageBaseShadowstep cannot be instantiated
        # without implementing the abstract edges property
        with pytest.raises(TypeError):
            # This should fail because PageBaseShadowstep is abstract
            PageBaseShadowstep()
