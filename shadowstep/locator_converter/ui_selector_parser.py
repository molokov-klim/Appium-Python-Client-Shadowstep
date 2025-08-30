# ui_selector_parser.py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Union

selectors = [
    'new UiSelector().textStartsWith("Оплат").className("android.widget.Button").childSelector(new UiSelector().className("android.widget.ImageView"));',
    'new UiSelector().className("android.widget.EditText").focused(true).instance(0);',
    'new UiSelector().packageName("ru.sigma.app.debug").resourceIdMatches(".*:id/btn.*");',
    'new UiSelector().descriptionContains("Карта").clickable(true);',
    'new UiSelector().className("androidx.appcompat.app.ActionBar$Tab").index(2);',
    'new UiSelector().className("android.widget.RadioButton").fromParent(new UiSelector().resourceId("ru.sigma.app.debug:id/paymentMethods"));',
    'new UiSelector().className("android.widget.EditText").textStartsWith("+7").enabled(true);',
    'new UiSelector().descriptionMatches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");',
    'new UiSelector().scrollable(true).childSelector(new UiSelector().text("История"));',
    'new UiSelector().className("android.widget.CheckBox").checkable(true).checked(false).instance(2);',
]


class UiMethod(str, Enum):
    # --- text-based ---
    TEXT = "text"
    TEXT_CONTAINS = "textContains"
    TEXT_STARTS_WITH = "textStartsWith"
    TEXT_MATCHES = "textMatches"

    # --- description ---
    DESCRIPTION = "description"
    DESCRIPTION_CONTAINS = "descriptionContains"
    DESCRIPTION_STARTS_WITH = "descriptionStartsWith"
    DESCRIPTION_MATCHES = "descriptionMatches"

    # --- resource id / package ---
    RESOURCE_ID = "resourceId"
    RESOURCE_ID_MATCHES = "resourceIdMatches"
    PACKAGE_NAME = "packageName"

    # --- class ---
    CLASS_NAME = "className"
    CLASS_NAME_MATCHES = "classNameMatches"

    # --- bool props ---
    CHECKABLE = "checkable"
    CHECKED = "checked"
    CLICKABLE = "clickable"
    ENABLED = "enabled"
    FOCUSABLE = "focusable"
    FOCUSED = "focused"
    LONG_CLICKABLE = "longClickable"
    SCROLLABLE = "scrollable"
    SELECTED = "selected"

    # --- numeric ---
    INDEX = "index"
    INSTANCE = "instance"

    # --- hierarchy ---
    CHILD_SELECTOR = "childSelector"
    FROM_PARENT = "fromParent"


UI_TO_XPATH = {
    UiMethod.TEXT: lambda v: f'[@text="{v}"]',
    UiMethod.TEXT_CONTAINS: lambda v: f'[contains(@text, "{v}")]',
    UiMethod.TEXT_STARTS_WITH: lambda v: f'[starts-with(@text, "{v}")]',
    UiMethod.TEXT_MATCHES: lambda v: f'[matches(@text, "{v}")]',  # Appium >= 2

    UiMethod.DESCRIPTION: lambda v: f'[@content-desc="{v}"]',
    UiMethod.DESCRIPTION_CONTAINS: lambda v: f'[contains(@content-desc, "{v}")]',
    UiMethod.DESCRIPTION_STARTS_WITH: lambda v: f'[starts-with(@content-desc, "{v}")]',
    UiMethod.DESCRIPTION_MATCHES: lambda v: f'[matches(@content-desc, "{v}")]',

    UiMethod.RESOURCE_ID: lambda v: f'[@resource-id="{v}"]',
    UiMethod.RESOURCE_ID_MATCHES: lambda v: f'[matches(@resource-id, "{v}")]',
    UiMethod.PACKAGE_NAME: lambda v: f'[@package="{v}"]',

    UiMethod.CLASS_NAME: lambda v: f'[@class="{v}"]',
    UiMethod.CLASS_NAME_MATCHES: lambda v: f'[matches(@class, "{v}")]',

    UiMethod.CHECKABLE: lambda v: f'[@checkable="{str(v).lower()}"]',
    UiMethod.CHECKED: lambda v: f'[@checked="{str(v).lower()}"]',
    UiMethod.CLICKABLE: lambda v: f'[@clickable="{str(v).lower()}"]',
    UiMethod.ENABLED: lambda v: f'[@enabled="{str(v).lower()}"]',
    UiMethod.FOCUSABLE: lambda v: f'[@focusable="{str(v).lower()}"]',
    UiMethod.FOCUSED: lambda v: f'[@focused="{str(v).lower()}"]',
    UiMethod.LONG_CLICKABLE: lambda v: f'[@long-clickable="{str(v).lower()}"]',
    UiMethod.SCROLLABLE: lambda v: f'[@scrollable="{str(v).lower()}"]',
    UiMethod.SELECTED: lambda v: f'[@selected="{str(v).lower()}"]',

    UiMethod.INDEX: lambda v: f'[position()={int(v) + 1}]',
    UiMethod.INSTANCE: lambda v: f'[position()={int(v) + 1}]',
}


