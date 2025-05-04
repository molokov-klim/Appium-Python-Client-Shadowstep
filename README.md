# Shadowstep (in development)

**Shadowstep** is a modular UI automation framework for Android applications, built on top of Appium.

It provides:

* Lazy element lookup and interaction (without driver interaction)
* PageObject navigation engine
* Reconnect logic on session failure
* ADB and Appium terminal integration
* DSL-style assertions (`should.have`, `should.be`)

---

## Contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Test Setup (Pytest)](#test-setup-pytest)
* [Element API](#element-api)
* [Collections API (`Elements`)](#collections-api-elements)
* [Page Objects and Navigation](#page-objects-and-navigation)
* [ADB and Terminal](#adb-and-terminal)
* [Architecture Notes](#architecture-notes)
* [Limitations](#limitations)
* [License](#license)

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
    "appium:UDID": 123456789,
    "appium:noReset": True,
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 900,
}
application.connect(server_ip='127.0.0.1', server_port=4723, capabilities=capabilities)
```

---

## Test Setup (Pytest)

```python
import pytest
from shadowstep.shadowstep import Shadowstep


@pytest.fixture()
def app():
    shadowstep = Shadowstep()
    shadowstep.connect(capabilities=Config.APPIUM_CAPABILITIES,
                       command_executor=Config.APPIUM_COMMAND_EXECUTOR,
                       server_ip=Config.APPIUM_IP,
                       server_port=Config.APPIUM_PORT,
                       ssh_user=Config.SSH_USERNAME,
                       ssh_password=Config.SSH_PASSWORD, )
    yield shadowstep
    shadowstep.disconnect()
```

---

## Element API

```python
el = app.get_element({"resource-id": "android:id/title"})
el.tap()
el.text
el.get_attribute("enabled")
```

Lazy DOM tree navigation (declarative)
```python
el = app.get_element({'class': 'android.widget.ImageView'}).\
    get_parent().get_sibling({'resource-id': 'android:id/summary'}).\
    get_cousin(
            ancestor_locator={'text': 'title', 'resource-id': 'android:id/title'},
            cousin_locator={'resource-id': 'android:id/summary'}
        ).get_element(
            {"resource-id": "android:id/switch_widget"})

```

**Key features:**

* Lazy evaluation (`find_element` only called on interaction)
* Support for `dict` and XPath locators
* Built-in retry and session reconnect
* Rich API: `tap`, `click`, `scroll_to`, `get_sibling`, `get_parent`, `drag_to`, `send_keys`, `wait_visible`, etc.

---

## ## Element Collections (`Elements`)

Returned by `get_elements()` (generator-based):

```python
elements = app.get_element({'class': 'android.widget.ImageView'}).get_elements({"class": "android.widget.TextView"})

first = elements.first()
all_items = elements.to_list()

filtered = elements.filter(lambda e: "Wi-Fi" in (e.text or ""))
filtered.should.have.count(minimum=1)
```

```python
els = app.get_elements({'class': 'android.widget.TextView'})    # lazy

els.first.get_attributes()     # driver interaction with first element only
...     # some logic
els.next.get_attributes()    # driver interation with second element only
```


**DSL assertions:**

```python
items.should.have.count(minimum=3)
items.should.have.text("Battery")
items.should.be.all_visible()
```

---

## Page Objects and Navigation

### Defining a Page

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
        except Exception as e:
            self.logger.error(e)
            return False
```

```python
import logging
import inspect
import os
import traceback
from typing import Dict, Any, Callable
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep

logger = logging.getLogger(__name__)

class PageEtalon(PageBaseShadowstep):
    def __init__(self):
        super().__init__()
        self.current_path = os.path.dirname(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename))

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Callable[[], None]]:
        return {}

    @property
    def name(self) -> str:
        return "PageEtalon"

    # --- Title bar ---

    @property
    def title_locator(self) -> Dict[str, Any]:
        return {
            "package": "com.android.launcher3",
            "class": "android.widget.FrameLayout",
            "text": "",
            "resource-id": "android:id/content",
        }

    @property
    def title(self) -> Element:
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self.shadowstep.get_element(locator=self.title_locator)

    # --- Main scrollable container ---

    @property
    def recycler_locator(self):
        # self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return {"scrollable": "true"}

    @property
    def recycler(self):
        # self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self.shadowstep.get_element(locator=self.recycler_locator)

    def _recycler_get(self, locator):
        # self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self.recycler.scroll_to_element(locator=locator)

    # --- Search button (if present) ---

    @property
    def search_button_locator(self) -> Dict[str, Any]:
        return {'text': 'Search'}

    @property
    def search_button(self) -> Element:
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self.shadowstep.get_element(locator=self.search_button_locator)

    # --- Back button button (if present) ---

    @property
    def back_button_locator(self) -> Dict[str, Any]:
        return {'text': 'back'}

    @property
    def back_button(self) -> Element:
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self.shadowstep.get_element(locator=self.back_button_locator)

    # --- Elements in scrollable container ---

    @property
    def element_text_view_locator(self) -> dict:
        return {"text": "Element in scrollable container"}

    @property
    def element_text_view(self) -> Element:
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self.recycler.scroll_to_element(self.element_text_view_locator)

    @property
    def summary_element_text_view(self) -> str:
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        return self._get_summary_text(self.element_text_view)

    # --- PRIVATE METHODS ---

    def _get_summary_text(self, element: Element) -> str:
        try:
            summary = element.get_sibling({"resource-id": "android:id/summary"})
            return self.recycler.scroll_to_element(summary.locator).get_attribute("text")
        except Exception as error:
            logger.error(f"Error:\n{error}\n{traceback.format_exc()}")
            return ""

    # --- is_current_page (always in bottom) ---

    def is_current_page(self) -> bool:
        try:
            if self.title.is_visible():
                return True
            return False
        except Exception as error:
            logger.info(f"{inspect.currentframe().f_code.co_name}: {error}")
            return False
```

### Auto-discovery Requirements

* File: `pages/page_*.py`
* Class: starts with `Page`, inherits from `PageBase`
* Must define `edges` property

### Navigation Example

```python
self.shadowstep.navigator.navigate(source_page=self.page_main, target_page=self.page_display)
assert self.page_display.is_current_page()
```

---

## ADB and Terminal

### ADB Usage

```python
app.adb.press_home()
app.adb.install_apk("path/to/app.apk")
app.adb.input_text("hello")
```

* Direct ADB via `subprocess`
* Supports input, app install/uninstall, screen record, file transfer, etc.

### Terminal Usage

```python
app.terminal.start_activity(package="com.example", activity=".MainActivity")
app.terminal.tap(x=1345, y=756)
app.terminal.past_text(text='hello')
```

* Uses driver.execute_script(`mobile: shell`) or SSH backend (will separate in future)
* Backend selected based on SSH credentials

---

## Architecture Notes

* All interactions are lazy (nothing fetched before usage)
* Reconnects on session loss (`InvalidSessionIdException`, etc.)
* Supports pytest and CI/CD workflows
* Designed for extensibility and modularity

---

## Limitations

* Android only (no iOS or web support)

---

## License
[MIT License](LICENSE)
