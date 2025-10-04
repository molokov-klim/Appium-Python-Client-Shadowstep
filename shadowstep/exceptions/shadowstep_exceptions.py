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

    def __init__(self, msg: str | None = None, screen: str | None = None, stacktrace: list[str] | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepException."""
        self.context_args = context_args
        self.context_kwargs = context_kwargs
        
        # Set common attributes as instance variables, prioritizing explicit parameters
        self.locator = context_kwargs.get('locator')
        self.driver = context_kwargs.get('driver')
        
        # Also set msg as instance variable for compatibility
        self.msg = msg or self.default_message
        
        # Pass screen and stacktrace to parent WebDriverException
        final_screen = screen if screen is not None else context_kwargs.get('screen')
        final_stacktrace = stacktrace if stacktrace is not None else context_kwargs.get('stacktrace')
        super().__init__(self.msg, screen=final_screen, stacktrace=final_stacktrace)

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
    
    def __init__(self, msg: str | None = None, screen: str | None = None, stacktrace: list[str] | None = None, original_exception: Exception | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepElementException."""
        # Check if screen is actually an exception (common pattern in tests)
        if screen is not None and isinstance(screen, Exception):
            self.original_exception = screen
            screen = None
        # Check if first positional argument after msg is an exception
        elif context_args and isinstance(context_args[0], Exception):
            self.original_exception = context_args[0]
            context_args = context_args[1:]
        else:
            self.original_exception = original_exception
        
        if self.original_exception:
            import traceback
            # Create a fake traceback for the original exception
            try:
                raise self.original_exception
            except Exception:
                self.traceback = traceback.format_exc()
        else:
            self.traceback = None
        super().__init__(msg=msg, screen=screen, stacktrace=stacktrace, *context_args, **context_kwargs)


class ShadowstepNoSuchElementException(ShadowstepElementException):
    """Raised when an element cannot be found with enhanced locator information.

    This exception extends the standard NoSuchElementException to provide
    additional context about the locator that was used and other debugging
    information.
    """

    default_message = "ShadowstepNoSuchElementException occurred"
    
    def __str__(self) -> str:
        """Return string representation with locator information."""
        parts = []
        # Check for message in args or as msg parameter
        message = None
        if self.args and self.args[0]:
            message = self.args[0]
        elif hasattr(self, 'context_kwargs') and 'msg' in self.context_kwargs:
            message = self.context_kwargs['msg']
        elif hasattr(self, 'msg'):
            message = self.msg
        
        if message:
            parts.append(f"Message: {message}")
        if hasattr(self, 'stacktrace') and self.stacktrace:
            parts.append("Stacktrace:")
            parts.append("".join(self.stacktrace))
        if hasattr(self, 'locator') and self.locator:
            parts.append(f"Locator: {self.locator}")
        return "\n".join(parts) if parts else super().__str__()


class ShadowstepTimeoutException(ShadowstepException):
    """Custom timeout exception with additional context."""

    default_message = "ShadowstepTimeoutException occurred"
    
    def __init__(self, msg: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepTimeoutException."""
        import datetime
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        super().__init__(msg=msg, *context_args, **context_kwargs)
    
    def __str__(self) -> str:
        """Return string representation with context information."""
        parts = []
        # Check for message in args or as msg parameter
        message = None
        if self.args and self.args[0]:
            message = self.args[0]
        elif hasattr(self, 'context_kwargs') and 'msg' in self.context_kwargs:
            message = self.context_kwargs['msg']
        elif hasattr(self, 'msg'):
            message = self.msg
        
        if message:
            parts.append(f"Message: {message}")
        if hasattr(self, 'stacktrace') and self.stacktrace:
            parts.append("Stacktrace:")
            parts.append("".join(self.stacktrace))
        if hasattr(self, 'driver') and self.driver and hasattr(self.driver, 'current_url'):
            parts.append(f"URL: {self.driver.current_url}")
        if hasattr(self, 'locator') and self.locator:
            parts.append(f"Locator: {self.locator}")
        return "\n".join(parts) if parts else super().__str__()


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
    
    def __init__(self, msg: str | None = None, operation: str | None = None, details: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepDictConversionError."""
        if operation and details:
            msg = f"Failed to convert dict to {operation}: {details}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepValidationError(ShadowstepLocatorConverterError):
    """Raised when validation fails."""

    default_message = "ShadowstepValidationError occurred"
    
    def __init__(self, msg: str | None = None, message: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepValidationError."""
        if message:
            msg = message
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepSelectorTypeError(ShadowstepValidationError):
    """Raised when selector is not a dictionary."""

    default_message = "Selector must be a dictionary"


class ShadowstepEmptySelectorError(ShadowstepValidationError):
    """Raised when selector dictionary is empty."""

    default_message = "Selector dictionary cannot be empty"


class ShadowstepConflictingTextAttributesError(ShadowstepValidationError):
    """Raised when conflicting text attributes are found."""

    default_message = "Conflicting text attributes"


class ShadowstepConflictingDescriptionAttributesError(ShadowstepValidationError):
    """Raised when conflicting description attributes are found."""

    default_message = "Conflicting description attributes"


class ShadowstepHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute has wrong type."""

    default_message = "ShadowstepHierarchicalAttributeError occurred"
    
    def __init__(self, msg: str | None = None, key: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepHierarchicalAttributeError."""
        if key:
            msg = f"Hierarchical attribute {key} must have dict value"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedSelectorFormatError(ShadowstepConversionError):
    """Raised when selector format is not supported."""

    default_message = "ShadowstepUnsupportedSelectorFormatError occurred"
    
    def __init__(self, msg: str | None = None, selector: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedSelectorFormatError."""
        if selector:
            msg = f"Unsupported selector format: {selector}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepConversionFailedError(ShadowstepConversionError):
    """Raised when conversion fails with context."""

    default_message = "ShadowstepConversionFailedError occurred"
    
    def __init__(self, msg: str | None = None, function_name: str | None = None, selector: str | None = None, details: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepConversionFailedError."""
        if function_name and selector and details:
            msg = f"{function_name} failed to convert selector: {selector}. {details}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedTupleFormatError(ShadowstepValidationError):
    """Raised when tuple format is not supported."""

    default_message = "ShadowstepUnsupportedTupleFormatError occurred"
    
    def __init__(self, msg: str | None = None, format_type: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedTupleFormatError."""
        if format_type:
            msg = f"Unsupported tuple format: {format_type}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepEmptyXPathError(ShadowstepValidationError):
    """Raised when XPath string is empty."""

    default_message = "XPath string cannot be empty"


class ShadowstepEmptySelectorStringError(ShadowstepValidationError):
    """Raised when selector string is empty."""

    default_message = "Selector string cannot be empty"


class ShadowstepUnsupportedSelectorTypeError(ShadowstepValidationError):
    """Raised when selector type is not supported."""

    default_message = "ShadowstepUnsupportedSelectorTypeError occurred"
    
    def __init__(self, msg: str | None = None, selector_type: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedSelectorTypeError."""
        if selector_type:
            msg = f"Unsupported selector type: {selector_type}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUiSelectorConversionError(ShadowstepConversionError):
    """Raised when UiSelector conversion fails."""

    default_message = "ShadowstepUiSelectorConversionError occurred"
    
    def __init__(self, msg: str | None = None, operation: str | None = None, details: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUiSelectorConversionError."""
        if operation and details:
            msg = f"Failed to convert UiSelector to {operation}: {details}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepInvalidUiSelectorStringError(ShadowstepInvalidUiSelectorError):
    """Raised when UiSelector string is invalid."""

    default_message = "ShadowstepInvalidUiSelectorStringError occurred"
    
    def __init__(self, msg: str | None = None, details: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepInvalidUiSelectorStringError."""
        if details:
            msg = f"Invalid UiSelector string: {details}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepSelectorToXPathError(ShadowstepConversionError):
    """Raised when selector to XPath conversion fails."""

    default_message = "ShadowstepSelectorToXPathError occurred"
    
    def __init__(self, msg: str | None = None, details: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepSelectorToXPathError."""
        if details:
            msg = f"Failed to convert selector to XPath: {details}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepMethodRequiresArgumentError(ShadowstepValidationError):
    """Raised when method requires an argument but none provided."""

    default_message = "ShadowstepMethodRequiresArgumentError occurred"
    
    def __init__(self, msg: str | None = None, method_name: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepMethodRequiresArgumentError."""
        if method_name:
            msg = f"Method '{method_name}' requires an argument"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepConflictingMethodsError(ShadowstepValidationError):
    """Raised when conflicting methods are found."""

    default_message = "Conflicting methods"


class ShadowstepUnsupportedNestedSelectorError(ShadowstepConversionError):
    """Raised when nested selector type is not supported."""

    default_message = "ShadowstepUnsupportedNestedSelectorError occurred"
    
    def __init__(self, msg: str | None = None, selector_type: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedNestedSelectorError."""
        if selector_type:
            msg = f"Unsupported nested selector type: {selector_type}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUiSelectorMethodArgumentError(ShadowstepConversionError):
    """Raised when UiSelector method has wrong number of arguments."""

    default_message = "ShadowstepUiSelectorMethodArgumentError occurred"
    
    def __init__(self, msg: str | None = None, arg_count: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUiSelectorMethodArgumentError."""
        if arg_count is not None:
            msg = f"UiSelector methods typically take 0-1 arguments, got {arg_count}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepLexerError(ShadowstepConversionError):
    """Raised when lexical analysis encounters an error."""

    default_message = "ShadowstepLexerError occurred"
    
    def __init__(self, msg: str | None = None, message: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepLexerError."""
        if message:
            msg = message
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnterminatedStringError(ShadowstepLexerError):
    """Raised when string is not properly terminated."""

    default_message = "ShadowstepUnterminatedStringError occurred"
    
    def __init__(self, msg: str | None = None, position: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnterminatedStringError."""
        if position is not None:
            msg = f"Unterminated string at {position}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepBadEscapeError(ShadowstepLexerError):
    """Raised when escape sequence is invalid."""

    default_message = "ShadowstepBadEscapeError occurred"
    
    def __init__(self, msg: str | None = None, position: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepBadEscapeError."""
        if position is not None:
            msg = f"Bad escape at {position}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnexpectedCharError(ShadowstepLexerError):
    """Raised when unexpected character is encountered."""

    default_message = "ShadowstepUnexpectedCharError occurred"
    
    def __init__(self, msg: str | None = None, char: str | None = None, position: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnexpectedCharError."""
        if char is not None and position is not None:
            msg = f"Unexpected char '{char}' at {position}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepParserError(ShadowstepException):
    """Raised when parsing encounters an error."""

    default_message = "ShadowstepParserError occurred"
    
    def __init__(self, msg: str | None = None, message: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepParserError."""
        if message:
            msg = message
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepExpectedTokenError(ShadowstepParserError):
    """Raised when expected token is not found."""

    default_message = "ShadowstepExpectedTokenError occurred"
    
    def __init__(self, msg: str | None = None, expected: str | None = None, got: str | None = None, position: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepExpectedTokenError."""
        if expected and got and position is not None:
            msg = f"Expected {expected}, got {got} at {position}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnexpectedTokenError(ShadowstepParserError):
    """Raised when unexpected token is encountered."""

    default_message = "ShadowstepUnexpectedTokenError occurred"
    
    def __init__(self, msg: str | None = None, token_type: str | None = None, position: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnexpectedTokenError."""
        if token_type and position is not None:
            msg = f"Unexpected token in arg: {token_type} at {position}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepXPathConversionError(ShadowstepConversionError):
    """Raised when XPath conversion fails."""

    default_message = "ShadowstepXPathConversionError occurred"
    
    def __init__(self, msg: str | None = None, message: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepXPathConversionError."""
        if message:
            msg = message
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepBooleanLiteralError(ShadowstepXPathConversionError):
    """Raised when boolean literal is invalid."""

    default_message = "ShadowstepBooleanLiteralError occurred"
    
    def __init__(self, msg: str | None = None, value: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepBooleanLiteralError."""
        if value:
            msg = f"Expected boolean literal, got: '{value}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepNumericLiteralError(ShadowstepXPathConversionError):
    """Raised when numeric literal is invalid."""

    default_message = "ShadowstepNumericLiteralError occurred"
    
    def __init__(self, msg: str | None = None, value: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepNumericLiteralError."""
        if value:
            msg = f"Expected numeric literal, got: '{value}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepLogicalOperatorsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when logical operators are not supported."""

    default_message = "Logical operators (and/or) are not supported"


class ShadowstepInvalidXPathError(ShadowstepXPathConversionError):
    """Raised when XPath is invalid."""

    default_message = "ShadowstepInvalidXPathError occurred"
    
    def __init__(self, msg: str | None = None, details: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepInvalidXPathError."""
        if details:
            msg = f"Invalid XPath: {details}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedAbbreviatedStepError(ShadowstepXPathConversionError):
    """Raised when abbreviated step is not supported."""

    default_message = "ShadowstepUnsupportedAbbreviatedStepError occurred"
    
    def __init__(self, msg: str | None = None, step: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedAbbreviatedStepError."""
        if step:
            msg = f"Unsupported abbreviated step in UiSelector: '{step}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedASTNodeError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported."""

    default_message = "ShadowstepUnsupportedASTNodeError occurred"
    
    def __init__(self, msg: str | None = None, node: Any | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedASTNodeError."""
        if node is not None:
            msg = f"Unsupported AST node in UiSelector: {node}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedASTNodeBuildError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported in build."""

    default_message = "ShadowstepUnsupportedASTNodeBuildError occurred"
    
    def __init__(self, msg: str | None = None, node: Any | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedASTNodeBuildError."""
        if node is not None:
            msg = f"Unsupported AST node in build: '{node}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepContainsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when contains() is not supported for attribute."""

    default_message = "ShadowstepContainsNotSupportedError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepContainsNotSupportedError."""
        if attr:
            msg = f"contains() is not supported for @{attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepStartsWithNotSupportedError(ShadowstepXPathConversionError):
    """Raised when starts-with() is not supported for attribute."""

    default_message = "ShadowstepStartsWithNotSupportedError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepStartsWithNotSupportedError."""
        if attr:
            msg = f"starts-with() is not supported for @{attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepMatchesNotSupportedError(ShadowstepXPathConversionError):
    """Raised when matches() is not supported for attribute."""

    default_message = "ShadowstepMatchesNotSupportedError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepMatchesNotSupportedError."""
        if attr:
            msg = f"matches() is not supported for @{attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedFunctionError(ShadowstepXPathConversionError):
    """Raised when function is not supported."""

    default_message = "ShadowstepUnsupportedFunctionError occurred"
    
    def __init__(self, msg: str | None = None, func_name: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedFunctionError."""
        if func_name:
            msg = f"Unsupported function: {func_name}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedComparisonOperatorError(ShadowstepXPathConversionError):
    """Raised when comparison operator is not supported."""

    default_message = "ShadowstepUnsupportedComparisonOperatorError occurred"
    
    def __init__(self, msg: str | None = None, operator: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedComparisonOperatorError."""
        if operator:
            msg = f"Unsupported comparison operator: {operator}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedAttributeError(ShadowstepXPathConversionError):
    """Raised when attribute is not supported."""

    default_message = "ShadowstepUnsupportedAttributeError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedAttributeError."""
        if attr:
            msg = f"Unsupported attribute: @{attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepAttributePresenceNotSupportedError(ShadowstepXPathConversionError):
    """Raised when attribute presence predicate is not supported."""

    default_message = "ShadowstepAttributePresenceNotSupportedError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepAttributePresenceNotSupportedError."""
        if attr:
            msg = f"Attribute presence predicate not supported for @{attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedPredicateError(ShadowstepXPathConversionError):
    """Raised when predicate is not supported."""

    default_message = "ShadowstepUnsupportedPredicateError occurred"
    
    def __init__(self, msg: str | None = None, predicate: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedPredicateError."""
        if predicate:
            msg = f"Unsupported predicate: '{predicate}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedAttributeExpressionError(ShadowstepXPathConversionError):
    """Raised when attribute expression is not supported."""

    default_message = "ShadowstepUnsupportedAttributeExpressionError occurred"
    
    def __init__(self, msg: str | None = None, node: Any | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedAttributeExpressionError."""
        if node is not None:
            msg = f"Unsupported attribute expression: '{node}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedLiteralError(ShadowstepXPathConversionError):
    """Raised when literal is not supported."""

    default_message = "ShadowstepUnsupportedLiteralError occurred"
    
    def __init__(self, msg: str | None = None, node: Any | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedLiteralError."""
        if node is not None:
            msg = f"Unsupported literal: '{node}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnbalancedUiSelectorError(ShadowstepXPathConversionError):
    """Raised when UiSelector string is unbalanced."""

    default_message = "ShadowstepUnbalancedUiSelectorError occurred"
    
    def __init__(self, msg: str | None = None, selector: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnbalancedUiSelectorError."""
        if selector:
            msg = f"Unbalanced UiSelector string: too many '(' in {selector}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepEqualityComparisonError(ShadowstepXPathConversionError):
    """Raised when equality comparison is invalid."""

    default_message = "Equality must compare @attribute or text() with a literal"


class ShadowstepFunctionArgumentCountError(ShadowstepXPathConversionError):
    """Raised when function has wrong number of arguments."""

    default_message = "ShadowstepFunctionArgumentCountError occurred"
    
    def __init__(self, msg: str | None = None, func_name: str | None = None, arg_count: int | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepFunctionArgumentCountError."""
        if func_name and arg_count is not None:
            msg = f"{func_name}() must have {arg_count} arguments"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedAttributeForUiSelectorError(ShadowstepValidationError):
    """Raised when attribute is not supported for UiSelector conversion."""

    default_message = "ShadowstepUnsupportedAttributeForUiSelectorError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedAttributeForUiSelectorError."""
        if attr:
            msg = f"Unsupported attribute for UiSelector conversion: {attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute is not supported."""

    default_message = "ShadowstepUnsupportedHierarchicalAttributeError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedHierarchicalAttributeError."""
        if attr:
            msg = f"Unsupported hierarchical attribute: {attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedAttributeForXPathError(ShadowstepValidationError):
    """Raised when attribute is not supported for XPath conversion."""

    default_message = "ShadowstepUnsupportedAttributeForXPathError occurred"
    
    def __init__(self, msg: str | None = None, attr: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedAttributeForXPathError."""
        if attr:
            msg = f"Unsupported attribute for XPath conversion: {attr}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedUiSelectorMethodError(ShadowstepValidationError):
    """Raised when UiSelector method is not supported."""

    default_message = "ShadowstepUnsupportedUiSelectorMethodError occurred"
    
    def __init__(self, msg: str | None = None, method: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedUiSelectorMethodError."""
        if method:
            msg = f"Unsupported UiSelector method: {method}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepUnsupportedXPathAttributeError(ShadowstepValidationError):
    """Raised when XPath attribute is not supported."""

    default_message = "ShadowstepUnsupportedXPathAttributeError occurred"
    
    def __init__(self, msg: str | None = None, method: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedXPathAttributeError."""
        if method:
            msg = f"Unsupported XPath attribute: {method}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepInvalidUiSelectorStringFormatError(ShadowstepValidationError):
    """Raised when UiSelector string format is invalid."""

    default_message = "Invalid UiSelector string format"


class ShadowstepLogcatError(ShadowstepException):
    """Raised when logcat operation fails."""

    default_message = "ShadowstepLogcatError occurred"


class ShadowstepPollIntervalError(ShadowstepLogcatError):
    """Raised when poll interval is invalid."""

    default_message = "poll_interval must be non-negative"


class ShadowstepEmptyFilenameError(ShadowstepLogcatError):
    """Raised when filename is empty."""

    default_message = "filename cannot be empty"


class ShadowstepLogcatConnectionError(ShadowstepLogcatError):
    """Raised when logcat WebSocket connection fails."""

    default_message = "Cannot connect to any logcat WS endpoint"


class ShadowstepNavigatorError(ShadowstepException):
    """Raised when navigation operation fails."""

    default_message = "ShadowstepNavigatorError occurred"


class ShadowstepPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when page is None."""

    default_message = "page cannot be None"


class ShadowstepFromPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when from_page is None."""

    default_message = "from_page cannot be None"


class ShadowstepToPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when to_page is None."""

    default_message = "to_page cannot be None"


class ShadowstepTimeoutMustBeNonNegativeError(ShadowstepNavigatorError):
    """Raised when timeout is negative."""

    default_message = "timeout must be non-negative"


class ShadowstepPathCannotBeEmptyError(ShadowstepNavigatorError):
    """Raised when path is empty."""

    default_message = "path cannot be empty"


class ShadowstepPathMustContainAtLeastTwoPagesError(ShadowstepNavigatorError):
    """Raised when path has less than 2 pages."""

    default_message = "path must contain at least 2 pages for dom"


class ShadowstepNavigationFailedError(ShadowstepNavigatorError):
    """Raised when navigation fails."""

    default_message = "ShadowstepNavigationFailedError occurred"
    
    def __init__(self, msg: str | None = None, from_page: str | None = None, to_page: str | None = None, method: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepNavigationFailedError."""
        if from_page and to_page and method:
            msg = f"Navigation error: failed to navigate from {from_page} to {to_page} using method {method}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepPageObjectError(ShadowstepException):
    """Raised when page object operation fails."""

    default_message = "ShadowstepPageObjectError occurred"


class ShadowstepUnsupportedRendererTypeError(ShadowstepPageObjectError):
    """Raised when renderer type is not supported."""

    default_message = "ShadowstepUnsupportedRendererTypeError occurred"
    
    def __init__(self, msg: str | None = None, renderer_type: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepUnsupportedRendererTypeError."""
        if renderer_type:
            msg = f"Unsupported renderer type: {renderer_type}"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepTitleNotFoundError(ShadowstepPageObjectError):
    """Raised when title is not found."""

    default_message = "Can't find title"


class ShadowstepNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when name is empty."""

    default_message = "Name cannot be empty"


class ShadowstepPageClassNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when page class name is empty."""

    default_message = "page_class_name cannot be empty"


class ShadowstepTitleNodeNoUsableNameError(ShadowstepPageObjectError):
    """Raised when title node has no usable name."""

    default_message = "Title node does not contain usable name"


class ShadowstepFailedToNormalizeScreenNameError(ShadowstepPageObjectError):
    """Raised when screen name normalization fails."""

    default_message = "ShadowstepFailedToNormalizeScreenNameError occurred"
    
    def __init__(self, msg: str | None = None, text: str | None = None, *context_args: Any, **context_kwargs: Any) -> None:
        """Initialize ShadowstepFailedToNormalizeScreenNameError."""
        if text:
            msg = f"Failed to normalize screen name from '{text}'"
        super().__init__(msg=msg, *context_args, **context_kwargs)


class ShadowstepNoClassDefinitionFoundError(ShadowstepPageObjectError):
    """Raised when no class definition is found."""

    default_message = "No class definition found in the given source."


class ShadowstepRootNodeFilteredOutError(ShadowstepPageObjectError):
    """Raised when root node is filtered out."""

    default_message = "Root node was filtered out and has no valid children."


class ShadowstepTerminalNotInitializedError(ShadowstepPageObjectError):
    """Raised when terminal is not initialized."""

    default_message = "Terminal is not initialized"


class ShadowstepNoClassDefinitionFoundInTreeError(ShadowstepPageObjectError):
    """Raised when no class definition is found in AST tree."""

    default_message = "No class definition found"


class ShadowstepTranslatorError(ShadowstepException):
    """Raised when translation operation fails."""

    default_message = "ShadowstepTranslatorError occurred"


class ShadowstepMissingYandexTokenError(ShadowstepTranslatorError):
    """Raised when Yandex token is missing."""

    default_message = "Missing yandexPassportOauthToken environment variable"


class ShadowstepTranslationFailedError(ShadowstepTranslatorError):
    """Raised when translation fails."""

    default_message = "Translation failed: empty response"
