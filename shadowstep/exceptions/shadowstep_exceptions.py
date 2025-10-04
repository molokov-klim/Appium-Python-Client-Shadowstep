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
        super().__init__(msg or self.default_message)

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


class ShadowstepNoSuchElementException(ShadowstepElementException):
    """Raised when an element cannot be found with enhanced locator information.

    This exception extends the standard NoSuchElementException to provide
    additional context about the locator that was used and other debugging
    information.
    """

    default_message = "ShadowstepNoSuchElementException occurred"


class ShadowstepTimeoutException(ShadowstepException):
    """Custom timeout exception with additional context."""

    default_message = "ShadowstepTimeoutException occurred"


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


class ShadowstepValidationError(ShadowstepLocatorConverterError):
    """Raised when validation fails."""

    default_message = "ShadowstepValidationError occurred"


class ShadowstepSelectorTypeError(ShadowstepValidationError):
    """Raised when selector is not a dictionary."""

    default_message = "ShadowstepSelectorTypeError occurred"


class ShadowstepEmptySelectorError(ShadowstepValidationError):
    """Raised when selector dictionary is empty."""

    default_message = "ShadowstepEmptySelectorError occurred"


class ShadowstepConflictingTextAttributesError(ShadowstepValidationError):
    """Raised when conflicting text attributes are found."""

    default_message = "ShadowstepConflictingTextAttributesError occurred"


class ShadowstepConflictingDescriptionAttributesError(ShadowstepValidationError):
    """Raised when conflicting description attributes are found."""

    default_message = "ShadowstepConflictingDescriptionAttributesError occurred"


class ShadowstepHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute has wrong type."""

    default_message = "ShadowstepHierarchicalAttributeError occurred"


class ShadowstepUnsupportedSelectorFormatError(ShadowstepConversionError):
    """Raised when selector format is not supported."""

    default_message = "ShadowstepUnsupportedSelectorFormatError occurred"


class ShadowstepConversionFailedError(ShadowstepConversionError):
    """Raised when conversion fails with context."""

    default_message = "ShadowstepConversionFailedError occurred"


class ShadowstepUnsupportedTupleFormatError(ShadowstepValidationError):
    """Raised when tuple format is not supported."""

    default_message = "ShadowstepUnsupportedTupleFormatError occurred"


class ShadowstepEmptyXPathError(ShadowstepValidationError):
    """Raised when XPath string is empty."""

    default_message = "ShadowstepEmptyXPathError occurred"


class ShadowstepEmptySelectorStringError(ShadowstepValidationError):
    """Raised when selector string is empty."""

    default_message = "ShadowstepEmptySelectorStringError occurred"


class ShadowstepUnsupportedSelectorTypeError(ShadowstepValidationError):
    """Raised when selector type is not supported."""

    default_message = "ShadowstepUnsupportedSelectorTypeError occurred"


class ShadowstepUiSelectorConversionError(ShadowstepConversionError):
    """Raised when UiSelector conversion fails."""

    default_message = "ShadowstepUiSelectorConversionError occurred"


class ShadowstepInvalidUiSelectorStringError(ShadowstepInvalidUiSelectorError):
    """Raised when UiSelector string is invalid."""

    default_message = "ShadowstepInvalidUiSelectorStringError occurred"


class ShadowstepSelectorToXPathError(ShadowstepConversionError):
    """Raised when selector to XPath conversion fails."""

    default_message = "ShadowstepSelectorToXPathError occurred"


class ShadowstepMethodRequiresArgumentError(ShadowstepValidationError):
    """Raised when method requires an argument but none provided."""

    default_message = "ShadowstepMethodRequiresArgumentError occurred"


class ShadowstepConflictingMethodsError(ShadowstepValidationError):
    """Raised when conflicting methods are found."""

    default_message = "ShadowstepConflictingMethodsError occurred"


class ShadowstepUnsupportedNestedSelectorError(ShadowstepConversionError):
    """Raised when nested selector type is not supported."""

    default_message = "ShadowstepUnsupportedNestedSelectorError occurred"


class ShadowstepUiSelectorMethodArgumentError(ShadowstepConversionError):
    """Raised when UiSelector method has wrong number of arguments."""

    default_message = "ShadowstepUiSelectorMethodArgumentError occurred"


class ShadowstepLexerError(ShadowstepConversionError):
    """Raised when lexical analysis encounters an error."""

    default_message = "ShadowstepLexerError occurred"


class ShadowstepUnterminatedStringError(ShadowstepLexerError):
    """Raised when string is not properly terminated."""

    default_message = "ShadowstepUnterminatedStringError occurred"


class ShadowstepBadEscapeError(ShadowstepLexerError):
    """Raised when escape sequence is invalid."""

    default_message = "ShadowstepBadEscapeError occurred"


class ShadowstepUnexpectedCharError(ShadowstepLexerError):
    """Raised when unexpected character is encountered."""

    default_message = "ShadowstepUnexpectedCharError occurred"


class ShadowstepParserError(ShadowstepException):
    """Raised when parsing encounters an error."""

    default_message = "ShadowstepParserError occurred"


class ShadowstepExpectedTokenError(ShadowstepParserError):
    """Raised when expected token is not found."""

    default_message = "ShadowstepExpectedTokenError occurred"


class ShadowstepUnexpectedTokenError(ShadowstepParserError):
    """Raised when unexpected token is encountered."""

    default_message = "ShadowstepUnexpectedTokenError occurred"


class ShadowstepXPathConversionError(ShadowstepConversionError):
    """Raised when XPath conversion fails."""

    default_message = "ShadowstepXPathConversionError occurred"


class ShadowstepBooleanLiteralError(ShadowstepXPathConversionError):
    """Raised when boolean literal is invalid."""

    default_message = "ShadowstepBooleanLiteralError occurred"


class ShadowstepNumericLiteralError(ShadowstepXPathConversionError):
    """Raised when numeric literal is invalid."""

    default_message = "ShadowstepNumericLiteralError occurred"


class ShadowstepLogicalOperatorsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when logical operators are not supported."""

    default_message = "ShadowstepLogicalOperatorsNotSupportedError occurred"


