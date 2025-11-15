<!--
SPDX-FileCopyrightText: 2023 Molokov Klim

SPDX-License-Identifier: MIT
-->

# SHADOWSTEP TESTING MANIFEST

> **Principle:** Test BEHAVIOR, not implementation. Test CONTRACTS, not details.

___

## TESTING PYRAMID

```
                E2E / Smoke
               ╱────────────╲      5-10%
              ╱   Critical   ╲
             ╱    flows with   ╲   • Complete user scenarios
            ╱   real Appium    ╲  • Regression suite
           ╱──────────────────────╲ • Slow (minutes)
          ╱                        ╲
         ╱──────────────────────────╲
        ╱                            ╲
       ╱       Integration Tests      ╲   20-25%
      ╱    Real Appium (mock driver)   ╲
     ╱      Module boundary checks      ╲  • Element + Appium
    ╱────────────────────────────────────╲ • Terminal + ADB
   ╱                                      ╲ • Medium speed
  ╱────────────────────────────────────────╲
 ╱                                          ╲
╱─────────────────────────────────────────────╲
╲─────────────────────────────────────────────╱
 ╲───────────────────────────────────────────╱
  ╲───────────────────────────────────────╱
   ╲─────────────────────────────────────╱    Unit Tests
    ╲───────────────────────────────────╱     75-80%
     ╲─────────────────────────────────╱
      ╲───────────────────────────────╱      • Isolated
       ╲─────────────────────────────╱       • With mocks
        ╲───────────────────────────╱        • Instant (<1s)
         ╲─────────────────────────╱         • Detailed checks
          ╲───────────────────────╱
           ╲─────────────────────╱
            ╲───────────────────╱
             ╲─────────────────╱
```

**Target distribution:** 75% unit / 20% integration / 5% e2e

___

## TARGET METRICS

```
╔═══════════════════════════════════════════════════════════╗
║  METRIC                        TARGET VALUE              ║
╠═══════════════════════════════════════════════════════════╣
║  Overall test coverage         ≥ 90%                     ║
║  Unit tests                     150-170 tests (75%)      ║
║  Integration tests              40-50 tests (20%)        ║
║  E2E/Smoke tests                10-15 tests (5%)         ║
║  Unit execution time            < 30 seconds             ║
║  Integration execution time     < 5 minutes              ║
║  Full suite execution time      < 6-7 minutes            ║
╚═══════════════════════════════════════════════════════════╝
```

### **Coverage by modules (minimum requirements):**

```
CRITICAL (100%):
├─ locator/converter/ui_selector_lexer.py      100%
├─ locator/converter/ui_selector_parser.py     100%
└─ locator/converter/ui_selector_ast.py        100%

IMPORTANT (95%+):
├─ locator/converter/locator_converter.py      95%
├─ locator/converter/*_converter.py            95%
├─ exceptions/shadowstep_exceptions.py         95%
└─ element/element.py (public methods)         95%

STANDARD (85-90%):
├─ element/actions.py                          90%
├─ element/gestures.py                         90%
├─ element/properties.py                       90%
├─ element/dom.py                              90%
├─ element/waiting.py                          90%
├─ navigator/navigator.py                      90%
├─ navigator/page_graph.py                     85%
├─ page_object/page_object_generator.py        85%
└─ page_object/page_object_parser.py           85%

BASIC (70-80%):
├─ utils/                                      80%
├─ decorators/                                 80%
├─ terminal/                                   75%
├─ image/                                      70%
└─ logcat/                                     70%
```

___

## TEST STRUCTURE

### **Mandatory organization:**

```
tests/
├─ test_unit/              # 75% of all tests, instant execution
│  ├─ test_locator/        # 100% coverage parser and converters
│  ├─ test_element/        # WebElement mocks, detailed checks
│  ├─ test_navigator/      # Graph and page mocks
│  ├─ test_page_object/    # XML fixtures, logic checks
│  ├─ test_exceptions/     # All 88 exception classes
│  ├─ test_utils/          # Pure functions
│  └─ test_decorators/     # Decorators with mocks
│
├─ test_integro/           # 20% of all tests, real Appium
│  ├─ test_element/        # Real UI interactions
│  ├─ test_terminal/       # ADB/AAPT/SSH commands
│  ├─ test_navigator/      # Real navigation
│  ├─ test_locator/        # Smoke tests (converters work)
│  ├─ test_page_object/    # Real page source
│  └─ test_*_integro.py    # Integration checks
│
└─ test_e2e/               # 5% tests (optional, can be added later)
   └─ test_critical_flows.py   # Complete user scenarios
```

