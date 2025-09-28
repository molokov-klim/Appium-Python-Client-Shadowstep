"""Custom exceptions for the Shadowstep framework.

This module defines custom exception classes that extend standard
Selenium and Appium exceptions to provide more specific error handling
and context for the Shadowstep automation framework.
"""
from __future__ import annotations

import datetime
import traceback
from typing import TYPE_CHECKING

from selenium.common import NoSuchElementException, TimeoutException, WebDriverException

if TYPE_CHECKING:
    from collections.abc import Sequence
    from appium.webdriver.webdriver import WebDriver


class ShadowstepException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self,
            msg: str | None = None,
            screen: str | None = None,
            stacktrace: "Sequence[str]" | None = None,
    ) -> None:
        """Initialize the ShadowstepException.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.

        """
        super().__init__(msg, screen, stacktrace)


class ShadowstepElementError(ShadowstepException):
    """Raised when an element operation fails with additional context.

    This exception provides additional context about the original exception
    that caused the element operation to fail, including the traceback.
    """

    def __init__(self,
                 message: str | None = None,
                 original_exception: Exception | None = None) -> None:
        """Initialize the ShadowstepElementError.

        Args:
            message: Error message.
            original_exception: The original exception that caused this error.

        """
        super().__init__(message)
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ShadowstepNoSuchElementError(NoSuchElementException):
    """Raised when an element cannot be found with enhanced locator information.

    This exception extends the standard NoSuchElementException to provide
    additional context about the locator that was used and other debugging
    information.
    """

    def __init__(self,
                 msg: str | None = None,
                 screen: str | None = None,
                 stacktrace: list[str] | None = None,
                 locator: str | dict | None = None) -> None:
        """Initialize the ShadowstepNoSuchElementError.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.
            locator: The locator that was used to find the element.

        """
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self) -> str:
        """Return string representation of the exception with locator and context info.

        Returns:
            str: Formatted string containing locator, message, and stacktrace.

        """
        return f"ShadowstepNoSuchElementError: Locator: {self.locator} \n Message: {self.msg} \n Stacktrace: {self.stacktrace}"


class ShadowstepTimeoutException(TimeoutException):
    """Custom timeout exception with additional context."""

    def __init__(self,
                 msg: str | None = None,
                 screen: str | None = None,
                 stacktrace: list[str] | None = None,
                 locator: str | dict | None = None,
                 driver: "WebDriver" | None = None) -> None:
        """Initialize the ShadowstepTimeoutException.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.
            locator: The locator that was used to find the element.
            driver: The WebDriver instance.

        """
        super().__init__(msg, screen, stacktrace)
        self.locator = locator
        self.driver = driver
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def __str__(self) -> str:
        """Return string representation of the timeout exception with detailed context.

        Returns:
            str: Formatted string containing timestamp, message, locator, URL, and stacktrace.

        """
        return (f"ShadowstepTimeoutException\n"
                f"Timestamp: {self.timestamp}\n"
                f"Message: {self.msg}\n"
                f"Locator: {self.locator}\n"
                f"Current URL: {self.driver.current_url if self.driver else 'N/A'}\n"
                f"Stacktrace:\n{''.join(self.stacktrace) if self.stacktrace else 'N/A'}")


class ShadowstepElementException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: str | None = None, screen: str | None = None,
            stacktrace: "Sequence[str]" | None = None,
    ) -> None:
        """Initialize the ShadowstepElementException.

        Args:
            msg: Error message.
            screen: Screenshot data.
            stacktrace: Stack trace information.

        """
        super().__init__(msg, screen, stacktrace)


class ShadowstepLocatorConverterError(Exception):
    """Base exception for locator conversion errors."""



class ShadowstepInvalidUiSelectorError(Exception):
    """Raised when UiSelector string is malformed."""



class ShadowstepConversionError(ShadowstepLocatorConverterError):
    """Raised when conversion between formats fails."""


class ShadowstepDictConversionError(ShadowstepConversionError):
    """Raised when dictionary conversion fails."""

    def __init__(self, operation: str, details: str = "") -> None:
        """Initialize with operation and optional details.
        
        Args:
            operation: The operation that failed
            details: Additional error details

        """
        msg = f"Failed to convert dict to {operation}"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class ShadowstepValidationError(ValueError):
    """Raised when validation fails."""

    def __init__(self, message: str) -> None:
        """Initialize with validation message.
        
        Args:
            message: The validation error message

        """
        super().__init__(message)


class ShadowstepSelectorTypeError(ShadowstepValidationError):
    """Raised when selector is not a dictionary."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Selector must be a dictionary")


class ShadowstepEmptySelectorError(ShadowstepValidationError):
    """Raised when selector dictionary is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Selector dictionary cannot be empty")


