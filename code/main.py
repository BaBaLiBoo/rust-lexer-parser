from __future__ import annotations

import argparse
import json
from pathlib import Path

from myLexer import Lexer
from myParser import ParseError, Parser


def run_lex(source: str):
    lexer = Lexer()
    tokens, errors = lexer.tokenize(source)
    if errors:
        for err in errors:
            print(f"LEX ERROR: {err.message} at line {err.line}, col {err.col}")
        return 1

    for tk in tokens:
        print(f"{tk.line}:{tk.col}\t{tk.kind.value}\t{tk.lexeme!r}")
    return 0


def run_parse(source: str, print_ast: bool):
    lexer = Lexer()
    tokens, errors = lexer.tokenize(source)
    if errors:
        for err in errors:
            print(f"LEX ERROR: {err.message} at line {err.line}, col {err.col}")
        return 1

    parser = Parser()
    try:
        ast = parser.parse(tokens)
    except ParseError as e:
        print(f"PARSE ERROR: {e}")
        return 1

    print("Parse succeeded.")
    if print_ast:
        print(json.dumps(ast, ensure_ascii=False, indent=2))
    return 0


def main():
    argp = argparse.ArgumentParser(description="Rust-like lexer + parser")
    argp.add_argument("file", type=Path, help="source file path")
    argp.add_argument("--mode", choices=["lex", "parse"], default="parse")
    argp.add_argument("--ast", action="store_true", help="print AST in parse mode")
    args = argp.parse_args()

    source = args.file.read_text(encoding="utf-8")
    if args.mode == "lex":
        raise SystemExit(run_lex(source))
    raise SystemExit(run_parse(source, args.ast))


if __name__ == "__main__":
    main()
