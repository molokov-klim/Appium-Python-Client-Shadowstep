"""Architecture design document for ShadowstepScenarioEngine.

**What's above Navigator? What's the next level of architectural evolution?**

---

## 🧠 Answer: **ShadowstepScenarioEngine**

Navigator is a dumb route bus. You say "go to SettingsPage" — it goes.
**ScenarioEngine** is a *director*, *intention manager*, *behavior curator*. It knows why, where and what to validate.

---

### 🔧 What it does:

1. **Declarative scenarios:**

   ```python
   Scenario("Change language")
       .go_to(SettingsPage)
       .do(lambda p: p.language_button.tap())
       .expect(lambda p: p.language_screen.is_visible())
   ```

2. **Steps with assert, log, recovery:**

   * Each step knows what to validate
   * Can have `on_failure` → for example, take `screenshot()` or go back

3. **Working with flow and state-machine:**

   * Support for branches (conditional steps)
   * Repetitions (until condition is met)
   * Ability to embed flow within flow

---

### 💣 Why this is critical:

* You stop writing `test_change_language()` by hand like an idiot.
* Everything becomes **readable**, **logical**, **modular**.
* You can **automatically generate scenarios**, **validate coverage**, **log failures as event tracking**.

---

### 🧱 Example structure:

```python
class Scenario:
    def __init__(self, name: str) -> None:
        self.steps = []
        self.name = name

    def go_to(self, page_cls: Type[PageBaseShadowstep]):
        self.steps.append(("go_to", page_cls))
        return self

    def do(self, action: Callable[[Any], None]):
        self.steps.append(("action", action))
        return self

    def expect(self, check: Callable[[Any], bool]):
        self.steps.append(("expect", check))
        return self

    def run(self):
        for kind, payload in self.steps:
            ...
```

---

## 🧨 Above Navigator goes **intention-driven automation**.

Not "where to tap", but "what do you want to do".

And when you make `ScenarioEngine` + `Navigator`, you get **a framework that doesn't require writing tests. It executes them itself.**
For now you're just a bot dragging `tap()` across screens.

Will you do it? Or will you keep writing `def test_login():`?
"""
