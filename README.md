# Shadowstep

**Shadowstep** — a modern Python framework for Android test automation powered by Appium. 
_Write tests, not boilerplate._

___

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![Appium](https://img.shields.io/badge/appium-5.2.2%2B-green)](https://appium.io)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

___

[![YouTube Playlist](https://img.shields.io/badge/YouTube--Playlist-red?logo=youtube)](https://www.youtube.com/playlist?list=PLGFbKpf3cI31d1TLlQXCszl88dutdruKx)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/molokov-klim/Appium-Python-Client-Shadowstep)

___

[![PyPI version](https://badge.fury.io/py/appium-python-client-shadowstep.svg)](https://badge.fury.io/py/appium-python-client-shadowstep)
[![Downloads](https://pepy.tech/badge/appium-python-client-shadowstep)](https://pepy.tech/project/appium-python-client-shadowstep)

___

[![Pyright Type Check](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/pyright.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/pyright.yml)
[![Ruff Lint](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/ruff.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/ruff.yml)
[![Unit Tests](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/unit_tests.yml)
[![Integration Tests](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep/actions/workflows/integration_tests.yml)

___

## 📋 Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Core API](#core-api)
  - [Shadowstep (Facade)](#shadowstep-facade)
  - [Element (Facade)](#element-facade)
  - [PageBase](#pagebase)
- [Additional Modules](#additional-modules)
  - [Navigator](#navigator)
  - [Locator System](#locator-system)
  - [Terminal](#terminal)
  - [Logcat](#logcat)
  - [Image Recognition](#image-recognition)
  - [Page Object Generator](#page-object-generator)
- [Usage Examples](#usage-examples)
- [Quality Tools](#quality-tools)

---

## 🚀 Key Features

### 🎯 Architectural Patterns
- **Facade Pattern** — simplified interface for Appium interactions
- **Page Object Pattern** — structured UI representation
- **Singleton Pattern** — single point of access to driver
- **Navigator Pattern** — graph-based page navigation

### 🔧 Functionality
- **Flexible locator system** — dict, xpath, UiSelector with auto-conversion
- **Rich DOM navigation** — parent, sibling, cousin relationships
- **Advanced gestures** — tap, swipe, fling, scroll, pinch, zoom
- **Lazy/Greedy element search** — performance optimization
- **Fail-safe decorators** — automatic error handling and reconnection
- **Built-in logging** — Loguru-style colored output
- **Image Recognition** — find elements by images (OpenCV)
- **Logcat Streaming** — capture logs via WebSocket
- **Page Object Generator** — auto-generate page objects from XML
- **SSH/ADB Support** — remote command execution

---

## 📦 Installation

### Requirements
- Python 3.9+
- Appium Server 2.x
- UiAutomator2 Driver
- Android Device/Emulator

### Install via pip

```bash
pip install appium-python-client-shadowstep
```

### Install via uv (recommended)

```bash
# Install uv
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

uv pip install appium-python-client-shadowstep
```

### Dependencies

Core:
- `Appium-Python-Client >= 5.2.2`
- `selenium >= 4.36`
- `networkx >= 3.2.1` — navigation
- `opencv-python >= 4.12.0.88` — image recognition
- `paramiko >= 4.0.0` — SSH
- `websocket-client >= 1.8.0` — logcat

Additional:
- `lxml >= 6.0.2` — XML parsing
- `jinja2 >= 3.1.6` — template engine
- `pytesseract >= 0.3.10` — OCR

---

## ⚡ Quick Start

### 1. Start Appium Server

```bash
appium --use-drivers=uiautomator2
```

### 2. Basic Example

```python
from shadowstep import Shadowstep

# Connect to device
app = Shadowstep()
app.connect(
    capabilities={
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": "emulator-5554",
        "appium:appPackage": "com.android.settings",
        "appium:appActivity": ".Settings",
    }
)

# Find and interact with element
element = app.get_element({"text": "Network & internet"})
element.tap()

# Wait for element
element.wait_visible(timeout=10)

# Check properties
print(element.text)  # "Network & internet"
print(element.is_displayed())  # True

# Disconnect
app.disconnect()
```

### 3. Page Object Example

```python
from shadowstep import PageBaseShadowstep, Element

class PageSettings(PageBaseShadowstep):
    @property
    def edges(self):
        return {
            "PageNetworkInternet": self.to_network_internet,
        }
    
    @property
    def title(self) -> Element:
        return self.shadowstep.get_element({
            "text": "Settings",
            "resource-id": "com.android.settings:id/homepage_title"
        })
    
    @property
    def network_internet(self) -> Element:
        return self.recycler.scroll_to_element({
            "text": "Network & internet"
        })
    
    @property
    def recycler(self) -> Element:
        return self.shadowstep.get_element({
            "resource-id": "com.android.settings:id/settings_homepage_container"
        })
    
    def to_network_internet(self):
        self.network_internet.tap()
        return self.shadowstep.get_page("PageNetworkInternet")
    
    def is_current_page(self) -> bool:
        return self.title.is_visible()

# Usage
app = Shadowstep()
# ... connect ...

page = app.get_page("PageSettings")
assert page.is_current_page()
page.to_network_internet()
```

---

## 🏗️ Architecture

### Facade Pattern

The project implements **Facade Pattern** at two levels:

#### 1. Shadowstep (Main Facade)

`Shadowstep` — the main facade that hides the complexity of Appium WebDriver interactions and provides a simple API.

```python
class Shadowstep(ShadowstepBase):
    """Main Facade for mobile automation."""
    
    def __init__(self):
        super().__init__()
        self.navigator = PageNavigator(self)
        self.converter = LocatorConverter()
        self.mobile_commands = MobileCommands()
```

**Hidden subsystems:**
- `ShadowstepBase` — WebDriver management, connections
- `PageNavigator` — page navigation
- `LocatorConverter` — locator conversion
- `MobileCommands` — UiAutomator2 commands
- `Terminal/Transport` — ADB and SSH
- `ShadowstepLogcat` — logging

#### 2. Element (Element Facade)

`Element` — facade for working with mobile elements, combining multiple specialized classes.

```python
class Element(ElementBase):
    """Public API for Element."""
    
    def __init__(self, locator, shadowstep, ...):
        super().__init__(...)
        self.utilities = ElementUtilities(self)
        self.properties = ElementProperties(self)
        self.dom = ElementDOM(self)
        self.actions = ElementActions(self)
        self.gestures = ElementGestures(self)
        self.coordinates = ElementCoordinates(self)
        self.screenshots = ElementScreenshots(self)
        self.waiting = ElementWaiting(self)
```

**Hidden subsystems:**
- `ElementDOM` — finding related elements (parent, sibling, cousin)
- `ElementActions` — text input, clearing
- `ElementGestures` — tap, swipe, scroll, fling
- `ElementProperties` — attributes, states
- `ElementCoordinates` — coordinates, center
- `ElementScreenshots` — screenshots
- `ElementWaiting` — waits
- `ElementUtilities` — helper functions

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User/Test Code                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌────────────────────┐      ┌──────────────────┐
│  Shadowstep        │◄─────┤  PageBase        │
│  (Main Facade)     │      │  (Page Objects)  │
└────────┬───────────┘      └──────────────────┘
         │
         ├─► Navigator (Page Graph)
         ├─► LocatorConverter
         ├─► MobileCommands
         ├─► Terminal/Transport
         └─► ShadowstepLogcat
         │
         ▼
┌────────────────────┐
│  Element (Facade)  │
└────────┬───────────┘
         │
         ├─► ElementDOM
         ├─► ElementActions
         ├─► ElementGestures
         ├─► ElementProperties
         ├─► ElementCoordinates
         ├─► ElementScreenshots
         └─► ElementWaiting
         │
         ▼
┌────────────────────┐
│  Appium/Selenium   │
│  (WebDriver)       │
└────────────────────┘
```

---

## 📚 Core API

### Shadowstep (Facade)

Main facade class for managing mobile testing.

#### Device Connection

```python
# Via capabilities
app.connect(
    capabilities={
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": "emulator-5554",
        "appium:appPackage": "com.android.settings",
        "appium:appActivity": ".Settings",
    },
    server_ip="127.0.0.1",
    server_port=4723
)

# Via options
from appium.options.android import UiAutomator2Options

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "com.android.settings"

app.connect(
    capabilities={},
    options=options
)

# With SSH for remote server
app.connect(
    capabilities={...},
    server_ip="192.168.1.100",
    ssh_user="user",
    ssh_password="password"
)

# Check connection
if app.is_connected():
    print("Connected successfully")

# Reconnect
app.reconnect()

# Disconnect
app.disconnect()
```

#### Finding Elements

```python
# Via dict
element = app.get_element({
    "text": "Network & internet",
    "resource-id": "android:id/title"
})

# Via xpath
element = app.get_element(("xpath", '//android.widget.TextView[@text="Settings"]'))

# Via UiSelector
from shadowstep.locator import UiSelector
element = app.get_element(UiSelector().text("Settings"))

# Multiple search (greedy)
elements = app.get_elements({"class": "android.widget.TextView"})
for el in elements:
    print(el.text)

# With timeout and polling
element = app.get_element(
    locator={"text": "Network"},
    timeout=30,
    poll_frequency=0.5
)
```

#### Screen-Level Gestures

```python
# Tap by coordinates
app.tap(x=500, y=1000, duration=100)

# Click
app.click(x=500, y=1000)

# Double click
app.double_click(x=500, y=1000)

# Long click
app.long_click(x=500, y=1000, duration=1000)

# Swipe
app.swipe(
    left=100, top=500,
    width=800, height=400,
    direction="up",
    percent=0.75,
    speed=5000
)

# Swipe shortcuts
app.swipe_up(percent=0.75, speed=5000)
app.swipe_down(percent=0.75)
app.swipe_left()
app.swipe_right()

# Scroll
app.scroll(
    left=100, top=500,
    width=800, height=400,
    direction="down",
    percent=0.5,
    speed=2000
)

# Drag
app.drag(start_x=500, start_y=1000, end_x=500, end_y=500, speed=2500)

# Fling
app.fling(
    left=100, top=500,
    width=800, height=400,
    direction="up",
    speed=7500
)

# Pinch (zoom)
app.pinch_open(left=100, top=500, width=800, height=600, percent=0.5)
app.pinch_close(left=100, top=500, width=800, height=600, percent=0.5)
```

#### Screenshots and Page Source

```python
# Get screenshot
screenshot = app.get_screenshot()  # bytes

# Save screenshot
app.save_screenshot(path="/tmp", filename="screen.png")

# Save page source
app.save_source(path="/tmp", filename="page.xml")
```

#### Application Management

```python
# Start activity
app.start_activity(
    intent="com.android.settings/.Settings",
    component="com.android.settings/.Settings"
)

# Get current application
package = app.get_current_package()  # "com.android.settings"
activity = app.get_current_activity()  # ".Settings"

# Background/Foreground
app.background_app(seconds=2)
app.activate_app(app_id="com.android.settings")

# Check installation
is_installed = app.is_app_installed(app_id="com.android.settings")

# Application state
state = app.query_app_state(app_id="com.android.settings")
# 0=not installed, 1=not running, 2=background, 3=background+suspended, 4=foreground

# Terminate application
app.terminate_app(app_id="com.android.settings")

# Clear data
app.clear_app(app_id="com.android.settings")
```

#### System Commands

```python
# Press keys
app.press_key(keycode=3)  # HOME
app.press_key(keycode=4)  # BACK

# Open notifications
app.open_notifications()

# Lock/unlock
app.lock()
app.unlock(key="1234", unlock_type="pin")
is_locked = app.is_locked()

# Shell commands
result = app.shell("echo test")

# Type text
app.type(text="test input")

# Keyboard
is_shown = app.is_keyboard_shown()
app.hide_keyboard()
```

#### File Operations

```python
import base64

# Push file
content = base64.b64encode(b"test content").decode()
app.push_file(remote_path="/sdcard/test.txt", payload=content)

# Pull file
content = app.pull_file(remote_path="/sdcard/test.txt")
decoded = base64.b64decode(content)

# Pull folder
folder_data = app.pull_folder(remote_path="/sdcard/Android")

# Delete file
app.delete_file(remote_path="/sdcard/test.txt")

# Via ADB wrapper
app.push(source_file_path="local.txt", destination_file_path="/sdcard/test.txt")
```

#### Clipboard

```python
import base64

# Set clipboard text
text = "test clipboard"
encoded = base64.b64encode(text.encode()).decode()
app.set_clipboard(content=encoded)

# Get clipboard text
clipboard = app.get_clipboard()
decoded = base64.b64decode(clipboard).decode()
```

#### Screen Recording

```python
# Start recording
app.start_recording_screen()

# Stop recording
video_bytes = app.stop_recording_screen()

# Save video
with open("recording.mp4", "wb") as f:
    f.write(video_bytes)
```

#### Network Settings

```python
# Get network state
connectivity = app.get_connectivity(services=["wifi", "data"])

# Set state
app.set_connectivity(wifi=True, data=False)

# Bluetooth
app.bluetooth(action="enable")
app.bluetooth(action="disable")

# GPS
app.toggle_gps()
is_enabled = app.is_gps_enabled()

# NFC
app.nfc(action="enable")
app.nfc(action="disable")

# Geolocation
app.set_geolocation(latitude=37.7749, longitude=-122.4194, altitude=10.0)
location = app.get_geolocation(latitude=37.7749, longitude=-122.4194, altitude=10.0)
app.reset_geolocation()
app.refresh_gps_cache(timeout_ms=5000)
```

#### Device Information

```python
# Battery
battery = app.battery_info()
# {"level": 80, "state": 2, "temperature": 25, ...}

# Device
device = app.device_info()

# Display density
density = app.get_display_density()  # 420

# System bars
bars = app.get_system_bars()
# {"statusBar": {...}, "navigationBar": {...}}

# Device time
time_str = app.get_device_time()

# Performance data
types = app.get_performance_data_types()
perf_data = app.get_performance_data(
    package_name="com.android.settings",
    data_type="cpuinfo"
)
```

#### Page Navigation

```python
# Get page instance
settings_page = app.get_page("PageSettings")

# Navigate via graph
settings_page = app.get_page("PageSettings")
network_page = settings_page.to_network_internet()

# Resolve page
page = app.resolve_page("PageNetworkInternet")
```

---

### Element (Facade)

Facade class for interacting with UI elements.

#### Creating Element

```python
# Via Shadowstep
element = app.get_element({"text": "Settings"})

# Directly
from shadowstep.element import Element
element = Element(
    locator={"text": "Settings"},
    shadowstep=app,
    timeout=30,
    poll_frequency=0.5
)

# With native WebElement
from appium.webdriver.webelement import WebElement
native_el = driver.find_element(...)
element = Element(
    locator={"text": "Settings"},
    shadowstep=app,
    native=native_el
)
```

#### DOM Navigation

```python
element = app.get_element({"text": "Network & internet"})

# Search within element (lazy)
inner = element.get_element({"class": "android.widget.TextView"})

# Multiple search (greedy)
children = element.get_elements({"class": "android.widget.TextView"})

# Parent
parent = element.get_parent()
all_parents = element.get_parents()

# Sibling
sibling = element.get_sibling({"resource-id": "android:id/summary"})
all_siblings = element.get_siblings({"class": "android.widget.TextView"})

# Cousin (sibling of parent)
cousin = element.get_cousin(
    cousin_locator={"text": "Apps"},
    depth_to_parent=1  # go up 1 level
)
cousins = element.get_cousins(
    cousin_locator={"class": "android.widget.TextView"},
    depth_to_parent=2
)
```

#### Actions (input)

```python
element = app.get_element({"resource-id": "search_field"})

# Send keys
element.send_keys("test query")

# Clear
element.clear()

# Set value (not supported in UiAutomator2)
element.set_value("new value")

# Submit (not supported in UiAutomator2)
element.submit()
```

#### Gestures

```python
element = app.get_element({"text": "Settings"})

# Tap
element.tap()
element.tap(duration=3000)  # long tap

# Tap and move
element.tap_and_move(x=100, y=500)
element.tap_and_move(locator={"text": "Apps"})
element.tap_and_move(direction=0, distance=1000)  # up

# Click
element.click()
element.click(duration=3000)
element.click_double()

# Drag
element.drag(end_x=500, end_y=1000, speed=2500)

# Fling
element.fling(speed=2500, direction="up")
element.fling_up(speed=2500)
element.fling_down()
element.fling_left()
element.fling_right()

# Scroll
recycler = app.get_element({"resource-id": "recycler_view"})
recycler.scroll(direction="down", percent=0.7, speed=2000)
recycler.scroll_down(percent=0.7)
recycler.scroll_up()
recycler.scroll_left()
recycler.scroll_right()

# Scroll to top/bottom
recycler.scroll_to_top(percent=0.7, speed=8000)
recycler.scroll_to_bottom()

# Scroll to element
target = recycler.scroll_to_element(
    locator={"text": "About phone"},
    max_swipes=30
)

# Swipe
element.swipe(direction="up", percent=0.75, speed=5000)
element.swipe_up()
element.swipe_down()
element.swipe_left()
element.swipe_right()

# Zoom
element.zoom(percent=0.75, speed=2500)
element.unzoom(percent=0.75, speed=2500)
```

#### Properties

```python
element = app.get_element({"text": "Network & internet"})

# Attributes
text = element.get_attribute("text")
attrs = element.get_attributes()  # all attributes from XML

# DOM attribute
content_desc = element.get_dom_attribute("content-desc")

# Property (not supported in UiAutomator2)
prop = element.get_property("checked")

# States
is_displayed = element.is_displayed()
is_visible = element.is_visible()
is_enabled = element.is_enabled()
is_selected = element.is_selected()

# Check containment
has_child = element.is_contains({"class": "android.widget.TextView"})

# Properties via property
tag = element.tag_name
all_attrs = element.attributes
text = element.text
resource_id = element.resource_id
class_name = element.class_name
class_ = element.class_  # alternative
index = element.index
package = element.package
bounds = element.bounds

# Boolean properties
checked = element.checked
checkable = element.checkable
enabled = element.enabled
focusable = element.focusable
focused = element.focused
long_clickable = element.long_clickable
password = element.password
scrollable = element.scrollable
selected = element.selected
displayed = element.displayed

# Size and position
size = element.size  # {"width": 800, "height": 100}
location = element.location  # {"x": 100, "y": 500}
rect = element.rect  # {"x": 100, "y": 500, "width": 800, "height": 100}
location_in_view = element.location_in_view

# Shadow root (not supported in UiAutomator2)
shadow_root = element.shadow_root

# CSS (not supported in UiAutomator2)
css_value = element.value_of_css_property("color")

# ARIA (not supported in UiAutomator2)
aria_role = element.aria_role
accessible_name = element.accessible_name
```

#### Coordinates

```python
element = app.get_element({"text": "Settings"})

# Coordinates (x, y, width, height)
x, y, width, height = element.get_coordinates()

# Element center
center_x, center_y = element.get_center()

# Location in view
loc = element.location_in_view  # {"x": 100, "y": 500}

# Location once scrolled (not supported in UiAutomator2)
loc = element.location_once_scrolled_into_view
```

#### Screenshots

```python
element = app.get_element({"text": "Settings"})

# Base64
screenshot_b64 = element.screenshot_as_base64

# PNG bytes
screenshot_png = element.screenshot_as_png

# Save to file
success = element.save_screenshot("/tmp/element.png")
```

#### Waiting

```python
element = app.get_element({"text": "Network & internet"})

# Wait until present
element.wait(timeout=10, poll_frequency=0.5)
# or return bool
success = element.wait(timeout=10, return_bool=True)

# Wait until visible
element.wait_visible(timeout=10)

# Wait until clickable
element.wait_clickable(timeout=10)

# Wait until NOT present
element.wait_for_not(timeout=10)

# Wait until NOT visible
element.wait_for_not_visible(timeout=10)

# Wait until NOT clickable
element.wait_for_not_clickable(timeout=10)
```

#### Should (DSL assertions)

```python
element = app.get_element({"text": "Settings"})

# Fluent assertions
element.should.be_visible()
element.should.be_enabled()
element.should.have_text("Settings")
element.should.have_attribute("text", "Settings")
element.should.be_displayed()
element.should.be_clickable()

# Negative checks
element.should.not_be_visible()
element.should.not_have_text("Other")
```

#### Native WebElement

```python
element = app.get_element({"text": "Settings"})

# Get native WebElement
native = element.get_native()
native.click()
```

---

### PageBase

Abstract base class for Page Object pattern with automatic navigation.

#### Creating Page Object

```python
from shadowstep import PageBaseShadowstep, Element

class PageSettings(PageBaseShadowstep):
    """Settings page representation."""
    
    # Required: define relationships with other pages
    @property
    def edges(self):
        return {
            "PageNetworkInternet": self.to_network_internet,
            "PageAboutPhone": self.to_about_phone,
        }
    
    # Page name
    @property
    def name(self) -> str:
        return "Settings"
    
    # Title element for page verification
    @property
    def title(self) -> Element:
        return self.shadowstep.get_element({
            "text": "Settings",
            "resource-id": "com.android.settings:id/homepage_title"
        })
    
    # Recycler (scrollable container)
    @property
    def recycler(self) -> Element:
        return self.shadowstep.get_element({
            "resource-id": "com.android.settings:id/settings_homepage_container"
        })
    
    # Page elements
    @property
    def network_internet(self) -> Element:
        return self.recycler.scroll_to_element({
            "text": "Network & internet",
            "resource-id": "android:id/title"
        })
    
    @property
    def network_internet_summary(self) -> Element:
        return self.network_internet.get_sibling({
            "resource-id": "android:id/summary"
        })
    
    @property
    def about_phone(self) -> Element:
        return self.recycler.scroll_to_element({
            "text": "About phone"
        })
    
    # Navigation methods
    def to_network_internet(self):
        """Navigate to Network & Internet page."""
        self.network_internet.tap()
        return self.shadowstep.get_page("PageNetworkInternet")
    
    def to_about_phone(self):
        """Navigate to About Phone page."""
        self.about_phone.tap()
        return self.shadowstep.get_page("PageAboutPhone")
    
    # Required: check current page
    def is_current_page(self) -> bool:
        """Check if Settings page is currently displayed."""
        try:
            return self.title.is_visible()
        except Exception:
            return False
```

#### Using Page Objects

```python
# Get instance (singleton)
settings = app.get_page("PageSettings")

# Check current page
assert settings.is_current_page()

# Interact with elements
print(settings.network_internet.text)
print(settings.network_internet_summary.text)

# Navigate
network_page = settings.to_network_internet()
assert network_page.is_current_page()

# Clear singleton
PageSettings.clear_instance()
```

#### Automatic Navigation (Navigator)

Navigator automatically finds paths between pages through the graph.

```python
from shadowstep.navigator import PageNavigator

# Navigator is created automatically in Shadowstep
# app.navigator = PageNavigator(app)

# Automatic page discovery and registration
app.navigator.auto_discover_pages()

# List registered pages
app.navigator.list_registered_pages()

# Navigate with automatic pathfinding
current_page = app.get_page("PageSettings")
target_page = app.get_page("PageAboutPhone")

# Navigator will find shortest path through graph
success = app.navigator.navigate(
    from_page=current_page,
    to_page=target_page,
    timeout=10
)
```

---

## 🧩 Additional Modules

### Navigator

Graph-based navigation system between pages.

#### How it Works

1. Each page defines `edges` — relationships with other pages
2. Navigator builds a graph from all pages
3. During navigation, uses shortest path algorithm (NetworkX or BFS fallback)

```python
from shadowstep.navigator import PageNavigator

navigator = PageNavigator(app)

# Auto-discover pages in sys.path
navigator.auto_discover_pages()

# Add page manually
page = PageSettings()
navigator.add_page(page, edges=page.edges)

# Find path
path = navigator.find_path(
    start=PageSettings(),
    target=PageAboutPhone()
)
# ["PageSettings", "PageNetworkInternet", "PageAboutPhone"]

# Navigate through path
navigator.perform_navigation(path, timeout=10)

# Direct navigation
success = navigator.navigate(
    from_page=PageSettings(),
    to_page=PageAboutPhone(),
    timeout=10
)
```

---

### Locator System

Flexible locator system supporting three formats: dict, xpath, UiSelector.

#### Locator Types

##### 1. Dictionary (Shadowstep Dict)

```python
# Simple locator
locator = {"text": "Settings"}

# Compound locator
locator = {
    "text": "Network & internet",
    "resource-id": "android:id/title",
    "class": "android.widget.TextView"
}

# With contains
locator = {"textContains": "Network"}

# With starts-with
locator = {"textStartsWith": "Net"}

# With matches (regex)
locator = {"textMatches": "Net.*"}

# All UiSelector attributes supported
locator = {
    "text": "Settings",
    "clickable": True,
    "index": 0,
    "instance": 0
}
```

##### 2. XPath

```python
# Simple xpath
locator = ("xpath", '//android.widget.TextView[@text="Settings"]')

# With functions
locator = ("xpath", '//android.widget.TextView[contains(@text, "Network")]')
locator = ("xpath", '//android.widget.TextView[starts-with(@text, "Net")]')

# With attributes
locator = ("xpath", '//*[@resource-id="android:id/title" and @text="Settings"]')

# With indices
locator = ("xpath", '(//android.widget.TextView)[1]')

# Parent/child
locator = ("xpath", '//android.widget.ScrollView//android.widget.TextView')
```

##### 3. UiSelector

```python
from shadowstep.locator import UiSelector

# Simple selector
locator = UiSelector().text("Settings")

# Chaining
locator = (UiSelector()
    .text("Network & internet")
    .resourceId("android:id/title")
    .className("android.widget.TextView"))

# Contains
locator = UiSelector().textContains("Network")

# Starts with
locator = UiSelector().textStartsWith("Net")

# Matches (regex)
locator = UiSelector().textMatches("Net.*")

# Boolean properties
locator = UiSelector().clickable(True).enabled(True)

# Index and instance
locator = UiSelector().className("android.widget.TextView").index(0)
locator = UiSelector().className("android.widget.TextView").instance(2)

# Description
locator = UiSelector().description("Phone")
locator = UiSelector().descriptionContains("Pho")

# Package
locator = UiSelector().packageName("com.android.settings")

# Child selector
parent = UiSelector().className("android.widget.ScrollView")
child = UiSelector().text("Settings")
locator = parent.childSelector(child)

# From parent
locator = UiSelector().text("Settings").fromParent(UiSelector().className("android.widget.LinearLayout"))
```

#### Locator Conversion

```python
from shadowstep.locator import LocatorConverter

converter = LocatorConverter()

# Dict -> XPath
dict_loc = {"text": "Settings", "class": "android.widget.TextView"}
xpath = converter.dict_to_xpath(dict_loc)
# '//*[@text="Settings" and @class="android.widget.TextView"]'

# Dict -> UiSelector
ui_selector = converter.dict_to_ui_selector(dict_loc)
# 'new UiSelector().text("Settings").className("android.widget.TextView")'

# UiSelector -> Dict
ui_loc = UiSelector().text("Settings").clickable(True)
dict_loc = converter.ui_selector_to_dict(str(ui_loc))
# {"text": "Settings", "clickable": True}

# UiSelector -> XPath
xpath = converter.ui_selector_to_xpath(str(ui_loc))

# XPath -> Dict
xpath = '//android.widget.TextView[@text="Settings"]'
dict_loc = converter.xpath_to_dict(xpath)
# {"text": "Settings", "class": "android.widget.TextView"}

# XPath -> UiSelector
ui_selector = converter.xpath_to_ui_selector(xpath)
```

---

### Terminal

Two options for command execution: via Appium (Terminal) and via SSH (Transport).

#### Terminal (via Appium)

```python
# Terminal is created automatically on connect()
terminal = app.terminal

# Shell commands
result = terminal.adb_shell(command="dumpsys", args="window windows")
result = terminal.adb_shell(command="pm", args="list packages")

# Application management
terminal.start_activity(package="com.android.settings", activity=".Settings")
terminal.close_app(package="com.android.settings")
terminal.reboot_app(package="com.android.settings", activity=".Settings")

package = terminal.get_current_app_package()

# Check installation
is_installed = terminal.is_app_installed(package="com.android.settings")
terminal.uninstall_app(package="com.android.settings")

# Buttons
terminal.press_home()
terminal.press_back()
terminal.press_menu()

# Input
terminal.input_keycode(keycode="KEYCODE_ENTER")
terminal.input_keycode_num_(num=5)
terminal.input_text(text="hello")

# Gestures
terminal.tap(x=500, y=1000)
terminal.swipe(start_x=500, start_y=1000, end_x=500, end_y=500, duration=300)
terminal.swipe_right_to_left(duration=300)
terminal.swipe_left_to_right()
terminal.swipe_top_to_bottom()
terminal.swipe_bottom_to_top()

# VPN
is_connected = terminal.check_vpn(ip_address="192.168.1.1")

# Processes
pid = terminal.know_pid(name="logcat")
exists = terminal.is_process_exist(name="logcat")
terminal.kill_by_pid(pid=1234)
terminal.kill_by_name(name="logcat")
terminal.kill_all(name="logcat")
terminal.run_background_process(command="logcat", args="-v time", process="logcat")

# Files
terminal.delete_file_from_internal_storage(path="/sdcard", filename="test.txt")
terminal.delete_files_from_internal_storage(path="/sdcard/Download")

# Video
terminal.record_video(time_limit=180000)
video_bytes = terminal.stop_video()

# System information
terminal.reboot()
width, height = terminal.get_screen_resolution()
properties = terminal.get_prop()
hardware = terminal.get_prop_hardware()
model = terminal.get_prop_model()
serial = terminal.get_prop_serial()
build = terminal.get_prop_build()
device = terminal.get_prop_device()

# Packages
packages = terminal.get_packages()

# WiFi IP
wifi_ip = terminal.get_wifi_ip()

# Paste text (via clipboard)
terminal.past_text(text="Hello World", tries=3)
```

#### Transport (via SSH)

**IMPORTANT:** SSH was removed from Terminal and is now only available via Transport.

```python
# Transport is created when connect() is called with SSH credentials
app.connect(
    capabilities={...},
    server_ip="192.168.1.100",
    ssh_user="user",
    ssh_password="password"
)

# Access SSH client (paramiko)
ssh_client = app.transport.ssh

# Execute command
stdin, stdout, stderr = ssh_client.exec_command("adb devices")
output = stdout.read().decode()

# Access SCP client
scp_client = app.transport.scp

# Upload file to server
scp_client.put("local_file.txt", remote_path="/tmp/remote_file.txt")

# Download file from server
scp_client.get("/tmp/remote_file.txt", local_path="downloaded_file.txt")

# Recursive folder upload
scp_client.put("local_folder", remote_path="/tmp/remote_folder", recursive=True)
```

#### ADB (local)

```python
# ADB is created automatically on connect()
adb = app.adb

# Get device list
devices = adb.get_devices()  # ["emulator-5554", "192.168.1.100:5555"]

# Device model
model = adb.get_device_model(udid="emulator-5554")

# Push/Pull files
adb.push(source="local.txt", destination="/sdcard/file.txt", udid="emulator-5554")
adb.pull(source="/sdcard/file.txt", destination="local.txt", udid="emulator-5554")

# Install APK
adb.install_app(source="app.apk", udid="emulator-5554")
adb.is_app_installed(package="com.example.app")
adb.uninstall_app(package="com.example.app")

# Application management
adb.start_activity(package="com.android.settings", activity=".Settings")
adb.get_current_activity()
adb.get_current_package()
adb.close_app(package="com.android.settings")
adb.reboot_app(package="com.android.settings", activity=".Settings")

# Buttons
adb.press_home()
adb.press_back()
adb.press_menu()

# Input
adb.input_keycode(keycode="KEYCODE_ENTER")
adb.input_keycode_num_(num=5)
adb.input_text(text="hello")

# Gestures
adb.tap(x=500, y=1000)
adb.swipe(start_x=500, start_y=1000, end_x=500, end_y=500, duration=300)

# VPN
adb.check_vpn(ip_address="192.168.1.1")

# Processes
adb.stop_logcat()
adb.is_process_exist(name="logcat")
adb.run_background_process(command="logcat -v time &", process="logcat")
pid = adb.know_pid(name="logcat")
adb.kill_by_pid(pid=1234)
adb.kill_by_name(name="logcat")
adb.kill_all(name="logcat")

# ADB server
adb.reload_adb()

# Files
adb.delete_files_from_internal_storage(path="/sdcard/Download")

# Video
process = adb.record_video(path="/sdcard/Movies", filename="recording.mp4")
# ... wait ...
adb.stop_video()
adb.pull_video(source="/sdcard/Movies", destination="./videos", delete=True)

# System information
adb.reboot()
width, height = adb.get_screen_resolution()
packages = adb.get_packages_list()

# Execute arbitrary command
output = adb.execute(command="shell getprop ro.build.version.release")
```

---

### Logcat

Android log capture via WebSocket with filtering and automatic reconnection.

```python
# Start log capture
app.start_logcat(filename="logcat.log")

# With tag filtering
app._logcat.filters = ["ActivityManager", "System.out"]
app.start_logcat(filename="filtered_logcat.log")

# Stop capture
app.stop_logcat()

# Context manager
with app._logcat:
    app._logcat.start(filename="logcat.log")
    # ... run tests ...
    # automatically stops on exit

# Configuration
logcat = app._logcat
logcat.filters = ["MyApp", "Firebase"]  # filter by tags
# logcat works in background thread with auto-reconnection
```

**Features:**
- Works via WebSocket to Appium server
- Automatic reconnection on connection drops
- Buffered file writing (buffering=1)
- Tag filtering with regex
- Graceful shutdown with proper file closing

---

### Image Recognition

Find elements by images using OpenCV.

```python
# Get ShadowstepImage
image_path = "tests/_test_data/connected_devices.png"
image = app.get_image(
    image=image_path,
    threshold=0.5,  # match accuracy [0-1]
    timeout=5.0     # search timeout
)

# Can pass bytes, ndarray, PIL.Image or file path
from PIL import Image
pil_image = Image.open("icon.png")
image = app.get_image(image=pil_image, threshold=0.8)

# Tap on image
image.tap()

# Wait for appearance
image.wait(timeout=10)

# Check visibility
if image.is_visible():
    print("Image found on screen")

# Coordinates
x, y = image.get_center()
coords = image.get_coordinates()

# Multiple search
images = app.get_images(image=image_path, threshold=0.7)
for img in images:
    img.tap()

# Screenshot + matching
screenshot = app.get_screenshot()  # bytes
# image.match(screenshot) - internal method
```

---

### Page Object Generator

Automatic generation of Page Object classes from UI XML dump.

```python
from shadowstep.page_object import (
    PageObjectGenerator,
    PageObjectParser,
    UiElementNode
)

# 1. Get XML page source
xml_source = app.driver.page_source

# 2. Parse XML into element tree
parser = PageObjectParser()
ui_tree: UiElementNode = parser.parse(xml_source)

# 3. Generate Page Object
generator = PageObjectGenerator()
output_path, class_name = generator.generate(
    ui_element_tree=ui_tree,
    output_dir="./generated_pages",
    filename_prefix="page_"
)

print(f"Generated: {output_path}")
print(f"Class: {class_name}")

# Result: page_settings.py
# class PageSettings(PageBaseShadowstep):
#     @property
#     def title(self) -> Element: ...
#     @property
#     def network_internet(self) -> Element: ...
#     ...
```

**Capabilities:**
- Auto-detection of title, recycler
- Recognition of anchor-switcher pairs (for switch elements)
- Recognition of anchor-summary pairs
- Filtering structural containers
- Generation of navigation methods
- Uses Jinja2 templates
- Supports translator (optional)

**Page Object Merger:**

```python
from shadowstep.page_object import PageObjectMerger

# Merge multiple dumps of same screen
merger = PageObjectMerger()

# Add dumps
merger.add_dump(xml_source_1)
merger.add_dump(xml_source_2)
merger.add_dump(xml_source_3)

# Get merged tree
merged_tree = merger.merge()

# Generate from merged tree
generator.generate(
    ui_element_tree=merged_tree,
    output_dir="./pages"
)
```

**Page Object Test Generator:**

```python
from shadowstep.page_object import PageObjectTestGenerator

# Generate tests for Page Object
test_generator = PageObjectTestGenerator()
test_path = test_generator.generate(
    page_class_name="PageSettings",
    output_dir="./tests",
    page_module="pages.page_settings"
)
```

---

## 💡 Usage Examples

### Basic Testing

```python
from shadowstep import Shadowstep

def test_settings_navigation():
    app = Shadowstep()
    app.connect(
        capabilities={
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "emulator-5554",
            "appium:appPackage": "com.android.settings",
            "appium:appActivity": ".Settings",
        }
    )
    
    # Find element
    network = app.get_element({
        "text": "Network & internet",
        "resource-id": "android:id/title"
    })
    
    # Check visibility
    assert network.is_visible()
    
    # Interact
    network.tap()
    
    # Verify navigation
    title = app.get_element({"text": "Network & internet"})
    assert title.wait_visible(timeout=5)
    
    app.disconnect()
```

### Working with Forms

```python
def test_search_form():
    app = Shadowstep()
    # ... connect ...
    
    # Find search field
    search_field = app.get_element({
        "resource-id": "com.android.quicksearchbox:id/search_widget_text"
    })
    search_field.tap()
    
    # Wait for input to appear
    search_input = app.get_element({
        "resource-id": "com.android.quicksearchbox:id/search_src_text"
    })
    search_input.wait_visible(timeout=3)
    
    # Enter text
    search_input.send_keys("test query")
    
    # Check value
    assert "test query" in search_input.text
    
    # Clear
    search_input.clear()
    assert search_input.text == ""
```

### Scrolling and Search

```python
def test_scroll_to_element():
    app = Shadowstep()
    # ... connect to Settings ...
    
    # Get scrollable container
    recycler = app.get_element({
        "resource-id": "com.android.settings:id/settings_homepage_container"
    })
    
    # Scroll to element
    about_phone = recycler.scroll_to_element(
        locator={"text": "About phone"},
        max_swipes=30
    )
    
    # Check element found
    assert about_phone.is_visible()
    
    # Interact
    about_phone.tap()
```

### DOM Navigation

```python
def test_dom_navigation():
    app = Shadowstep()
    # ... connect to Settings ...
    
    # Find anchor element
    network = app.get_element({
        "text": "Network & internet",
        "resource-id": "android:id/title"
    })
    
    # Find sibling (summary)
    summary = network.get_sibling({
        "resource-id": "android:id/summary"
    })
    print(f"Summary: {summary.text}")
    
    # Get parent
    parent = network.get_parent()
    print(f"Parent class: {parent.class_name}")
    
    # Find cousin (same level, different parent)
    cousin = network.get_cousin(
        cousin_locator={"resource-id": "android:id/summary"},
        depth_to_parent=1
    )
```

### Multiple Elements

```python
def test_multiple_elements():
    app = Shadowstep()
    # ... connect to Settings ...
    
    # Find all TextView
    textviews = app.get_elements({
        "class": "android.widget.TextView"
    })
    
    # Process each
    for tv in textviews:
        text = tv.text
        if text and "Settings" not in text:
            print(f"Found: {text}")
```

### Gestures and Animations

```python
def test_gestures():
    app = Shadowstep()
    # ... connect ...
    
    # Get element
    icon = app.get_element({"content-desc": "Gallery"})
    
    # Remember position
    x1, y1 = icon.get_center()
    
    # Drag
    icon.drag(end_x=x1 + 200, end_y=y1, speed=2500)
    
    # Check new position
    x2, y2 = icon.get_center()
    assert x2 > x1
    
    # Drag back
    icon.drag(end_x=x1, end_y=y1, speed=2500)
    
    # Fling gesture
    recycler = app.get_element({"resource-id": "recycler_view"})
    recycler.fling_up(speed=5000)
```

### Page Object with Navigation

```python
from shadowstep import PageBaseShadowstep, Element

class PageSettings(PageBaseShadowstep):
    @property
    def edges(self):
        return {
            "PageNetwork": self.to_network,
            "PageApps": self.to_apps,
        }
    
    @property
    def recycler(self) -> Element:
        return self.shadowstep.get_element({
            "resource-id": "com.android.settings:id/settings_homepage_container"
        })
    
    @property
    def network(self) -> Element:
        return self.recycler.scroll_to_element({"text": "Network & internet"})
    
    @property
    def apps(self) -> Element:
        return self.recycler.scroll_to_element({"text": "Apps"})
    
    def to_network(self):
        self.network.tap()
        return self.shadowstep.get_page("PageNetwork")
    
    def to_apps(self):
        self.apps.tap()
        return self.shadowstep.get_page("PageApps")
    
    def is_current_page(self) -> bool:
        title = self.shadowstep.get_element({"text": "Settings"})
        return title.is_visible()

# Test
def test_page_navigation():
    app = Shadowstep()
    # ... connect ...
    
    settings = app.get_page("PageSettings")
    assert settings.is_current_page()
    
    # Automatic navigation via Navigator
    network = settings.to_network()
    assert network.is_current_page()
```

### Screenshots and Logs

```python
def test_with_logs_and_screenshots():
    app = Shadowstep()
    # ... connect ...
    
    # Start logcat
    app.start_logcat(filename="test_logs.log")
    
    try:
        # Perform actions
        element = app.get_element({"text": "Settings"})
        element.tap()
        
        # Take screenshot
        app.save_screenshot(path="./screenshots", filename="settings.png")
        
        # Element screenshot
        element.save_screenshot("./screenshots/element.png")
        
    finally:
        # Stop logcat
        app.stop_logcat()
        app.disconnect()
```

### Working with Images

```python
def test_image_recognition():
    app = Shadowstep()
    # ... connect ...
    
    # Search by image
    icon = app.get_image(
        image="icons/settings_icon.png",
        threshold=0.8,
        timeout=10
    )
    
    # Check visibility
    if icon.is_visible():
        # Tap on image
        icon.tap()
    
    # Coordinates
    x, y = icon.get_center()
    print(f"Icon center: {x}, {y}")
```

### Working with ADB and SSH

```python
def test_adb_commands():
    app = Shadowstep()
    # ... connect ...
    
    # Via Terminal (Appium)
    app.terminal.start_activity(
        package="com.android.settings",
        activity=".Settings"
    )
    
    # Check current application
    package = app.terminal.get_current_app_package()
    assert "settings" in package.lower()
    
    # Via local ADB
    devices = app.adb.get_devices()
    print(f"Connected devices: {devices}")
    
    model = app.adb.get_device_model(udid="emulator-5554")
    print(f"Device model: {model}")

def test_ssh_commands():
    app = Shadowstep()
    app.connect(
        capabilities={...},
        server_ip="192.168.1.100",
        ssh_user="user",
        ssh_password="password"
    )
    
    # SSH commands via transport
    stdin, stdout, stderr = app.transport.ssh.exec_command("adb devices")
    output = stdout.read().decode()
    print(output)
    
    # SCP files
    app.transport.scp.put("local.txt", remote_path="/tmp/remote.txt")
    app.transport.scp.get("/tmp/remote.txt", local_path="downloaded.txt")
```

---

## 🛠️ Quality Tools

The project uses modern tools to ensure code quality:

### Linters and Formatters

```bash
# Ruff - fast linter and formatter
uv run ruff check .
uv run ruff format .

# Pyright - strict typing
uv run pyright
```

### Testing

```bash
# Run all tests
uv run pytest

# Only unit tests
uv run pytest tests/test_unit

# Only integration tests
uv run pytest tests/test_integro

# With coverage
uv run pytest --cov=shadowstep --cov-report=html

# With rerun failed
uv run pytest --reruns 3 --reruns-delay 1
```

### Pre-commit Hooks

```bash
# Install
uv run pre-commit install

# Manual run
uv run pre-commit run --all-files
```

### Configuration

Tool settings are in `pyproject.toml`:

- **Ruff:** `select = ["ALL"]` with docstring style conflict ignoring
- **Pyright:** `typeCheckingMode = "strict"` for maximum type safety
- **Pytest:** logging, short traceback, setup show

---

## 📖 Additional Information

### Supported Python Versions
- Python 3.9+
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

### Links
- [GitHub Repository](https://github.com/molokov-klim/Appium-Python-Client-Shadowstep)
- [Appium Documentation](https://appium.io/docs/en/latest/)
- [UiAutomator2 Driver](https://github.com/appium/appium-uiautomator2-driver)

### License
MIT License

---

## 🤝 Contributing

The project follows:
- **Clean Architecture** — separation of concerns
- **Clean Code** — readability and maintainability
- **Best Practices** — design patterns
- **Type Safety** — strict typing (Pyright strict mode)
- **PEP 8** — Python coding style

When developing, use:
- Strict typing with `typing`
- Docstrings in English
- Comments in English
- Type hints for all functions and methods
- Pyright strict mode
- Ruff for linting

---

**Author:** Molokov Klim  
**Email:** ultrakawaii9654449192@gmail.com
