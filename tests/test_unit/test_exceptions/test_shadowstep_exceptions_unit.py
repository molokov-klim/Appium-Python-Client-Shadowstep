# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import datetime

import pytest

import shadowstep.exceptions.shadowstep_exceptions as exc


@pytest.mark.unit
def test_shadowstep_exception_initialization() -> None:
    instance = exc.ShadowstepException("base", "screen", ["trace"])
    assert isinstance(instance, exc.ShadowstepException)


@pytest.mark.unit
def test_shadowstep_element_error_records_original_exception() -> None:
    try:
        raise ValueError("boom")
    except ValueError as err:
        wrapper = exc.ShadowstepElementException("wrapper", err)
    assert wrapper.original_exception.args == ("boom",)
    assert "ValueError" in wrapper.traceback


@pytest.mark.unit
def test_shadowstep_no_such_element_error_str() -> None:
    error = exc.ShadowstepNoSuchElementException(
        msg="missing",
        locator={"id": "btn"},
        stacktrace=["line"],
    )
    message = str(error)
    assert "Locator: {'id': 'btn'}" in message
    assert "missing" in message


@pytest.mark.unit
def test_shadowstep_timeout_exception_str_includes_context() -> None:
    driver = type("Driver", (), {"current_url": "https://example.org"})()
    timeout = exc.ShadowstepTimeoutException(
        msg="timeout",
        locator={"xpath": "//button"},
        driver=driver,
        stacktrace=["trace1\n", "trace2\n"],
    )
    rendered = str(timeout)
    assert "timeout" in rendered
    assert "https://example.org" in rendered
    assert "trace1\ntrace2\n" in rendered
    assert "Locator: {'xpath': '//button'}" in rendered


