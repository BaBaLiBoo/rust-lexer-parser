from __future__ import annotations

import json
from dataclasses import dataclass

from myLexer import Lexer
from myParser import ParseError, Parser


@dataclass
class AnalysisResult:
    ok: bool
    output: str
    ast: dict | None = None


def lex_source(source: str) -> AnalysisResult:
    lexer = Lexer()
    tokens, errors = lexer.tokenize(source)
    if errors:
        lines = [f"词法错误: {err.message} (line {err.line}, col {err.col})" for err in errors]
        return AnalysisResult(False, "\n".join(lines), None)

    token_lines = [f"{tk.line}:{tk.col}\t{tk.kind.value}\t{tk.lexeme!r}" for tk in tokens]
    return AnalysisResult(True, "\n".join(token_lines), None)


def parse_source(source: str, with_ast: bool = False) -> AnalysisResult:
    lexer = Lexer()
    tokens, errors = lexer.tokenize(source)
    if errors:
        lines = [f"词法错误: {err.message} (line {err.line}, col {err.col})" for err in errors]
        return AnalysisResult(False, "\n".join(lines), None)

    parser = Parser()
    try:
        ast = parser.parse(tokens)
    except ParseError as err:
        return AnalysisResult(False, f"语法错误: {err.message} (line {err.line}, col {err.col})", None)

    if with_ast:
        return AnalysisResult(True, "Parse succeeded.\n\n" + json.dumps(ast, ensure_ascii=False, indent=2), ast)
    return AnalysisResult(True, "Parse succeeded.", ast)
