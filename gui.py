from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

from analyzer import lex_source, parse_source
from graphical_ast_viewer import GraphicalASTViewer

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

        # 用于存储当前解析的AST，以便切换显示格式
        self.current_ast = None
        self.ast_visual_mode = True  # True: 图形界面, False: JSON格式
        self.graphical_viewer = None  # 图形化查看器实例

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

        # 输入区标题和内容
        input_header = tk.Frame(left)
        input_header.pack(fill=tk.X, pady=(0, 4))
        tk.Label(input_header, text="源码输入区", font=("Arial", 11, "bold")).pack(side=tk.LEFT)

        self.source_text = scrolledtext.ScrolledText(left, wrap=tk.NONE, font=("Consolas", 11))
        self.source_text.pack(fill=tk.BOTH, expand=True)

        # 输出区标题和内容
        output_header = tk.Frame(right)
        output_header.pack(fill=tk.X, pady=(0, 4))
        tk.Label(output_header, text="输出区", font=("Arial", 11, "bold")).pack(side=tk.LEFT)

        # 按钮容器
        button_container = tk.Frame(output_header)
        button_container.pack(side=tk.RIGHT, padx=4)

        self.toggle_button = tk.Button(button_container, text="切换为 JSON 格式",
                                      command=self.toggle_ast_format,
                                      state=tk.DISABLED)
        self.toggle_button.pack(side=tk.LEFT, padx=2)

        # 缩放控制按钮（仅在图形模式显示）
        self.zoom_frame = tk.Frame(button_container)
        tk.Button(self.zoom_frame, text="🔍+", width=3,
                 command=self.zoom_in).pack(side=tk.LEFT, padx=1)
        tk.Button(self.zoom_frame, text="🔍-", width=3,
                 command=self.zoom_out).pack(side=tk.LEFT, padx=1)
        tk.Button(self.zoom_frame, text="↺", width=2,
                 command=self.reset_zoom).pack(side=tk.LEFT, padx=1)
        tk.Button(self.zoom_frame, text="适应", width=3,
                 command=self.fit_zoom).pack(side=tk.LEFT, padx=1)

        # 创建输出区域容器
        self.output_container = tk.Frame(right)
        self.output_container.pack(fill=tk.BOTH, expand=True)

        # 文本输出区域
        self.output_text = scrolledtext.ScrolledText(self.output_container, wrap=tk.NONE,
                                                    font=("Consolas", 11), state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # 图形化输出区域 (初始隐藏)
        self.graphical_frame = tk.Frame(self.output_container)

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
        self.mode_var.set("模式：语法分析 + 图形化AST")
        src = self.get_source()
        # 使用可视化模式获取AST
        result = parse_source(src, with_ast=True, visual_ast=True)
        self.current_ast = result.ast
        self.ast_visual_mode = True

        if result.ok and result.ast:
            self.toggle_button.config(state=tk.NORMAL, text="切换为 JSON 格式")
            # 直接显示图形化AST
            self.show_graphical_ast()
            self.set_output("Parse succeeded.\n\n图形化AST已显示！")
        else:
            self.toggle_button.config(state=tk.DISABLED)
            self.set_output(result.output)

        self.status_var.set("状态：成功" if result.ok else "状态：失败")

    def switch_view_mode(self) -> None:
        """切换视图模式（文本/图形）"""
        if self.view_mode.get() == "graphical":
            # 切换到图形模式
            self.zoom_frame.pack(side=tk.LEFT, padx=2)
            if self.current_ast:
                self.show_graphical_ast()
        else:
            # 切换到文本模式
            self.zoom_frame.pack_forget()
            self.graphical_frame.pack_forget()
            self.output_text.pack(fill=tk.BOTH, expand=True)
            if self.current_ast:
                # 重新生成文本输出
                if self.ast_visual_mode:
                    from ast_visualizer import create_text_tree
                    tree_output = create_text_tree(self.current_ast, use_unicode=True)
                    output = "Parse succeeded.\n\n" + "=" * 50 + "\n"
                    output += "AST 可视化树状结构\n"
                    output += "=" * 50 + "\n\n"
                    output += tree_output
                else:
                    import json
                    output = "Parse succeeded.\n\n" + json.dumps(self.current_ast,
                                                                 ensure_ascii=False, indent=2)
                self.set_output(output)

    def show_graphical_ast(self) -> None:
        """显示图形化AST"""
        if not self.current_ast:
            return

        # 隐藏文本输出，显示图形输出
        self.output_text.pack_forget()
        self.graphical_frame.pack(fill=tk.BOTH, expand=True)

        # 显示缩放按钮
        self.zoom_frame.pack(side=tk.LEFT, padx=2)

        # 创建或更新图形化查看器
        if self.graphical_viewer is None:
            self.graphical_viewer = GraphicalASTViewer(self.graphical_frame)

        self.graphical_viewer.display_ast(self.current_ast)

    def zoom_in(self) -> None:
        """放大图形"""
        if self.graphical_viewer:
            self.graphical_viewer.zoom_in()

    def zoom_out(self) -> None:
        """缩小图形"""
        if self.graphical_viewer:
            self.graphical_viewer.zoom_out()

    def reset_zoom(self) -> None:
        """重置缩放"""
        if self.graphical_viewer:
            self.graphical_viewer.reset_zoom()

    def fit_zoom(self) -> None:
        """适应窗口大小"""
        if self.graphical_viewer:
            self.graphical_viewer.fit_to_window()

    def toggle_ast_format(self) -> None:
        """切换AST显示格式（图形界面 <-> JSON）"""
        if self.current_ast is None:
            return

        self.ast_visual_mode = not self.ast_visual_mode

        if self.ast_visual_mode:
            # 切换为图形界面
            self.show_graphical_ast()
            self.zoom_frame.pack(side=tk.LEFT, padx=2)  # 显示缩放按钮
            self.toggle_button.config(text="切换为 JSON 格式")
            self.set_output("Parse succeeded.\n\n图形化AST已显示！")
        else:
            # 切换为JSON格式
            self.graphical_frame.pack_forget()
            self.output_text.pack(fill=tk.BOTH, expand=True)
            self.zoom_frame.pack_forget()  # 隐藏缩放按钮

            import json
            output = "Parse succeeded.\n\n" + json.dumps(self.current_ast,
                                                         ensure_ascii=False, indent=2)
            self.set_output(output)
            self.toggle_button.config(text="切换为图形界面")

    def clear_all(self) -> None:
        self.source_text.delete("1.0", tk.END)
        self.set_output("")
        self.current_ast = None
        self.ast_visual_mode = True
        self.toggle_button.config(state=tk.DISABLED, text="切换为 JSON 格式")

        # 隐藏缩放按钮
        self.zoom_frame.pack_forget()

        # 重置到文本模式
        self.graphical_frame.pack_forget()
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # 清空图形化查看器
        if self.graphical_viewer:
            self.graphical_viewer.canvas.delete("all")

        self.mode_var.set("模式：等待操作")
        self.status_var.set("状态：已清空")


def main() -> None:
    root = tk.Tk()
    app = AnalyzerGUI(root)
    app.load_demo("minimum_demo")
    root.mainloop()


if __name__ == "__main__":
    main()
