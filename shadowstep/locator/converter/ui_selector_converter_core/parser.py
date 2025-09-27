"""Parser for UiSelector expressions.

This module provides the Parser class for parsing tokenized
UiSelector expressions into an Abstract Syntax Tree (AST)
representation that can be used for further processing and
conversion to other locator formats.
"""
from __future__ import annotations

from typing import Any, cast

from shadowstep.locator.converter.ui_selector_converter_core.ast import MethodCall, Selector
from shadowstep.locator.converter.ui_selector_converter_core.lexer import (
    ParserError,
    Token,
    TokenType,
)


class Parser:
    """Parser (finite automaton from left to right)."""

    def __init__(self, tokens: list[Token]):
        """Initialize the Parser.

        Args:
            tokens: List of tokens to parse into an AST.

        """
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
            raise ParserError(f"Expected {ttype}, got {tok.type} at {tok.pos}")
        return self._advance()

    def parse(self) -> Selector:
        """Parse tokens into a Selector object.

        Returns:
            Selector: Parsed selector object containing method calls.

        """
        # Optional prefix "new UiSelector()"
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
        return MethodCall(name=cast("str", name_tok.value), args=args)

    def _parse_arg(self) -> str | int | bool | Selector:
        tok = self._peek()
        if tok.type == TokenType.STRING:
            self._advance()
            return cast("str", tok.value)
        if tok.type == TokenType.TRUE:
            self._advance()
            return True
        if tok.type == TokenType.FALSE:
            self._advance()
            return False
        if tok.type == TokenType.NUMBER:
            self._advance()
            return int(cast("str", tok.value))
        if tok.type == TokenType.NEW:
            return self._parse_nested_selector()
        if tok.type == TokenType.IDENT:
            self._advance()
            return cast("str", tok.value)
        raise ParserError(f"Unexpected token in arg: {tok.type} at {tok.pos}")

    def _parse_nested_selector(self) -> Selector:
        # Mandatory “new UiSelector()”
        self._expect(TokenType.NEW)
        self._expect(TokenType.UISELECTOR)
        self._expect(TokenType.LPAREN)
        self._expect(TokenType.RPAREN)
        nested = Selector()
        # Read .method(...) until we reach the parent's closing RPAREN
        while self._peek().type == TokenType.DOT:
            nested.methods.append(self._parse_method_call())
        return nested
