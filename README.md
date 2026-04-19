# Rust-like Lexer & Parser (Final Submission)

A coursework-ready lexer and recursive-descent parser for a Rust-like subset. The project meets minimum requirements and includes stable higher-value extensions (`else/else if`, `loop/for/break/continue`, references/dereference, arrays/indexing, tuples).

## Supported Syntax (Overview)

- **Program shape**: `Program -> FunctionDecl*`
- **Functions**: `fn name(params?) (-> i32)? { ... }`
- **Statements**: empty `;`, `return`, `let mut`, assignment, expression statements
- **Control flow**: `if / else if / else`, `while`, `loop`, `for i in start..end`, `break`, `continue`
- **Expressions**:
  - comparison: `< <= > >= == !=`
  - additive: `+ -`
  - multiplicative: `* /`
  - unary: `&expr`, `*expr`
  - postfix: calls `foo(...)`, indexing `arr[0]`
  - primary: integer, identifier, grouped `(expr)`, array literal, tuple literal

## AST Node Overview

Core nodes include:
- `Program`, `FunctionDecl`, `Block`
- `ReturnStmt`, `VarDecl`, `AssignStmt`, `ExprStmt`
- `IfStmt`, `WhileStmt`, `LoopStmt`, `ForStmt`, `BreakStmt`, `ContinueStmt`
- `Binary`, `Unary`, `Call`, `Grouped`
- `ArrayLiteral`, `IndexExpr`, `TupleLiteral`

## Demo Files

- `code/examples/minimum_requirements_demo.rsx`
- `code/examples/control_flow_demo.rsx`
- `code/examples/advanced_expressions_demo.rsx`

## Run Demos (from repository root)

```bash
python code/main.py --mode lex code/examples/minimum_requirements_demo.rsx
python code/main.py --mode parse code/examples/minimum_requirements_demo.rsx
python code/main.py --mode parse --ast code/examples/minimum_requirements_demo.rsx

python code/main.py --mode parse --ast code/examples/control_flow_demo.rsx
python code/main.py --mode parse --ast code/examples/advanced_expressions_demo.rsx
```

## Run Tests (from repository root)

```bash
python -m unittest discover -s code/tests -p 'test_*.py'
```

## Known Limitations

- Single-element tuple syntax `(expr,)` is not supported.
- Tuple trailing comma `(1,2,)` is not supported.
- No new language features beyond coursework scope are included.

## Final Submission Checklist

- [x] Source code ready
- [x] Root-level run commands ready
- [x] Test command ready
- [x] Sample demo inputs ready
- [x] AST demo workflow ready
