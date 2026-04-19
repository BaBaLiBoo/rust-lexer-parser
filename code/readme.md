# Rust-like Lexer & Parser (课程大作业版)

本项目实现了一个**类 Rust 语言**的词法分析器与语法分析器，重点覆盖课程要求的最低强制规则。

## 功能概览

- 词法分析（最长匹配，多字符运算符）
- 语法分析（递归下降）
- 表达式优先级：括号 > 乘除 > 加减 > 比较
- 清晰的错误位置（line/col）
- 命令行模式：
  - `lex`：仅词法分析
  - `parse`：词法 + 语法分析（可打印 AST）

## 支持的词法元素

- 关键字：`i32 let if else while return mut fn for in loop break continue`
- 标识符：`(字母|_)(字母|数字|_)*`
- 整数：`数字(数字)*`
- 运算/符号：
  - `= + - * / == > >= < <= != &`
  - `() {} [] ; : , -> . .. #`
- 注释：`//` 与 `/* */`

## 支持的最低语法范围

- `Program -> 函数声明串`
- 函数声明：`fn ID(形参) [-> i32] 语句块`
- 参数：`[mut] ID : i32`
- 语句：
  - 空语句 `;`
  - `return;`
  - `return expr;`
  - `let mut ID [ : i32 ] [ = expr ] ;`
  - `ID = expr;`
  - `if expr { ... } [else ...]`
  - `while expr { ... }`
  - 表达式语句（含函数调用）
- 表达式：数字、标识符、括号、函数调用、比较/加减/乘除

## 运行方式

### 1) 词法分析

```bash
python main.py --mode lex test.c
```

### 2) 语法分析

```bash
python main.py --mode parse test.c
```

### 3) 输出 AST

```bash
python main.py --mode parse --ast test.c
```

## 测试

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

测试已覆盖：
- `if123` 与 `if=123`
- `== >= <= != -> ..`
- `//` 与 `/* */`
- 关键字/标识符区分
- 最低语法范围样例程序
- 常见非法输入场景
