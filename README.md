# 📱 Shadowstep (in development)

> Powerful and resilient Appium-based framework for Android UI automation.

[![PyPI](https://img.shields.io/pypi/v/appium-python-client-shadowstep?color=brightgreen)](https://pypi.org/project/appium-python-client-shadowstep/)
[![License](https://img.shields.io/github/license/molokov-klim/Appium-Python-Client-Shadowstep?color=blue)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/blob/main/LICENSE)


[//]: # ([![PyPI]&#40;https://img.shields.io/pypi/v/shadowstep?color=brightgreen&#41;]&#40;https://pypi.org/project/appium-python-client-shadowstep/&#41;)

[//]: # ([![License]&#40;https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/blob/main/LICENSE&#41;]&#40;LICENSE&#41;)



---

## 🔍 Overview

**Shadowstep** is a flexible UI automation framework built on top of **Appium** and designed to improve test reliability and developer experience.  
It introduces powerful abstractions for Android testing: dynamic element wrappers, retry logic, visual change detection, and custom ADB terminal integration.

---

## ✨ Features

- 📲 **Robust UI Automation** – with custom `Element` class and retryable tap/click logic
- 🔁 **Automatic Session Recovery** – handles `NoSuchDriver`, `InvalidSessionId`, and reconnects
- 🎯 **Dict-to-XPath Locator DSL** – write intuitive locators like `{"class": "TextView", "text": "OK"}`
- 🎥 **Video + Screenshot Reporting** – Allure integration with visual context for failed steps
- 📷 **Visual DOM/Window Waits** – wait for or detect screen changes by screenshot diffs
- 👤 **Direct ADB Access** – push/pull/install/uninstall/interact with device via custom ADB wrapper
- 🧱 **Testable Components** – override every interaction and build new ones with ease

---

## 🚀 Quickstart

### 1. 📦 Installation

```bash
pip install appium-python-client-shadowstep
```

---

### 2. ⚙️ Integration via Composition

> ⚠️ Do **not** inherit from `Shadowstep` directly. Use composition to preserve singleton behavior.

```python
from shadowstep.shadowstep import Shadowstep

class ExamplePlatform:
    def __init__(self):
        self.app = Shadowstep.get_instance()

    def __getattr__(self, item):
        return getattr(self.app, item)
```

---

## 📚 PageObject Navigator

### ✅ Requirements for Shadowstep Pages (Auto-discovery)

### 📦 1. File Location
- Must reside in a directory named `pages`
- Filename must start with `page` and end with `.py`

> Example: `applications/android_settings/android_settings_7/pages/page_main/page_main.py`

### 🧩 2. Class Name
- Must start with `Page`, e.g. `PageMain7`

### 🧬 3. Inheritance
- Must inherit from `PageBase`:

```python
from shadowstep.page_base import PageBase
class PageMain7(PageBase): ...
```

### 🧠 4. Required: `edges` Property
Each page must define:

```python
@property
def edges(self) -> Dict[str, Callable[[], PageBase]]:
    return {
        "PageWifi7": self.to_wifi
    }
```

Used by the navigation system to build the screen transition graph.

### 🔄 5. Navigation Methods
- Methods listed in `edges` must:
  - trigger interaction (e.g. `tap()`)
  - return the corresponding Page instance via `self.app.get_page(...)`

```python
def to_wifi(self) -> PageBase:
    self.wifi.tap()
    return self.app.get_page("PageWifi7")
```

### 🌐 6. Auto-discovery Mechanism

The `Shadowstep._auto_discover_pages()` method:

- Iterates over all paths in `sys.path`
- Looks for directories named `pages`
- Skips ignored folders (e.g. `__pycache__`, `venv`, etc.)
- Imports every module with a filename starting with `page`
- Registers each class that:
  - starts with `Page`
  - is a subclass of `PageBase`
  - is **not** the base class itself
- Stores them in `self.pages`
- Adds them to the `PageNavigator`

---

## 📄 Example Page Class

```python
from shadowstep.page_base import PageBase
from shadowstep.element.element import Element
from typing import Dict, Callable

class PageExample(PageBase):
    @property
    def edges(self) -> Dict[str, Callable[[], PageBase]]:
        return {"PageNext": self.to_next}

    def to_next(self) -> PageBase:
        self.next_button.tap()
        return self.app.get_page("PageNext")

    @property
    def next_button(self) -> Element:
        return self.app.get_element(locator={"text": "Next"})
```

---

## 🔮 Example Test

```python
def test_wifi_navigation(example_platform: ExamplePlatform):
    page = example_platform.get_page("PageMain7")
    assert page.is_current_page()

    wifi_page = page.to_wifi()
    assert wifi_page.is_current_page()
```

---

## 🔧 Under the Hood
- Supports retry logic with session recovery
- Lazy element evaluation until interaction
- ADB integration via custom wrapper
- Navigator auto-registers page transitions as a graph

---

## 🚫 Limitations
- Currently Android-only
- Web support not implemented
- Visual detection (image matching) WIP

---

## ✍️ Contributing
We welcome pull requests! Please open an issue before submitting large changes.

---

## ⚖️ License
[MIT License](LICENSE)

