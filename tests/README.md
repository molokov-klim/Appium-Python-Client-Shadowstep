# 📋 МАНИФЕСТ ТЕСТИРОВАНИЯ SHADOWSTEP

> **Принцип:** Тестируй ПОВЕДЕНИЕ, а не реализацию. Тестируй КОНТРАКТЫ, а не детали.

---

## 🎯 ПИРАМИДА ТЕСТИРОВАНИЯ

```
                E2E / Smoke
               ╱────────────╲      5-10%
              ╱  Критичные   ╲     
             ╱    flows с      ╲   • Полные user scenarios
            ╱  реальным Appium  ╲  • Regression suite
           ╱──────────────────────╲ • Медленные (минуты)
          ╱                        ╲
         ╱──────────────────────────╲
        ╱                            ╲
       ╱       Integration Tests      ╲   20-25%
      ╱   Реальный Appium (мок driver) ╲
     ╱     Проверка границ модулей      ╲  • Element + Appium
    ╱────────────────────────────────────╲ • Terminal + ADB  
   ╱                                      ╲ • Средняя скорость
  ╱────────────────────────────────────────╲
 ╱                                          ╲
╱─────────────────────────────────────────────╲
╲─────────────────────────────────────────────╱
 ╲───────────────────────────────────────────╱
  ╲───────────────────────────────────────╱
   ╲─────────────────────────────────────╱    Unit Tests
    ╲───────────────────────────────────╱     75-80%
     ╲─────────────────────────────────╱
      ╲───────────────────────────────╱      • Изолированные
       ╲─────────────────────────────╱       • С моками
        ╲───────────────────────────╱        • Мгновенные (<1с)
         ╲─────────────────────────╱         • Детальные проверки
          ╲───────────────────────╱
           ╲─────────────────────╱
            ╲───────────────────╱
             ╲─────────────────╱
```

**Целевое распределение:** 75% unit / 20% integration / 5% e2e

---

## 📊 ЦЕЛЕВЫЕ МЕТРИКИ

```
╔═══════════════════════════════════════════════════════════╗
║  ПОКАЗАТЕЛЬ                    ЦЕЛЕВОЕ ЗНАЧЕНИЕ          ║
╠═══════════════════════════════════════════════════════════╣
║  Общее test coverage           ≥ 90%                     ║
║  Unit tests                     150-170 тестов (75%)     ║
║  Integration tests              40-50 тестов (20%)       ║
║  E2E/Smoke tests                10-15 тестов (5%)        ║
║  Время выполнения unit          < 30 секунд              ║
║  Время выполнения integration   < 5 минут                ║
║  Время выполнения полного suite < 6-7 минут             ║
╚═══════════════════════════════════════════════════════════╝
```

### **Coverage по модулям (минимальные требования):**

```
КРИТИЧНЫЕ (100%):
├─ locator/converter/ui_selector_lexer.py      100%
├─ locator/converter/ui_selector_parser.py     100%
└─ locator/converter/ui_selector_ast.py        100%

ВАЖНЫЕ (95%+):
├─ locator/converter/locator_converter.py      95%
├─ locator/converter/*_converter.py            95%
├─ exceptions/shadowstep_exceptions.py         95%
└─ element/element.py (public methods)         95%

СТАНДАРТНЫЕ (85-90%):
├─ element/actions.py                          90%
├─ element/gestures.py                         90%
├─ element/properties.py                       90%
├─ element/dom.py                              90%
├─ element/waiting.py                          90%
├─ navigator/navigator.py                      90%
├─ navigator/page_graph.py                     85%
├─ page_object/page_object_generator.py        85%
└─ page_object/page_object_parser.py           85%

БАЗОВЫЕ (70-80%):
├─ utils/                                      80%
├─ decorators/                                 80%
├─ terminal/                                   75%
├─ image/                                      70%
└─ logcat/                                     70%
```

---

## 🏗️ СТРУКТУРА ТЕСТОВ

### **Обязательная организация:**

