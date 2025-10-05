"""Custom exceptions for the Shadowstep framework.

This module defines custom exception classes that extend standard
Selenium and Appium exceptions to provide more specific error handling
and context for the Shadowstep automation framework.
"""

from __future__ import annotations

from typing import Any

from selenium.common import WebDriverException


class ShadowstepException(WebDriverException):
    """Base class for all Shadowstep exceptions."""

    default_message = "ShadowstepException occurred"

    def __init__(self, msg: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepException."""
        self.context_args = context_args
        self.context_kwargs = context_kwargs
        # Use the provided message or construct one from context
        if msg:
            message = msg
        elif context_kwargs:
            # Construct message from context kwargs
            message = self._construct_message_from_context(**context_kwargs)
        else:
            # Try to construct message from context even if no kwargs provided
            message = self._construct_message_from_context()
        super().__init__(message)

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        # This method should be overridden by subclasses to provide specific message construction
        return self.default_message

    def __str__(self) -> str:
        """Return ShadowstepException string."""
        base = super().__str__()
        if self.context_args:
            base += f" | Context: {self.context_args}"
        if self.context_kwargs:
            context = ", ".join(f"{k}={v}" for k, v in self.context_kwargs.items())
            base += f" [{context}]"
        return base

    def __repr__(self) -> str:
        """Return ShadowstepException repr string."""
        base = super().__str__()
        if self.context_args:
            base += f" | Context: {self.context_args}"
        if self.context_kwargs:
            context = ", ".join(f"{k}={v}" for k, v in self.context_kwargs.items())
            base += f" [{context}]"
        return base


class ShadowstepElementException(ShadowstepException):
    """Base class for all ShadowstepElement exceptions."""

    default_message = "ShadowstepElementException occurred"

    def __init__(self, msg: str | None = None, original_exception: Exception | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepElementException."""
        super().__init__(msg, *context_args, **context_kwargs)
        self.original_exception = original_exception
        self.traceback = type(original_exception).__name__ if original_exception else ""


class ShadowstepNoSuchElementException(ShadowstepElementException):
    """Raised when an element cannot be found with enhanced locator information.

    This exception extends the standard NoSuchElementException to provide
    additional context about the locator that was used and other debugging
    information.
    """

    default_message = "ShadowstepNoSuchElementException occurred"

    def __init__(self, msg: str | None = None, locator: Any = None, stacktrace: list[str] | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepNoSuchElementException."""
        super().__init__(msg, *context_args, **context_kwargs)
        self.locator = locator
        self.stacktrace = stacktrace or []

    def __str__(self) -> str:
        """Return ShadowstepNoSuchElementException string."""
        base = super().__str__()
        if self.locator:
            base += f"\nLocator: {self.locator}"
        if self.stacktrace:
            base += f"\nStacktrace: {self.stacktrace}"
        return base


class ShadowstepTimeoutException(ShadowstepException):
    """Custom timeout exception with additional context."""

    default_message = "ShadowstepTimeoutException occurred"

    def __init__(self, msg: str | None = None, locator: Any = None, driver: Any = None, stacktrace: list[str] | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepTimeoutException."""
        super().__init__(msg, *context_args, **context_kwargs)
        self.locator = locator
        self.driver = driver
        self.stacktrace = stacktrace or []

    def __str__(self) -> str:
        """Return ShadowstepTimeoutException string."""
        base = super().__str__()
        if self.locator:
            base += f"\nLocator: {self.locator}"
        if self.driver and hasattr(self.driver, 'current_url'):
            base += f"\nCurrent URL: {self.driver.current_url}"
        if self.stacktrace and len(self.stacktrace) > 0:
            base += f"\nStacktrace: {''.join(self.stacktrace)}"
        return base


class ShadowstepLocatorConverterError(ShadowstepException):
    """Base exception for locator conversion errors."""

    default_message = "ShadowstepLocatorConverterError occurred"


class ShadowstepResolvingLocatorError(ShadowstepLocatorConverterError):
    """Raised when locator resolving is failed (used in shadowstep.element.dom)."""

    default_message = "ShadowstepResolvingLocatorError occurred"


class ShadowstepInvalidUiSelectorError(ShadowstepLocatorConverterError):
    """Raised when UiSelector string is malformed."""

    default_message = "ShadowstepInvalidUiSelectorError occurred"


class ShadowstepConversionError(ShadowstepLocatorConverterError):
    """Raised when conversion between formats fails."""

    default_message = "ShadowstepConversionError occurred"


class ShadowstepDictConversionError(ShadowstepConversionError):
    """Raised when dictionary conversion fails."""

    default_message = "ShadowstepConversionError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        operation = context_kwargs.get('operation', 'conversion')
        details = context_kwargs.get('details', 'unknown error')
        return f"Failed to convert dict to {operation}: {details}"


class ShadowstepValidationError(ShadowstepLocatorConverterError):
    """Raised when validation fails."""

    default_message = "ShadowstepValidationError occurred"


class ShadowstepSelectorTypeError(ShadowstepValidationError):
    """Raised when selector is not a dictionary."""

    default_message = "ShadowstepSelectorTypeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Selector must be a dictionary"


class ShadowstepEmptySelectorError(ShadowstepValidationError):
    """Raised when selector dictionary is empty."""

    default_message = "ShadowstepEmptySelectorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Selector dictionary cannot be empty"


class ShadowstepConflictingTextAttributesError(ShadowstepValidationError):
    """Raised when conflicting text attributes are found."""

    default_message = "ShadowstepConflictingTextAttributesError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Conflicting text attributes"


class ShadowstepConflictingDescriptionAttributesError(ShadowstepValidationError):
    """Raised when conflicting description attributes are found."""

    default_message = "ShadowstepConflictingDescriptionAttributesError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Conflicting description attributes"


class ShadowstepHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute has wrong type."""

    default_message = "ShadowstepHierarchicalAttributeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        key = context_kwargs.get('key', 'attribute')
        return f"Hierarchical attribute {key} must have dict value"


class ShadowstepUnsupportedSelectorFormatError(ShadowstepConversionError):
    """Raised when selector format is not supported."""

    default_message = "ShadowstepUnsupportedSelectorFormatError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        selector = context_kwargs.get('selector', 'unknown')
        return f"Unsupported selector format: {selector}"


class ShadowstepConversionFailedError(ShadowstepConversionError):
    """Raised when conversion fails with context."""

    default_message = "ShadowstepConversionFailedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        function_name = context_kwargs.get('function_name', 'Unknown')
        selector = context_kwargs.get('selector', 'unknown')
        details = context_kwargs.get('details', 'unknown error')
        return f"{function_name} failed to convert selector: {selector}. {details}"


class ShadowstepUnsupportedTupleFormatError(ShadowstepValidationError):
    """Raised when tuple format is not supported."""

    default_message = "ShadowstepUnsupportedTupleFormatError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        format_type = context_kwargs.get('format_type', 'unknown')
        return f"Unsupported tuple format: {format_type}"


class ShadowstepEmptyXPathError(ShadowstepValidationError):
    """Raised when XPath string is empty."""

    default_message = "ShadowstepEmptyXPathError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "XPath string cannot be empty"


class ShadowstepEmptySelectorStringError(ShadowstepValidationError):
    """Raised when selector string is empty."""

    default_message = "ShadowstepEmptySelectorStringError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Selector string cannot be empty"


class ShadowstepUnsupportedSelectorTypeError(ShadowstepValidationError):
    """Raised when selector type is not supported."""

    default_message = "ShadowstepUnsupportedSelectorTypeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        selector_type = context_kwargs.get('selector_type', 'unknown')
        return f"Unsupported selector type: {selector_type}"


class ShadowstepUiSelectorConversionError(ShadowstepConversionError):
    """Raised when UiSelector conversion fails."""

    default_message = "ShadowstepUiSelectorConversionError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        operation = context_kwargs.get('operation', 'conversion')
        details = context_kwargs.get('details', 'unknown error')
        return f"Failed to convert UiSelector to {operation}: {details}"


class ShadowstepInvalidUiSelectorStringError(ShadowstepInvalidUiSelectorError):
    """Raised when UiSelector string is invalid."""

    default_message = "ShadowstepInvalidUiSelectorStringError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        details = context_kwargs.get('details', 'unknown error')
        return f"Invalid UiSelector string: {details}"


class ShadowstepSelectorToXPathError(ShadowstepConversionError):
    """Raised when selector to XPath conversion fails."""

    default_message = "ShadowstepSelectorToXPathError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        details = context_kwargs.get('details', 'unknown error')
        return f"Failed to convert selector to XPath: {details}"


class ShadowstepMethodRequiresArgumentError(ShadowstepValidationError):
    """Raised when method requires an argument but none provided."""

    default_message = "ShadowstepMethodRequiresArgumentError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        method_name = context_kwargs.get('method_name', 'method')
        return f"Method '{method_name}' requires an argument"


class ShadowstepConflictingMethodsError(ShadowstepValidationError):
    """Raised when conflicting methods are found."""

    default_message = "ShadowstepConflictingMethodsError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Conflicting methods"


class ShadowstepUnsupportedNestedSelectorError(ShadowstepConversionError):
    """Raised when nested selector type is not supported."""

    default_message = "ShadowstepUnsupportedNestedSelectorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        selector_type = context_kwargs.get('selector_type', 'unknown')
        return f"Unsupported nested selector type: {selector_type}"


class ShadowstepUiSelectorMethodArgumentError(ShadowstepConversionError):
    """Raised when UiSelector method has wrong number of arguments."""

    default_message = "ShadowstepUiSelectorMethodArgumentError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        arg_count = context_kwargs.get('arg_count', 0)
        return f"UiSelector methods typically take 0-1 arguments, got {arg_count}"


class ShadowstepLexerError(ShadowstepConversionError):
    """Raised when lexical analysis encounters an error."""

    default_message = "ShadowstepLexerError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'lexical error')
        return message


class ShadowstepUnterminatedStringError(ShadowstepLexerError):
    """Raised when string is not properly terminated."""

    default_message = "ShadowstepUnterminatedStringError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        position = context_kwargs.get('position', 0)
        return f"Unterminated string at {position}"


class ShadowstepBadEscapeError(ShadowstepLexerError):
    """Raised when escape sequence is invalid."""

    default_message = "ShadowstepBadEscapeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        position = context_kwargs.get('position', 0)
        return f"Bad escape at {position}"


class ShadowstepUnexpectedCharError(ShadowstepLexerError):
    """Raised when unexpected character is encountered."""

    default_message = "ShadowstepUnexpectedCharError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        char = context_kwargs.get('char', '?')
        position = context_kwargs.get('position', 0)
        return f"Unexpected char '{char}' at {position}"


class ShadowstepParserError(ShadowstepException):
    """Raised when parsing encounters an error."""

    default_message = "ShadowstepParserError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'parse error')
        return message


class ShadowstepExpectedTokenError(ShadowstepParserError):
    """Raised when expected token is not found."""

    default_message = "ShadowstepExpectedTokenError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        expected = context_kwargs.get('expected', 'TOKEN')
        got = context_kwargs.get('got', 'UNKNOWN')
        position = context_kwargs.get('position', 0)
        return f"Expected {expected}, got {got} at {position}"


class ShadowstepUnexpectedTokenError(ShadowstepParserError):
    """Raised when unexpected token is encountered."""

    default_message = "ShadowstepUnexpectedTokenError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        token_type = context_kwargs.get('token_type', 'UNKNOWN')
        position = context_kwargs.get('position', 0)
        return f"Unexpected token in arg: {token_type} at {position}"


class ShadowstepXPathConversionError(ShadowstepConversionError):
    """Raised when XPath conversion fails."""

    default_message = "ShadowstepXPathConversionError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'xpath error')
        return message


class ShadowstepBooleanLiteralError(ShadowstepXPathConversionError):
    """Raised when boolean literal is invalid."""

    default_message = "ShadowstepBooleanLiteralError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        value = context_kwargs.get('value', 'unknown')
        return f"Expected boolean literal, got: '{value}'"


class ShadowstepNumericLiteralError(ShadowstepXPathConversionError):
    """Raised when numeric literal is invalid."""

    default_message = "ShadowstepNumericLiteralError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        value = context_kwargs.get('value', 'unknown')
        return f"Expected numeric literal, got: '{value}'"


class ShadowstepLogicalOperatorsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when logical operators are not supported."""

    default_message = "ShadowstepLogicalOperatorsNotSupportedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Logical operators (and/or) are not supported"


class ShadowstepInvalidXPathError(ShadowstepXPathConversionError):
    """Raised when XPath is invalid."""

    default_message = "ShadowstepInvalidXPathError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        details = context_kwargs.get('details', 'unknown error')
        return f"Invalid XPath: {details}"


class ShadowstepUnsupportedAbbreviatedStepError(ShadowstepXPathConversionError):
    """Raised when abbreviated step is not supported."""

    default_message = "ShadowstepUnsupportedAbbreviatedStepError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        step = context_kwargs.get('step', 'unknown')
        return f"Unsupported abbreviated step in UiSelector: '{step}'"


class ShadowstepUnsupportedASTNodeError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported."""

    default_message = "ShadowstepUnsupportedASTNodeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        node = context_kwargs.get('node', {})
        return f"Unsupported AST node in UiSelector: {node}"


class ShadowstepUnsupportedASTNodeBuildError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported in build."""

    default_message = "ShadowstepUnsupportedASTNodeBuildError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        node = context_kwargs.get('node', 'unknown')
        return f"Unsupported AST node in build: '{node}'"


class ShadowstepContainsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when contains() is not supported for attribute."""

    default_message = "ShadowstepContainsNotSupportedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'attribute')
        return f"contains() is not supported for @{attr}"


class ShadowstepStartsWithNotSupportedError(ShadowstepXPathConversionError):
    """Raised when starts-with() is not supported for attribute."""

    default_message = "ShadowstepStartsWithNotSupportedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'attribute')
        return f"starts-with() is not supported for @{attr}"


class ShadowstepMatchesNotSupportedError(ShadowstepXPathConversionError):
    """Raised when matches() is not supported for attribute."""

    default_message = "ShadowstepMatchesNotSupportedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'attribute')
        return f"matches() is not supported for @{attr}"


class ShadowstepUnsupportedFunctionError(ShadowstepXPathConversionError):
    """Raised when function is not supported."""

    default_message = "ShadowstepUnsupportedFunctionError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        func_name = context_kwargs.get('func_name', 'unknown')
        return f"Unsupported function: {func_name}"


class ShadowstepUnsupportedComparisonOperatorError(ShadowstepXPathConversionError):
    """Raised when comparison operator is not supported."""

    default_message = "ShadowstepUnsupportedComparisonOperatorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        operator = context_kwargs.get('operator', 'unknown')
        return f"Unsupported comparison operator: {operator}"


class ShadowstepUnsupportedAttributeError(ShadowstepXPathConversionError):
    """Raised when attribute is not supported."""

    default_message = "ShadowstepUnsupportedAttributeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'unknown')
        return f"Unsupported attribute: @{attr}"


class ShadowstepAttributePresenceNotSupportedError(ShadowstepXPathConversionError):
    """Raised when attribute presence predicate is not supported."""

    default_message = "ShadowstepAttributePresenceNotSupportedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'unknown')
        return f"Attribute presence predicate not supported for @{attr}"


class ShadowstepUnsupportedPredicateError(ShadowstepXPathConversionError):
    """Raised when predicate is not supported."""

    default_message = "ShadowstepUnsupportedPredicateError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        predicate = context_kwargs.get('predicate', 'unknown')
        return f"Unsupported predicate: '{predicate}'"


class ShadowstepUnsupportedAttributeExpressionError(ShadowstepXPathConversionError):
    """Raised when attribute expression is not supported."""

    default_message = "ShadowstepUnsupportedAttributeExpressionError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        node = context_kwargs.get('node', 'unknown')
        return f"Unsupported attribute expression: '{node}'"


class ShadowstepUnsupportedLiteralError(ShadowstepXPathConversionError):
    """Raised when literal is not supported."""

    default_message = "ShadowstepUnsupportedLiteralError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        node = context_kwargs.get('node', 'unknown')
        return f"Unsupported literal: '{node}'"


class ShadowstepUnbalancedUiSelectorError(ShadowstepXPathConversionError):
    """Raised when UiSelector string is unbalanced."""

    default_message = "ShadowstepUnbalancedUiSelectorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        selector = context_kwargs.get('selector', 'unknown')
        return f"Unbalanced UiSelector string: too many '(' in {selector}"


class ShadowstepEqualityComparisonError(ShadowstepXPathConversionError):
    """Raised when equality comparison is invalid."""

    default_message = "ShadowstepEqualityComparisonError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Equality must compare @attribute or text() with a literal"


class ShadowstepFunctionArgumentCountError(ShadowstepXPathConversionError):
    """Raised when function has wrong number of arguments."""

    default_message = "ShadowstepFunctionArgumentCountError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        func_name = context_kwargs.get('func_name', 'function')
        arg_count = context_kwargs.get('arg_count', 0)
        return f"{func_name}() must have {arg_count} arguments"


class ShadowstepUnsupportedAttributeForUiSelectorError(ShadowstepValidationError):
    """Raised when attribute is not supported for UiSelector conversion."""

    default_message = "ShadowstepUnsupportedAttributeForUiSelectorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'unknown')
        return f"Unsupported attribute for UiSelector conversion: {attr}"


class ShadowstepUnsupportedHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute is not supported."""

    default_message = "ShadowstepUnsupportedHierarchicalAttributeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'unknown')
        return f"Unsupported hierarchical attribute: {attr}"


class ShadowstepUnsupportedAttributeForXPathError(ShadowstepValidationError):
    """Raised when attribute is not supported for XPath conversion."""

    default_message = "ShadowstepUnsupportedAttributeForXPathError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        attr = context_kwargs.get('attr', 'unknown')
        return f"Unsupported attribute for XPath conversion: {attr}"


class ShadowstepUnsupportedUiSelectorMethodError(ShadowstepValidationError):
    """Raised when UiSelector method is not supported."""

    default_message = "ShadowstepUnsupportedUiSelectorMethodError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        method = context_kwargs.get('method', 'unknown')
        return f"Unsupported UiSelector method: {method}"


class ShadowstepUnsupportedXPathAttributeError(ShadowstepValidationError):
    """Raised when XPath attribute is not supported."""

    default_message = "ShadowstepUnsupportedXPathAttributeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        method = context_kwargs.get('method', 'unknown')
        return f"Unsupported XPath attribute: {method}"


class ShadowstepInvalidUiSelectorStringFormatError(ShadowstepValidationError):
    """Raised when UiSelector string format is invalid."""

    default_message = "ShadowstepInvalidUiSelectorStringFormatError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Invalid UiSelector string format"


class ShadowstepLogcatError(ShadowstepException):
    """Raised when logcat operation fails."""

    default_message = "ShadowstepLogcatError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'logcat error')
        return message


class ShadowstepPollIntervalError(ShadowstepLogcatError):
    """Raised when poll interval is invalid."""

    default_message = "ShadowstepPollIntervalError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "poll_interval must be non-negative"


class ShadowstepEmptyFilenameError(ShadowstepLogcatError):
    """Raised when filename is empty."""

    default_message = "ShadowstepEmptyFilenameError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "filename cannot be empty"


class ShadowstepLogcatConnectionError(ShadowstepLogcatError):
    """Raised when logcat WebSocket connection fails."""

    default_message = "ShadowstepLogcatConnectionError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Cannot connect to any logcat WS endpoint"


class ShadowstepNavigatorError(ShadowstepException):
    """Raised when navigation operation fails."""

    default_message = "ShadowstepNavigatorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'navigation error')
        return message


class ShadowstepPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when page is None."""

    default_message = "ShadowstepPageCannotBeNoneError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "page cannot be None"


class ShadowstepFromPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when from_page is None."""

    default_message = "ShadowstepFromPageCannotBeNoneError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "from_page cannot be None"


class ShadowstepToPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when to_page is None."""

    default_message = "ShadowstepToPageCannotBeNoneError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "to_page cannot be None"


class ShadowstepTimeoutMustBeNonNegativeError(ShadowstepNavigatorError):
    """Raised when timeout is negative."""

    default_message = "ShadowstepTimeoutMustBeNonNegativeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "timeout must be non-negative"


class ShadowstepPathCannotBeEmptyError(ShadowstepNavigatorError):
    """Raised when path is empty."""

    default_message = "ShadowstepPathCannotBeEmptyError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "path cannot be empty"


class ShadowstepPathMustContainAtLeastTwoPagesError(ShadowstepNavigatorError):
    """Raised when path has less than 2 pages."""

    default_message = "ShadowstepPathMustContainAtLeastTwoPagesError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "path must contain at least 2 pages for dom"


class ShadowstepNavigationFailedError(ShadowstepNavigatorError):
    """Raised when navigation fails."""

    default_message = "ShadowstepNavigationFailedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        from_page = context_kwargs.get('from_page', 'unknown')
        to_page = context_kwargs.get('to_page', 'unknown')
        method = context_kwargs.get('method', 'unknown')
        return f"Navigation error: failed to navigate from {from_page} to {to_page} using method {method}"


class ShadowstepPageObjectError(ShadowstepException):
    """Raised when page object operation fails."""

    default_message = "ShadowstepPageObjectError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'page object error')
        return message


class ShadowstepUnsupportedRendererTypeError(ShadowstepPageObjectError):
    """Raised when renderer type is not supported."""

    default_message = "ShadowstepUnsupportedRendererTypeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        renderer_type = context_kwargs.get('renderer_type', 'unknown')
        return f"Unsupported renderer type: {renderer_type}"


class ShadowstepTitleNotFoundError(ShadowstepPageObjectError):
    """Raised when title is not found."""

    default_message = "ShadowstepTitleNotFoundError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Can't find title"


class ShadowstepNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when name is empty."""

    default_message = "ShadowstepNameCannotBeEmptyError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Name cannot be empty"


class ShadowstepPageClassNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when page class name is empty."""

    default_message = "ShadowstepPageClassNameCannotBeEmptyError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "page_class_name cannot be empty"


class ShadowstepTitleNodeNoUsableNameError(ShadowstepPageObjectError):
    """Raised when title node has no usable name."""

    default_message = "ShadowstepTitleNodeNoUsableNameError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Title node does not contain usable name"


class ShadowstepFailedToNormalizeScreenNameError(ShadowstepPageObjectError):
    """Raised when screen name normalization fails."""

    default_message = "ShadowstepFailedToNormalizeScreenNameError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        text = context_kwargs.get('text', 'unknown')
        return f"Failed to normalize screen name from '{text}'"


class ShadowstepNoClassDefinitionFoundError(ShadowstepPageObjectError):
    """Raised when no class definition is found."""

    default_message = "ShadowstepNoClassDefinitionFoundError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "No class definition found in the given source."


class ShadowstepRootNodeFilteredOutError(ShadowstepPageObjectError):
    """Raised when root node is filtered out."""

    default_message = "ShadowstepRootNodeFilteredOutError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Root node was filtered out and has no valid children."


class ShadowstepTerminalNotInitializedError(ShadowstepPageObjectError):
    """Raised when terminal is not initialized."""

    default_message = "ShadowstepTerminalNotInitializedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Terminal is not initialized"


class ShadowstepNoClassDefinitionFoundInTreeError(ShadowstepPageObjectError):
    """Raised when no class definition is found in AST tree."""

    default_message = "ShadowstepNoClassDefinitionFoundInTreeError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "No class definition found"


class ShadowstepTranslatorError(ShadowstepException):
    """Raised when translation operation fails."""

    default_message = "ShadowstepTranslatorError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        message = context_kwargs.get('message', 'translation error')
        return message


class ShadowstepMissingYandexTokenError(ShadowstepTranslatorError):
    """Raised when Yandex token is missing."""

    default_message = "ShadowstepMissingYandexTokenError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Missing yandexPassportOauthToken environment variable"


class ShadowstepTranslationFailedError(ShadowstepTranslatorError):
    """Raised when translation fails."""

    default_message = "ShadowstepTranslationFailedError occurred"

    def _construct_message_from_context(self, **context_kwargs: Any) -> str:
        """Construct message from context kwargs."""
        return "Translation failed: empty response"
