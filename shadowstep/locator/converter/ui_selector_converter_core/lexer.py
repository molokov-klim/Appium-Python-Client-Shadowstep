# shadowstep/locator/ui_selector_converter_core/lexer.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import cast


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

    def tokens(self) -> list[Token]:  # noqa: C901
        toks: list[Token] = []
        while self.i < self.n:
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
                continue
            if ch == ".":
                toks.append(Token(TokenType.DOT, ".", self.i))
                self._advance()
                continue
            if ch == "(":
                toks.append(Token(TokenType.LPAREN, "(", self.i))
                self._advance()
                continue
            if ch == ")":
                toks.append(Token(TokenType.RPAREN, ")", self.i))
                self._advance()
                continue
            if ch == ";":
                toks.append(Token(TokenType.SEMI, ";", self.i))
                self._advance()
                continue

            if ch in ('"', "'"):
                quote_char = ch
                start = self.i
                self._advance()
                buf = []
                while True:
                    if self.i >= self.n:
                        raise LexerError(f"Unterminated string at {start}")
                    c = self._advance()
                    if c == "\\":
                        if self.i >= self.n:
                            raise LexerError(f"Bad escape at {self.i}")
                        nxt = self._advance()
                        if nxt in (quote_char, "\\"):
                            buf.append(nxt)
                        elif nxt == "n":
                            buf.append("\n")
                        elif nxt == "t":
                            buf.append("\t")
                        else:
                            buf.append("\\" + nxt)
                        continue
                    if c == quote_char:
                        break
                    buf.append(c)
                toks.append(Token(TokenType.STRING, "".join(cast(list[str], buf)), start))
                continue

            if ch.isdigit():
                start = self.i
                while self.i < self.n and self._peek().isdigit():
                    self._advance()
                toks.append(Token(TokenType.NUMBER, self.text[start:self.i], start))
                continue

            if ch.isalpha() or ch == "_":
                start = self.i
                while self.i < self.n and (self._peek().isalnum() or self._peek() in "_$"):
                    self._advance()
                ident = self.text[start:self.i]
                low = ident.lower()
                if low == "new":
                    toks.append(Token(TokenType.NEW, ident, start))
                elif ident == "UiSelector":
                    toks.append(Token(TokenType.UISELECTOR, ident, start))
                elif low == "true":
                    toks.append(Token(TokenType.TRUE, ident, start))
                elif low == "false":
                    toks.append(Token(TokenType.FALSE, ident, start))
                else:
                    toks.append(Token(TokenType.IDENT, ident, start))
                continue

            raise LexerError(f"Unexpected char {ch!r} at {self.i}")

        toks.append(Token(TokenType.EOF, None, self.i))
        return toks