```
tests/
├─ test_unit/              # 75% всех тестов, мгновенное выполнение
│  ├─ test_locator/        # 100% coverage парсера и конверторов
│  ├─ test_element/        # Моки WebElement, детальные проверки
│  ├─ test_navigator/      # Моки графа и страниц
│  ├─ test_page_object/    # XML фикстуры, проверка логики
│  ├─ test_exceptions/     # Все 88 exception классов
│  ├─ test_utils/          # Чистые функции
│  └─ test_decorators/     # Декораторы с моками
│
├─ test_integro/           # 20% всех тестов, реальный Appium
│  ├─ test_element/        # Реальные взаимодействия с UI
│  ├─ test_terminal/       # ADB/AAPT/SSH команды
│  ├─ test_navigator/      # Реальная навигация
│  ├─ test_locator/        # Smoke tests (конверторы работают)
│  ├─ test_page_object/    # Реальный page source
│  └─ test_*_integro.py    # Интеграционные проверки
│
└─ test_e2e/               # 5% тестов (опционально, можно выделить позже)
   └─ test_critical_flows.py   # Полные user scenarios
```

---

## 📜 ПРАВИЛА НАПИСАНИЯ ТЕСТОВ

### **ПРАВИЛО 1: Unit тесты**

```
ЧТО ТЕСТИРУЕМ В UNIT:
✅ Чистая логика (парсинг, конвертация, валидация)
✅ Публичный API (методы классов)
✅ Edge cases (пустой ввод, None, некорректные данные)
✅ Exception handling
✅ Утилиты и хелперы

КАК ТЕСТИРУЕМ:
✅ Моки для внешних зависимостей (WebDriver, WebElement)
✅ Фикстуры для тестовых данных (XML, словари)
✅ Параметризация (@pytest.mark.parametrize)
✅ Изоляция (без сети, БД, файловой системы)

ОБЯЗАТЕЛЬНО:
✅ Время выполнения: < 100ms на тест
✅ Нет реальных Appium/Selenium вызовов
✅ Нет sleep/time.sleep
✅ Тестируем контракт, не реализацию

ПРИМЕР:
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

### **ПРАВИЛО 2: Integration тесты**

```
ЧТО ТЕСТИРУЕМ В INTEGRATION:
✅ Взаимодействие Element с реальным Appium
✅ ADB/AAPT команды на реальном устройстве
✅ Terminal команды (SSH, транспорт)
✅ Навигация между реальными страницами
✅ Page source парсинг
✅ Логи (logcat через WebSocket)
✅ Timing и race conditions

КОГДА ПИСАТЬ INTEGRATION:
✅ Когда НЕ МОЖЕМ адекватно замокировать
✅ Когда проверяем РЕАЛЬНОЕ устройство/Appium
✅ Когда важны timing/async/race conditions
✅ Когда проверяем boundary между системами

НЕ ПИСАТЬ INTEGRATION:
❌ Для чистой логики (парсинг, конвертация)
❌ Для exception классов
❌ Для утилит без внешних зависимостей
❌ Если можно адекватно замокировать

ОБЯЗАТЕЛЬНО:
✅ Фикстура app: Shadowstep (conftest.py)
✅ Фикстура stability (ожидание стабильности UI)
✅ Smoke tests с параметризацией (не детальные проверки)
✅ Минимум дублирования с unit

ПРИМЕР:
```python
@pytest.mark.parametrize("gesture", ["swipe_up", "swipe_down", "scroll_left"])
def test_element_gestures_work_on_real_device(self, app, gesture):
    """Smoke: жесты работают на реальном устройстве"""
    element = app.get_element({"class": "android.widget.ScrollView"})
    method = getattr(element, gesture)
    result = method()  # Выполняем на реальном устройстве
    assert result is element  # Chainable
```
```

### **ПРАВИЛО 3: E2E/Smoke тесты**

```
ЧТО ТЕСТИРУЕМ В E2E:
✅ Критичные user flows (end-to-end)
✅ Регрессионные сценарии
✅ Примеры использования фреймворка

