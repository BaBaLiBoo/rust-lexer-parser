# 类 Rust 子集词法分析与语法分析器

## 1. 项目简介
本项目是一个面向课程作业验收的类 Rust 子集编译前端实验实现，包含词法分析器与递归下降语法分析器。项目目标是对输入源码进行分词、语法检查，并在需要时输出 AST（抽象语法树），用于演示“从源码到结构化语法表示”的完整流程。

当前版本已完成最低强制要求，并在不破坏基础能力的前提下实现了若干扩展能力（如 `else if`、`for`、`loop`、`break`、`continue`、引用/解引用、数组/索引、元组）。本仓库已整理为可提交、可演示、可写报告的最终包装状态。

## 2. 功能概览
- **词法分析能力**：将源码切分为关键字、标识符、字面量、运算符、分隔符等 token，并记录行列号。
- **最低强制语法能力**：支持函数、参数、返回、变量声明、赋值、基本表达式、`if`、`while` 等。
- **扩展语法能力**：支持 `else / else if / for / loop / break / continue`。
- **高级表达式能力**：支持 `&expr`、`*expr`、数组字面量、索引表达式、元组字面量，以及分组表达式与元组的区分。
- **AST 输出能力**：解析成功后可通过命令行输出 JSON 结构 AST。
- **错误定位能力**：词法错误和语法错误均包含行号、列号，便于定位。

## 3. 支持的词法规则
### 3.1 关键字
`fn`、`let`、`mut`、`return`、`if`、`else`、`while`、`for`、`in`、`loop`、`break`、`continue`、`i32`。

### 3.2 标识符
以字母或下划线开头，后续可包含字母、数字、下划线；关键字与标识符可正确区分。

### 3.3 整数字面量
支持十进制整数。

### 3.4 多字符运算符
`==`、`!=`、`<=`、`>=`、`->`、`..`。

### 3.5 单字符符号
`+`、`-`、`*`、`/`、`=`、`<`、`>`、`&`、`;`、`,`、`:`、`(`、`)`、`{`、`}`、`[`、`]`。

### 3.6 注释
支持行注释 `// ...` 与块注释 `/* ... */`（块注释不支持嵌套）。

### 3.7 最长匹配原则
词法分析遵循最长匹配原则，优先识别多字符运算符，避免把 `==` 错分为两个 `=`，把 `..` 错分为两个 `.`。

## 4. 支持的语法规则
### 4.1 最低强制规则
- 程序由 0 个或多个函数声明组成；
- 函数声明支持参数列表与可选返回类型 `-> i32`；
- 语句支持空语句、`return`、`let mut` 声明、赋值、表达式语句；
- 控制流支持 `if` 与 `while`；
- 表达式支持比较、加减、乘除、分组、标识符、整数、函数调用。

### 4.2 扩展规则
- 分支扩展：`if / else if / else`；
- 循环扩展：`loop`、`for i in start..end`；
- 跳转扩展：`break`、`continue`；
- 表达式扩展：一元 `&`、`*`，数组字面量，索引表达式，元组字面量。

### 4.3 表达式优先级层次（由低到高）
1. 比较层：`< <= > >= == !=`
2. 加减层：`+ -`
3. 乘除层：`* /`
4. 一元层：`&expr`、`*expr`
5. 后缀层：函数调用 `f(...)`、索引 `a[i]`
6. 基础层：整数、标识符、分组表达式、数组字面量、元组字面量

## 5. AST 节点概览
- `Program`：整棵语法树根节点，包含多个函数。
- `FunctionDecl`：函数声明节点，记录函数名、参数、返回类型、函数体。
- `Block`：语句块节点，包含语句序列。
- `ReturnStmt`：返回语句。
- `LetStmt`：`let mut` 声明语句。
- `AssignStmt`：赋值语句（当前左值限定为标识符）。
- `IfStmt`：条件分支，可链式承载 `else if` 与 `else`。
- `WhileStmt`：`while` 循环语句。
- `LoopStmt`：`loop` 无限循环语句。
- `ForStmt`：区间 `for` 循环语句。
- `BreakStmt`：循环内跳出语句。
- `ContinueStmt`：循环内继续下一轮语句。
- `Binary`：二元运算表达式。
- `Unary`：一元运算表达式（引用/解引用）。
- `Call`：函数调用表达式。
- `ArrayLiteral`：数组字面量表达式。
- `IndexExpr`：索引表达式。
- `TupleLiteral`：元组字面量表达式。
- `Grouped`：分组表达式 `(expr)`。
- `Identifier`：标识符表达式。
- `IntLiteral`：整数字面量表达式。