class ShadowstepConflictingTextAttributesError(ShadowstepValidationError):
    """Raised when conflicting text attributes are found."""

    def __init__(self, attributes: list[str]) -> None:
        """Initialize with conflicting attributes.
        
        Args:
            attributes: List of conflicting attributes

        """
        super().__init__(f"Conflicting text attributes: {attributes}")


class ShadowstepConflictingDescriptionAttributesError(ShadowstepValidationError):
    """Raised when conflicting description attributes are found."""

    def __init__(self, attributes: list[str]) -> None:
        """Initialize with conflicting attributes.
        
        Args:
            attributes: List of conflicting attributes

        """
        super().__init__(f"Conflicting description attributes: {attributes}")


class ShadowstepHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute has wrong type."""

    def __init__(self, key: str) -> None:
        """Initialize with attribute key.
        
        Args:
            key: The hierarchical attribute key

        """
        super().__init__(f"Hierarchical attribute {key} must have dict value")


class ShadowstepUnsupportedSelectorFormatError(ShadowstepConversionError):
    """Raised when selector format is not supported."""

    def __init__(self, selector: str) -> None:
        """Initialize with unsupported selector.
        
        Args:
            selector: The unsupported selector

        """
        super().__init__(f"Unsupported selector format: {selector}")


class ShadowstepConversionFailedError(ShadowstepConversionError):
    """Raised when conversion fails with context."""

    def __init__(self, function_name: str, selector: str, details: str) -> None:
        """Initialize with conversion context.
        
        Args:
            function_name: Name of the function that failed
            selector: The selector being converted
            details: Additional error details

        """
        super().__init__(f"{function_name} failed to convert selector: {selector}. {details}")


class ShadowstepUnsupportedTupleFormatError(ShadowstepValidationError):
    """Raised when tuple format is not supported."""

    def __init__(self, format_type: str) -> None:
        """Initialize with unsupported format type.
        
        Args:
            format_type: The unsupported format type

        """
        super().__init__(f"Unsupported tuple format: {format_type}")


class ShadowstepEmptyXPathError(ShadowstepValidationError):
    """Raised when XPath string is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("XPath string cannot be empty")


class ShadowstepEmptySelectorStringError(ShadowstepValidationError):
    """Raised when selector string is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Selector string cannot be empty")


class ShadowstepUnsupportedSelectorTypeError(ShadowstepValidationError):
    """Raised when selector type is not supported."""

    def __init__(self, selector_type: str) -> None:
        """Initialize with unsupported selector type.
        
        Args:
            selector_type: The unsupported selector type

        """
        super().__init__(f"Unsupported selector type: {selector_type}")


class ShadowstepUiSelectorConversionError(ShadowstepConversionError):
    """Raised when UiSelector conversion fails."""

    def __init__(self, operation: str, details: str = "") -> None:
        """Initialize with operation and optional details.
        
        Args:
            operation: The operation that failed
            details: Additional error details

        """
        msg = f"Failed to convert UiSelector to {operation}"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class ShadowstepInvalidUiSelectorStringError(ShadowstepInvalidUiSelectorError):
    """Raised when UiSelector string is invalid."""

    def __init__(self, details: str = "") -> None:
        """Initialize with error details.
        
        Args:
            details: Additional error details

        """
        msg = "Invalid UiSelector string"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class ShadowstepSelectorToXPathError(ShadowstepConversionError):
    """Raised when selector to XPath conversion fails."""

    def __init__(self, details: str = "") -> None:
        """Initialize with error details.
        
        Args:
            details: Additional error details

        """
        msg = "Failed to convert selector to XPath"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class ShadowstepMethodRequiresArgumentError(ShadowstepValidationError):
    """Raised when method requires an argument but none provided."""

    def __init__(self, method_name: str) -> None:
        """Initialize with method name.
        
        Args:
            method_name: The method that requires an argument

        """
        super().__init__(f"Method '{method_name}' requires an argument")


class ShadowstepConflictingMethodsError(ShadowstepValidationError):
    """Raised when conflicting methods are found."""

    def __init__(self, existing: str, new_method: str, group_name: str) -> None:
        """Initialize with conflicting methods.
        
        Args:
            existing: The existing method
            new_method: The new method
            group_name: The group name

        """
        super().__init__(
            f"Conflicting methods: '{existing}' and '{new_method}' "
            f"belong to the same group '{group_name}'. "
            f"Only one method per group is allowed.",
        )


class ShadowstepUnsupportedNestedSelectorError(ShadowstepConversionError):
    """Raised when nested selector type is not supported."""

    def __init__(self, selector_type: str) -> None:
        """Initialize with unsupported selector type.
        
        Args:
            selector_type: The unsupported selector type

        """
        super().__init__(f"Unsupported nested selector type: {selector_type}")


class ShadowstepUiSelectorMethodArgumentError(ShadowstepConversionError):
    """Raised when UiSelector method has wrong number of arguments."""

    def __init__(self, arg_count: int) -> None:
        """Initialize with argument count.
        
        Args:
            arg_count: The number of arguments provided

        """
        super().__init__(f"UiSelector methods typically take 0-1 arguments, got {arg_count}")


class ShadowstepLexerError(Exception):
    """Raised when lexical analysis encounters an error."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepUnterminatedStringError(ShadowstepLexerError):
    """Raised when string is not properly terminated."""

    def __init__(self, position: int) -> None:
        """Initialize with position.
        
        Args:
            position: The position where the string started

        """
        super().__init__(f"Unterminated string at {position}")


