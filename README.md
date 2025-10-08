# Shadowstep

Shadowstep is appium-based testing framework with Page Object codegen.

- Lazy element lookup and interaction (driver is touched only when necessary)
- PageObject generation
- PageObject navigation engine with page auto-discovery
- Reconnect logic on session loss
- Integration with ADB and an Appium/SSH "terminal"
- DSL-style assertions for readable checks (`should.have`, `should.be`)
- Image-based actions on screen

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/molokov-klim/Appium-Python-Client-Shadowstep)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[![PyPI version](https://badge.fury.io/py/appium-python-client-shadowstep.svg)](https://badge.fury.io/py/appium-python-client-shadowstep)
[![Downloads](https://pepy.tech/badge/appium-python-client-shadowstep)](https://pepy.tech/project/appium-python-client-shadowstep)

[![Pyright Type Check](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/pyright.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/pyright.yml)
[![Ruff Lint](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/ruff.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/ruff.yml)

[![Unit Tests](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/unit_tests.yml)
[![Integration Tests](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/integration_tests.yml)


---

## Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Test Setup (Pytest)](#test-setup-pytest)
- [Element API (`Element`)](#element-api-element)
- [DSL Assertions](#dsl-assertions)
- [Page Objects and Navigation](#page-objects-and-navigation)
- [ADB and Terminal](#adb-and-terminal)
- [Image Operations](#image-operations)
- [Logcat Logs](#logcat-logs)
- [Page Object module (generation)](#page-object-module-generation)
- [Components](#components)
- [Quick Start (PO generation)](#quick-start-po-generation)
- [Templates](#templates)
- [Limitations and Details](#limitations-and-details)
- [Code References](#code-references)
- [Architecture Notes](#architecture-notes)
- [Limitations](#limitations)
- [License](#license)

---

## Installation

```bash
pip install appium-python-client-shadowstep
```

---

## Quick Start

```python
from shadowstep.shadowstep import Shadowstep

application = Shadowstep()
capabilities = {
    "platformName": "android",
    "appium:automationName": "uiautomator2",
    "appium:UDID": "192.168.56.101:5555",
    "appium:noReset": True,
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 900,
}
application.connect(server_ip='127.0.0.1', server_port=4723, capabilities=capabilities)
```

- You may pass `command_executor` directly (e.g., `http://127.0.0.1:4723/wd/hub`), then `server_ip/port` are optional.
- If you pass `capabilities` as a `dict`, they will be converted into `UiAutomator2Options` internally.


```python
from shadowstep.shadowstep import Shadowstep

shadowstep = Shadowstep.get_instance()
```
Shadowstep is a singleton, so if you’ve already created an instance, you can access it from anywhere.

---

## Test Setup (Pytest)

Session-scoped fixture example:

```python
import pytest
from shadowstep.shadowstep import Shadowstep


@pytest.fixture(scope='session', autouse=True)
def app():
    application = Shadowstep()

    APPIUM_IP = '127.0.0.1'
    APPIUM_PORT = 4723
    APPIUM_COMMAND_EXECUTOR = f'http://{APPIUM_IP}:{APPIUM_PORT}/wd/hub'

    capabilities = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": "192.168.56.101:5555",
        "appium:noReset": True,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 900,
    }

    application.connect(server_ip=APPIUM_IP,
                        server_port=APPIUM_PORT,
                        command_executor=APPIUM_COMMAND_EXECUTOR,
                        capabilities=capabilities)
    yield application
    application.disconnect()
```

Run tests:

```bash
pytest -svl --log-cli-level INFO --tb=short tests/test_shadowstep.py
```

Run Appium server locally:

```bash
npm i -g appium@next
appium driver install uiautomator2
appium server -ka 800 --log-level debug -p 4723 -a 0.0.0.0 -pa /wd/hub --allow-insecure=adb_shell
```

---

## Element API (`Element`)

```python
el = app.get_element({"resource-id": "android:id/title"})
el.tap()
el.text
el.get_attribute("enabled") 
```

Call chains
```python
el = app.get_element({"resource-id": "android:id/title"})
el.zoom().click()
```

Lazy DOM navigation (declarative):

```python
el = app.get_element({'class': 'android.widget.ImageView'}).\
         get_parent().\
         get_sibling({'resource-id': 'android:id/summary'}).\
         get_cousin(cousin_locator={'resource-id': 'android:id/summary'}).\
         get_element({"resource-id": "android:id/switch_widget"})
```

Key features:

- Lazy evaluation: the actual `find_element` happens on the first interaction with an element:
  el = app.get_element({'class': 'android.widget.ImageView'})      # find_element is not called here
  el.swipe_left()     # find_element is called here

- Locators: `dict` and XPath (tuples default to XPath strategy)
- Built-in retries and auto-reconnect on session failures
- Rich API: `tap`, `click`, `scroll_to`, `get_sibling`, `get_parent`, `drag_to`, `send_keys`, `wait_visible`, and more

---

## DSL Assertions

```python
item = app.get_element({'text': 'Network & internet'})
item.should.have.text("Network & internet").have.resource_id("android:id/title")
item.should.be.visible()
item.should.not_be.focused()
```

See more examples in `tests/test_element_should.py`.

---

## Page Objects and Navigation

Base page class is `PageBaseShadowstep`.
A page must:

- inherit from `PageBaseShadowstep`
- have class name starting with `Page`
- provide `edges: Dict[str, Callable[[], PageBaseShadowstep]]` — navigation graph edges
- implement `is_current_page()`

Example page:

```python
import logging
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep

class PageAbout(PageBaseShadowstep):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self):
        return {"PageMain": self.to_main}

    def to_main(self):
        self.shadowstep.terminal.press_back()
        return self.shadowstep.get_page("PageMain")

    @property
    def name(self) -> str:
        return "About"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element(locator={'text': 'About', 'class': 'android.widget.TextView'})

    def is_current_page(self) -> bool:
        try:
            return self.title.is_visible()
        except Exception as error:
            self.logger.error(error)
            return False
```

Auto-discovery of pages:

- classes inheriting `PageBaseShadowstep` and starting with `Page`
- files `page*.py` (usually `pages/page_*.py`) in project paths
- pages are registered automatically when `Shadowstep` is created

Navigation:

```python
app.shadowstep.navigator.navigate(from_page=app.page_main, to_page=app.page_display)
assert app.page_display.is_current_page()
```

---

## ADB and Terminal

Two ways to perform low-level actions:

- `app.adb.*` — direct ADB via `subprocess` (good for local runs)
- `app.terminal.*` — `mobile: shell` via Appium or SSH transport (if `ssh_user/ssh_password` were provided in `connect()`)

ADB examples:

```python
app.adb.press_home()
app.adb.install_app(source="/path/app._apk", udid="192.168.56.101:5555")
app.adb.input_text("hello")
```

Terminal examples:

```python
app.terminal.start_activity(package="com.example", activity=".MainActivity")
app.terminal.tap(x=1345, y=756)
app.terminal.past_text(text='hello')
```

---

## Image Operations

```python
image = app.get_image(image="tests/_test_data/connected_devices.png", threshold=0.5, timeout=3.0)
assert image.is_visible()
image.tap()
image.scroll_down(max_attempts=3)
image.zoom().unzoom().drag(to=(100, 100))
```

Under the hood it uses `opencv-python`, `numpy`, `Pillow`.

---

## Logcat Logs

```python
app.start_logcat("device.logcat")
# ... test steps ...
app.stop_logcat()
```

---

## Architecture Notes

- The element tree is not fetched upfront
- Reconnects on session loss (`InvalidSessionIdException`, `NoSuchDriverException`)
- Works well with Pytest and CI/CD
- Modular architecture: `element`, `elements`, `navigator`, `terminal`, `image`, `utils`

---

## Page Object Generation Module

Tools to automatically generate PageObject classes from UI XML (uiautomator2), enrich them while scrolling, merge results, and generate baseline tests.

- Generate `PageObject` from current `page_source` via Jinja2 template
- Detect title, main container (recycler/scrollable), anchors and related elements (summary/switch)
- Discover additional items inside scrollable lists and merge results
- Generate a simple test class for quick smoke coverage of page properties

---

## Components

- `PageObjectParser`
  - Parses XML (`uiautomator2`) into a `UiElementNode` tree
  - Filters by white/black lists for classes and resource-id, plus a container whitelist
  - API: `parse(xml: str) -> UiElementNode`

- `PageObjectGenerator`
  - Generates a Python page class from `UiElementNode` tree using `templates/page_object.py.j2`
  - Determines `title`, `name`, optional `recycler`, properties, anchors/summary, etc.
  - API: `generate(ui_element_tree: UiElementNode, output_dir: str, filename_prefix: str = "") -> (path, class_name)`

- `PageObjectRecyclerExplorer`
  - Scrolls the screen, re-captures `page_source`, re-generates PO and merges them
  - Requires active `Shadowstep` session (scroll/adb_shell)
  - API: `explore(output_dir: str) -> str` (path to merged file)

- `PageObjectMerger`
  - Merges two generated classes into one: preserves imports/header and combines unique methods
  - API: `merge(file1, file2, output_path) -> str`

- `PageObjectTestGenerator`
  - Generates a basic Pytest class for an existing PageObject (`templates/page_object_test.py.j2`)
  - Verifies visibility of properties at minimum
  - API: `generate_test(input_path: str, class_name: str, output_dir: str) -> (test_path, test_class_name)`

Note: `crawler.py` and `scenario.py` are conceptual notes/ideas, not stable API.

---

## Quick Start (PO generation)

1) Capture XML and generate a page class

```python
from shadowstep.shadowstep import Shadowstep
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_generator import PageObjectGenerator

app = Shadowstep()
xml = app.driver.page_source

parser = PageObjectParser()
tree = parser.parse(xml)

generator = PageObjectGenerator(translator=None)
path, class_name = generator.generate(ui_element_tree=tree, output_dir="pages")
print(path, class_name)
```

2) Explore recycler and merge results

```python
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer

explorer = PageObjectRecyclerExplorer(base=app, translator=None)
merged_path = explorer.explore(output_dir="pages")
print(merged_path)
```

Method/property names are formed from extracted values from text/content-desc/class. 
If the language is not English, the default transliteration is used. 
If you can pass an object with the `def translate(text: str) -> str:` method, they will be translated.

3) Generate a test for the page

```python
from shadowstep.page_object.page_object_test_generator import PageObjectTestGenerator

tg = PageObjectTestGenerator()
test_path, test_class_name = tg.generate_test(input_path=path, class_name=class_name, output_dir="tests/pages")
print(test_path, test_class_name)
```

---

## Templates

- `templates/page_object.py.j2` — PageObject Python class template
- `templates/page_object_test.py.j2` — Pytest class template

To tweak generated code structure, edit these files. (The generator uses the local `templates` folder.)

---

## Code References

- `shadowstep/page_object/page_object_parser.py`
- `shadowstep/page_object/page_object_generator.py`
- `shadowstep/page_object/page_object_recycler_explorer.py`
- `shadowstep/page_object/page_object_merger.py`
- `shadowstep/page_object/page_object_test_generator.py`

---

## Limitations

- Android only (no iOS or Web)
- Singleton session — for parallel testing, use separate runners or containers.

---

## License

MIT — see `LICENSE`.
