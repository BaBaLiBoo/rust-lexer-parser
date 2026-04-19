# Rust-like Lexer & Parser（课程作业验收版）

本项目实现一个**类 Rust 子集**的词法分析器（Lexer）与递归下降语法分析器（Parser），目标是满足课程最低强制规则并可用于作业验收提交。

## 1. 项目用途

- 对输入源代码做词法切分（tokenize）。
- 在词法正确的前提下进行语法分析并构建 AST（Python `dict` 结构）。
- 在命令行输出错误位置（line/col），用于快速定位作业样例中的错误。

## 2. 支持的词法规则

- 关键字：`i32 let if else while return mut fn for in loop break continue`
- 标识符：`(字母|_)(字母|数字|_)*`
- 整数字面量：`数字+`
- 多字符符号：`== >= <= != -> ..`
- 单字符符号：`= + - * / > < & ( ) { } [ ] ; : , . #`
- 注释：单行 `//`、块注释 `/* ... */`
- 最长匹配策略（例如优先识别 `>=`，不是 `>` + `=`）

## 3. 支持的语法规则（含本阶段扩展）

- `Program -> FunctionDecl*`
- 函数声明：`fn ID (params?) (-> i32)? block`
- 形参：`[mut] ID : i32`
- 语句：
  - 空语句 `;`
  - `return;` / `return expr;`
  - `let mut ID [:i32] [=expr] ;`
  - 赋值 `ID = expr;`
  - `if expr { ... } [else ...]`
  - `if expr { ... } else if expr { ... }`（支持链式 `else if` 与最终 `else`）
  - `while expr { ... }`
  - `loop { ... }`
  - `for ID in expr .. expr { ... }`（至少覆盖 `for i in 0..10 { ... }`）
  - `break;` / `continue;`（语句形式）
  - 表达式语句（含函数调用）
- 表达式优先级：
  - 比较：`< <= > >= == !=`
  - 加减：`+ -`
  - 乘除：`* /`
  - 一元：`&expr`、`*expr`
  - 后缀：函数调用 `foo(...)`、索引 `arr[0]`
  - 原子：整数、标识符、括号分组、数组字面量、元组字面量

### 3.1 本阶段新增语法（高阶扩展）

- 引用表达式：`&expr`（如 `&a`、`foo(&a)`）
- 解引用表达式：`*expr`（如 `*p`、`*p+1`）
- 数组字面量：`[]`、`[1]`、`[1,2,3]`
- 索引表达式：`arr[0]`（支持嵌入调用参数，如 `foo([1,2], arr[0])`）
- 元组字面量：`(1,2)`、`(a,b+1)`、嵌套元组（如 `((1,2),(3,4))`）
- 分组与元组区分：`(a)` 视为分组表达式，`(a,b)` 视为元组字面量

当前限制（明确说明）：
- 暂不支持单元素元组语法 `(expr,)`（会报语法错误）。

## 4. 从仓库根目录运行

> 下列命令都在仓库根目录执行。

### 4.1 运行词法分析

```bash
python code/main.py --mode lex code/sample.rsx
```

### 4.2 运行语法分析

```bash
python code/main.py --mode parse code/sample.rsx
```

### 4.3 打印 AST

```bash
python code/main.py --mode parse --ast code/sample.rsx
```

### 4.4 执行测试

```bash
python -m unittest discover -s code/tests -p 'test_*.py'
```

## 5. 输入示例

### 5.1 合法输入样例

`code/sample.rsx`

```rs
fn program_5_1(mut n:i32){
  while n>0 {
    n=n-1;
  }
}
```

新增示例（引用/数组/元组）：

```rs
fn feature_demo(mut a:i32, mut p:i32, mut arr:i32){
  foo(&a);
  *p+1;
  [1,2,3];
  arr[0];
  (a, arr[0]+1);
}
```

### 5.2 报错输入样例

```rs
fn bad(){ return +; }
```

