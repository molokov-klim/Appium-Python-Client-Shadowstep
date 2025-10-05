# ruff: noqa
# pyright: ignore
"""Integration tests for the navigator module.

This module contains integration tests for the PageNavigator and PageGraph classes,
testing real navigation scenarios with actual Android pages.
"""

import pytest
from shadowstep.navigator.navigator import PageNavigator, PageGraph
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepPageCannotBeNoneError,
    ShadowstepFromPageCannotBeNoneError,
    ShadowstepToPageCannotBeNoneError,
    ShadowstepTimeoutMustBeNonNegativeError,
    ShadowstepPathCannotBeEmptyError,
    ShadowstepPathMustContainAtLeastTwoPagesError,
    ShadowstepNavigationFailedError,
)


class TestPageNavigator:
    """Integration tests for PageNavigator class with real Android pages."""
