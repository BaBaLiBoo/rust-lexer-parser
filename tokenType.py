from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenKind(Enum):
    # literals / identifiers
    IDENTIFIER = "identifier"
    INTEGER = "integer"

    # keywords
    KW_I32 = "i32"
    KW_LET = "let"
    KW_IF = "if"
    KW_ELSE = "else"
    KW_WHILE = "while"
    KW_RETURN = "return"
    KW_MUT = "mut"
    KW_FN = "fn"
    KW_FOR = "for"
    KW_IN = "in"
    KW_LOOP = "loop"
    KW_BREAK = "break"
    KW_CONTINUE = "continue"

    # operators and punctuation
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    EQ = "=="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    NE = "!="
    AMP = "&"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    SEMI = ";"
    COLON = ":"
    COMMA = ","

    ARROW = "->"
    DOT = "."
    DOT_DOT = ".."
    HASH = "#"

    EOF = "<eof>"


KEYWORDS = {
    "i32": TokenKind.KW_I32,
    "let": TokenKind.KW_LET,
    "if": TokenKind.KW_IF,
    "else": TokenKind.KW_ELSE,
    "while": TokenKind.KW_WHILE,
    "return": TokenKind.KW_RETURN,
    "mut": TokenKind.KW_MUT,
    "fn": TokenKind.KW_FN,
    "for": TokenKind.KW_FOR,
    "in": TokenKind.KW_IN,
    "loop": TokenKind.KW_LOOP,
    "break": TokenKind.KW_BREAK,
    "continue": TokenKind.KW_CONTINUE,
}


MULTI_CHAR_SYMBOLS = {
    "==": TokenKind.EQ,
    ">=": TokenKind.GE,
    "<=": TokenKind.LE,
    "!=": TokenKind.NE,
    "->": TokenKind.ARROW,
    "..": TokenKind.DOT_DOT,
}


SINGLE_CHAR_SYMBOLS = {
    "=": TokenKind.ASSIGN,
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    ">": TokenKind.GT,
    "<": TokenKind.LT,
    "&": TokenKind.AMP,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    "{": TokenKind.LBRACE,
    "}": TokenKind.RBRACE,
    "[": TokenKind.LBRACKET,
    "]": TokenKind.RBRACKET,
    ";": TokenKind.SEMI,
    ":": TokenKind.COLON,
    ",": TokenKind.COMMA,
    ".": TokenKind.DOT,
    "#": TokenKind.HASH,
}


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    line: int
    col: int