___

## TEST WRITING RULES

### **RULE 1: Unit tests**

```
WHAT TO TEST IN UNIT:
✅ Pure logic (parsing, conversion, validation)
✅ Public API (class methods)
✅ Edge cases (empty input, None, invalid data)
✅ Exception handling
✅ Utilities and helpers

HOW TO TEST:
✅ Mocks for external dependencies (WebDriver, WebElement)
✅ Fixtures for test data (XML, dictionaries)
✅ Parametrization (@pytest.mark.parametrize)
✅ Isolation (no network, DB, file system)

MANDATORY:
✅ Execution time: < 100ms per test
✅ No real Appium/Selenium calls
✅ No sleep/time.sleep
✅ Test contract, not implementation

EXAMPLE:
```python

@pytest.mark.parametrize("locator,expected", [
    ({"text": "foo"}, ("//*[@text='foo']", "xpath")),
    (("id", "bar"), ("//*[@resource-id='bar']", "xpath")),
])
def test_to_xpath_all_formats(locator, expected):
    converter = LocatorConverter()
    result = converter.to_xpath(locator)
    assert result == expected

```
```

### **RULE 2: Integration tests**

```
WHAT TO TEST IN INTEGRATION:
✅ Element interaction with real Appium
✅ ADB/AAPT commands on real device
✅ Terminal commands (SSH, transport)
✅ Navigation between real pages
✅ Page source parsing
✅ Logs (logcat via WebSocket)
✅ Timing and race conditions

WHEN TO WRITE INTEGRATION:
✅ When we CANNOT adequately mock
✅ When checking REAL device/Appium
✅ When timing/async/race conditions matter
✅ When checking boundary between systems

DO NOT WRITE INTEGRATION:
❌ For pure logic (parsing, conversion)
❌ For exception classes
❌ For utilities without external dependencies
❌ If can adequately mock

MANDATORY:
✅ Fixture app: Shadowstep (conftest.py)
✅ Fixture stability (wait for UI stability)
✅ Smoke tests with parametrization (not detailed checks)
✅ Minimum duplication with unit

EXAMPLE:
```python

@pytest.mark.parametrize("gesture", ["swipe_up", "swipe_down", "scroll_left"])
def test_element_gestures_work_on_real_device(self, app, gesture):
    """Smoke: gestures work on real device"""
    element = app.get_element({"class": "android.widget.ScrollView"})
    method = getattr(element, gesture)
    result = method()  # Execute on real device
    assert result is element  # Chainable

```
```

### **RULE 3: E2E/Smoke tests**

```
WHAT TO TEST IN E2E:
✅ Critical user flows (end-to-end)
✅ Regression scenarios
✅ Framework usage examples

WHEN TO WRITE:
✅ After major refactoring (regression check)
✅ Before release (smoke suite)
✅ For documentation (live examples)

CHARACTERISTICS:
✅ Complete scenarios (multiple actions)
✅ Realistic use cases
✅ Minimum asserts (check flow, not details)

EXAMPLE:
```python

def test_full_page_object_workflow_e2e(app):
    """E2E: complete workflow with Page Objects"""
    # 1. Navigate
    app.navigator.navigate(PageA(), PageB())

    # 2. Interact
    PageB().button.click()

    # 3. Verify
    assert PageC().title.is_visible()

```
```

___

## ANTI-PATTERNS (what NOT to do)

### Anti-pattern 1: Testing implementation details

```python
# BAD:
def test_element_has_actions_attribute():
    element = Element(...)
    assert hasattr(element, 'actions')  # Testing structure!
    assert isinstance(element.actions, ElementActions)

# GOOD:
def test_element_provides_action_methods():
    element = Element(...)
    result = element.click()  # Testing behavior!
    assert result is element
```

