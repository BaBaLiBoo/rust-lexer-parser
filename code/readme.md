# Rust-like Lexer & Parser (Submission Notes)

This folder belongs to the same coursework submission documented in the root `README.md`.

## Summary

The project implements a Rust-like subset lexer and parser with:
- required coursework grammar coverage,
- `if / else if / else`,
- `while / loop / for`,
- `break / continue`,
- unary `&expr` / `*expr`,
- array literals and indexing,
- tuple literals.

## Demo Inputs

- `code/examples/minimum_requirements_demo.rsx`
- `code/examples/control_flow_demo.rsx`
- `code/examples/advanced_expressions_demo.rsx`

## Commands (run from repository root)

```bash
python code/main.py --mode lex code/examples/minimum_requirements_demo.rsx
python code/main.py --mode parse --ast code/examples/control_flow_demo.rsx
python code/main.py --mode parse --ast code/examples/advanced_expressions_demo.rsx
python -m unittest discover -s code/tests -p 'test_*.py'
```

For complete syntax/AST details and submission checklist, use the root `README.md` as the source of truth.
