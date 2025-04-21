# 📱 Shadowstep (in development)

> Powerful and resilient Appium-based framework for Android UI automation.

[![PyPI](https://img.shields.io/pypi/v/shadowstep?color=brightgreen)](https://pypi.org/project/shadowstep/)
[![Lint](https://github.com/your-org/shadowstep/actions/workflows/pylint.yml/badge.svg)](https://github.com/your-org/shadowstep/actions/workflows/pylint.yml)
[![Test](https://github.com/your-org/shadowstep/actions/workflows/tests.yml/badge.svg)](https://github.com/your-org/shadowstep/actions/workflows/tests.yml)
[![License](https://img.shields.io/github/license/your-org/shadowstep)](LICENSE)

---

## 🔍 Overview

Shadowstep is a flexible UI automation framework built on top of **Appium** and designed to improve test reliability and developer experience.  
It introduces powerful abstractions for Android testing: dynamic element wrappers, retry logic, visual change detection, and custom ADB terminal integration.

---

## ✨ Features

- 📲 **Robust UI Automation** – with custom `Element` class and retryable tap/click logic
- 🔁 **Automatic Session Recovery** – handles `NoSuchDriver`, `InvalidSessionId`, and reconnects
- 🎯 **Dict-to-XPath Locator DSL** – write intuitive locators like `{"class": "TextView", "text": "OK"}`  
- 🎥 **Video + Screenshot Reporting** – Allure integration with visual context for failed steps
- 📷 **Visual DOM/Window Waits** – wait for or detect screen changes by screenshot diffs
- 🐚 **Direct ADB Access** – push/pull/install/uninstall/interact with device via custom ADB wrapper
- 🧱 **Testable Components** – override every interaction and build new ones with ease

---

## 🚀 Quickstart

### 1. 📦 Installation

```bash
pip install appium-python-client-shadowstep


navigator
✅ Инструкция для пользователя Shadowstep
🔧 Требования к структуре проекта:

Все страницы (PageObjects) хранятся в .../pages/.

Файлы называются по шаблону page_<имя>.py.

Классы внутри — строго Page<Имя>, наследуются от PageBase.

ВАЖНО!
Используйте композицию Shadowstep, а не наследование от него
⚙️ Минимально необходимая реализация:
Если тебе не нужно перегружать никакие методы — можешь оставить вообще только это:

python
Копировать
Редактировать
class AtolMobilePlatform:
    def __init__(self):
        self.app = Shadowstep.get_instance()

    def __getattr__(self, item):
        return getattr(self.app, item)