### Anti-pattern 2: Duplicating unit and integration

```python
# BAD:
# unit test:
def test_converter_to_dict():
    assert converter.to_dict({"text": "foo"}) == {"text": "foo"}

# integration test (DUPLICATE!):
def test_converter_to_dict_integro(app):
    assert converter.to_dict({"text": "foo"}) == {"text": "foo"}
    element = app.get_element(...)  # Unnecessary check

# GOOD:
# unit test (detailed):
@pytest.mark.parametrize("input,expected", [...])  # 20 cases
def test_converter_all_cases(input, expected):
    assert converter.to_dict(input) == expected

# integration test (smoke):
def test_converted_locators_work_with_app(app):
    for loc in [dict, xpath, ui]:  # Only check it works
        assert app.get_element(converter.to_dict(loc)) is not None
```

### Anti-pattern 3: Mocking internal methods

```python
# BAD:
def test_element_click():
    with patch.object(element, '_internal_method'):  # Internal method!
        element.click()

# GOOD:
def test_element_click():
    mock_native = Mock(spec=WebElement)  # System boundary!
    element = Element(..., native=mock_native)
    element.click()
    mock_native.click.assert_called_once()
```

### Anti-pattern 4: Integration for pure logic

```python
# BAD:
def test_parser_integro(app):  # Parser DOESN'T NEED app!
    result = Parser(Lexer("text('foo')").tokens()).parse()
    assert result.methods[0].name == "text"

# GOOD:
def test_parser_unit():  # Pure logic in unit!
    result = Parser(Lexer("text('foo')").tokens()).parse()
    assert result.methods[0].name == "text"
```

___

## MODULE REQUIREMENTS

### **Tier 1: CRITICAL (100% coverage mandatory)**

```
Modules where bug = catastrophe

locator/converter/ui_selector_lexer.py       [100%] ← Parser core
locator/converter/ui_selector_parser.py      [100%] ← Parser core
locator/converter/ui_selector_ast.py         [100%] ← Parser core

Tests:
├─ Unit: ALL edge cases (malformed input, escaped, unicode)
├─ Parametrization: every UiSelector method
└─ Integration: smoke test "parser works with Appium"
```

### **Tier 2: IMPORTANT (95%+ coverage)**

```
Public API modules

locator/converter/locator_converter.py       [95%+]
locator/converter/xpath_converter.py         [95%+]
locator/converter/dict_converter.py          [95%+]
element/element.py (public methods only)     [95%+]
exceptions/shadowstep_exceptions.py          [95%+]

Tests:
├─ Unit: All public methods + edge cases
├─ Integration: Smoke tests (works with real app)
└─ Don't test private methods (starting with _)
```

### **Tier 3: STANDARD (85-90% coverage)**

```
element/actions.py                           [90%]
element/gestures.py                          [90%]
element/properties.py                        [90%]
element/dom.py                               [90%]
element/waiting.py                           [90%]
element/coordinates.py                       [85%]
element/screenshots.py                       [85%]
navigator/navigator.py                       [90%]
navigator/page_graph.py                      [85%]
page_object/page_object_generator.py         [85%]
page_object/page_object_parser.py            [85%]

Tests:
├─ Unit: Public methods, main edge cases
├─ Integration: Critical flows with real device
└─ Balance between coverage and practicality
```

### **Tier 4: BASIC (70-80% coverage)**

```
utils/utils.py                               [80%]
utils/adb.py                                 [75%]
decorators/                                  [80%]
terminal/terminal.py                         [75%]
terminal/adb.py                              [75%]
image/image.py                               [70%]
logcat/shadowstep_logcat.py                  [70%]

Tests:
├─ Unit: Main functions
├─ Integration: If require external dependencies (ADB, SSH)
└─ Don't chase 100%
```

___

## TEST DISTRIBUTION RULES

### **UNIT tests should include:**