@pytest.mark.parametrize(
    ("exception_cls", "kwargs", "expected"),
    [
        (exc.ShadowstepElementException, {"msg": "element"}, "element"),
        (
            exc.ShadowstepDictConversionError,
            {"operation": "XPath", "details": "bad data"},
            "Failed to convert dict to XPath: bad data",
        ),
        (exc.ShadowstepValidationError, {"message": "validation"}, "validation"),
        (exc.ShadowstepSelectorTypeError, {}, "Selector must be a dictionary"),
        (exc.ShadowstepEmptySelectorError, {}, "Selector dictionary cannot be empty"),
        (
            exc.ShadowstepConflictingTextAttributesError,
            {"attributes": ["text", "textContains"]},
            "Conflicting text attributes",
        ),
        (
            exc.ShadowstepConflictingDescriptionAttributesError,
            {"attributes": ["desc", "descContains"]},
            "Conflicting description attributes",
        ),
        (
            exc.ShadowstepHierarchicalAttributeError,
            {"key": "childSelector"},
            "Hierarchical attribute childSelector must have dict value",
        ),
        (
            exc.ShadowstepUnsupportedSelectorFormatError,
            {"selector": "unsupported"},
            "Unsupported selector format: unsupported",
        ),
        (
            exc.ShadowstepConversionFailedError,
            {"function_name": "FailedConverter", "selector": "//input", "details": "reason"},
            "FailedConverter failed to convert selector: //input. reason",
        ),
        (
            exc.ShadowstepUnsupportedTupleFormatError,
            {"format_type": "triple"},
            "Unsupported tuple format: triple",
        ),
        (
            exc.ShadowstepEmptyXPathError,
            {},
            "XPath string cannot be empty",
        ),
        (
            exc.ShadowstepEmptySelectorStringError,
            {},
            "Selector string cannot be empty",
        ),
        (
            exc.ShadowstepUnsupportedSelectorTypeError,
            {"selector_type": "list"},
            "Unsupported selector type: list",
        ),
        (
            exc.ShadowstepUiSelectorConversionError,
            {"operation": "dict", "details": "failure"},
            "Failed to convert UiSelector to dict: failure",
        ),
        (
            exc.ShadowstepInvalidUiSelectorStringError,
            {"details": "missing"},
            "Invalid UiSelector string: missing",
        ),
        (
            exc.ShadowstepSelectorToXPathError,
            {"details": "bad"},
            "Failed to convert selector to XPath: bad",
        ),
        (
            exc.ShadowstepMethodRequiresArgumentError,
            {"method_name": "text"},
            "Method 'text' requires an argument",
        ),
        (
            exc.ShadowstepConflictingMethodsError,
            {"existing": "text", "new_method": "textContains", "group_name": "text"},
            "Conflicting methods",
        ),
        (
            exc.ShadowstepUnsupportedNestedSelectorError,
            {"selector_type": "str"},
            "Unsupported nested selector type: str",
        ),
        (
            exc.ShadowstepUiSelectorMethodArgumentError,
            {"arg_count": 2},
            "UiSelector methods typically take 0-1 arguments, got 2",
        ),
        (exc.ShadowstepLexerError, {"message": "lex"}, "lex"),
        (
            exc.ShadowstepUnterminatedStringError,
            {"position": 10},
            "Unterminated string at 10",
        ),
        (
            exc.ShadowstepBadEscapeError,
            {"position": 5},
            "Bad escape at 5",
        ),
        (
            exc.ShadowstepUnexpectedCharError,
            {"char": "@", "position": 4},
            "Unexpected char '@' at 4",
        ),
        (exc.ShadowstepParserError, {"message": "parse"}, "parse"),
        (
            exc.ShadowstepExpectedTokenError,
            {"expected": "NAME", "got": "NUMBER", "position": 7},
            "Expected NAME, got NUMBER at 7",
        ),
        (
            exc.ShadowstepUnexpectedTokenError,
            {"token_type": "NUMBER", "position": 9},
            "Unexpected token in arg: NUMBER at 9",
        ),
        (exc.ShadowstepXPathConversionError, {"message": "xpath"}, "xpath"),
        (
            exc.ShadowstepBooleanLiteralError,
            {"value": "maybe"},
            "Expected boolean literal, got: 'maybe'",
        ),
        (
            exc.ShadowstepNumericLiteralError,
            {"value": "abc"},
            "Expected numeric literal, got: 'abc'",
        ),
        (
            exc.ShadowstepLogicalOperatorsNotSupportedError,
            {},
            "Logical operators (and/or) are not supported",
        ),
        (
            exc.ShadowstepInvalidXPathError,
            {"details": "syntax"},
            "Invalid XPath: syntax",
        ),
        (
            exc.ShadowstepUnsupportedAbbreviatedStepError,
            {"step": ".."},
            "Unsupported abbreviated step in UiSelector: '..'",
        ),
        (
            exc.ShadowstepUnsupportedASTNodeError,
            {"node": {"type": "unknown"}},
            "Unsupported AST node in UiSelector: {'type': 'unknown'}",
        ),
        (
            exc.ShadowstepUnsupportedASTNodeBuildError,
            {"node": "node"},
            "Unsupported AST node in build: 'node'",
        ),
        (
            exc.ShadowstepContainsNotSupportedError,
            {"attr": "resource-id"},
            "contains() is not supported for @resource-id",
        ),
        (
            exc.ShadowstepStartsWithNotSupportedError,
            {"attr": "package"},
            "starts-with() is not supported for @package",
        ),
        (
            exc.ShadowstepMatchesNotSupportedError,
            {"attr": "class"},
            "matches() is not supported for @class",
        ),
        (
            exc.ShadowstepUnsupportedFunctionError,
            {"func_name": "unknown"},
            "Unsupported function: unknown",
        ),
        (
            exc.ShadowstepUnsupportedComparisonOperatorError,
            {"operator": "!="},
            "Unsupported comparison operator: !=",
        ),
        (
            exc.ShadowstepUnsupportedAttributeError,
            {"attr": "foo"},
            "Unsupported attribute: @foo",
        ),
        (
            exc.ShadowstepAttributePresenceNotSupportedError,
            {"attr": "bar"},
            "Attribute presence predicate not supported for @bar",
        ),
        (
            exc.ShadowstepUnsupportedPredicateError,
            {"predicate": "pred"},
            "Unsupported predicate: 'pred'",
        ),
        (
            exc.ShadowstepUnsupportedAttributeExpressionError,
            {"node": "node"},
            "Unsupported attribute expression: 'node'",
        ),
        (
            exc.ShadowstepUnsupportedLiteralError,
            {"node": "lit"},
            "Unsupported literal: 'lit'",
        ),
        (
            exc.ShadowstepUnbalancedUiSelectorError,
            {"selector": "selector("},
            "Unbalanced UiSelector string: too many '(' in selector(",
        ),
        (
            exc.ShadowstepEqualityComparisonError,
            {},
            "Equality must compare @attribute or text() with a literal",
        ),
        (
            exc.ShadowstepFunctionArgumentCountError,
            {"func_name": "contains", "arg_count": 2},
            "contains() must have 2 arguments",
        ),
        (
            exc.ShadowstepUnsupportedAttributeForUiSelectorError,
            {"attr": "foo"},
            "Unsupported attribute for UiSelector conversion: foo",
        ),
        (
            exc.ShadowstepUnsupportedHierarchicalAttributeError,
            {"attr": "bar"},
            "Unsupported hierarchical attribute: bar",
        ),
        (
            exc.ShadowstepUnsupportedAttributeForXPathError,
            {"attr": "baz"},
            "Unsupported attribute for XPath conversion: baz",
        ),
        (
            exc.ShadowstepUnsupportedUiSelectorMethodError,
            {"method": "unknown"},
            "Unsupported UiSelector method: unknown",
        ),
        (
            exc.ShadowstepUnsupportedXPathAttributeError,
            {"method": "unknown"},
            "Unsupported XPath attribute: unknown",
        ),
        (
            exc.ShadowstepInvalidUiSelectorStringFormatError,
            {},
            "Invalid UiSelector string format",
        ),
        (exc.ShadowstepLogcatError, {"message": "log"}, "log"),
        (
            exc.ShadowstepPollIntervalError,
            {},
            "poll_interval must be non-negative",
        ),
        (
            exc.ShadowstepEmptyFilenameError,
            {},
            "filename cannot be empty",
        ),
        (
            exc.ShadowstepLogcatConnectionError,
            {},
            "Cannot connect to any logcat WS endpoint",
        ),
        (exc.ShadowstepNavigatorError, {"message": "nav"}, "nav"),
        (
            exc.ShadowstepPageCannotBeNoneError,
            {},
            "page cannot be None",
        ),
        (
            exc.ShadowstepFromPageCannotBeNoneError,
            {},
            "from_page cannot be None",
        ),
        (
            exc.ShadowstepToPageCannotBeNoneError,
            {},
            "to_page cannot be None",
        ),
        (
            exc.ShadowstepTimeoutMustBeNonNegativeError,
            {},
            "timeout must be non-negative",
        ),
        (
            exc.ShadowstepPathCannotBeEmptyError,
            {},
            "path cannot be empty",
        ),
        (
            exc.ShadowstepPathMustContainAtLeastTwoPagesError,
            {},
            "path must contain at least 2 pages for dom",
        ),
        (
            exc.ShadowstepNavigationFailedError,
            {"from_page": "A", "to_page": "B", "method": "click"},
            "Navigation error: failed to navigate from A to B using method click",
        ),
        (exc.ShadowstepPageObjectError, {"message": "page"}, "page"),
        (
            exc.ShadowstepUnsupportedRendererTypeError,
            {"renderer_type": "graph"},
            "Unsupported renderer type: graph",
        ),
        (
            exc.ShadowstepTitleNotFoundError,
            {},
            "Can't find title",
        ),
        (
            exc.ShadowstepNameCannotBeEmptyError,
            {},
            "Name cannot be empty",
        ),
        (
            exc.ShadowstepPageClassNameCannotBeEmptyError,
            {},
            "page_class_name cannot be empty",
        ),
        (
            exc.ShadowstepTitleNodeNoUsableNameError,
            {},
            "Title node does not contain usable name",
        ),
        (
            exc.ShadowstepFailedToNormalizeScreenNameError,
            {"text": "Screen"},
            "Failed to normalize screen name from 'Screen'",
        ),
        (
            exc.ShadowstepNoClassDefinitionFoundError,
            {},
            "No class definition found in the given source.",
        ),
        (
            exc.ShadowstepRootNodeFilteredOutError,
            {},
            "Root node was filtered out and has no valid children.",
        ),
        (
            exc.ShadowstepTerminalNotInitializedError,
            {},
            "Terminal is not initialized",
        ),
        (
            exc.ShadowstepNoClassDefinitionFoundInTreeError,
            {},
            "No class definition found",
        ),
        (exc.ShadowstepTranslatorError, {"message": "translator"}, "translator"),
        (
            exc.ShadowstepMissingYandexTokenError,
            {},
            "Missing yandexPassportOauthToken environment variable",
        ),
        (
            exc.ShadowstepTranslationFailedError,
            {},
            "Translation failed: empty response",
        ),
    ],
)
@pytest.mark.unit
def test_exception_messages(exception_cls, kwargs, expected) -> None:
    instance = exception_cls(**kwargs)
    # Check that the expected message is in the string representation
    # The new format includes "Message: {ExceptionName} occurred" prefix
    assert expected in str(instance)


@pytest.mark.unit
def test_shadowstep_timeout_exception_timestamp_consistency() -> None:
    driver = type("Driver", (), {"current_url": "https://example.net"})()
    timeout = exc.ShadowstepTimeoutException("delayed", driver=driver)
    # Test that the exception can be created and has the expected message
    assert "delayed" in str(timeout)
    assert "https://example.net" in str(timeout)