КОГДА ПИСАТЬ:
✅ После major рефакторинга (regression check)
✅ Перед релизом (smoke suite)
✅ Для документации (живые примеры)

ХАРАКТЕРИСТИКИ:
✅ Полные сценарии (несколько действий)
✅ Реалистичные use cases
✅ Минимум ассертов (проверяем flow, не детали)

ПРИМЕР:
```python
def test_full_page_object_workflow_e2e(app):
    """E2E: полный workflow с Page Objects"""
    # 1. Navigate
    app.navigator.navigate(PageA(), PageB())
    
    # 2. Interact
    PageB().button.click()
    
    # 3. Verify
    assert PageC().title.is_visible()
```
```

---

## 🚫 АНТИ-ПАТТЕРНЫ (что НЕ делать)

### **❌ Анти-паттерн 1: Тестирование implementation details**

```python
# ❌ ПЛОХО:
def test_element_has_actions_attribute():
    element = Element(...)
    assert hasattr(element, 'actions')  # Тестируем структуру!
    assert isinstance(element.actions, ElementActions)

# ✅ ХОРОШО:
def test_element_provides_action_methods():
    element = Element(...)
    result = element.click()  # Тестируем поведение!
    assert result is element
```

### **❌ Анти-паттерн 2: Дублирование unit и integration**

```python
# ❌ ПЛОХО:
# unit test:
def test_converter_to_dict():
    assert converter.to_dict({"text": "foo"}) == {"text": "foo"}

# integration test (ДУБЛЬ!):
def test_converter_to_dict_integro(app):
    assert converter.to_dict({"text": "foo"}) == {"text": "foo"}
    element = app.get_element(...)  # Лишняя проверка

# ✅ ХОРОШО:
# unit test (детально):
@pytest.mark.parametrize("input,expected", [...])  # 20 кейсов
def test_converter_all_cases(input, expected):
    assert converter.to_dict(input) == expected

# integration test (smoke):
def test_converted_locators_work_with_app(app):
    for loc in [dict, xpath, ui]:  # Только проверка что работает
        assert app.get_element(converter.to_dict(loc)) is not None
```

### **❌ Анти-паттерн 3: Мокирование внутренних методов**

```python
# ❌ ПЛОХО:
def test_element_click():
    with patch.object(element, '_internal_method'):  # Внутренний метод!
        element.click()

# ✅ ХОРОШО:
def test_element_click():
    mock_native = Mock(spec=WebElement)  # Граница системы!
    element = Element(..., native=mock_native)
    element.click()
    mock_native.click.assert_called_once()
```

### **❌ Анти-паттерн 4: Integration для чистой логики**

```python
# ❌ ПЛОХО:
def test_parser_integro(app):  # Парсеру НЕ НУЖЕН app!
    result = Parser(Lexer("text('foo')").tokens()).parse()
    assert result.methods[0].name == "text"

# ✅ ХОРОШО:
def test_parser_unit():  # Чистая логика в unit!
    result = Parser(Lexer("text('foo')").tokens()).parse()
    assert result.methods[0].name == "text"
```

---

## 📊 ТРЕБОВАНИЯ ПО МОДУЛЯМ

### **Tier 1: КРИТИЧНЫЕ (100% coverage обязательно)**

```
Модули где баг = катастрофа

locator/converter/ui_selector_lexer.py       [100%] ← Парсер ядро
locator/converter/ui_selector_parser.py      [100%] ← Парсер ядро
locator/converter/ui_selector_ast.py         [100%] ← Парсер ядро

Тесты:
├─ Unit: ВСЕ edge cases (malformed input, escaped, unicode)
├─ Параметризация: каждый метод UiSelector
└─ Integration: smoke test "парсер работает с Appium"
```

### **Tier 2: ВАЖНЫЕ (95%+ coverage)**

```
Модули публичного API