```
✅ Parsers (Lexer, Parser, AST)
   └─ Pure logic, string → structure

✅ Converters (all *_converter.py)
   └─ Data transformation between formats

✅ Exceptions (all exception classes)
   └─ Pure Python, raise/catch checks

✅ Utils (pure functions without I/O)
   └─ Transformation functions, calculations

✅ Element public API (with mocks)
   └─ click(), send_keys(), get_element() etc.
   └─ Mock WebElement

✅ Navigator logic (with mocks)
   └─ Graph, pathfinding with mock pages

✅ Decorators
   └─ Check wrapper logic
```

### **INTEGRATION tests should include:**

```
✅ Element interactions (actions, gestures, waiting)
   └─ Real clicks, swipes on device

✅ Terminal commands (ADB, AAPT, SSH)
   └─ Cannot adequately mock

✅ Navigator with real pages
   └─ Navigation requires real UI

✅ Page Object with real page source
   └─ Crawler, real XML tree

✅ Logcat
   └─ WebSocket connection to Appium

✅ Image processing
   └─ OpenCV with real screenshots

✅ Smoke tests
   └─ Converters/parsers work with Appium
```

___

## TEST CODE STANDARDS

### **Naming:**

```
test_unit/test_[module]/test_[feature]_unit.py
test_integro/test_[module]/test_[feature]_integro.py

Classes:
class Test[Feature]:
    def test_[specific_case](self):
        ...

Descriptions:
"""Test that [subject] [action] when [condition]."""
```

### **Unit test structure:**

```python
# Arrange
mock_dependency = Mock()
instance = ClassUnderTest(dependency=mock_dependency)

# Act
result = instance.method(arguments)

# Assert
assert result == expected
mock_dependency.some_method.assert_called_once()
```

### **Integration test structure:**

```python
def test_feature_integro(self, app: Shadowstep, stability: None):
    """Integration: [what is checked] on real device"""
    # Arrange (minimal setup)
    element = app.get_element({"text": "foo"})

    # Act (real action)
    result = element.click()

    # Assert (basic check)
    assert result is element
```

### **Mandatory fixtures:**

```python
# conftest.py
@pytest.fixture(scope="session")
def app() -> Shadowstep:
    """Shadowstep instance for integration tests"""
    ...

@pytest.fixture
def stability() -> None:
    """Wait for UI stability before test"""
    time.sleep(1)
```

___

## TEST QUALITY CRITERIA

### **Good unit test:**

```
✅ Executes instantly (< 100ms)
✅ Isolated (no external dependencies)
✅ Uses mocks for boundaries
✅ Parametrized (many cases, little code)
✅ Checks edge cases
✅ Tests contract, not implementation
✅ Clear description (docstring)
✅ Fallible (fails if functionality breaks)
✅ Resistant to refactoring
✅ Doesn't use time.sleep
```

### **Good integration test:**

```
✅ Checks real interaction
✅ Doesn't duplicate unit tests
✅ Smoke nature (basic operability)
✅ Parametrized (where possible)
✅ Fast (1-5 seconds per test)
✅ Reliable (not flaky)
✅ Uses stability fixture
✅ Minimum asserts (check flow, not details)
```

___

## PROCESS: Code Review checklist

### **Before merging a new test:**

```
□ Test in correct category (unit/integration)?
□ No duplication with existing tests?
□ Unit test uses mocks (not real Appium)?
□ Integration test REALLY requires Appium?
□ Parametrization used where possible?
□ Tests contract, not implementation?
□ Docstring clearly describes what is tested?
□ Test passes (green)?
□ Test fails when functionality breaks (verified)?
□ Coverage hasn't dropped?
```

___

## MONITORING AND METRICS

### **Commands for checking:**

```bash
# Overall coverage
uv run pytest --cov=shadowstep --cov-report=term-missing

# Specific module coverage
uv run pytest --cov=shadowstep.element --cov-report=html

# Unit tests only
uv run pytest tests/test_unit -v

# Integration tests only
uv run pytest tests/test_integro -v

# Execution time
time uv run pytest tests/test_unit
time uv run pytest tests/test_integro

# Test count
pytest --collect-only tests/ | grep "test session starts" -A 1
```