# --- Лексер ---

class TokenType(Enum):
    DOT = auto()
    IDENT = auto()
    LPAREN = auto()
    RPAREN = auto()
    STRING = auto()
    NUMBER = auto()
    TRUE = auto()
    FALSE = auto()
    NEW = auto()
    UISELECTOR = auto()
    SEMI = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str | None = None
    pos: int = -1


class LexerError(Exception): ...


class ParserError(Exception): ...


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.n = len(text)

    def _peek(self) -> str:
        return self.text[self.i] if self.i < self.n else ""

    def _advance(self) -> str:
        ch = self._peek()
        self.i += 1
        return ch

    def tokens(self) -> list[Token]:
        toks: list[Token] = []
        while self.i < self.n:
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
                continue
            if ch == '.':
                toks.append(Token(TokenType.DOT, '.', self.i))
                self._advance()
                continue
            if ch == '(':
                toks.append(Token(TokenType.LPAREN, '(', self.i))
                self._advance()
                continue
            if ch == ')':
                toks.append(Token(TokenType.RPAREN, ')', self.i))
                self._advance()
                continue
            if ch == ';':
                toks.append(Token(TokenType.SEMI, ';', self.i))
                self._advance()
                continue

            if ch == '"':
                start = self.i
                self._advance()  # opening "
                buf = []
                while True:
                    if self.i >= self.n:
                        raise LexerError(f'Unterminated string at {start}')
                    c = self._advance()
                    if c == '\\':
                        if self.i >= self.n:
                            raise LexerError(f'Bad escape at {self.i}')
                        nxt = self._advance()
                        if nxt in '"\\':
                            buf.append(nxt)
                        elif nxt == 'n':
                            buf.append('\n')
                        elif nxt == 't':
                            buf.append('\t')
                        else:
                            buf.append('\\' + nxt)
                        continue
                    if c == '"':
                        break
                    buf.append(c)
                toks.append(Token(TokenType.STRING, ''.join(buf), start))
                continue

            if ch.isdigit():
                start = self.i
                while self.i < self.n and self._peek().isdigit():
                    self._advance()
                toks.append(Token(TokenType.NUMBER, self.text[start:self.i], start))
                continue

            if ch.isalpha() or ch == '_':
                start = self.i
                while self.i < self.n and (self._peek().isalnum() or self._peek() in "_$"):
                    self._advance()
                ident = self.text[start:self.i]
                low = ident.lower()
                if low == 'new':
                    toks.append(Token(TokenType.NEW, ident, start))
                elif ident == 'UiSelector':
                    toks.append(Token(TokenType.UISELECTOR, ident, start))
                elif low == 'true':
                    toks.append(Token(TokenType.TRUE, ident, start))
                elif low == 'false':
                    toks.append(Token(TokenType.FALSE, ident, start))
                else:
                    toks.append(Token(TokenType.IDENT, ident, start))
                continue

            raise LexerError(f'Unexpected char {ch!r} at {self.i}')

        toks.append(Token(TokenType.EOF, None, self.i))
        return toks


# --- AST ---