运行：

```bash
python code/main.py --mode parse /tmp/invalid.rsx
```

期望包含错误信息：

```text
PARSE ERROR: Expected expression at line 1, col 18
```

## 6. 作业要求符合性对照表（最低强制 + 本阶段增量）

> 仅列最低强制规则：`0.1 0.2 0.3 1.1 1.2 1.3 1.4 1.5 2.0 2.1 2.2 3.1 3.2 3.3 3.4 3.5 4.1 5.0 5.1`。

| 规则编号 | 是否支持 | 实际支持代码位置 | 实际测试用例 |
|---|---|---|---|
| 0.1（变量属性 / `mut`） | ✅ | `code/myLexer.py`（`KEYWORDS` 分流）、`code/myParser.py::parse_param`、`code/myParser.py::parse_var_decl` | `LexerTests.test_mut_and_i32_keywords`，`ParserTests.test_required_programs` (`program_1_4`, `program_2_0`, `program_2_1`) |
| 0.2（类型 `i32`） | ✅ | `code/myLexer.py`（`KEYWORDS` 分流）、`code/myParser.py::parse_type` | `LexerTests.test_mut_and_i32_keywords`，`ParserTests.test_required_programs` (`program_1_4`, `program_1_5`, `program_2_0`) |
| 0.3（左值 / 标识符） | ✅ | `code/myLexer.py`（标识符扫描）、`code/myParser.py::parse_primary`、`code/myParser.py::parse_statement`（赋值分支） | `ParserTests.test_identifier_as_lvalue_assignment`，`ParserTests.test_required_programs` (`program_2_2`, `program_3_1__2`) |
| 1.1 | ✅ | `code/myParser.py::parse_program`、`parse_function` | `ParserTests.test_required_programs` (`program_1_1`) |
| 1.2 | ✅ | `code/myParser.py::parse_block`、`parse_statement`（空语句） | `ParserTests.test_required_programs` (`program_1_2`) |
| 1.3 | ✅ | `code/myParser.py::parse_statement`（`return` 分支） | `ParserTests.test_required_programs` (`program_1_3`) |
| 1.4 | ✅ | `code/myParser.py::parse_param` | `ParserTests.test_required_programs` (`program_1_4`) |
| 1.5 | ✅ | `code/myParser.py::parse_function`（`->` 返回类型） | `ParserTests.test_required_programs` (`program_1_5`) |
| 2.0 | ✅ | `code/myParser.py::parse_var_decl`（`let mut ... :i32 = expr`） | `ParserTests.test_required_programs` (`program_2_0`) |
| 2.1 | ✅ | `code/myParser.py::parse_var_decl`（可选类型与初始化） | `ParserTests.test_required_programs` (`program_2_1`) |
| 2.2 | ✅ | `code/myParser.py::parse_statement`（`ID = expr;`） | `ParserTests.test_required_programs` (`program_2_2`)、`ParserTests.test_identifier_as_lvalue_assignment` |
| 3.1 | ✅ | `code/myParser.py::parse_primary`（整数、标识符、括号） | `ParserTests.test_required_programs` (`program_3_1__1`, `program_3_1__2`) |
| 3.2 | ✅ | `code/myParser.py::parse_comparison` | `ParserTests.test_comparison_operators_parse_success` |
| 3.3 | ✅ | `code/myParser.py::parse_additive` | `ParserTests.test_required_programs` (`program_3_3`) |
| 3.4 | ✅ | `code/myParser.py::parse_multiplicative` | `ParserTests.test_required_programs` (`program_3_4`) |
| 3.5 | ✅ | `code/myParser.py::parse_primary`（函数调用） | `ParserTests.test_required_programs` (`program_3_5__1`, `program_3_5__2`)、`ParserTests.test_precedence` |
| 4.1 | ✅ | `code/myParser.py::parse_statement`、`parse_if_stmt`（`if/else if/else`） | `ParserTests.test_required_programs` (`program_4_1`) |
| 5.0（循环语句类别） | ✅ | `code/myParser.py::parse_statement`（`while` 分支，循环语句） | `ParserTests.test_loop_statement_while` |
| 5.1 | ✅ | `code/myParser.py::parse_statement`（`while`）+ `parse_statement`（循环体内赋值） | `ParserTests.test_required_programs` (`program_5_1`) |

