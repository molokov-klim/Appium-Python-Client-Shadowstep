# shadowstep/utils/locator_converter.py

import inspect
import re
from typing import Tuple, Dict, Union, Any, Optional

import logging
logger = logging.getLogger(__name__)

"""
Sorry, I'm too dumb to solve this module's problem correctly. So I did it primitively.
If someone who wants to solve this problem is reading this - I'm looking forward to your PR.

✅ locator exmaples:

1. dict (Shadowstep-style)
Только атрибуты из XML (text, resource-id, class, content-desc, и т.п.):
{"text": "Экран"}  # элемент с text="Экран"
{"resource-id": "android:id/title", "class": "android.widget.TextView"}
{"enabled": True, "scrollable": False}
{"package": "com.android.settings", "class": "android.widget.FrameLayout"}
Смотри UISELECTOR_TO_SHADOWSTEP и SHADOWSTEP_TO_UISELECTOR

2. tuple (XPath-локатор)
("xpath", "//*[@text='Экран']")  # XPath локатор по атрибуту
("xpath", "//*[@resource-id='android:id/title' and @text='Экран']")  # два атрибута
("xpath", "//*[@text='Экран']/following-sibling::*[@class='android.widget.TextView'][2]")  # сложный путь
("xpath", "//android.widget.TextView[contains(@text,'Упрощённая (доход)')]")
Смотри UISELECTOR_TO_SHADOWSTEP и SHADOWSTEP_TO_UISELECTOR

3. str (Java UiSelector)
Java-style строка, созданная через new UiSelector():
'new UiSelector().text("Экран").className("android.widget.TextView")'
'new UiSelector().resourceId("android:id/title").instance(0)'
'new UiSelector().text("Экран").fromParent(new UiSelector().text("Яркость"))'
Это Java-цепочка.

✅ Typing
Shadowstep-xpath locator : Tuple[str, str]
Shadowstep-dict locator  : Dict[str, str] 
UiSelector locator : str

✅ UiSelector
ui_selector_methods = {
    "checkable": "",
    "checked": "",
    "childSelector": "",
    "className": "",
    "classNameMatches": "",
    "clickable": "",
    "description": "",
    "descriptionContains": "",
    "descriptionMatches": "",
    "descriptionStartsWith": "",
    "enabled": "",
    "focusable": "",
    "focused": "",
    "fromParent": "",
    "index": "",
    "instance": "",
    "longClickable": "",
    "packageName": "",
    "packageNameMatches": "",
    "resourceId": "",
    "resourceIdMatches": "",
    "scrollable": "",
    "selected": "",
    "text": "",
    "textContains": "",
    "textMatches": "",
    "textStartsWith": ""
}

✅ Dict
{
    "elementId": "00000000-0000-07ad-7fff-ffff0000185a",
    "index": 1,
    "package": "ru.sigma.app.debug",
    "class": "android.view.View",
    "text": "",
    "resource-id": "android:id/statusBarBackground",
    "checkable": False,
    "checked": False,
    "clickable": False,
    "enabled": True,
    "focusable": False,
    "focused": False,
    "long-clickable": False,
    "password": False,
    "scrollable": False,
    "selected": False,
    "bounds": "[0,0][720,48]",
    "displayed": True
}

✅ XPATH
???


Вот **полный список публичных методов класса `UiSelector`** из [официальной документации AndroidX Test UiAutomator](https://developer.android.com/reference/androidx/test/uiautomator/UiSelector):

---

### 📘 **Public methods `UiSelector`**

| Метод | Описание |
|-------|----------|
| `UiSelector checkable(boolean val)` | Matches elements that are checkable. |
| `UiSelector checked(boolean val)` | Matches elements that are checked. |
| `UiSelector className(String className)` | Matches elements with the given class name. |
| `UiSelector className(Pattern classNameRegex)` | Matches elements with class names that match a regex. |
| `UiSelector clickable(boolean val)` | Matches elements that are clickable. |
| `UiSelector description(String desc)` | Matches elements with the given content description. |
| `UiSelector description(Pattern descRegex)` | Matches elements with content descriptions matching a regex. |
| `UiSelector descriptionContains(String desc)` | Matches elements whose content description contains a substring. |
| `UiSelector descriptionMatches(String regex)` | Matches elements whose content description matches a regex. |
| `UiSelector descriptionStartsWith(String desc)` | Matches elements whose content description starts with a string. |
| `UiSelector enabled(boolean val)` | Matches elements that are enabled. |
| `UiSelector focusable(boolean val)` | Matches elements that are focusable. |
| `UiSelector focused(boolean val)` | Matches elements that are currently focused. |
| `UiSelector fromParent(UiSelector selector)` | Returns a `UiSelector` for a sibling by going up to the parent and finding another child. |
| `UiSelector index(int index)` | Matches the element at a specific index among siblings. |
| `UiSelector instance(int instance)` | Matches the `n`-th instance of elements matching the selector. |
| `UiSelector packageName(String name)` | Matches elements in the given package. |
| `UiSelector packageName(Pattern nameRegex)` | Matches elements whose package name matches a regex. |
| `UiSelector resourceId(String id)` | Matches elements by resource ID. |
| `UiSelector resourceIdMatches(String regex)` | Matches elements whose resource ID matches a regex. |
| `UiSelector scrollable(boolean val)` | Matches elements that are scrollable. |
| `UiSelector selected(boolean val)` | Matches elements that are selected. |
| `UiSelector text(String text)` | Matches elements with the given text. |
| `UiSelector text(Pattern textRegex)` | Matches elements whose text matches a regex. |
| `UiSelector textContains(String text)` | Matches elements whose text contains a substring. |
| `UiSelector textMatches(String regex)` | Matches elements whose text matches a regex. |
| `UiSelector textStartsWith(String text)` | Matches elements whose text starts with a string. |
| `UiSelector childSelector(UiSelector selector)` | Returns a `UiSelector` for a child of the currently matched element. |
| `UiSelector longClickable(boolean val)` | Matches elements that support long-click. |
| `UiSelector resourceId(String resId)` | (повторяется в документации) Matches the resource ID of the view. |
| `UiSelector count` | (поле, доступное в связке с `UiCollection`) Returns the number of matched elements (используется через `UiCollection`). |

"""