### **CI/CD requirements:**

```
Pre-commit hook:
└─ Run only unit tests (fast)

Pull Request:
└─ Run unit + integration

Release:
└─ Full suite + coverage report
```

___

## CURRENT STATE

### **Actual metrics (updated 2025-10-18):**

```
TESTS:
├─ Unit:        162 tests (78%) ✅ TARGET: 75%
├─ Integration:  46 tests (22%) ✅ TARGET: 20-25%
└─ Total:       208 tests

FILES:
├─ test_unit:    41 files
├─ test_integro: 46 files
└─ Total:        87 files

COVERAGE:
└─ Target: 90%+ (needs verification)

EXECUTION TIME:
└─ Needs measurement
```

___

## MANIFEST COMPLIANCE

### **Unit tests (VERIFIED):**

```
✅ locator/converter/ - full coverage
   ├─ test_converter_xpath_unit.py (70KB!)
   ├─ test_converter_dict_unit.py (29KB)
   ├─ test_converter_ui_selector_unit.py (29KB)
   └─ test_converter_unit.py (11KB)

✅ element/ - detailed coverage
   ├─ test_element_unit.py (43KB)
   ├─ test_actions_unit.py (12KB) ⚠️ potential duplication
   ├─ test_gestures_unit.py (22KB)
   ├─ test_dom_unit.py (24KB)
   ├─ test_utilities_unit.py (30KB)
   ├─ test_waiting_unit.py (18KB)
   └─ test_should_unit.py (18KB)

✅ exceptions/ - moved from integro
✅ utils/ - pure functions in unit
✅ decorators/ - has unit tests
```

### **Integration tests (VERIFIED):**

```
✅ element/ - critical interactions
   ├─ test_actions_integro.py (real clicks)
   ├─ test_gestures_integro.py (real swipes)
   └─ test_waiting_integro.py (real timeouts)

✅ terminal/ - commands require device
   ├─ test_terminal_adb_integro.py
   ├─ test_terminal_aapt_integro.py
   └─ test_terminal_transport_integro.py

✅ locator/ - smoke tests
   └─ test_locator_converter_integro.py (parametrized!)

✅ navigator/ - real navigation
✅ page_object/ - real UI tree
✅ logcat/ - WebSocket to Appium
```

___

## ARCHITECTURE: Three-tier system (ADVANCED)

### **IMPORTANT: test_element_unit.py - these are NOT DUPLICATES!**

```
ARCHITECTURE:

test_element_unit.py:
└─ Checks DELEGATION
   Example: Element.click() → correctly calls gestures.click()

test_actions_unit.py, test_gestures_unit.py, etc:
└─ Check component LOGIC
   Example: ElementActions.send_keys() → works correctly

THESE ARE DIFFERENT ABSTRACTION LEVELS!

Analogy:
├─ test_element_unit.py = testing the car (component integration)
└─ test_actions_unit.py = testing the engine (component logic)

BOTH ARE NEEDED!
```

### **Three testing levels:**

```
╔═══════════════════════════════════════════════════════════╗
║  LEVEL                    WHAT IT CHECKS                  ║
╠═══════════════════════════════════════════════════════════╣
║  1. Real Integration      Element + Appium + device      ║
║     (test_integro/)       Real clicks, swipes            ║
║                                                           ║
║  2. Component Integration Element delegates correctly    ║
║     (test_element_unit)   Element.click() → gestures     ║
║                                                           ║
║  3. Component Unit        Component logic in isolation   ║
║     (test_actions_unit)   ElementActions.send_keys()     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

ADVANTAGES:
✅ Fast bug localization (see which level)
✅ Safe refactoring (only needed levels break)
✅ Complete coverage (test ENTIRE chain)
```

___

## IMPROVEMENT RECOMMENDATIONS

### **Recommendation 1: Add Contract Tests (optional)**

```
Create: tests/test_unit/test_element/test_element_contract_unit.py

Goal: Verify public API CONTRACTS

Content:
├─ All public methods exist
├─ All methods chainable (return self)
├─ All methods have correct signatures
└─ Backward compatibility

Example:
```python

