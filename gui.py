from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

from analyzer import lex_source, parse_source

BASE_DIR = Path(__file__).resolve().parent
EXAMPLES = {
    "minimum_demo": BASE_DIR / "examples" / "minimum_demo.rsx",
    "control_flow_demo": BASE_DIR / "examples" / "control_flow_demo.rsx",
    "advanced_expr_demo": BASE_DIR / "examples" / "advanced_expr_demo.rsx",
}


class AnalyzerGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Rust 子集词法/语法分析演示")
        self.root.geometry("1180x760")

        self.status_var = tk.StringVar(value="状态：就绪")
        self.mode_var = tk.StringVar(value="模式：等待操作")

        self._build_layout()

    def _build_layout(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(top, text="快速加载 Demo：", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        tk.Button(top, text="加载 minimum_demo", command=lambda: self.load_demo("minimum_demo")).pack(
            side=tk.LEFT, padx=4
        )
        tk.Button(
            top, text="加载 control_flow_demo", command=lambda: self.load_demo("control_flow_demo")
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            top, text="加载 advanced_expr_demo", command=lambda: self.load_demo("advanced_expr_demo")
        ).pack(side=tk.LEFT, padx=4)

        action = tk.Frame(self.root)
        action.pack(fill=tk.X, padx=10, pady=4)
        tk.Button(action, text="词法分析", width=16, command=self.run_lex).pack(side=tk.LEFT, padx=4)
        tk.Button(action, text="语法分析", width=16, command=self.run_parse).pack(side=tk.LEFT, padx=4)
        tk.Button(action, text="语法分析并显示 AST", width=22, command=self.run_parse_ast).pack(
            side=tk.LEFT, padx=4
        )
        tk.Button(action, text="清空", width=10, command=self.clear_all).pack(side=tk.LEFT, padx=4)

        panes = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = tk.Frame(panes)
        right = tk.Frame(panes)
        panes.add(left, stretch="always")
        panes.add(right, stretch="always")

        tk.Label(left, text="源码输入区", font=("Arial", 11, "bold")).pack(anchor="w")
        self.source_text = scrolledtext.ScrolledText(left, wrap=tk.NONE, font=("Consolas", 11))
        self.source_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        tk.Label(right, text="输出区", font=("Arial", 11, "bold")).pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(right, wrap=tk.NONE, font=("Consolas", 11), state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        status = tk.Frame(self.root)
        status.pack(fill=tk.X, padx=10, pady=(0, 8))
        tk.Label(status, textvariable=self.mode_var, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(status, textvariable=self.status_var, anchor="e").pack(side=tk.RIGHT)

    def set_output(self, text: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.configure(state=tk.DISABLED)

    def load_demo(self, key: str) -> None:
        path = EXAMPLES[key]
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as err:
            self.status_var.set("状态：加载失败")
            self.mode_var.set(f"模式：加载 {key}")
            messagebox.showerror("加载失败", f"无法读取文件：{path}\n{err}")
            return

        self.source_text.delete("1.0", tk.END)
        self.source_text.insert(tk.END, content)
        self.mode_var.set(f"模式：已加载 {key}")
        self.status_var.set(f"状态：成功 ({path.name})")

    def get_source(self) -> str:
        return self.source_text.get("1.0", tk.END).rstrip("\n")

    def run_lex(self) -> None:
        self.mode_var.set("模式：词法分析")
        src = self.get_source()
        result = lex_source(src)
        self.set_output(result.output)
        self.status_var.set("状态：成功" if result.ok else "状态：失败")

    def run_parse(self) -> None:
        self.mode_var.set("模式：语法分析")
        src = self.get_source()
        result = parse_source(src, with_ast=False)
        self.set_output(result.output)
        self.status_var.set("状态：成功" if result.ok else "状态：失败")

    def run_parse_ast(self) -> None:
        self.mode_var.set("模式：语法分析 + AST")
        src = self.get_source()
        result = parse_source(src, with_ast=True)
        self.set_output(result.output)
        self.status_var.set("状态：成功" if result.ok else "状态：失败")

    def clear_all(self) -> None:
        self.source_text.delete("1.0", tk.END)
        self.set_output("")
        self.mode_var.set("模式：等待操作")
        self.status_var.set("状态：已清空")


def main() -> None:
    root = tk.Tk()
    app = AnalyzerGUI(root)
    app.load_demo("minimum_demo")
    root.mainloop()


if __name__ == "__main__":
    main()
