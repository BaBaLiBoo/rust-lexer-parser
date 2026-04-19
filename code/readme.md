# Rust-like Lexer & Parser（课程作业验收版）

> `code/readme.md` 与仓库根目录 `README.md` 保持一致，避免文档分叉。

本项目实现一个**类 Rust 子集**的词法分析器（Lexer）与递归下降语法分析器（Parser），在保留课程最低要求的基础上，已支持更高价值语法扩展：`else/else if/for/loop/break/continue`、引用/解引用、数组、元组。

## 当前支持（摘要）

- 语句：`return`、`let mut`、赋值、`if/else if/else`、`while`、`loop`、`for in ..`、`break`、`continue`、表达式语句。
- 表达式优先级：comparison > additive > multiplicative > unary > postfix > primary。
- 一元表达式：`&expr`、`*expr`。
- 数组：`[]`、`[1,2,3]`、`arr[0]`。
- 元组：`(1,2)`、`(a,b+1)`，并区分 `(a)`（分组）与 `(a,b)`（元组）。

## AST 扩展节点

- `Unary`：一元引用/解引用。
- `ArrayLiteral`：数组字面量。
- `IndexExpr`：索引表达式。
- `TupleLiteral`：元组字面量。
- `Grouped`：括号分组表达式（用于与元组区分）。

## 已知限制

- 暂不支持单元素元组 `(expr,)`。
- 暂不支持元组末尾逗号（例如 `(1,2,)`）。

## 运行与测试（仓库根目录）

```bash
python code/main.py --mode lex code/sample.rsx
python code/main.py --mode parse code/sample.rsx
python code/main.py --mode parse --ast code/sample.rsx
python -m unittest discover -s code/tests -p 'test_*.py'
```

## 参考

- 详细规则、样例、符合性对照表请见根目录：`README.md`。