### 6.1 本阶段额外支持规则（非最低强制）

| 扩展规则 | 是否支持 | 实际支持代码位置 | 实际测试用例 |
|---|---|---|---|
| 4.2（`if ... else ...`） | ✅ | `code/myParser.py::parse_if_stmt` | `ParserTests.test_if_else_parse` |
| 4.3（`if ... else if ...` 链） | ✅ | `code/myParser.py::parse_if_stmt`（`else` 分支递归为 `IfStmt`） | `ParserTests.test_if_else_if_parse`、`ParserTests.test_chained_else_if_else_parse` |
| 5.2（`for ID in expr..expr {}`） | ✅ | `code/myParser.py::parse_statement`（`KW_FOR` 分支） | `ParserTests.test_for_range_parse`、`ParserTests.test_for_range_with_break_parse` |
| 5.3（`loop {}`） | ✅ | `code/myParser.py::parse_statement`（`KW_LOOP` 分支） | `ParserTests.test_loop_break_parse` |
| 5.4（`break;` / `continue;`） | ✅ | `code/myParser.py::parse_statement`（`KW_BREAK` / `KW_CONTINUE` 分支） | `ParserTests.test_loop_break_parse`、`ParserTests.test_while_continue_parse` |
| 6.1（引用 `&expr`） | ✅ | `code/myParser.py::parse_unary` | `ParserTests.test_reference_unary_expr` |
| 6.2（解引用 `*expr`） | ✅ | `code/myParser.py::parse_unary` | `ParserTests.test_dereference_unary_expr` |
| 6.3（数组字面量 / 索引） | ✅ | `code/myParser.py::parse_primary`（`ArrayLiteral`）、`parse_postfix`（`IndexExpr`） | `ParserTests.test_array_literal_and_index_expr` |
| 6.4（元组字面量） | ✅ | `code/myParser.py::parse_primary`（`TupleLiteral`） | `ParserTests.test_tuple_literal_and_grouped_distinction` |

## 7. 额外覆盖（验收补强）

- 词法注释覆盖：`//` 与 `/* */`。
- 比较运算全覆盖：`< <= > >= == !=`。
- 优先级与调用覆盖：`1+2*3`、`(1+2)*3`、`a+b<c`、`foo(1,2+3)`。
- 负向用例覆盖：缺右括号、缺分号、非法 token、表达式不完整、`if/while` 后缺语句块、`return` 后语法错误。
- 选择语句扩展覆盖：`if ... else ...`、`if ... else if ...`、链式 `else if ... else ...`。
- 循环语句扩展覆盖：`loop { ... }`、`for i in 0..10 { ... }`。
- 循环控制语句覆盖：`break;`、`continue;` 以及对应缺失分号的负向用例。

## 8. 验收结论（submission-ready）

- **最低规则满足情况**：第 6 节列出的最低强制规则（`0.1`~`5.1` 指定集合）均已覆盖并有对应代码/测试定位。
- **额外支持**：注释词法、比较运算全覆盖、表达式优先级、函数调用、多类负向错误用例。
- **从仓库根目录执行命令**：
  - 词法分析：`python code/main.py --mode lex code/sample.rsx`
  - 语法分析：`python code/main.py --mode parse code/sample.rsx`
  - AST 输出：`python code/main.py --mode parse --ast code/sample.rsx`
  - 测试执行：`python -m unittest discover -s code/tests -p 'test_*.py'`
- **测试执行状态**：已执行以上测试命令，当前全部通过。
