from __future__ import annotations

from dataclasses import dataclass

from tokenType import (
    KEYWORDS,
    MULTI_CHAR_SYMBOLS,
    SINGLE_CHAR_SYMBOLS,
    Token,
    TokenKind,
)


@dataclass(frozen=True)
class LexError:
    message: str
    line: int
    col: int


class Lexer:
    """Rust-like lexer with longest-match for multi-char operators."""

    def tokenize(self, source: str) -> tuple[list[Token], list[LexError]]:
        tokens: list[Token] = []
        errors: list[LexError] = []

        i = 0
        line = 1
        col = 1
        n = len(source)

        while i < n:
            ch = source[i]

            # whitespace
            if ch in " \t\r":
                i += 1
                col += 1
                continue
            if ch == "\n":
                i += 1
                line += 1
                col = 1
                continue

            # comments
            if source.startswith("//", i):
                i += 2
                col += 2
                while i < n and source[i] != "\n":
                    i += 1
                    col += 1
                continue
            if source.startswith("/*", i):
                start_line, start_col = line, col
                i += 2
                col += 2
                closed = False
                while i < n:
                    if source.startswith("*/", i):
                        i += 2
                        col += 2
                        closed = True
                        break
                    if source[i] == "\n":
                        i += 1
                        line += 1
                        col = 1
                    else:
                        i += 1
                        col += 1
                if not closed:
                    errors.append(LexError("Unterminated block comment", start_line, start_col))
                continue

            # identifier / keyword
            if ch.isalpha() or ch == "_":
                start_i, start_col = i, col
                i += 1
                col += 1
                while i < n and (source[i].isalnum() or source[i] == "_"):
                    i += 1
                    col += 1
                lex = source[start_i:i]
                kind = KEYWORDS.get(lex, TokenKind.IDENTIFIER)
                tokens.append(Token(kind, lex, line, start_col))
                continue

            # integer
            if ch.isdigit():
                start_i, start_col = i, col
                i += 1
                col += 1
                while i < n and source[i].isdigit():
                    i += 1
                    col += 1
                lex = source[start_i:i]
                tokens.append(Token(TokenKind.INTEGER, lex, line, start_col))
                continue

            # operators/punctuation (longest match)
            matched = None
            for op, kind in MULTI_CHAR_SYMBOLS.items():
                if source.startswith(op, i):
                    matched = (op, kind)
                    break
            if matched is not None:
                op, kind = matched
                tokens.append(Token(kind, op, line, col))
                i += len(op)
                col += len(op)
                continue

            if ch in SINGLE_CHAR_SYMBOLS:
                kind = SINGLE_CHAR_SYMBOLS[ch]
                tokens.append(Token(kind, ch, line, col))
                i += 1
                col += 1
                continue

            errors.append(LexError(f"Illegal character: {ch!r}", line, col))
            i += 1
            col += 1

        tokens.append(Token(TokenKind.EOF, "", line, col))
        return tokens, errors

    def getLex(self, lines: list[str]):
        """Backward compatible output for legacy UI glue code."""
        text = "\n".join(lines)
        tokens, errors = self.tokenize(text)
        items = []
        for idx, tk in enumerate(tokens, start=1):
            items.append(
                {
                    "id": idx,
                    "content": tk.lexeme,
                    "prop": tk.kind,
                    "loc": {"row": tk.line, "col": tk.col},
                }
            )
        return items, len(errors) == 0
