# Shadowstep (в разработке)

Shadowstep — модульный фреймворк для UI‑автоматизации Android‑приложений поверх Appium.

- Ленивый поиск и взаимодействие с элементами (драйвер дергается только при необходимости)
- Движок навигации PageObject с авто‑обнаружением страниц
- Логика переподключения при потере сессии
- Интеграция с ADB и «терминалом» Appium/SSH
- DSL‑утверждения для удобных проверок (`should.have`, `should.be`)
- Работа с изображениями на экране 

---

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Настройка тестов (Pytest)](#настройка-тестов-pytest)
- [API элемента (`Element`)](#api-элемента-element)
- [Коллекции элементов (`Elements`)](#коллекции-элементов-elements)
- [DSL‑проверки](#dsl-проверки)
- [Page Object и навигация](#page-object-и-навигация)
- [ADB и Терминал](#adb-и-терминал)
- [Работа с изображениями](#работа-с-изображениями)
- [Логи logcat](#логи-logcat)
- [Архитектурные заметки](#архитектурные-заметки)
- [Ограничения](#ограничения)
- [Лицензия](#лицензия)

---

## Установка

```bash
pip install appium-python-client-shadowstep
```

---

## Быстрый старт

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

- Можно передать `command_executor` напрямую (например, `http://127.0.0.1:4723/wd/hub`), тогда `server_ip/port` не обязательны.
- Если передать `capabilities` как `dict`, они будут сконвертированы во внутренний `UiAutomator2Options`.

---

## Настройка тестов (Pytest)

Пример с фикстурой для одной сессии:

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

Запуск теста:

```bash
pytest -svl --log-cli-level INFO --tb=short tests/test_shadowstep.py
```

Подготовка Appium‑сервера локально:

```bash
npm i -g appium@next
appium driver install uiautomator2
appium server -ka 800 --log-level debug -p 4723 -a 0.0.0.0 -pa /wd/hub --allow-insecure=adb_shell
```

---

## API элемента (`Element`)

```python
el = app.get_element({"resource-id": "android:id/title"})
el.tap()
el.text
el.get_attribute("enabled") 
```

Цепочки вызовов
```python
el = app.get_element({"resource-id": "android:id/title"})
el.zoom().click()
```

Ленивое перемещение по DOM (декларативно):

```python
el = app.get_element({'class': 'android.widget.ImageView'}).\
         get_parent().\
         get_sibling({'resource-id': 'android:id/summary'}).\
         get_cousin(cousin_locator={'resource-id': 'android:id/summary'}).\
         get_element({"resource-id": "android:id/switch_widget"})
```

Ключевые возможности:

- Ленивое вычисление: реальный поиск (`find_element`) происходит при первом взаимодействии c элементом:
el = app.get_element({'class': 'android.widget.ImageView'})      # find_element не вызывается
el.swipe_left()     # find_element вызывается здесь

- Локаторы: `dict` и XPath (для кортежей по умолчанию используется стратегия XPath)
- Повторы и авто‑переподключение при падении сессии
- Богатый набор методов: `tap`, `click`, `scroll_to`, `get_sibling`, `get_parent`, `drag_to`, `send_keys`, `wait_visible`, и др.

---

## DSL‑проверки

```python
item = app.get_element({'text': 'Network & internet'})
item.should.have.text("Network & internet").have.resource_id("android:id/title")
item.should.be.visible()
item.should.not_be.focused()
```

См. больше примеров в `tests/test_element_should.py`.

---

## Page Object и навигация

Базовый класс страницы — `PageBaseShadowstep`. 
Страница должна:

- наследоваться от `PageBaseShadowstep`
- иметь имя класса, начинающееся с `Page`
- реализовывать свойство `edges: Dict[str, Callable[[], PageBaseShadowstep]]` — рёбра графа навигации
- реализовывать метод `is_current_page()`

Пример страницы:

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

Авто‑обнаружение страниц:

- классы, наследующие `PageBaseShadowstep`, название начинается с `Page`
- файлы `page*.py` (как правило, `pages/page_*.py`) в путях проекта
- страницы регистрируются автоматически при создании `Shadowstep`

Навигация:

```python
self.shadowstep.navigator.navigate(from_page=self.page_main, to_page=self.page_display)
assert self.page_display.is_current_page()
```

---

## ADB и Терминал

Два способа низкоуровневых действий:

- `app.adb.*` — прямой вызов ADB через `subprocess` (подходит для локального запуска)
- `app.terminal.*` — выполнение `mobile: shell` через Appium или через SSH‑транспорт (если заданы `ssh_user/ssh_password` при `connect()`)

Примеры ADB:

```python
app.adb.press_home()
app.adb.install_app(source="/path/app.apk", udid="192.168.56.101:5555")
app.adb.input_text("hello")
```

Примеры Терминала:

```python
app.terminal.start_activity(package="com.example", activity=".MainActivity")
app.terminal.tap(x=1345, y=756)
app.terminal.past_text(text='hello')
```

---

## Работа с изображениями

```python
image = app.get_image(image="tests/test_data/connected_devices.png", threshold=0.5, timeout=3.0)
assert image.is_visible()
image.tap()
image.scroll_down(max_attempts=3)
image.zoom().unzoom().drag(to=(100, 100))
```

Под капотом используются `opencv-python`, `numpy`, `Pillow`.

---

## Логи logcat

```python
app.start_logcat("device.logcat")
# ... шаги теста ...
app.stop_logcat()
```

---

## Архитектурные заметки

- Дерево элементов не извлекается заранее
- Переподключение при потере сессии (`InvalidSessionIdException`, `NoSuchDriverException`)
- Совместим с Pytest и CI/CD
- Модульная архитектура: `element`, `elements`, `navigator`, `terminal`, `image`, `utils`

---

## Ограничения

- Поддерживается только Android (нет iOS и Web)

---

## Лицензия

MIT — см. `LICENSE`.
