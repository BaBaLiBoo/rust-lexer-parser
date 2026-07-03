from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

from analyzer import lex_source, parse_source
from graphical_ast_viewer import GraphicalASTViewer
from syntax_highlight import LineTextWidget

BASE_DIR = Path(__file__).resolve().parent
EXAMPLES = {
    "minimum_demo": BASE_DIR / "examples" / "minimum_demo.rsx",
    "control_flow_demo": BASE_DIR / "examples" / "control_flow_demo.rsx",
    "advanced_expr_demo": BASE_DIR / "examples" / "advanced_expr_demo.rsx",
}


class AnalyzerGUI:
    # 配色方案
    COLORS = {
        "primary": "#4A90E2",        # 主色调：浅蓝色
        "primary_dark": "#3A7BC8",   # 深蓝色
        "bg": "#F5F6F7",             # 背景色：浅灰
        "card_bg": "#FFFFFF",        # 卡片背景：白色
        "text": "#2C3E50",           # 文字颜色：深灰
        "text_light": "#7F8C8D",     # 浅色文字
        "border": "#E8EAED",         # 边框颜色
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Rust 子集词法/语法分析演示")
        self.root.geometry("1180x760")

        # 设置窗口背景色
        self.root.configure(bg=self.COLORS["bg"])

        self.status_var = tk.StringVar(value="状态：就绪")
        self.mode_var = tk.StringVar(value="模式：等待操作")

        # 用于存储当前解析的AST，以便切换显示格式
        self.current_ast = None
        self.ast_visual_mode = True  # True: 图形界面, False: JSON格式
        self.graphical_viewer = None  # 图形化查看器实例

        # 按钮状态管理
        self.active_button = None
        self.action_buttons = {}

        self._build_layout()

    def _build_layout(self) -> None:
        # 主容器
        main_container = tk.Frame(self.root, bg=self.COLORS["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Demo 加载区域
        demo_frame = tk.Frame(main_container, bg=self.COLORS["card_bg"])
        demo_frame.pack(fill=tk.X, pady=(0, 8))

        demo_label = tk.Label(demo_frame, text="快速加载 Demo",
                             font=("Microsoft YaHei UI", 10, "bold"),
                             bg=self.COLORS["card_bg"], fg=self.COLORS["text"])
        demo_label.pack(anchor="w", padx=10, pady=(6, 4))

        demo_buttons = tk.Frame(demo_frame, bg=self.COLORS["card_bg"])
        demo_buttons.pack(fill=tk.X, padx=10, pady=(0, 6))

        self._create_styled_button(demo_buttons, "加载 minimum_demo",
                                  lambda: self.load_demo("minimum_demo")).pack(side=tk.LEFT, padx=4)
        self._create_styled_button(demo_buttons, "加载 control_flow_demo",
                                  lambda: self.load_demo("control_flow_demo")).pack(side=tk.LEFT, padx=4)
        self._create_styled_button(demo_buttons, "加载 advanced_expr_demo",
                                  lambda: self.load_demo("advanced_demo")).pack(side=tk.LEFT, padx=4)

        # 操作按钮区域
        action_frame = tk.Frame(main_container, bg=self.COLORS["card_bg"])
        action_frame.pack(fill=tk.X, pady=(0, 8))

        action_label = tk.Label(action_frame, text="操作面板",
                               font=("Microsoft YaHei UI", 10, "bold"),
                               bg=self.COLORS["card_bg"], fg=self.COLORS["text"])
        action_label.pack(anchor="w", padx=10, pady=(6, 4))

        action_buttons = tk.Frame(action_frame, bg=self.COLORS["card_bg"])
        action_buttons.pack(fill=tk.X, padx=10, pady=(0, 6))

        self.action_buttons['lex'] = self._create_primary_button(action_buttons, "词法分析",
                                                                   self._on_lex_click)
        self.action_buttons['lex'].pack(side=tk.LEFT, padx=2)

        self.action_buttons['parse'] = self._create_primary_button(action_buttons, "语法分析",
                                                                    self._on_parse_click)
        self.action_buttons['parse'].pack(side=tk.LEFT, padx=2)

        self.action_buttons['parse_ast'] = self._create_primary_button(action_buttons, "语法分析并显示 AST",
                                                                        self._on_parse_ast_click)
        self.action_buttons['parse_ast'].pack(side=tk.LEFT, padx=2)

        self.action_buttons['clear'] = self._create_danger_button(action_buttons, "清空",
                                                                   self._on_clear_click)
        self.action_buttons['clear'].pack(side=tk.LEFT, padx=2)

        # 分割面板
        panes = tk.PanedWindow(main_container, orient=tk.HORIZONTAL,
                              bg=self.COLORS["bg"], bd=0, sashwidth=4)
        panes.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(panes, bg=self.COLORS["card_bg"])
        right = tk.Frame(panes, bg=self.COLORS["card_bg"])
        panes.add(left, stretch="always")
        panes.add(right, stretch="always")

        # 输入区
        input_header = tk.Frame(left, bg=self.COLORS["card_bg"])
        input_header.pack(fill=tk.X, pady=(8, 4))
        tk.Label(input_header, text="源码输入区",
                font=("Microsoft YaHei UI", 10, "bold"),
                bg=self.COLORS["card_bg"], fg=self.COLORS["text"]).pack(side=tk.LEFT)

        self.source_text = LineTextWidget(left, wrap=tk.NONE, font=("Consolas", 11))
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        # 绑定源码输入区内容变化事件
        self.source_text.text.bind("<<Modified>>", self._on_source_modified)
        self.source_was_modified = False

        # 输出区
        output_header = tk.Frame(right, bg=self.COLORS["card_bg"])
        output_header.pack(fill=tk.X, pady=(8, 4))

        tk.Label(output_header, text="输出区",
                font=("Microsoft YaHei UI", 10, "bold"),
                bg=self.COLORS["card_bg"], fg=self.COLORS["text"]).pack(side=tk.LEFT)

        # 按钮容器
        button_container = tk.Frame(output_header, bg=self.COLORS["card_bg"])
        button_container.pack(side=tk.RIGHT)

        self.toggle_button = self._create_secondary_button(button_container, "切换为 JSON 格式",
                                                           self.toggle_ast_format)
        self.toggle_button.pack(side=tk.LEFT, padx=2)
        self.toggle_button.config(state=tk.DISABLED)

        # 缩放控制按钮
        self.zoom_frame = tk.Frame(button_container, bg=self.COLORS["card_bg"])
        self.zoom_frame.pack(side=tk.LEFT, padx=2)

        self._create_icon_button(self.zoom_frame, "+", self.zoom_in).pack(side=tk.LEFT, padx=1)
        self._create_icon_button(self.zoom_frame, "-", self.zoom_out).pack(side=tk.LEFT, padx=1)
        self._create_icon_button(self.zoom_frame, "↺", self.reset_zoom).pack(side=tk.LEFT, padx=1)
        self._create_icon_button(self.zoom_frame, "适应", self.fit_zoom).pack(side=tk.LEFT, padx=1)

        # 创建输出区域容器
        self.output_container = tk.Frame(right, bg=self.COLORS["card_bg"])
        self.output_container.pack(fill=tk.BOTH, expand=True)

        # 文本输出区域
        self.output_text = scrolledtext.ScrolledText(self.output_container, wrap=tk.NONE,
                                                    font=("Consolas", 11), state=tk.DISABLED,
                                                    bg="#FAFBFC", fg=self.COLORS["text"],
                                                    relief=tk.FLAT, bd=0)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        # 图形化输出区域 (初始隐藏)
        self.graphical_frame = tk.Frame(self.output_container, bg=self.COLORS["card_bg"])

        # 状态栏
        status = tk.Frame(main_container, bg=self.COLORS["card_bg"], height=30)
        status.pack(fill=tk.X, pady=(8, 0))
        status.pack_propagate(False)

        tk.Label(status, textvariable=self.mode_var,
                font=("Microsoft YaHei UI", 9),
                bg=self.COLORS["card_bg"], fg=self.COLORS["text_light"],
                anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        tk.Label(status, textvariable=self.status_var,
                font=("Microsoft YaHei UI", 9),
                bg=self.COLORS["card_bg"], fg=self.COLORS["primary"],
                anchor="e").pack(side=tk.RIGHT, padx=10)

    def _create_styled_button(self, parent, text, command):
        """创建样式化按钮"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Microsoft YaHei UI", 9),
                       bg=self.COLORS["card_bg"],
                       fg=self.COLORS["primary"],
                       activebackground=self.COLORS["primary"],
                       activeforeground="white",
                       relief=tk.FLAT, bd=1, cursor="hand2",
                       padx=12, pady=5)
        return btn

    def _create_primary_button(self, parent, text, command):
        """创建主要按钮"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Microsoft YaHei UI", 9, "bold"),
                       bg=self.COLORS["primary"],
                       fg="white",
                       activebackground=self.COLORS["primary_dark"],
                       activeforeground="white",
                       disabledforeground="white",
                       relief=tk.FLAT, bd=0, cursor="hand2",
                       padx=15, pady=6)
        return btn

    def _create_secondary_button(self, parent, text, command):
        """创建次要按钮"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Microsoft YaHei UI", 9),
                       bg=self.COLORS["primary"],
                       fg="white",
                       activebackground=self.COLORS["primary_dark"],
                       activeforeground="white",
                       disabledforeground="white",
                       relief=tk.FLAT, bd=0, cursor="hand2",
                       padx=12, pady=5)
        return btn

    def _create_danger_button(self, parent, text, command):
        """创建危险按钮（使用灰色）"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Microsoft YaHei UI", 9),
                       bg=self.COLORS["text_light"],
                       fg="white",
                       activebackground=self.COLORS["text"],
                       activeforeground="white",
                       disabledforeground="white",
                       relief=tk.FLAT, bd=0, cursor="hand2",
                       padx=12, pady=6)
        return btn

    def _create_icon_button(self, parent, text, command):
        """创建图标按钮"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Microsoft YaHei UI", 9),
                       bg=self.COLORS["card_bg"],
                       fg=self.COLORS["text"],
                       activebackground=self.COLORS["border"],
                       activeforeground=self.COLORS["text"],
                       relief=tk.FLAT, bd=1, cursor="hand2",
                       width=3, pady=3)
        return btn

    def set_output(self, text: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.configure(state=tk.DISABLED)

    def _clear_output(self) -> None:
        """清空输出区并重置相关状态"""
        self._switch_to_text_mode()
        self.set_output("")
        self.toggle_button.pack_forget()
        self.current_ast = None

    def _on_source_modified(self, event=None) -> None:
        """源码输入区内容变化时的处理"""
        # 检查是否真的被修改了
        if self.source_text.text.edit_modified():
            self.source_text.text.edit_modified(False)

            # 只有在有输出内容时才清空
            current_output = self.output_text.get("1.0", tk.END).strip()
            if current_output:
                self._clear_output()
                self.mode_var.set("模式：源码已修改，请重新分析")
                self.status_var.set("状态：等待操作")

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
        self.source_text.highlight_all()  # 触发语法高亮
        self.mode_var.set(f"模式：已加载 {key}")
        self.status_var.set(f"状态：成功 ({path.name})")

        # 清空输出区
        self._clear_output()

    def get_source(self) -> str:
        return self.source_text.get("1.0", tk.END).rstrip("\n")

    def run_lex(self) -> None:
        self.mode_var.set("模式：词法分析")
        src = self.get_source()
        result = lex_source(src)

        # 切换到文本模式
        self._switch_to_text_mode()

        # 隐藏切换按钮
        self.toggle_button.pack_forget()

        self.set_output(result.output)
        self.status_var.set("状态：成功" if result.ok else "状态：失败")

    def run_parse(self) -> None:
        self.mode_var.set("模式：语法分析")
        src = self.get_source()
        result = parse_source(src, with_ast=False)

        # 切换到文本模式
        self._switch_to_text_mode()

        # 隐藏切换按钮
        self.toggle_button.pack_forget()

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
            # 显示切换按钮
            self.toggle_button.config(state=tk.NORMAL, text="切换为 JSON 格式")
            self.toggle_button.pack(side=tk.LEFT, padx=2)
            # 直接显示图形化AST
            self.show_graphical_ast()
            self.set_output("Parse succeeded.\n\n图形化AST已显示！")
        else:
            # 隐藏切换按钮
            self.toggle_button.pack_forget()
            self._switch_to_text_mode()
            self.set_output(result.output)

        self.status_var.set("状态：成功" if result.ok else "状态：失败")

    def _switch_to_text_mode(self) -> None:
        """切换到文本输出模式"""
        # 隐藏图形化AST
        self.graphical_frame.pack_forget()
        self.zoom_frame.pack_forget()

        # 显示文本输出
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def _update_button_state(self, button_name: str) -> None:
        """更新按钮激活状态"""
        # 重置所有按钮样式
        for name, btn in self.action_buttons.items():
            if name == 'clear':
                continue  # 跳过清空按钮
            btn.config(bg=self.COLORS["primary"], relief=tk.FLAT)

        # 设置激活按钮样式
        if button_name in self.action_buttons:
            self.active_button = button_name
            active_btn = self.action_buttons[button_name]
            active_btn.config(bg=self.COLORS["primary_dark"], relief=tk.SUNKEN)

    def _on_lex_click(self) -> None:
        """词法分析按钮点击"""
        self._update_button_state('lex')
        self.run_lex()

    def _on_parse_click(self) -> None:
        """语法分析按钮点击"""
        self._update_button_state('parse')
        self.run_parse()

    def _on_parse_ast_click(self) -> None:
        """语法分析并显示AST按钮点击"""
        self._update_button_state('parse_ast')
        self.run_parse_ast()

    def _on_clear_click(self) -> None:
        """清空按钮点击"""
        # 重置所有按钮状态
        for name, btn in self.action_buttons.items():
            if name == 'clear':
                continue
            btn.config(bg=self.COLORS["primary"], relief=tk.FLAT)
        self.active_button = None
        self.clear_all()

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
