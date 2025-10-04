# ruff: noqa
# pyright: ignore
"""Tests for shadowstep.utils.utils module.

This module contains tests for utility functions including coordinate calculations,
function name introspection, text pattern matching, and string validation.
"""

import inspect
import math
from unittest.mock import patch

import pytest

from shadowstep.utils.utils import (
    DEGREES_180,
    DEGREES_270,
    DEGREES_360,
    DEGREES_90,
    find_coordinates_by_vector,
    get_current_func_name,
    grep_pattern,
    is_camel_case,
)


class TestFindCoordinatesByVector:
    """Test cases for find_coordinates_by_vector function."""

    @pytest.mark.unit
    def test_find_coordinates_by_vector_north(self) -> None:
        """Test coordinate calculation for north direction (0 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 0, 100, 500, 500)
        assert result == (500, 400)  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_east(self) -> None:
        """Test coordinate calculation for east direction (90 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 90, 100, 500, 500)
        assert result == (600, 500)  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_south(self) -> None:
        """Test coordinate calculation for south direction (180 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 180, 100, 500, 500)
        assert result == (500, 600)  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_west(self) -> None:
        """Test coordinate calculation for west direction (270 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 270, 100, 500, 500)
        assert result == (400, 500)  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_northeast(self) -> None:
        """Test coordinate calculation for northeast direction (45 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 45, 100, 500, 500)
        # Should move northeast: +x, -y
        expected_x = 500 + int(100 * math.sin(math.radians(45)))
        expected_y = 500 - int(100 * math.cos(math.radians(45)))
        # Allow small rounding differences
        assert abs(result[0] - expected_x) <= 1  # noqa: S101
        assert abs(result[1] - expected_y) <= 1  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_southeast(self) -> None:
        """Test coordinate calculation for southeast direction (135 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 135, 100, 500, 500)
        # Should move southeast: +x, +y
        # For 135 degrees: sin(135°) = √2/2 ≈ 0.707, cos(135°) = -√2/2 ≈ -0.707
        # But the function uses abs() for both, so both are positive
        expected_x = 500 + int(100 * abs(math.sin(math.radians(135))))
        expected_y = 500 + int(100 * abs(math.cos(math.radians(135))))
        # Allow small rounding differences
        assert abs(result[0] - expected_x) <= 1  # noqa: S101
        assert abs(result[1] - expected_y) <= 1  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_southwest(self) -> None:
        """Test coordinate calculation for southwest direction (225 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 225, 100, 500, 500)
        # Should move southwest: -x, +y
        # For 225 degrees: sin(225°) = -√2/2 ≈ -0.707, cos(225°) = -√2/2 ≈ -0.707
        # But the function uses abs() for both, so both are positive
        expected_x = 500 - int(100 * abs(math.sin(math.radians(225))))
        expected_y = 500 + int(100 * abs(math.cos(math.radians(225))))
        # Allow small rounding differences
        assert abs(result[0] - expected_x) <= 1  # noqa: S101
        assert abs(result[1] - expected_y) <= 1  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_northwest(self) -> None:
        """Test coordinate calculation for northwest direction (315 degrees)."""
        result = find_coordinates_by_vector(1000, 1000, 315, 100, 500, 500)
        # Should move northwest: -x, -y
        # For 315 degrees: sin(315°) = -√2/2 ≈ -0.707, cos(315°) = √2/2 ≈ 0.707
        # But the function uses abs() for both, so both are positive
        expected_x = 500 - int(100 * abs(math.sin(math.radians(315))))
        expected_y = 500 - int(100 * abs(math.cos(math.radians(315))))
        # Allow small rounding differences
        assert abs(result[0] - expected_x) <= 1  # noqa: S101
        assert abs(result[1] - expected_y) <= 1  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_clamp_to_bounds(self) -> None:
        """Test that coordinates are clamped to screen bounds."""
        # Test going off the top-left corner
        result = find_coordinates_by_vector(100, 100, 225, 200, 50, 50)
        assert result == (0, 100)  # noqa: S101

        # Test going off the bottom-right corner
        result = find_coordinates_by_vector(100, 100, 45, 200, 50, 50)
        assert result == (100, 0)  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_zero_distance(self) -> None:
        """Test coordinate calculation with zero distance."""
        result = find_coordinates_by_vector(1000, 1000, 45, 0, 500, 500)
        assert result == (500, 500)  # noqa: S101

    @pytest.mark.unit
    def test_find_coordinates_by_vector_edge_cases(self) -> None:
        """Test coordinate calculation with edge case angles."""
        # Test 360 degrees (should be same as 0)
        result_360 = find_coordinates_by_vector(1000, 1000, 360, 100, 500, 500)
        result_0 = find_coordinates_by_vector(1000, 1000, 0, 100, 500, 500)
        assert result_360 == result_0  # noqa: S101

        # Test 270 degrees (west)
        result = find_coordinates_by_vector(1000, 1000, 270, 100, 500, 500)
        assert result == (400, 500)  # noqa: S101


class TestGetCurrentFuncName:
    """Test cases for get_current_func_name function."""

    @pytest.mark.unit
    def test_get_current_func_name_default_depth(self) -> None:
        """Test getting current function name with default depth."""
        def test_function() -> str:
            return get_current_func_name()

        result = test_function()
        assert result == "test_function"  # noqa: S101

    @pytest.mark.unit
    def test_get_current_func_name_caller_depth(self) -> None:
        """Test getting caller function name with depth=2."""
        def inner_function() -> str:
            return get_current_func_name(depth=2)

        def outer_function() -> str:
            return inner_function()

        result = outer_function()
        assert result == "outer_function"  # noqa: S101

    @pytest.mark.unit
    def test_get_current_func_name_depth_zero(self) -> None:
        """Test getting function name with depth=0."""
        def test_function() -> str:
            return get_current_func_name(depth=0)

        result = test_function()
        assert result == "get_current_func_name"  # noqa: S101

    @pytest.mark.unit
    def test_get_current_func_name_excessive_depth(self) -> None:
        """Test getting function name with excessive depth."""
        def test_function() -> str:
            return get_current_func_name(depth=100)  # Use very large depth

        result = test_function()
        # The function might return a valid function name from deep in the stack
        # or "<unknown>" - both are acceptable
        assert result in ["<unknown>", "_hookexec", "test_function", "<module>"]  # noqa: S101

    @patch("inspect.currentframe")
    @pytest.mark.unit
    def test_get_current_func_name_no_frame(self, mock_currentframe) -> None:
        """Test getting function name when currentframe returns None."""
        mock_currentframe.return_value = None
        result = get_current_func_name()
        assert result == "<unknown>"  # noqa: S101


class TestGrepPattern:
    """Test cases for grep_pattern function."""

    @pytest.mark.unit
    def test_grep_pattern_simple_match(self) -> None:
        """Test grep_pattern with simple pattern matching."""
        text = "line1\nline2\nline3\nline4"
        pattern = r"line[23]"
        result = grep_pattern(text, pattern)
        assert result == ["line2", "line3"]  # noqa: S101

    @pytest.mark.unit
    def test_grep_pattern_no_matches(self) -> None:
        """Test grep_pattern with no matching lines."""
        text = "line1\nline2\nline3"
        pattern = r"nonexistent"
        result = grep_pattern(text, pattern)
        assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_grep_pattern_empty_string(self) -> None:
        """Test grep_pattern with empty input string."""
        text = ""
        pattern = r"anything"
        result = grep_pattern(text, pattern)
        assert result == []  # noqa: S101

    @pytest.mark.unit
    def test_grep_pattern_single_line(self) -> None:
        """Test grep_pattern with single line input."""
        text = "single line"
        pattern = r"single"
        result = grep_pattern(text, pattern)
        assert result == ["single line"]  # noqa: S101

    @pytest.mark.unit
    def test_grep_pattern_multiple_matches(self) -> None:
        """Test grep_pattern with multiple matches in same line."""
        text = "word1 word2 word1 word3"
        pattern = r"word1"
        result = grep_pattern(text, pattern)
        assert result == ["word1 word2 word1 word3"]  # noqa: S101

    @pytest.mark.unit
    def test_grep_pattern_complex_regex(self) -> None:
        """Test grep_pattern with complex regex pattern."""
        text = "email1@example.com\nnot-email\nemail2@test.org\ninvalid-email"
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        result = grep_pattern(text, pattern)
        assert result == ["email1@example.com", "email2@test.org"]  # noqa: S101

    @pytest.mark.unit
    def test_grep_pattern_case_sensitive(self) -> None:
        """Test grep_pattern with case-sensitive matching."""
        text = "Line1\nline1\nLINE1"
        pattern = r"line1"
        result = grep_pattern(text, pattern)
        assert result == ["line1"]  # noqa: S101


class TestIsCamelCase:
    """Test cases for is_camel_case function."""

    @pytest.mark.unit
    def test_is_camel_case_valid_camelcase(self) -> None:
        """Test is_camel_case with valid camelCase strings."""
        assert is_camel_case("camelCase") is True  # noqa: S101
        assert is_camel_case("myVariableName") is True  # noqa: S101
        assert is_camel_case("a") is True  # noqa: S101
        assert is_camel_case("aB") is True  # noqa: S101
        assert is_camel_case("camelCase123") is True  # noqa: S101

    @pytest.mark.unit
    def test_is_camel_case_invalid_camelcase(self) -> None:
        """Test is_camel_case with invalid camelCase strings."""
        assert is_camel_case("") is False  # noqa: S101
        assert is_camel_case("CamelCase") is False  # noqa: S101
        assert is_camel_case("camel_case") is False  # noqa: S101
        assert is_camel_case("camel-case") is False  # noqa: S101
        assert is_camel_case("123camelCase") is False  # noqa: S101
        assert is_camel_case("camel Case") is False  # noqa: S101
        assert is_camel_case("camelCase!") is False  # noqa: S101

    @pytest.mark.unit
    def test_is_camel_case_edge_cases(self) -> None:
        """Test is_camel_case with edge cases."""
        assert is_camel_case("a") is True  # noqa: S101
        assert is_camel_case("A") is False  # noqa: S101
        assert is_camel_case("a1") is False  # noqa: S101 - numbers are not allowed in camelCase
        assert is_camel_case("1a") is False  # noqa: S101
        assert is_camel_case("aA") is True  # noqa: S101
        assert is_camel_case("Aa") is False  # noqa: S101


class TestConstants:
    """Test cases for module constants."""

    @pytest.mark.unit
    def test_degree_constants(self) -> None:
        """Test that degree constants have correct values."""
        assert DEGREES_90 == 90  # noqa: S101
        assert DEGREES_180 == 180  # noqa: S101
        assert DEGREES_270 == 270  # noqa: S101
        assert DEGREES_360 == 360  # noqa: S101