class ShadowstepInvalidXPathError(ShadowstepXPathConversionError):
    """Raised when XPath is invalid."""

    default_message = "ShadowstepInvalidXPathError occurred"


class ShadowstepUnsupportedAbbreviatedStepError(ShadowstepXPathConversionError):
    """Raised when abbreviated step is not supported."""

    default_message = "ShadowstepUnsupportedAbbreviatedStepError occurred"


class ShadowstepUnsupportedASTNodeError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported."""

    default_message = "ShadowstepUnsupportedASTNodeError occurred"


class ShadowstepUnsupportedASTNodeBuildError(ShadowstepXPathConversionError):
    """Raised when AST node is not supported in build."""

    default_message = "ShadowstepUnsupportedASTNodeBuildError occurred"


class ShadowstepContainsNotSupportedError(ShadowstepXPathConversionError):
    """Raised when contains() is not supported for attribute."""

    default_message = "ShadowstepContainsNotSupportedError occurred"


class ShadowstepStartsWithNotSupportedError(ShadowstepXPathConversionError):
    """Raised when starts-with() is not supported for attribute."""

    default_message = "ShadowstepStartsWithNotSupportedError occurred"


class ShadowstepMatchesNotSupportedError(ShadowstepXPathConversionError):
    """Raised when matches() is not supported for attribute."""

    default_message = "ShadowstepMatchesNotSupportedError occurred"


class ShadowstepUnsupportedFunctionError(ShadowstepXPathConversionError):
    """Raised when function is not supported."""

    default_message = "ShadowstepUnsupportedFunctionError occurred"


class ShadowstepUnsupportedComparisonOperatorError(ShadowstepXPathConversionError):
    """Raised when comparison operator is not supported."""

    default_message = "ShadowstepUnsupportedComparisonOperatorError occurred"


class ShadowstepUnsupportedAttributeError(ShadowstepXPathConversionError):
    """Raised when attribute is not supported."""

    default_message = "ShadowstepUnsupportedAttributeError occurred"


class ShadowstepAttributePresenceNotSupportedError(ShadowstepXPathConversionError):
    """Raised when attribute presence predicate is not supported."""

    default_message = "ShadowstepAttributePresenceNotSupportedError occurred"


class ShadowstepUnsupportedPredicateError(ShadowstepXPathConversionError):
    """Raised when predicate is not supported."""

    default_message = "ShadowstepUnsupportedPredicateError occurred"


class ShadowstepUnsupportedAttributeExpressionError(ShadowstepXPathConversionError):
    """Raised when attribute expression is not supported."""

    default_message = "ShadowstepUnsupportedAttributeExpressionError occurred"


class ShadowstepUnsupportedLiteralError(ShadowstepXPathConversionError):
    """Raised when literal is not supported."""

    default_message = "ShadowstepUnsupportedLiteralError occurred"


class ShadowstepUnbalancedUiSelectorError(ShadowstepXPathConversionError):
    """Raised when UiSelector string is unbalanced."""

    default_message = "ShadowstepUnbalancedUiSelectorError occurred"


class ShadowstepEqualityComparisonError(ShadowstepXPathConversionError):
    """Raised when equality comparison is invalid."""

    default_message = "ShadowstepEqualityComparisonError occurred"


class ShadowstepFunctionArgumentCountError(ShadowstepXPathConversionError):
    """Raised when function has wrong number of arguments."""

    default_message = "ShadowstepFunctionArgumentCountError occurred"


class ShadowstepUnsupportedAttributeForUiSelectorError(ShadowstepValidationError):
    """Raised when attribute is not supported for UiSelector conversion."""

    default_message = "ShadowstepUnsupportedAttributeForUiSelectorError occurred"


class ShadowstepUnsupportedHierarchicalAttributeError(ShadowstepValidationError):
    """Raised when hierarchical attribute is not supported."""

    default_message = "ShadowstepUnsupportedHierarchicalAttributeError occurred"


class ShadowstepUnsupportedAttributeForXPathError(ShadowstepValidationError):
    """Raised when attribute is not supported for XPath conversion."""

    default_message = "ShadowstepUnsupportedAttributeForXPathError occurred"


class ShadowstepUnsupportedUiSelectorMethodError(ShadowstepValidationError):
    """Raised when UiSelector method is not supported."""

    default_message = "ShadowstepUnsupportedUiSelectorMethodError occurred"


class ShadowstepUnsupportedXPathAttributeError(ShadowstepValidationError):
    """Raised when XPath attribute is not supported."""

    default_message = "ShadowstepUnsupportedXPathAttributeError occurred"


class ShadowstepInvalidUiSelectorStringFormatError(ShadowstepValidationError):
    """Raised when UiSelector string format is invalid."""

    default_message = "ShadowstepInvalidUiSelectorStringFormatError occurred"


class ShadowstepLogcatError(ShadowstepException):
    """Raised when logcat operation fails."""

    default_message = "ShadowstepLogcatError occurred"


class ShadowstepPollIntervalError(ShadowstepLogcatError):
    """Raised when poll interval is invalid."""

    default_message = "ShadowstepPollIntervalError occurred"


class ShadowstepEmptyFilenameError(ShadowstepLogcatError):
    """Raised when filename is empty."""

    default_message = "ShadowstepEmptyFilenameError occurred"


class ShadowstepLogcatConnectionError(ShadowstepLogcatError):
    """Raised when logcat WebSocket connection fails."""

    default_message = "ShadowstepLogcatConnectionError occurred"


class ShadowstepNavigatorError(ShadowstepException):
    """Raised when navigation operation fails."""

    default_message = "ShadowstepNavigatorError occurred"


class ShadowstepPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when page is None."""

    default_message = "ShadowstepPageCannotBeNoneError occurred"


class ShadowstepFromPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when from_page is None."""

    default_message = "ShadowstepFromPageCannotBeNoneError occurred"


class ShadowstepToPageCannotBeNoneError(ShadowstepNavigatorError):
    """Raised when to_page is None."""

    default_message = "ShadowstepToPageCannotBeNoneError occurred"


class ShadowstepTimeoutMustBeNonNegativeError(ShadowstepNavigatorError):
    """Raised when timeout is negative."""

    default_message = "ShadowstepTimeoutMustBeNonNegativeError occurred"


class ShadowstepPathCannotBeEmptyError(ShadowstepNavigatorError):
    """Raised when path is empty."""

    default_message = "ShadowstepPathCannotBeEmptyError occurred"


class ShadowstepPathMustContainAtLeastTwoPagesError(ShadowstepNavigatorError):
    """Raised when path has less than 2 pages."""

    default_message = "ShadowstepPathMustContainAtLeastTwoPagesError occurred"


class ShadowstepNavigationFailedError(ShadowstepNavigatorError):
    """Raised when navigation fails."""

    default_message = "ShadowstepNavigationFailedError occurred"


class ShadowstepPageObjectError(ShadowstepException):
    """Raised when page object operation fails."""

    default_message = "ShadowstepPageObjectError occurred"


class ShadowstepUnsupportedRendererTypeError(ShadowstepPageObjectError):
    """Raised when renderer type is not supported."""

    default_message = "ShadowstepUnsupportedRendererTypeError occurred"


class ShadowstepTitleNotFoundError(ShadowstepPageObjectError):
    """Raised when title is not found."""

    default_message = "ShadowstepTitleNotFoundError occurred"


class ShadowstepNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when name is empty."""

    default_message = "ShadowstepNameCannotBeEmptyError occurred"


