"""
Да, ты прав — текущая реализация `Terminal` перегружена и нарушает принцип единственной ответственности (SRP из SOLID), потому что:

- часть методов использует **Appium driver (`self.driver`)**, что не требует никакой `transport`;
- другая часть (например, `push`, `install_app`) использует **`self.transport` и SSH**, что тянет за собой зависимости и обязательность наличия SSH-соединения.

---

### 💡 Анализ

**Методы, зависящие от `self.transport`:**
- `push`
- `install_app`
- `get_package_manifest` (через `pull_package`)
- всё, что использует `scp` и `ssh.exec_command`

**Методы, не зависящие от SSH:**
- `adb_shell`
- `pull` (через Appium `mobile: pullFile`)
- `tap`, `swipe`, `input_text`, `press_*`
- `record_video`, `stop_video`
- `get_prop`, `reboot`, `check_vpn`
- все `get_prop_*`, `get_packages`, `get_package_path` и др.

---

### ✅ Рекомендации

1. **Разделить Terminal на 2 компонента:**
   - `TerminalInterface` (всё, что работает через Appium `driver`)
   - `RemoteTerminal` или `SshTerminal` (всё, что требует `transport` и `ssh`)

2. **Сделать `TerminalInterface` базовым классом, или отдельной обёрткой вокруг `driver`:**
   ```python
   class TerminalInterface:
       def __init__(self, driver): ...
       def adb_shell(self, ...) -> Any: ...
       def swipe(...) -> bool: ...
       ...
   ```

3. **Добавить в `Shadowstep` выбор реализации:**
   ```python
   if self.ssh_login and self.ssh_password:
       self.terminal = RemoteTerminal(...)
   else:
       self.terminal = TerminalInterface(...)
   ```

4. **Удалить `self.transport` из `TerminalInterface` — это явно не его зона ответственности.**

5. **Методы вроде `get_package_manifest`, `pull_package` можно обернуть в отдельный `ApkAnalyzer`, а не пихать в `Terminal`.**

---

### 💭 Плюсы

- Нет избыточной зависимости от `Transport`, если она не нужна
- Упрощается тестирование и CI: `TerminalInterface` будет работать локально, без SSH
- Код станет понятнее и легче расширяем


Отлично! Вот предложенный **план рефакторинга** и **каркас классов**, чтобы разделить `Terminal` на "чистый" `TerminalInterface` (через Appium) и `RemoteTerminal` (через SSH).

---

## 🔧 ПЛАН

### 1. 📁 Структура
Разнести классы по модулям:
```
shadowstep/
├── terminal_interface.py        ← Только Appium (driver)
├── terminal_remote.py           ← SSH и SCP (transport)
├── apk_analyzer.py              ← get_package_manifest и т.п.
```

---

### 2. ✅ Новый базовый интерфейс: `TerminalInterface`

```python
from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchDriverException, InvalidSessionIdException

class TerminalInterface:
    def __init__(self, driver: WebDriver, base=None):
        self.driver = driver
        self.base = base

    def adb_shell(self, command: str, args: str = "", tries: int = 3):
        for _ in range(tries):
            try:
                return self.driver.execute_script("mobile: shell", {"command": command, "args": [args]})
            except (NoSuchDriverException, InvalidSessionIdException):
                if self.base:
                    self.base.reconnect()
```

> Остальные методы (`tap`, `swipe`, `press_home`, `get_prop`, `record_video`, и т.д.) — добавляются сюда, без `transport`.

---

### 3. 🌐 Расширенный интерфейс: `RemoteTerminal`

```python
from .terminal_interface import TerminalInterface
from .terminal import Transport  # или как у тебя определён transport

class RemoteTerminal(TerminalInterface):
    def __init__(self, driver, transport: Transport, base=None):
        super().__init__(driver, base)
        self.transport = transport

    def push(self, source_path: str, remote_server_path: str, filename: str, destination: str, udid: str) -> bool:
        # Твой push через ssh
        ...
```

---

### 4. 🧠 Автовыбор реализации

```python
def create_terminal(base) -> TerminalInterface:
    if base.ssh_login and base.ssh_password:
        return RemoteTerminal(driver=base.driver, transport=base.transport, base=base)
    else:
        return TerminalInterface(driver=base.driver, base=base)
```

---

### 5. 📦 Вынос `get_package_manifest` → `ApkAnalyzer`

```python
class ApkAnalyzer:
    @staticmethod
    def get_manifest(apk_path: str) -> dict:
        ...
```

Или можно передавать `TerminalInterface` внутрь `ApkAnalyzer`, если тебе нужно будет `pull_package`.

---

## 🚀 Результат

- `TerminalInterface` — компактный, независимый от SSH, можно использовать в любом окружении.
- `RemoteTerminal` — всё, что требует SCP или SSH.
- Чистое разделение ответственности (SRP).
- Легко мокается, тестируется и расширяется.
- Умный выбор реализации без "выпендрежа".



"""