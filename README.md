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

## 3. 支持的最低语法规则

- `Program -> FunctionDecl*`
- 函数声明：`fn ID (params?) (-> i32)? block`
- 形参：`[mut] ID : i32`
- 语句：
  - 空语句 `;`
  - `return;` / `return expr;`
  - `let mut ID [:i32] [=expr] ;`
  - 赋值 `ID = expr;`
  - `if expr { ... } [else ...]`
  - `while expr { ... }`
  - 表达式语句（含函数调用）
- 表达式优先级：
  - 比较：`< <= > >= == !=`
  - 加减：`+ -`
  - 乘除：`* /`
  - 原子：整数、标识符、括号、函数调用

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

## 6. 作业要求符合性对照表（最低强制）

| 规则编号 | 是否支持 | 对应代码文件 | 对应测试名 |
|---|---|---|---|
| 0.1 | ✅ | `code/myLexer.py` | `LexerTests.test_if123_identifier` |
| 0.2 | ✅ | `code/myLexer.py` | `LexerTests.test_if_equal_number` |
| 0.3 | ✅ | `code/myLexer.py` | `LexerTests.test_multi_char_ops` |
| 1.1 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_1_1`) |
| 1.2 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_1_2`) |
| 1.3 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_1_3`) |
| 1.4 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_1_4`) |
| 1.5 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_1_5`) |
| 2.0 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_2_0`) |
| 2.1 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_2_1`) |
| 2.2 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_2_2`) |
| 3.1 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_3_1__1`, `program_3_1__2`) |
| 3.2 | ✅ | `code/myParser.py` | `ParserTests.test_comparison_operators_parse_success` |
| 3.3 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_3_3`) |
| 3.4 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_3_4`) |
| 3.5 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_3_5__1`, `program_3_5__2`) |
| 4.1 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_4_1`) |
| 5.0 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_5_0`) |
| 5.1 | ✅ | `code/myParser.py` | `ParserTests.test_required_programs` (`program_5_1`) |

## 7. 额外覆盖（验收补强）

- 词法注释覆盖：`//` 与 `/* */`。
- 比较运算全覆盖：`< <= > >= == !=`。
- 优先级与调用覆盖：`1+2*3`、`(1+2)*3`、`a+b<c`、`foo(1,2+3)`。
- 负向用例覆盖：缺右括号、缺分号、非法 token、表达式不完整、`if/while` 后缺语句块、`return` 后语法错误。
