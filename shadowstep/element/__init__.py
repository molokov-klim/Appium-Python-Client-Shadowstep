# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""Element package for Shadowstep framework.

This package provides comprehensive element interaction capabilities for mobile UI automation.
It includes classes for element actions, properties, gestures, coordinates, DOM navigation,
screenshots, waiting mechanisms, and assertion helpers.

Main Components:
- Element: Main element class that combines all functionality
- ElementActions: Methods for interacting with elements (click, send_keys, etc.)
- ElementProperties: Property access and state checking methods
- ElementGestures: Touch gestures and mobile-specific interactions
- ElementCoordinates: Coordinate and positioning utilities
- ElementDOM: DOM navigation and element finding methods
- ElementScreenshots: Screenshot capture functionality
- ElementWaiting: Wait conditions and timing utilities
- ElementUtilities: Helper methods and utilities
- Should: DSL for element assertions

Example:
    from shadowstep.element import Element
    from shadowstep.shadowstep import Shadowstep

    # Create element instance
    element = Element(
        locator=("id", "com.example.button"),
        shadowstep=shadowstep_instance
    )

    # Perform actions
    element.click()
    element.send_keys("Hello World")

    # Check properties
    assert element.is_visible()
    assert element.text == "Hello World"

    # Use assertion DSL
    element.should.be.visible()
    element.should.have.text("Hello World")

"""

from __future__ import annotations

# Condition functions for waiting
from . import conditions

# Core element functionality classes
from .actions import ElementActions
from .base import ElementBase
from .coordinates import ElementCoordinates
from .dom import ElementDOM

# Main Element class
from .element import Element
from .gestures import ElementGestures
from .properties import ElementProperties
from .screenshots import ElementScreenshots

# Assertion DSL
from .should import Should
from .utilities import ElementUtilities
from .waiting import ElementWaiting

# Re-export main classes for convenience
__all__ = [
    # Main element class
    "Element",

    # Core functionality classes
    "ElementActions",
    "ElementBase",
    "ElementCoordinates",
    "ElementDOM",
    "ElementGestures",
    "ElementProperties",
    "ElementScreenshots",
    "ElementUtilities",
    "ElementWaiting",

    # Assertion DSL
    "Should",

    # Condition functions
    "conditions",
]