class TestElementPublicAPIContract:
    """Contract tests: public API should not change without major version"""

    def test_element_has_all_required_methods(self):
        """Element has all required public methods"""
        required_methods = [
            'click', 'tap', 'send_keys', 'clear',
            'get_element', 'get_elements', 'get_parent',
            'swipe_up', 'swipe_down', 'scroll_to_element',
            'wait', 'wait_visible', 'wait_clickable',
            # ... complete list
        ]

        element = Element({"text": "test"}, Mock())

        for method_name in required_methods:
            assert hasattr(element, method_name), f"Missing method: {method_name}"
            assert callable(getattr(element, method_name))

    @pytest.mark.parametrize("method_name", [
        "click", "tap", "clear", "swipe_up", "scroll_down", ...
    ])
    def test_action_methods_are_chainable(self, method_name):
        """All action methods return self for chaining"""
        element = Element({"text": "test"}, Mock())
        method = getattr(element, method_name)

        with patch.object(element, 'get_native'):
            result = method() if method_name != "send_keys" else method("text")

        assert result is element

```
```

___

## RECOMMENDED IMPROVEMENTS

### **Improvement 1: Add comments for clarity**

```
File: tests/test_unit/test_element/test_element_unit.py

ACTION:
□ Add docstring at module start:
  """Component Integration Tests - check Element → components delegation"""

□ Can rename classes for clarity:
  class TestElementActions → class TestElementActionsDelegation
  class TestElementGestures → class TestElementGesturesDelegation

To make it clear these are delegation tests, not logic!

GOAL: Clarity for contributors
```

### **Improvement 2: Pytest markers**

```
ADD markers for categorization:

@pytest.mark.unit - all unit tests
@pytest.mark.integration - all integration tests
@pytest.mark.smoke - smoke tests
@pytest.mark.slow - slow tests

USAGE:
pytest -m unit              # Unit only (fast)
pytest -m integration       # Integration only
pytest -m "not slow"        # Exclude slow
```

___

## REPORTING

### **After each change:**

```markdown
## [Date] - [Module] optimization

BEFORE:
- test_element_unit.py: 1153 lines
- Duplication: yes

AFTER:
- test_element_unit.py: XXX lines
- Duplication: no

REMOVED:
- XX duplicate tests

COVERAGE:
- Before: X%
- After: Y%
- Change: +/-Z%
```

___

## QUICK START

### **Manifest compliance check:**

```bash
# 1. Check coverage
cd /home/sigma/Projects/Appium-Python-Client-Shadowstep
uv run pytest --cov=shadowstep --cov-report=html --cov-report=term-missing

# 2. Check timing
time uv run pytest tests/test_unit -v
time uv run pytest tests/test_integro -v

# 3. Find duplicates
grep "def test_send_keys\|def test_clear\|def test_click" tests/test_unit/test_element/*.py

# 4. Compare with metrics
# Record results in this file (section "Current State")
```

### **Cleanup duplication:**

```bash
# For each duplicate:
# 1. Open both files
# 2. Compare tests
# 3. If detailed test in specialized file:
# Remove basic from test_element_unit.py
# 4. Run both files
# 5. Check coverage
```

___

## LINKS AND RESOURCES

**Best Practices:**

- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Test Doubles](https://martinfowler.com/bliki/TestDouble.html)

**Quality test examples:**

- [requests tests](https://github.com/psf/requests/tree/main/tests)
- [flask tests](https://github.com/pallets/flask/tree/main/tests)
- [pytest tests](https://github.com/pytest-dev/pytest/tree/main/testing)

___

## GOALS FOR NEXT RELEASE

```
v0.36.0: Test Quality Milestone
□ Coverage ≥ 90%
□ No test duplication
□ All tests categorized correctly
□ Contract tests added
□ Coverage badge in README
□ Test writing documentation
□ CI/CD optimized (< 7 minutes)
```

___

*This manifest is a living document. Update metrics and statuses as the project evolves.*

___

## CONTACTS

Testing questions: GitHub Discussions
Test bugs: GitHub Issues (label: tests)