## 6. 演示样例文件说明
演示样例位于 `examples/`：
- `minimum_demo.rsx`：最低要求覆盖样例（函数、参数、`return`、`let mut`、赋值、调用、`if`、`while`）。
- `control_flow_demo.rsx`：控制流扩展示例（`if / else if / else`、`while / loop / for`、`break / continue`）。
- `advanced_expr_demo.rsx`：高级表达式示例（`&expr`、`*expr`、数组/索引、元组、分组与元组区分）。

## 7. 运行方式（仓库根目录）
### 7.1 运行词法分析
```bash
python main.py --mode lex examples/minimum_demo.rsx
```

### 7.2 运行语法分析
```bash
python main.py --mode parse examples/minimum_demo.rsx
```

### 7.3 打印 AST
```bash
python main.py --mode parse --ast examples/control_flow_demo.rsx
```

### 7.4 执行测试
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 7.5 运行新增 demo 文件示例
```bash
python main.py --mode parse examples/minimum_demo.rsx
python main.py --mode parse --ast examples/control_flow_demo.rsx
python main.py --mode parse examples/advanced_expr_demo.rsx
```


## 8. 图形界面使用说明（tkinter）
为便于课程答辩演示，项目新增了一个轻量本地 GUI：`gui.py`。该界面基于 Python 标准库 `tkinter`，无需额外安装大型依赖。

### 8.1 启动方式
```bash
python gui.py
```

### 8.2 界面功能
- **源码输入区**：可直接粘贴/编辑源码；
- **快速加载 Demo**：
  - `minimum_demo`
  - `control_flow_demo`
  - `advanced_expr_demo`
- **操作按钮**：
  - 词法分析
  - 语法分析
  - 语法分析并显示 AST
  - 清空
- **输出区**：
  - 展示 token 列表（词法分析结果）
  - 展示解析成功/失败信息（语法分析结果）
  - **图形化AST显示**：默认显示可视化的树状结构
  - **JSON格式切换**：可在图形界面和JSON格式间切换
  - **缩放控制**：支持放大、缩小、重置、适应窗口大小
- **状态栏**：展示当前模式和执行成功/失败状态。

### 8.3 AST可视化功能
项目支持将抽象语法树(AST)以可视化的图形界面显示，比传统的JSON格式更加直观易读。

#### 8.3.1 图形化AST特点
- **层次清晰**：使用节点和连接线绘制树状结构，父子关系一目了然
- **信息直观**：节点显示类型和关键信息（如函数名、运算符、值等）
- **交互操作**：
  - **拖动浏览**：按住鼠标左键拖动画布查看不同区域
  - **缩放控制**：
    - `🔍+` 按钮：放大查看细节
    - `🔍-` 按钮：缩小查看整体
    - `↺` 按钮：重置到原始大小
    - `适应` 按钮：自动缩放使整个树可见
  - **滚轮操作**：
    - 鼠标滚轮：上下滚动
    - Ctrl+滚轮：快速缩放
- **格式切换**：点击”切换为 JSON 格式”按钮可在图形界面和JSON格式间切换

#### 8.3.2 支持的节点类型
所有AST节点类型都支持图形化显示，包括：
- **程序结构**: `Program`, `FunctionDecl`
- **语句**: `Block`, `ReturnStmt`, `LetStmt`, `AssignStmt`, `IfStmt`, `WhileStmt`, `LoopStmt`, `ForStmt`, `BreakStmt`, `ContinueStmt`
- **表达式**: `Binary`, `Unary`, `Call`, `ArrayLiteral`, `IndexExpr`, `TupleLiteral`, `Grouped`, `Identifier`, `IntLiteral`

### 8.4 GUI 演示建议流程
1. 点击”加载 minimum_demo”，再点”词法分析”，查看 token（行列号、类型、词素）。
2. 点击”语法分析”，确认输出 `Parse succeeded.`。
3. 点击”语法分析并显示 AST”，查看**图形化AST树状结构**。
4. 使用**缩放控制按钮**或**鼠标拖动**浏览完整的AST树。
5. 点击”切换为 JSON 格式”查看传统的JSON格式AST。
6. 切换加载 `control_flow_demo`、`advanced_expr_demo` 重复上述步骤。
7. 人为输入非法代码（如缺失分号），点击语法分析，查看错误行列定位。