locator/converter/locator_converter.py       [95%+]
locator/converter/xpath_converter.py         [95%+]
locator/converter/dict_converter.py          [95%+]
element/element.py (public methods only)     [95%+]
exceptions/shadowstep_exceptions.py          [95%+]

Тесты:
├─ Unit: Все публичные методы + edge cases
├─ Integration: Smoke tests (работает с реальным app)
└─ Не тестируем private методы (начинающиеся с _)
```

### **Tier 3: СТАНДАРТНЫЕ (85-90% coverage)**

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

Тесты:
├─ Unit: Публичные методы, основные edge cases
├─ Integration: Критичные flows с реальным устройством
└─ Баланс между покрытием и практичностью
```

### **Tier 4: БАЗОВЫЕ (70-80% coverage)**

```
utils/utils.py                               [80%]
utils/adb.py                                 [75%]
decorators/                                  [80%]
terminal/terminal.py                         [75%]
terminal/adb.py                              [75%]
image/image.py                               [70%]
logcat/shadowstep_logcat.py                  [70%]

Тесты:
├─ Unit: Основные функции
├─ Integration: Если требуют внешние зависимости (ADB, SSH)
└─ Не гонимся за 100%
```

---

## 🎯 ПРАВИЛА РАСПРЕДЕЛЕНИЯ ТЕСТОВ

### **В UNIT должны быть:**

```
✅ Парсеры (Lexer, Parser, AST)
   └─ Чистая логика, строка → структура

✅ Конверторы (все *_converter.py)
   └─ Преобразование данных между форматами

✅ Exceptions (все классы исключений)
   └─ Чистый Python, raise/catch проверки

✅ Utils (чистые функции без I/O)
   └─ Функции преобразования, вычисления

✅ Element публичный API (с моками)
   └─ click(), send_keys(), get_element() и т.д.
   └─ Мокируем WebElement

✅ Navigator логика (с моками)
   └─ Граф, pathfinding с мок страницами

✅ Decorators
   └─ Проверка логики обёрток
```

### **В INTEGRATION должны быть:**

```
✅ Element взаимодействия (actions, gestures, waiting)
   └─ Реальные клики, свайпы на устройстве

✅ Terminal команды (ADB, AAPT, SSH)
   └─ Нельзя адекватно замокировать

✅ Navigator с реальными страницами
   └─ Навигация требует реальный UI

✅ Page Object с реальным page source
   └─ Crawler, реальное XML дерево

✅ Logcat
   └─ WebSocket соединение к Appium

✅ Image processing
   └─ OpenCV с реальными screenshots

✅ Smoke tests
   └─ Конверторы/парсеры работают с Appium
```

---

## 🛠️ СТАНДАРТЫ КОДА ТЕСТОВ

### **Именование:**

```
test_unit/test_[module]/test_[feature]_unit.py
test_integro/test_[module]/test_[feature]_integro.py

Классы:
class Test[Feature]:
    def test_[specific_case](self):
        ...

Описания:
"""Test that [subject] [action] when [condition]."""
```

### **Структура unit теста:**

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

### **Структура integration теста:**

```python
def test_feature_integro(self, app: Shadowstep, stability: None):
    """Integration: [что проверяется] на реальном устройстве"""
    # Arrange (минимальный setup)
    element = app.get_element({"text": "foo"})
    
    # Act (реальное действие)
    result = element.click()
    
    # Assert (базовая проверка)
    assert result is element
```

### **Обязательные фикстуры:**

```python
# conftest.py
@pytest.fixture(scope="session")
def app() -> Shadowstep:
    """Shadowstep instance для integration тестов"""
    ...

@pytest.fixture
def stability() -> None:
    """Ожидание стабильности UI перед тестом"""
    time.sleep(1)
```

---

## 🎯 КРИТЕРИИ КАЧЕСТВА ТЕСТА

### **Хороший unit тест:**