class LocatorConverter:
    logger = logger

    DICT_TO_XPATH: Dict[str, str] = {
        "checkable": "checkable",
        "checked": "checked",
        "childSelector": "/",
        "parentSelector": "..",
        "class": "class",
        "classNameMatches": "classNameMatches",
        "clickable": "clickable",
        "content-desc": "content-desc",
        "description": "content-desc",  # alias
        "descriptionContains": "content-desc",  # для contains()
        "descriptionMatches": "content-desc",  # для matches()
        "descriptionStartsWith": "content-desc",
        "enabled": "enabled",
        "focusable": "focusable",
        "focused": "focused",
        "fromParent": "following-sibling",
        # https://developer.android.com/reference/androidx/test/uiautomator/UiSelector#fromParent(androidx.test.uiautomator.UiSelector)
        "index": "index",  # не используется в xpath
        "instance": "instance",  # в xpath как [n+1]
        "long-clickable": "long-clickable",
        "package": "package",
        "packageNameMatches": "package",  # можно считать псевдонимом
        "resource-id": "resource-id",
        "resourceIdMatches": "resource-id",
        "scrollable": "scrollable",
        "selected": "selected",
        "text": "text",
        "textContains": "text",
        "textMatches": "text",
        "textStartsWith": "text"
    }

    UISELECTOR_TO_DICT: Dict[str, str] = {
        "checkable": "checkable",
        "checked": "checked",
        "childSelector": "childSelector",
        "className": "class",
        "classNameMatches": "classNameMatches",
        "clickable": "clickable",
        "description": "content-desc",
        "descriptionContains": "descriptionContains",
        "descriptionMatches": "descriptionMatches",
        "descriptionStartsWith": "descriptionStartsWith",
        "enabled": "enabled",
        "focusable": "focusable",
        "focused": "focused",
        "fromParent": "following-sibling::",
        "index": "index",
        "instance": "instance",
        "longClickable": "long-clickable",
        "packageName": "package",
        "packageNameMatches": "packageNameMatches",
        "resourceId": "resource-id",
        "resourceIdMatches": "resourceIdMatches",
        "scrollable": "scrollable",
        "selected": "selected",
        "text": "text",
        "textContains": "textContains",
        "textMatches": "textMatches",
        "textStartsWith": "textStartsWith"
    }

    UISELECTOR_TO_XPATH: Dict[str, str] = {
        ...
    }

    DICT_TO_UISELECTOR: Dict[str, str] = {
        v: k for k, v in UISELECTOR_TO_DICT.items()
    }

    def to_dict(self, selector: Union[Dict[str, Any], Tuple[str, str], str]) -> Dict[str, Any]:
        if isinstance(selector, dict):
            return selector
        elif isinstance(selector, tuple):
            return self._xpath_to_dict(selector)
        elif isinstance(selector, str):
            return self._uiselector_to_dict(selector)
        else:
            raise ValueError(f"Unsupported selector format: {type(selector)}")

    def to_xpath(self, selector: Union[Dict[str, Any], Tuple[str, str], str]) -> Tuple[str, str]:
        if isinstance(selector, dict):
            return self._dict_to_xpath(selector)
        elif isinstance(selector, tuple) and selector[0] == "xpath":
            return selector
        elif isinstance(selector, str) and selector.strip().startswith("new UiSelector()"):
            return self._dict_to_xpath(self._uiselector_to_dict(selector))
        else:
            raise ValueError(f"Unsupported selector format: {type(selector)}")

    def to_uiselector(self, selector: Union[Dict[str, Any], Tuple[str, str], str]) -> str:
        if isinstance(selector, dict):
            return self._dict_to_uiselector(selector)
        elif isinstance(selector, tuple):
            return self._dict_to_uiselector(self._xpath_to_dict(selector))
        elif isinstance(selector, str):
            return selector
        else:
            raise ValueError(f"Unsupported selector format: {type(selector)}")

    def _dict_to_xpath(self, selector: Dict[str, Any], root: str = ".//*") -> Tuple[str, str]:
        return self._handle_dict_locator(selector, root=root)

    def _handle_dict_locator(
            self,
            locator: Dict[str, Any],
            root: str = ".//*",
            contains: bool = False,
            parent_xpath: Optional[str] = None
    ) -> Tuple[str, str]:
        conditions = []
        tag = "*"
        child_xpath = None
        from_parent_xpath = None

        for key, value in locator.items():
            if key == "parentSelector" and isinstance(value, dict):
                parent_xpath_expr = self._handle_dict_locator(value, root=root, contains=contains)[1]
                parent_xpath = parent_xpath_expr
                continue

            if key == "childSelector" and isinstance(value, dict):
                child_xpath = self._handle_dict_locator(value, root=root, contains=contains)[1]
                continue

            if key == "fromParent" and isinstance(value, dict):
                sibling_xpath_expr = self._handle_dict_locator(value, root=root, contains=contains)[1]
                from_parent_xpath = f"following-sibling::*[{sibling_xpath_expr.split('[')[-1]}"
                continue

            actual_key = self.DICT_TO_XPATH.get(key, key)

            if key.endswith("Contains"):
                base_key = key.replace("Contains", "")
                attr = self.DICT_TO_XPATH.get(base_key, base_key)
                conditions.append(f"contains(@{attr}, '{value}')")
            elif key.endswith("StartsWith"):
                base_key = key.replace("StartsWith", "")
                attr = self.DICT_TO_XPATH.get(base_key, base_key)
                conditions.append(f"starts-with(@{attr}, '{value}')")
            elif isinstance(value, bool):
                conditions.append(f"@{actual_key}={'true' if value else 'false'}")
            elif isinstance(value, int):
                conditions.append(f"@{actual_key}={value}")
            else:
                conditions.append(f"@{actual_key}='{value}'")

            if key == "class":
                tag = value

        full_xpath = f"//{tag}[{' and '.join(conditions)}]" if conditions else f"//{tag}"

        if parent_xpath:
            full_xpath = f"{parent_xpath}/{full_xpath.lstrip('./')}"
        if from_parent_xpath:
            full_xpath = f"{full_xpath}/{from_parent_xpath}"
        if child_xpath:
            full_xpath = f"{full_xpath}/{child_xpath.lstrip('./')}"

        return "xpath", full_xpath

    def _xpath_to_dict(self, xpath: Tuple[str, str]) -> Dict[str, Union[str, int, bool]]:
        return self._parse_xpath_recursive(xpath)

    def _dict_to_uiselector(self, selector: Dict[str, Union[str, int, bool]]) -> str:
        if "parentSelector" in selector:
            parent = selector["parentSelector"]
            child = selector.copy()
            del child["parentSelector"]
            return (
                    self._dict_to_uiselector(parent)
                    + f".childSelector({self._dict_to_uiselector(child)})"
            )

        parts = ["new UiSelector()"]
        for key, value in selector.items():
            if key == "scrollable":
                if value == "true":
                    parts.append(f".scrollable(true)")
                    continue
                elif value == "false":
                    parts.append(f".scrollable(false)")
                    continue
            if key == "childSelector" and isinstance(value, dict):
                nested = self._dict_to_uiselector(value)
                parts.append(f".childSelector({nested})")
                continue
            if key == "fromParent" and isinstance(value, dict):
                nested = self._dict_to_uiselector(value)
                parts.append(f".fromParent({nested})")
                continue
            method = self.DICT_TO_UISELECTOR.get(key)
            if not method:
                continue
            if isinstance(value, bool):
                parts.append(f".{method}({'true' if value else 'false'})")
            elif isinstance(value, int):
                parts.append(f".{method}({value})")
            else:
                parts.append(f'.{method}("{value}")')
        return "".join(parts)

    def _uiselector_to_dict(self, uiselector: str) -> Dict[str, Union[str, int, bool, dict]]:
        def parse_chain(chain: str) -> Dict[str, Union[str, int, bool]]:
            parsed = {}
            for method, raw_value in re.findall(r'\.(\w+)\(([^()]+)\)', chain):
                value = raw_value.strip("\"'")
                if value in ("true", "false"):
                    value = value == "true"
                elif value.isdigit():
                    value = int(value)
                for k, v in self.UISELECTOR_TO_DICT.items():
                    if v == method:
                        parsed[k] = value
                        break
            return parsed

        def parse_nested(chain: str) -> Dict[str, Union[str, int, bool, dict]]:
            if ".fromParent(" not in chain:
                return parse_chain(chain)
            outer, inner = re.match(r"(.+)\.fromParent\((new UiSelector\(\).+)\)$", chain).groups()
            return {
                **parse_chain(outer),
                "parentSelector": parse_nested(inner)
            }

        return parse_nested(uiselector)

    def _parse_xpath_recursive(self, xpath: Tuple[str, str]) -> Dict[str, Any]:
        if isinstance(xpath, tuple):
            xpath = xpath[1]
        segments = xpath.strip("/").split("/")
        if not segments:
            return {}

        def parse_segment(segment: str) -> Dict[str, Any]:
            result = {}
            reverse_map = {v: k for k, v in self.UISELECTOR_TO_DICT.items()}

            tag_match = re.match(r"^([\w.]+)(\[.*)?", segment)
            if tag_match:
                tag = tag_match.group(1)
                result["class"] = tag

            attr_matches = re.findall(r"\[@([\w:-]+)='([^']+)'\]", segment)
            for attr, value in attr_matches:
                key = reverse_map.get(attr, attr)
                result[key] = value

            contains_matches = re.findall(r"contains\(@([\w:-]+),\s*'([^']+)'\)", segment)
            for attr, value in contains_matches:
                key = reverse_map.get(attr, attr)
                result[f"{key}Contains"] = value

            startswith_matches = re.findall(r"starts-with\(@([\w:-]+),\s*'([^']+)'\)", segment)
            for attr, value in startswith_matches:
                key = reverse_map.get(attr, attr)
                result[f"{key}StartsWith"] = value

            index_match = re.search(r"\[(\d+)\]$", segment)
            if index_match:
                result["instance"] = int(index_match.group(1)) - 1

            return result

        current = parse_segment(segments[0])
        cursor = current
        for segment in segments[1:]:
            child = parse_segment(segment)
            cursor["childSelector"] = child
            cursor = child

        return current