@dataclass
class MethodCall:
    name: str
    args: list[Union[str, int, bool, 'Selector']] = field(default_factory=list)


@dataclass
class Selector:
    methods: list[MethodCall] = field(default_factory=list)


# --- Парсер (конечный автомат слева направо) ---

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = 0

    def _peek(self) -> Token:
        return self.tokens[self.i]

    def _advance(self) -> Token:
        tok = self._peek()
        self.i += 1
        return tok

    def _expect(self, ttype: TokenType) -> Token:
        tok = self._peek()
        if tok.type != ttype:
            raise ParserError(f'Expected {ttype}, got {tok.type} at {tok.pos}')
        return self._advance()

    def parse(self) -> Selector:
        # Опциональный префикс "new UiSelector()"
        if self._peek().type == TokenType.NEW:
            self._advance()
            self._expect(TokenType.UISELECTOR)
            self._expect(TokenType.LPAREN)
            self._expect(TokenType.RPAREN)
        sel = Selector()
        while True:
            tok = self._peek()
            if tok.type == TokenType.DOT:
                sel.methods.append(self._parse_method_call())
            elif tok.type in (TokenType.SEMI, TokenType.EOF, TokenType.RPAREN):
                break
            else:
                break
        if self._peek().type == TokenType.SEMI:
            self._advance()
        return sel

    def _parse_method_call(self) -> MethodCall:
        self._expect(TokenType.DOT)
        name_tok = self._expect(TokenType.IDENT)
        self._expect(TokenType.LPAREN)
        args: list[Any] = []
        if self._peek().type != TokenType.RPAREN:
            args.append(self._parse_arg())
        self._expect(TokenType.RPAREN)
        return MethodCall(name=name_tok.value, args=args)

    def _parse_arg(self) -> str | int | bool | Selector:
        tok = self._peek()
        if tok.type == TokenType.STRING:
            self._advance()
            return tok.value
        if tok.type == TokenType.TRUE:
            self._advance()
            return True
        if tok.type == TokenType.FALSE:
            self._advance()
            return False
        if tok.type == TokenType.NUMBER:
            self._advance()
            return int(tok.value)
        if tok.type == TokenType.NEW:
            return self._parse_nested_selector()
        if tok.type == TokenType.IDENT:
            self._advance()
            return tok.value
        raise ParserError(f'Unexpected token in arg: {tok.type} at {tok.pos}')

    def _parse_nested_selector(self) -> Selector:
        # Обязательное "new UiSelector()"
        self._expect(TokenType.NEW)
        self._expect(TokenType.UISELECTOR)
        self._expect(TokenType.LPAREN)
        self._expect(TokenType.RPAREN)
        nested = Selector()
        # Читаем .method(...) пока не дойдём до закрывающей RPAREN родителя
        while self._peek().type == TokenType.DOT:
            nested.methods.append(self._parse_method_call())
        return nested


# --- Публичный API ---

def selector_to_dict(sel: Selector) -> dict[str, Any]:
    def conv(arg):
        if isinstance(arg, Selector):
            return selector_to_dict(arg)
        return arg

    return {
        "methods": [
            {"name": m.name, "args": [conv(a) for a in m.args]}
            for m in sel.methods
        ]
    }


def parse_selector_string(s: str) -> dict[str, Any]:
    s = s.strip()
    # Если пришло в одинарных кавычках — снимем их
    if s.startswith("'") and s.endswith("'"):
        s = s[1:-1]
    toks = Lexer(s).tokens()
    sel = Parser(toks).parse()
    return selector_to_dict(sel)


# --- Обратная сборка (опционально) ---

def dict_to_selector(d: dict, top_level: bool = True) -> str:
    def fmt_arg(a: Any) -> str:
        if isinstance(a, dict):
            # вложенный селектор — без завершающей точки с запятой
            return dict_to_selector(a, top_level=False)
        if isinstance(a, bool):
            return "true" if a else "false"
        if isinstance(a, int):
            return str(a)
        escaped = str(a).replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    parts = ["new UiSelector()"]
    for m in d.get("methods", []):
        args = m.get("args", [])
        if len(args) > 1:
            raise ValueError("UiSelector обычно унарный; поддерживаются 0/1 аргумент.")
        arg_str = fmt_arg(args[0]) if args else ""
        parts.append(f'.{m["name"]}({arg_str})')
    s = "".join(parts)
    return s + ";" if top_level else s