```
✅ Выполняется мгновенно (< 100ms)
✅ Изолирован (без внешних зависимостей)
✅ Использует моки для границ
✅ Параметризован (много кейсов, мало кода)
✅ Проверяет edge cases
✅ Тестирует контракт, не реализацию
✅ Понятное описание (docstring)
✅ Fallible (падает если функционал сломан)
✅ Устойчив к рефакторингу
✅ Не использует time.sleep
```

### **Хороший integration тест:**

```
✅ Проверяет реальное взаимодействие
✅ Не дублирует unit тесты
✅ Smoke характер (базовая работоспособность)
✅ Параметризован (где возможно)
✅ Быстрый (1-5 секунд на тест)
✅ Надёжный (не flaky)
✅ Использует stability фикстуру
✅ Минимум ассертов (проверяем flow, не детали)
```

---

## 🔍 PROCESS: Code Review чеклист

### **Перед merge нового теста:**

```
□ Тест в правильной категории (unit/integration)?
□ Нет дублирования с существующими тестами?
□ Unit тест использует моки (не реальный Appium)?
□ Integration тест РЕАЛЬНО требует Appium?
□ Параметризация использована где возможно?
□ Тестируется контракт, не реализация?
□ Docstring понятно описывает что проверяется?
□ Тест проходит (зелёный)?
□ Тест падает при поломке функционала (проверено)?
□ Coverage не упало?
```

---

## 📈 МОНИТОРИНГ И МЕТРИКИ

### **Команды для проверки:**

```bash
# Coverage общее
uv run pytest --cov=shadowstep --cov-report=term-missing

# Coverage конкретного модуля
uv run pytest --cov=shadowstep.element --cov-report=html

# Только unit тесты
uv run pytest tests/test_unit -v

# Только integration тесты
uv run pytest tests/test_integro -v

# Время выполнения
time uv run pytest tests/test_unit
time uv run pytest tests/test_integro

# Количество тестов
pytest --collect-only tests/ | grep "test session starts" -A 1
```

### **CI/CD требования:**

```
Pre-commit hook:
└─ Запускать только unit тесты (быстро)

Pull Request:
└─ Запускать unit + integration

Release:
└─ Полный suite + coverage report
```

---

## 🏆 ТЕКУЩЕЕ СОСТОЯНИЕ

### **Фактические метрики (обновлено 2025-10-18):**

```
ТЕСТЫ:
├─ Unit:        162 теста (78%) ✅ ЦЕЛЬ: 75%
├─ Integration:  46 тестов (22%) ✅ ЦЕЛЬ: 20-25%
└─ Общее:       208 тестов

ФАЙЛЫ:
├─ test_unit:    41 файл
├─ test_integro: 46 файлов
└─ Общее:        87 файлов

ПОКРЫТИЕ:
└─ Целевое: 90%+ (требуется проверка)

ВРЕМЯ ВЫПОЛНЕНИЯ:
└─ Требуется замер
```

---

## ✅ СООТВЕТСТВИЕ МАНИФЕСТУ

### **Unit тесты (ПРОВЕРЕНО):**

```
✅ locator/converter/ - полное покрытие
   ├─ test_converter_xpath_unit.py (70KB!)
   ├─ test_converter_dict_unit.py (29KB)
   ├─ test_converter_ui_selector_unit.py (29KB)
   └─ test_converter_unit.py (11KB)

✅ element/ - детальное покрытие
   ├─ test_element_unit.py (43KB)
   ├─ test_actions_unit.py (12KB) ⚠️ потенциальное дублирование
   ├─ test_gestures_unit.py (22KB)
   ├─ test_dom_unit.py (24KB)
   ├─ test_utilities_unit.py (30KB)
   ├─ test_waiting_unit.py (18KB)
   └─ test_should_unit.py (18KB)

✅ exceptions/ - перенесено из integro
✅ utils/ - чистые функции в unit
✅ decorators/ - есть unit тесты
```

### **Integration тесты (ПРОВЕРЕНО):**