class ShadowstepPageClassNameCannotBeEmptyError(ShadowstepPageObjectError):
    """Raised when page class name is empty."""

    default_message = "ShadowstepPageClassNameCannotBeEmptyError occurred"


class ShadowstepTitleNodeNoUsableNameError(ShadowstepPageObjectError):
    """Raised when title node has no usable name."""

    default_message = "ShadowstepTitleNodeNoUsableNameError occurred"


class ShadowstepFailedToNormalizeScreenNameError(ShadowstepPageObjectError):
    """Raised when screen name normalization fails."""

    default_message = "ShadowstepFailedToNormalizeScreenNameError occurred"


class ShadowstepNoClassDefinitionFoundError(ShadowstepPageObjectError):
    """Raised when no class definition is found."""

    default_message = "ShadowstepNoClassDefinitionFoundError occurred"


class ShadowstepRootNodeFilteredOutError(ShadowstepPageObjectError):
    """Raised when root node is filtered out."""

    default_message = "ShadowstepRootNodeFilteredOutError occurred"


class ShadowstepTerminalNotInitializedError(ShadowstepPageObjectError):
    """Raised when terminal is not initialized."""

    default_message = "ShadowstepTerminalNotInitializedError occurred"


class ShadowstepNoClassDefinitionFoundInTreeError(ShadowstepPageObjectError):
    """Raised when no class definition is found in AST tree."""

    default_message = "ShadowstepNoClassDefinitionFoundInTreeError occurred"


class ShadowstepTranslatorError(ShadowstepException):
    """Raised when translation operation fails."""

    default_message = "ShadowstepTranslatorError occurred"


class ShadowstepMissingYandexTokenError(ShadowstepTranslatorError):
    """Raised when Yandex token is missing."""

    default_message = "ShadowstepMissingYandexTokenError occurred"


class ShadowstepTranslationFailedError(ShadowstepTranslatorError):
    """Raised when translation fails."""

    default_message = "ShadowstepTranslationFailedError occurred"