def selector_to_xpath(sel: dict, base_xpath="//*") -> str:
    """
    sel = {
      "methods": [
         {"name": "className", "args": ["android.widget.Button"]},
         {"name": "textStartsWith", "args": ["Оплат"]},
         ...
      ]
    }
    """
    xpath = base_xpath
    for m in sel.get("methods", []):
        name = m["name"]
        args = m["args"]

        try:
            method = UiMethod(name)
        except ValueError:
            # неизвестный метод — пропускаем
            continue

        if method in UI_TO_XPATH:
            xpath += UI_TO_XPATH[method](*args)
        elif method in (UiMethod.CHILD_SELECTOR, UiMethod.FROM_PARENT):
            # рекурсивный селектор
            child = selector_to_xpath(args[0], base_xpath="*")
            if method == UiMethod.CHILD_SELECTOR:
                xpath += f'/{child}'
            else:
                xpath = f'{xpath}/..{child}'

    return xpath


if __name__ == "__main__":
    for ex in selectors:
        parsed = parse_selector_string(ex)
        xpath = selector_to_xpath(parsed)
        print(ex)
        print(parsed)
        print(xpath)
        # проверка обратной сборки — туда-обратно
        rebuilt = dict_to_selector(parsed)
        print("REBUILT OK:", rebuilt == ex)
        print("-" * 80)

"""

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

"""
    # --- Класс ---
    "className({value})": '//*[@class="{value}"]',
    "classNameRegex({value})": '//*[contains(@class, "{value}")]',  # костыль

    # --- Resource ID ---
    "resourceId({value})": '//*[@resource-id="{value}"]',
    "resourceIdMatches({value})": '//*[contains(@resource-id, "{value}")]',  # костыль

    # --- Text ---
    "text"({value}): '//*[@text="{value}"]',
    "textRegex({value})": '//*[contains(@text, "{value}")]',  # костыль
    "textContains({value})": '//*[contains(@text,"{value}")]',
    "textStartsWith({value})": '//*[starts-with(@text,"{value}")]',
    "textMatches({value})": '//*[contains(@text,"{value}")]',  # костыль

    # --- Content Description ---
    "description({value})": '//*[@content-desc="{value}"]',
    "descriptionRegex({value})": '//*[contains(@content-desc,"{value}")]',  # костыль
    "descriptionContains({value})": '//*[contains(@content-desc,"{value}")]',
    "descriptionStartsWith({value})": '//*[starts-with(@content-desc,"{value}")]',
    "descriptionMatches({value})": '//*[contains(@content-desc,"{value}")]',  # костыль

    # --- Boolean attributes ---
    "checkable({value})": '//*[@checkable="{value}"]',
    "checked({value})": '//*[@checked="{value}"]',
    "clickable({value})": '//*[@clickable="{value}"]',
    "enabled({value})": '//*[@enabled="{value}"]',
    "focusable({value})": '//*[@focusable="{value}"]',
    "focused({value})": '//*[@focused="{value}"]',
    "longClickable({value})": '//*[@long-clickable="{value}"]',
    "scrollable({value})": '//*[@scrollable="{value}"]',
    "selected({value})": '//*[@selected="{value}"]',

    # --- Index & instance ---
    "index({value})": '//*[@index="{value}"]',
    "instance({value})": '({base_xpath})[{value}]',  # костыль, {base_xpath} нужен

    # --- Package ---
    "packageName({value})": '//*[@package="{value}"]',
    "packageNameRegex({value})": '//*[contains(@package,"{value}")]',  # костыль

    # --- Parent / Child ---
    "fromParent({value})": '{parent_xpath}/child::*[{value}]',  # костыль
    "childSelector({value})": './*[{value}]',  # костыль

    # --- Count ---
    "count({value})": 'count({base_xpath})',  # костыль

"""