```
✅ element/ - критичные взаимодействия
   ├─ test_actions_integro.py (реальные клики)
   ├─ test_gestures_integro.py (реальные свайпы)
   └─ test_waiting_integro.py (реальные таймауты)

✅ terminal/ - команды требуют устройство
   ├─ test_terminal_adb_integro.py
   ├─ test_terminal_aapt_integro.py
   └─ test_terminal_transport_integro.py

✅ locator/ - smoke tests
   └─ test_locator_converter_integro.py (параметризован!)

✅ navigator/ - реальная навигация
✅ page_object/ - реальное UI дерево
✅ logcat/ - WebSocket к Appium
```

---

## ⚠️ ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ

### **ПРОБЛЕМА 1: Дублирование в test_element/**

```
ДУБЛЬ ОБНАРУЖЕН:

test_element_unit.py (43KB):
└─ class TestElementActions:
   ├─ def test_send_keys(self):
   ├─ def test_clear(self):
   └─ def test_click(self):

test_actions_unit.py (12KB):
└─ class TestSendKeys:
   ├─ def test_send_keys_with_single_string(self):
   ├─ def test_send_keys_with_multiple_strings(self):
   └─ def test_send_keys_returns_element_for_chaining(self):
└─ class TestClear:
   └─ def test_clear_calls_native_clear(self):

РЕШЕНИЕ: Убрать базовые тесты из test_element_unit.py,
         оставить только детальные в test_actions_unit.py

СТАТУС: Требует очистки ⚠️
```

### **ПРОБЛЕМА 2: Возможное дублирование в других модулях**

```
Потенциально:
├─ test_element_unit.py содержит TestElement[Feature]
└─ test_[feature]_unit.py содержит детальные тесты

Требуется проверка:
□ test_element_unit.py vs test_gestures_unit.py
□ test_element_unit.py vs test_dom_unit.py
□ test_element_unit.py vs test_waiting_unit.py
□ test_element_unit.py vs test_utilities_unit.py
```

---

## 🔧 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### **Рекомендация 1: Рефакторинг test_element_unit.py**

```
ЦЕЛЬ: Убрать дублирование с специализированными файлами

СТРАТЕГИЯ:
test_element_unit.py должен содержать ТОЛЬКО:
├─ TestElementInit (инициализация)
├─ TestElementIntegration (как элементы работают вместе)
└─ TestElementContract (проверка контрактов)

Специализированные тесты ТОЛЬКО в:
├─ test_actions_unit.py → ВСЕ тесты actions
├─ test_gestures_unit.py → ВСЕ тесты gestures
├─ test_dom_unit.py → ВСЕ тесты DOM navigation
├─ test_waiting_unit.py → ВСЕ тесты waiting
└─ test_utilities_unit.py → ВСЕ тесты utilities

ПЛАН:
1. Определи что в test_element_unit.py дублируется
2. Если метод детально покрыт в специализированном файле
   → Удали из test_element_unit.py
3. Оставь только уникальные проверки и контракты
```

### **Рекомендация 2: Создать Contract Tests**

```
Создать: tests/test_unit/test_element/test_element_contract_unit.py

Цель: Проверка КОНТРАКТОВ публичного API

Содержание:
├─ Все публичные методы существуют
├─ Все методы chainable (return self)
├─ Все методы имеют правильные signatures
└─ Обратная совместимость

Пример:
```python
class TestElementPublicAPIContract:
    """Contract tests: публичный API не должен меняться без major version"""
    
    def test_element_has_all_required_methods(self):
        """Element имеет все обязательные публичные методы"""
        required_methods = [
            'click', 'tap', 'send_keys', 'clear',
            'get_element', 'get_elements', 'get_parent',
            'swipe_up', 'swipe_down', 'scroll_to_element',
            'wait', 'wait_visible', 'wait_clickable',
            # ... полный список
        ]
        
        element = Element({"text": "test"}, Mock())
        
        for method_name in required_methods:
            assert hasattr(element, method_name), f"Missing method: {method_name}"
            assert callable(getattr(element, method_name))
    
    @pytest.mark.parametrize("method_name", [
        "click", "tap", "clear", "swipe_up", "scroll_down", ...
    ])
    def test_action_methods_are_chainable(self, method_name):
        """Все action методы возвращают self для chaining"""
        element = Element({"text": "test"}, Mock())
        method = getattr(element, method_name)
        
        with patch.object(element, 'get_native'):
            result = method() if method_name != "send_keys" else method("text")
        
        assert result is element
