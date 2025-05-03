# Shadowstep (in development)

**Shadowstep** is a modular UI automation framework for Android applications, built on top of Appium.

It provides:

* Lazy element lookup and interaction
* Structured Page Object architecture
* Screen navigation engine
* ADB and Appium terminal integration
* Reconnect logic on session failure
* Full typing and docstrings (Google style)
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

app = Shadowstep.get_instance()
app.connect(
    server_ip='127.0.0.1',
    server_port=4723,
    capabilities={
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": "192.168.56.101:5555",
        "appium:noReset": True,
        "appium:autoGrantPermissions": True,
    },
)
```

---

## Test Setup (Pytest)

```python
import pytest
from shadowstep.shadowstep import Shadowstep

UDID = "192.168.56.101:5555"

@pytest.fixture(scope='session', autouse=True)
def app(request) -> Shadowstep:
    application = Shadowstep()
    capabilities = {
        "platformName": "android",
        "appium:automationName": "uiautomator2",
        "appium:UDID": UDID,
        "appium:noReset": True,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 900,
    }
    application.connect(server_ip='127.0.0.1', server_port=4723, capabilities=capabilities)
    application.adb.press_home()

    def finalizer():
        try:
            application.adb.press_home()
        finally:
            application.disconnect()

    request.addfinalizer(finalizer)
    yield application
```

---

## Element API

```python
el = app.get_element({"resource-id": "android:id/title"})
el.tap()
el.text
el.get_attribute("enabled")
```

**Key features:**

* Lazy evaluation (`find_element` only called on interaction)
* Support for `dict` and XPath locators
* Built-in retry and session reconnect
* Rich API: `tap`, `click`, `scroll_to`, `get_sibling`, `get_parent`, `drag_to`, `send_keys`, `wait_visible`, etc.

---

## Collections API (`Elements`)

Returned by `get_elements()` (generator-based):

```python
elements = app.get_element(container).get_elements({"class": "android.widget.TextView"})

first = elements.first()
all_items = elements.to_list()

filtered = elements.filter(lambda e: "Wi-Fi" in (e.text or ""))
filtered.should.have.count(minimum=1)
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
from shadowstep.page_base import PageBaseShadowstep

class PageMain(PageBaseShadowstep):
    @property
    def wifi(self):
        return self.app.get_element({"text": "Wi-Fi"})

    def to_wifi(self):
        self.wifi.tap()
        return self.app.get_page("PageWifi")

    @property
    def edges(self):
        return {"PageWifi": self.to_wifi}
```

### Auto-discovery Requirements

* File: `pages/page_*.py`
* Class: starts with `Page`, inherits from `PageBase`
* Must define `edges` property

### Navigation Example

```python
page = app.get_page("PageMain")
wifi_page = page.to_wifi()
assert wifi_page.is_current_page()
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
app.terminal.shell("ls /sdcard")
app.terminal.start_activity(package="com.example", activity=".MainActivity")
```

* Uses `mobile: shell` or SSH backend
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
* Appium server must be running
* Visual testing and OCR not yet implemented

---

## License

MIT License
[MIT License](LICENSE)
