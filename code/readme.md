# 说明（以仓库根目录 README.md 为准）

本目录属于同一份课程作业提交工程，内容与仓库根目录 `README.md` 保持一致。

## 使用说明
- 本文件为简版索引说明。
- 详细的功能说明、规则对照表、已知限制、运行命令、测试说明、报告写作辅助，请统一查看仓库根目录 `README.md`。
- 如本文件与根目录 `README.md` 存在表述差异，以根目录 `README.md` 为唯一准则。

## 演示样例文件
- `code/examples/minimum_demo.rsx`：最低要求样例。
- `code/examples/control_flow_demo.rsx`：控制流扩展样例。
- `code/examples/advanced_expr_demo.rsx`：高级表达式扩展样例。

## 常用命令（在仓库根目录执行）
```bash
python code/main.py --mode lex code/examples/minimum_demo.rsx
python code/main.py --mode parse code/examples/minimum_demo.rsx
python code/main.py --mode parse --ast code/examples/control_flow_demo.rsx
python code/main.py --mode parse code/examples/advanced_expr_demo.rsx
python -m unittest discover -s code/tests -p 'test_*.py'
```