```
```

---

## 📋 TODO: Очистка дублирования

### **Задача 1: test_element_unit.py cleanup**

```
Файл: tests/test_unit/test_element/test_element_unit.py (43KB)

АНАЛИЗ:
□ Проверить какие тесты дублируются с:
  □ test_actions_unit.py
  □ test_gestures_unit.py
  □ test_dom_unit.py
  □ test_waiting_unit.py
  
□ Удалить дубликаты

□ Оставить только:
  □ TestElementInit
  □ TestElementContract (создать новый класс)
  □ Уникальные интеграционные проверки

ОЖИДАЕМЫЙ РАЗМЕР: 15-20KB (сокращение 50%)
```

### **Задача 2: Проверка других дублей**

```
□ Проверить test_shadowstep_unit.py vs test_shadowstep_base_unit.py
□ Проверить test_terminal_*_unit.py на дубли
□ Проверить test_navigator_unit.py
```

---

## 📊 ОТЧЁТНОСТЬ

### **После каждого изменения:**

```markdown
## [Дата] - [Модуль] оптимизация

БЫЛО:
- test_element_unit.py: 1153 строки
- Дублирование: да

СТАЛО:
- test_element_unit.py: XXX строк
- Дублирование: нет

УДАЛЕНО:
- XX дублирующихся тестов

COVERAGE:
- До: X%
- После: Y%
- Изменение: +/-Z%
```

---

## 🚀 БЫСТРЫЙ СТАРТ

### **Проверка соответствия манифесту:**

```bash
# 1. Проверить coverage
cd /home/sigma/Projects/Appium-Python-Client-Shadowstep
uv run pytest --cov=shadowstep --cov-report=html --cov-report=term-missing

# 2. Проверить время
time uv run pytest tests/test_unit -v
time uv run pytest tests/test_integro -v

# 3. Найти дубли
grep "def test_send_keys\|def test_clear\|def test_click" tests/test_unit/test_element/*.py

# 4. Сравнить с метриками
# Записать результаты в этот файл (секция "Текущее состояние")
```

### **Очистка дублирования:**

```bash
# Для каждого дубля:
# 1. Открыть оба файла
# 2. Сравнить тесты
# 3. Если детальный тест в специализированном файле:
#    → Удалить базовый из test_element_unit.py
# 4. Запустить оба файла
# 5. Проверить coverage
```

---

## 📚 ССЫЛКИ И РЕСУРСЫ

**Best Practices:**
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Test Doubles](https://martinfowler.com/bliki/TestDouble.html)

**Примеры качественных тестов:**
- [requests tests](https://github.com/psf/requests/tree/main/tests)
- [flask tests](https://github.com/pallets/flask/tree/main/tests)
- [pytest tests](https://github.com/pytest-dev/pytest/tree/main/testing)

---

## 🎯 ЦЕЛИ НА СЛЕДУЮЩИЙ РЕЛИЗ

```
v0.36.0: Test Quality Milestone
□ Coverage ≥ 90%
□ Нет дублирования тестов
□ Все тесты категоризированы правильно
□ Contract tests добавлены
□ Coverage badge в README
□ Документация по написанию тестов
□ CI/CD оптимизирован (< 7 минут)
```

---

*Этот манифест - живой документ. Обновляй метрики и статусы по мере развития проекта.*

---

## 📞 КОНТАКТЫ

Вопросы по тестированию: GitHub Discussions
Баги в тестах: GitHub Issues (label: tests)