class ShadowstepBadEscapeError(ShadowstepLexerError):
    """Raised when escape sequence is invalid."""

    def __init__(self, position: int) -> None:
        """Initialize with position.
        
        Args:
            position: The position of the bad escape

        """
        super().__init__(f"Bad escape at {position}")


class ShadowstepUnexpectedCharError(ShadowstepLexerError):
    """Raised when unexpected character is encountered."""

    def __init__(self, char: str, position: int) -> None:
        """Initialize with character and position.
        
        Args:
            char: The unexpected character
            position: The position of the character

        """
        super().__init__(f"Unexpected char {char!r} at {position}")


class ShadowstepParserError(Exception):
    """Raised when parsing encounters an error."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepExpectedTokenError(ShadowstepParserError):
    """Raised when expected token is not found."""

    def __init__(self, expected: str, got: str, position: int) -> None:
        """Initialize with expected and got tokens.
        
        Args:
            expected: The expected token type
            got: The actual token type
            position: The position of the token

        """
        super().__init__(f"Expected {expected}, got {got} at {position}")


class ShadowstepUnexpectedTokenError(ShadowstepParserError):
    """Raised when unexpected token is encountered."""

    def __init__(self, token_type: str, position: int) -> None:
        """Initialize with token type and position.
        
        Args:
            token_type: The unexpected token type
            position: The position of the token

        """
        super().__init__(f"Unexpected token in arg: {token_type} at {position}")


class ShadowstepXPathConversionError(ShadowstepConversionError):
    """Raised when XPath conversion fails."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepBooleanLiteralError(ShadowstepXPathConversionError):
    """Raised when boolean literal is invalid."""

    def __init__(self, value: str | float | bool) -> None:  # noqa: FBT001
        """Initialize with invalid value.
        
        Args:
            value: The invalid value

        """
        super().__init__(f"Expected boolean literal, got: {value!r}")


class ShadowstepNumericLiteralError(ShadowstepXPathConversionError):
    """Raised when numeric literal is invalid."""

    def __init__(self, value: str | float | bool) -> None:  # noqa: FBT001
        """Initialize with invalid value.
        
        Args:
            value: The invalid value

        """
        super().__init__(f"Expected numeric literal, got: {value!r}")


class ShadowstepLogicalOperatorsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when logical operators are not supported."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Logical operators (and/or) are not supported")


class ShadowstepInvalidXPathError(ShadowstepXPathConversionError):
    """Raised when XPath is invalid."""

    def __init__(self, details: str = "") -> None:
        """Initialize with error details.
        
        Args:
            details: Additional error details

        """
        msg = "Invalid XPath"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class ShadowstepUnsupportedAbbreviatedStepError(ShadowstepXPathConversionError):
    """Raised when abbreviated step is not supported."""

    def __init__(self, step: str) -> None:
        """Initialize with unsupported step.
        
        Args:
            step: The unsupported step

        """
        super().__init__(f"Unsupported abbreviated step in UiSelector: {step!r}")


class ShadowstepUnsupportedASTNodeError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported."""

    def __init__(self, node: object) -> None:
        """Initialize with unsupported node.
        
        Args:
            node: The unsupported node

        """
        super().__init__(f"Unsupported AST node in UiSelector: {node!r}")


class ShadowstepUnsupportedASTNodeBuildError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported in build."""

    def __init__(self, node: object) -> None:
        """Initialize with unsupported node.
        
        Args:
            node: The unsupported node

        """
        super().__init__(f"Unsupported AST node in build: {node!r}")


class ShadowstepContainsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when contains() is not supported for attribute."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The attribute name

        """
        super().__init__(f"contains() is not supported for @{attr}")


class ShadowstepStartsWithNotSupportedError(ShadowstepXPathConversionError):
    """Raised when starts-with() is not supported for attribute."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The attribute name

        """
        super().__init__(f"starts-with() is not supported for @{attr}")


class ShadowstepMatchesNotSupportedError(ShadowstepXPathConversionError):
    """Raised when matches() is not supported for attribute."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The attribute name

        """
        super().__init__(f"matches() is not supported for @{attr}")


class ShadowstepUnsupportedFunctionError(ShadowstepXPathConversionError):
    """Raised when function is not supported."""

    def __init__(self, func_name: str) -> None:
        """Initialize with function name.
        
        Args:
            func_name: The function name

        """
        super().__init__(f"Unsupported function: {func_name}")


class ShadowstepUnsupportedComparisonOperatorError(ShadowstepXPathConversionError):
    """Raised when comparison operator is not supported."""

    def __init__(self, operator: str) -> None:
        """Initialize with operator.
        
        Args:
            operator: The operator

        """
        super().__init__(f"Unsupported comparison operator: {operator}")


class ShadowstepUnsupportedAttributeError(ShadowstepXPathConversionError):
    """Raised when attribute is not supported."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The attribute name

        """
        super().__init__(f"Unsupported attribute: @{attr}")


class ShadowstepAttributePresenceNotSupportedError(ShadowstepXPathConversionError):
    """Raised when attribute presence predicate is not supported."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The attribute name

        """
        super().__init__(f"Attribute presence predicate not supported for @{attr}")


class ShadowstepUnsupportedPredicateError(ShadowstepXPathConversionError):
    """Raised when predicate is not supported."""

    def __init__(self, predicate: object) -> None:
        """Initialize with predicate.
        
        Args:
            predicate: The predicate

        """
        super().__init__(f"Unsupported predicate: {predicate!r}")


class ShadowstepUnsupportedAttributeExpressionError(ShadowstepXPathConversionError):
    """Raised when attribute expression is not supported."""

    def __init__(self, node: object) -> None:
        """Initialize with node.
        
        Args:
            node: The node

        """
        super().__init__(f"Unsupported attribute expression: {node!r}")


class ShadowstepUnsupportedLiteralError(ShadowstepXPathConversionError):
    """Raised when literal is not supported."""

    def __init__(self, node: object) -> None:
        """Initialize with node.
        
        Args:
            node: The node

        """
        super().__init__(f"Unsupported literal: {node!r}")


class ShadowstepUnbalancedUiSelectorError(ShadowstepXPathConversionError):
    """Raised when UiSelector string is unbalanced."""

    def __init__(self, selector: str) -> None:
        """Initialize with selector.
        
        Args:
            selector: The selector string

        """
        super().__init__(f"Unbalanced UiSelector string: too many '(' in {selector}")


class ShadowstepEqualityComparisonError(ShadowstepXPathConversionError):
    """Raised when equality comparison is invalid."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Equality must compare @attribute or text() with a literal")


class ShadowstepFunctionArgumentCountError(ShadowstepXPathConversionError):
    """Raised when function has wrong number of arguments."""

    def __init__(self, func_name: str, arg_count: int) -> None:
        """Initialize with function name and argument count.
        
        Args:
            func_name: The function name
            arg_count: The number of arguments

        """
        super().__init__(f"{func_name}() must have {arg_count} arguments")


class ShadowstepUnsupportedAttributeForUiSelectorError(ShadowstepValidationError):
    """Raised when attribute is not supported for UiSelector conversion."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The unsupported attribute

        """
        super().__init__(f"Unsupported attribute for UiSelector conversion: {attr}")


class ShadowstepUnsupportedHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute is not supported."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The unsupported hierarchical attribute

        """
        super().__init__(f"Unsupported hierarchical attribute: {attr}")


class ShadowstepUnsupportedAttributeForXPathError(ShadowstepValidationError):
    """Raised when attribute is not supported for XPath conversion."""

    def __init__(self, attr: str) -> None:
        """Initialize with attribute.
        
        Args:
            attr: The unsupported attribute

        """
        super().__init__(f"Unsupported attribute for XPath conversion: {attr}")


class ShadowstepUnsupportedUiSelectorMethodError(ShadowstepValidationError):
    """Raised when UiSelector method is not supported."""

    def __init__(self, method: str) -> None:
        """Initialize with method.
        
        Args:
            method: The unsupported method

        """
        super().__init__(f"Unsupported UiSelector method: {method}")


class ShadowstepUnsupportedXPathAttributeError(ShadowstepValidationError):
    """Raised when XPath attribute is not supported."""

    def __init__(self, method: str) -> None:
        """Initialize with method.
        
        Args:
            method: The unsupported XPath attribute

        """
        super().__init__(f"Unsupported XPath attribute: {method}")


class ShadowstepInvalidUiSelectorStringFormatError(ShadowstepValidationError):
    """Raised when UiSelector string format is invalid."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Invalid UiSelector string format")