### 8.5 技术实现
- **图形化核心模块**: `graphical_ast_viewer.py`
- **文本可视化模块**: `ast_visualizer.py`
- **GUI集成**: `gui.py`
- **向后兼容**: 保持原有命令行JSON输出功能

## 9. 测试说明
- 测试覆盖词法关键点：关键字/标识符区分、多字符运算符、注释处理、`mut` 与 `i32` 识别等。
- 测试覆盖语法关键点：最低强制规则、控制流扩展、表达式优先级、高级表达式、多种非法输入报错。
- 当前测试命令：
  ```bash
  python -m unittest discover -s tests -p "test_*.py"
  ```
- 当前状态：全部测试通过（以本次最终验证结果为准）。

## 10. 已知限制
- 单元素元组 `(expr,)` 暂不支持。
- 元组末尾逗号 `(1,2,)` 暂不支持。
- 类型系统当前仅支持 `i32`。
- `for` 当前仅支持 `start..end` 这种区间形式。
- 赋值语句左值当前仅支持标识符，不支持更复杂左值。

## 11. 作业要求符合性说明
下表给出最低强制规则的实现对照（规则编号与测试样例命名保持一致）：

| 规则编号 | 规则说明（中文） | 语义映射（实现方式） | 关键代码位置 | 对应测试样例 |
|---|---|---|---|---|
| 1.1 | 空函数体 | `fn name(){}` | `parse_function` / `parse_block` | `program_1_1` |
| 1.2 | 空语句序列 | `;` 作为 `EmptyStmt` | `parse_statement` | `program_1_2` |
| 1.3 | `return ;` | 无返回值返回语句 | `parse_statement` | `program_1_3` |
| 1.4 | 函数参数 | 参数支持 `mut name:i32` | `parse_params` / `parse_param` | `program_1_4` |
| 1.5 | 函数返回类型 | `-> i32` | `parse_function` / `parse_type` | `program_1_5` |
| 2.0 | 声明并初始化 | `let mut a:i32 = expr;` | `parse_var_decl` | `program_2_0` |
| 2.1 | 声明不初始化 | `let mut a;` / `let mut b:i32;` | `parse_var_decl` | `program_2_1` |
| 2.2 | 赋值语句 | `a = expr;` | `parse_statement`（赋值分支） | `program_2_2` |
| 3.1 | 基础表达式 | 整数、标识符、分组 | `parse_primary` | `program_3_1__1`、`program_3_1__2` |
| 3.2 | 比较表达式 | `< <= > >= == !=` | `parse_comparison` | `program_3_2` |
| 3.3 | 加减表达式 | `+ -` | `parse_additive` | `program_3_3` |
| 3.4 | 乘除表达式 | `* /` | `parse_multiplicative` | `program_3_4` |
| 3.5 | 函数调用 | `f(...)` | `parse_postfix` | `program_3_5__1`、`program_3_5__2` |
| 4.1 | 条件语句 | `if cond { ... }` | `parse_if_stmt` | `program_4_1` |
| 5.0 | 函数返回表达式 | `return a+b;` | `parse_statement` + 表达式链 | `program_5_0` |
| 5.1 | `while` 循环 | `while cond { ... }` | `parse_statement`（`while` 分支） | `program_5_1` |

## 12. 最终提交检查清单
- [x] 源代码已准备
- [x] README 已准备
- [x] 测试命令可运行
- [x] 演示样例已准备
- [x] AST 演示可运行
- [x] 已知限制已说明

## 13. 报告写作辅助
- **词法分析实现思路**：按字符扫描，跳过空白与注释，按最长匹配识别多字符运算符，输出带位置信息的 token 序列。
- **语法分析实现思路**：使用递归下降解析器，按“程序—函数—语句—表达式”分层，实现明确的 `expect/match` 错误检查。
- **表达式优先级设计**：通过多层函数（比较→加减→乘除→一元→后缀→基础）保证优先级与结合顺序正确。
- **AST 设计思路**：每个语法结构映射为一个 JSON 节点类型，便于调试、可视化和后续语义扩展。
- **测试策略**：同时覆盖“成功解析”与“失败报错”两类用例，覆盖最低要求、扩展语法与边界输入。
- **已知限制**：明确记录尚未支持的语法点，避免在报告中夸大实现范围。
