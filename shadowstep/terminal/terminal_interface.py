# shadowstep/terminal/terminal_interface.py
"""Yes, you're right — current `Terminal` implementation is overloaded and violates Single Responsibility Principle (SRP from SOLID), because:

- some methods use **Appium driver (`self.driver`)**, which doesn't require any `transport`;
- other part (e.g., `push`, `install_app`) uses **`self.transport` and SSH**, which brings dependencies and mandatory SSH connection requirement.

---

### 💡 Analysis

**Methods depending on `self.transport`:**
- `push`
- `install_app`
- `get_package_manifest` (via `pull_package`)
- everything that uses `scp` and `ssh.exec_command`

**Methods not depending on SSH:**
- `adb_shell`
- `pull` (via Appium `mobile: pullFile`)
- `tap`, `swipe`, `input_text`, `press_*`
- `record_video`, `stop_video`
- `get_prop`, `reboot`, `check_vpn`
- all `get_prop_*`, `get_packages`, `get_package_path` etc.

---

### ✅ Recommendations

1. **Split Terminal into 2 components:**
   - `TerminalInterface` (everything that works via Appium `driver`)
   - `RemoteTerminal` or `SshTerminal` (everything that requires `transport` and `ssh`)

2. **Make `TerminalInterface` base class, or separate wrapper around `driver`:**
   ```python
   class TerminalInterface:
       def __init__(self, driver): ...
       def adb_shell(self, ...) -> Any: ...
       def swipe(...) -> bool: ...
       ...
   ```

3. **Add implementation choice to `Shadowstep`:**
   ```python
   if self.ssh_login and self.ssh_password:
       self.terminal = RemoteTerminal(...)
   else:
       self.terminal = TerminalInterface(...)
   ```

4. **Remove `self.transport` from `TerminalInterface` — this is clearly not its responsibility.**

5. **Methods like `get_package_manifest`, `pull_package` can be wrapped in separate `ApkAnalyzer`, not stuffed into `Terminal`.**

---

### 💭 Benefits

- No excessive dependency on `Transport` if not needed
- Testing and CI simplified: `TerminalInterface` will work locally, without SSH
- Code becomes clearer and easier to extend


Great! Here's proposed **refactoring plan** and **class skeleton** to split `Terminal` into "clean" `TerminalInterface` (via Appium) and `RemoteTerminal` (via SSH).

---

## 🔧 PLAN

### 1. 📁 Structure
Split classes by modules:
```
shadowstep/
├── terminal_interface.py        ← Only Appium (driver)
├── terminal_remote.py           ← SSH and SCP (transport)
├── apk_analyzer.py              ← get_package_manifest etc.
```

---

### 2. ✅ New base interface: `TerminalInterface`

```python
from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchDriverException, InvalidSessionIdException

class TerminalInterface:
    def __init__(self, driver: WebDriver, shadowstep=None):
        self.driver = driver
        self.shadowstep = shadowstep

    def adb_shell(self, command: str, args: str = "", tries: int = 3):
        for _ in range(tries):
            try:
                return self.driver.execute_script("mobile: shell", {"command": command, "args": [args]})
            except (NoSuchDriverException, InvalidSessionIdException):
                if self.shadowstep:
                    self.shadowstep.reconnect()
```

> Other methods (`tap`, `swipe`, `press_home`, `get_prop`, `record_video`, etc.) — add here, without `transport`.

---

### 3. 🌐 Extended interface: `RemoteTerminal`

```python
from .terminal_interface import TerminalInterface
from .terminal import Transport  # or however you define transport

class RemoteTerminal(TerminalInterface):
    def __init__(self, driver, transport: Transport, shadowstep=None):
        super().__init__(driver, shadowstep)
        self.transport = transport

    def push(self, source_path: str, remote_server_path: str, filename: str, destination: str, udid: str) -> bool:
        # Your push via ssh
        ...
```

---

### 4. 🧠 Auto-selection of implementation

```python
def create_terminal(shadowstep) -> TerminalInterface:
    if shadowstep.ssh_login and shadowstep.ssh_password:
        return RemoteTerminal(driver=shadowstep.driver, transport=shadowstep.transport, shadowstep=shadowstep)
    else:
        return TerminalInterface(driver=shadowstep.driver, shadowstep=shadowstep)
```

---

### 5. 📦 Extract `get_package_manifest` → `ApkAnalyzer`

```python
class ApkAnalyzer:
    @staticmethod
    def get_manifest(apk_path: str) -> dict:
        ...
```

Or you can pass `TerminalInterface` inside `ApkAnalyzer` if you need `pull_package`.

---

## 🚀 Result

- `TerminalInterface` — compact, SSH-independent, can be used in any environment.
- `RemoteTerminal` — everything that requires SCP or SSH.
- Clean separation of responsibilities (SRP).
- Easy to mock, test and extend.
- Smart implementation choice without "showing off".



"""