class ShadowstepLogcatError(Exception):
    """Raised when logcat operation fails."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepPollIntervalError(ShadowstepLogcatError):
    """Raised when poll interval is invalid."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("poll_interval must be non-negative")


class ShadowstepEmptyFilenameError(ShadowstepLogcatError):
    """Raised when filename is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("filename cannot be empty")


class ShadowstepLogcatConnectionError(ShadowstepLogcatError):
    """Raised when logcat WebSocket connection fails."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Cannot connect to any logcat WS endpoint")


class ShadowstepNavigatorError(Exception):
    """Raised when navigation operation fails."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when page is None."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("page cannot be None")


class ShadowstepFromPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when from_page is None."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("from_page cannot be None")


class ShadowstepToPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when to_page is None."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("to_page cannot be None")


class ShadowstepTimeoutMustBeNonNegativeError(ShadowstepNavigatorError):
    """Raised when timeout is negative."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("timeout must be non-negative")


class ShadowstepPathCannotBeEmptyError(ShadowstepNavigatorError):
    """Raised when path is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("path cannot be empty")


class ShadowstepPathMustContainAtLeastTwoPagesError(ShadowstepNavigatorError):
    """Raised when path has less than 2 pages."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("path must contain at least 2 pages for dom")


class ShadowstepNavigationFailedError(ShadowstepNavigatorError):
    """Raised when navigation fails."""

    def __init__(self, from_page: str, to_page: str, method: str) -> None:
        """Initialize with navigation context.
        
        Args:
            from_page: The source page
            to_page: The target page
            method: The transition method

        """
        super().__init__(
            f"Navigation error: failed to navigate from {from_page} to {to_page} "
            f"using method {method}",
        )


class ShadowstepPageObjectError(Exception):
    """Raised when page object operation fails."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepUnsupportedRendererTypeError(ShadowstepPageObjectError):
    """Raised when renderer type is not supported."""

    def __init__(self, renderer_type: str) -> None:
        """Initialize with renderer type.
        
        Args:
            renderer_type: The unsupported renderer type

        """
        super().__init__(f"Unsupported renderer type: {renderer_type}")


class ShadowstepTitleNotFoundError(ShadowstepPageObjectError):
    """Raised when title is not found."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Can't find title")


class ShadowstepNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when name is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Name cannot be empty")


class ShadowstepPageClassNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when page class name is empty."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("page_class_name cannot be empty")


class ShadowstepTitleNodeNoUsableNameError(ShadowstepPageObjectError):
    """Raised when title node has no usable name."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Title node does not contain usable name")


class ShadowstepFailedToNormalizeScreenNameError(ShadowstepPageObjectError):
    """Raised when screen name normalization fails."""

    def __init__(self, text: str) -> None:
        """Initialize with text.
        
        Args:
            text: The text that failed to normalize

        """
        super().__init__(f"Failed to normalize screen name from '{text}'")


class ShadowstepNoClassDefinitionFoundError(ShadowstepPageObjectError):
    """Raised when no class definition is found."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("No class definition found in the given source.")


class ShadowstepRootNodeFilteredOutError(ShadowstepPageObjectError):
    """Raised when root node is filtered out."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Root node was filtered out and has no valid children.")


class ShadowstepTerminalNotInitializedError(ShadowstepPageObjectError):
    """Raised when terminal is not initialized."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Terminal is not initialized")


class ShadowstepNoClassDefinitionFoundInTreeError(ShadowstepPageObjectError):
    """Raised when no class definition is found in AST tree."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("No class definition found")


class ShadowstepTranslatorError(Exception):
    """Raised when translation operation fails."""

    def __init__(self, message: str) -> None:
        """Initialize with error message.
        
        Args:
            message: The error message

        """
        super().__init__(message)


class ShadowstepMissingYandexTokenError(ShadowstepTranslatorError):
    """Raised when Yandex token is missing."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Missing yandexPassportOauthToken environment variable")


class ShadowstepTranslationFailedError(ShadowstepTranslatorError):
    """Raised when translation fails."""

    def __init__(self) -> None:
        """Initialize with predefined message."""
        super().__init__("Translation failed: empty response")



class ShadowstepResolvingLocatorError(Exception):
    """Raised when locator resolving is failed (used in shadowstep.element.dom)."""


