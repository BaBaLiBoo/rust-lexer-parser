"""语法高亮文本编辑器（带行号）"""

import re
import tkinter as tk
from tkinter import scrolledtext


class LineTextWidget(tk.Frame):
    """带行号的文本编辑器组件"""

    def __init__(self, master=None, wrap=tk.NONE, font=("Consolas", 11), **kw):
        super().__init__(master)

        # 创建行号区域
        self.linenumbers = tk.Text(self, width=4, padx=3, pady=5,
                                   font=("Consolas", 11),
                                   bg="#FFFFFF", fg="#666666",
                                   state=tk.DISABLED, wrap=tk.NONE,
                                   relief=tk.FLAT, bd=0, highlightthickness=0)
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        # 创建代码编辑区域
        self.text = SyntaxHighlightText(self, wrap=wrap, font=font,
                                        relief=tk.FLAT, bd=0, highlightthickness=0, **kw)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 同步滚动
        self._sync_scroll()

        # 绑定事件以更新行号
        self.text.bind("<<KeyRelease>>", self._on_text_change)
        self.text.bind("<<Modified>>", self._on_text_change)
        self.text.bind("<ButtonRelease-1>", self._on_text_change)

        # 初始化行号
        self._update_line_numbers()

    def _sync_scroll(self):
        """同步滚动"""
        # 代码区域滚动时，行号区域跟随滚动
        def on_textscroll(*args):
            self.linenumbers.yview_moveto(args[0])

        self.text['yscrollcommand'] = on_textscroll

    def _on_text_change(self, event=None):
        """文本内容改变时更新行号"""
        self._update_line_numbers()

    def _update_line_numbers(self):
        """更新行号显示"""
        # 获取文本行数
        lines = self.text.get("1.0", tk.END).count("\n")

        # 生成行号文本，使用空格实现居中效果
        line_numbers = "\n".join(f" {i} " for i in range(1, lines + 2))

        # 更新行号区域
        self.linenumbers.config(state=tk.NORMAL)
        self.linenumbers.delete("1.0", tk.END)
        self.linenumbers.insert("1.0", line_numbers)
        self.linenumbers.config(state=tk.DISABLED)

    def get(self, *args, **kwargs):
        """代理get方法到文本区域"""
        return self.text.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        """代理insert方法到文本区域"""
        return self.text.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """代理delete方法到文本区域"""
        return self.text.delete(*args, **kwargs)

    def index(self, *args, **kwargs):
        """代理index方法到文本区域"""
        return self.text.index(*args, **kwargs)

    def mark_set(self, *args, **kwargs):
        """代理mark_set方法到文本区域"""
        return self.text.mark_set(*args, **kwargs)

    def edit_modified(self, *args, **kwargs):
        """代理edit_modified方法到文本区域"""
        return self.text.edit_modified(*args, **kwargs)

    def highlight_all(self):
        """手动触发语法高亮"""
        self.text.highlight_all()
        self._update_line_numbers()


class SyntaxHighlightText(scrolledtext.ScrolledText):
    """支持语法高亮的文本编辑器"""

    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._bind_events()
        self._configure_tags()
        self._setup_highlight_rules()

    def _bind_events(self):
        """绑定事件"""
        self.bind("<<KeyRelease>>", self._on_key_release)
        self.bind("<<Modified>>", self._on_modified)

    def _configure_tags(self):
        """配置语法高亮标签"""
        # 关键字 - 柔和蓝色斜体
        self.tag_configure("keyword", foreground="#4A90E2", font=("Consolas", 11, "italic"))

        # 类型 - 柔和紫色斜体
        self.tag_configure("type", foreground="#9B59B6", font=("Consolas", 11, "italic"))

        # 数字 - 柔和绿色斜体
        self.tag_configure("number", foreground="#27AE60", font=("Consolas", 11, "italic"))

        # 字符串 - 柔和橙色
        self.tag_configure("string", foreground="#F39C12")

        # 注释 - 浅灰色斜体
        self.tag_configure("comment", foreground="#95A5A6", font=("Consolas", 11, "italic"))

        # 运算符 - 柔和红色
        self.tag_configure("operator", foreground="#E74C3C")

        # 标识符 - 黑色（默认）
        self.tag_configure("identifier", foreground="#000000")

    def _setup_highlight_rules(self):
        """设置语法高亮规则"""
        # Rust 关键字
        self.keywords = [
            "fn", "let", "mut", "return", "if", "else", "while",
            "for", "in", "loop", "break", "continue"
        ]

        # 类型关键字
        self.types = ["i32"]

        # 运算符
        self.operators = [
            r"==", r"!=", r"<=", r">=", r"->", r"\.\.",  # 多字符运算符
            r"\+", r"-", r"\*", r"/", r"=", r"<", r">",  # 单字符运算符
            r"&", r";", r",", r":", r"\(", r"\)", r"\{", r"\}",
            r"\[", r"\]"
        ]

    def _on_key_release(self, event=None):
        """按键释放时触发高亮"""
        self._highlight_syntax()

    def _on_modified(self, event=None):
        """内容修改时触发高亮"""
        if self.edit_modified():
            self.edit_modified(False)
            self._highlight_syntax()

    def _highlight_syntax(self):
        """执行语法高亮"""
        # 保存当前插入位置
        current_insert = self.index("insert")

        # 移除所有标签
        self.tag_remove("keyword", "1.0", tk.END)
        self.tag_remove("type", "1.0", tk.END)
        self.tag_remove("number", "1.0", tk.END)
        self.tag_remove("string", "1.0", tk.END)
        self.tag_remove("comment", "1.0", tk.END)
        self.tag_remove("operator", "1.0", tk.END)
        self.tag_remove("identifier", "1.0", tk.END)

        # 获取所有文本
        text = self.get("1.0", tk.END)

        # 1. 先高亮注释（避免注释内的内容被其他规则匹配）
        self._highlight_comments(text)

        # 2. 高亮字符串字面量（暂不支持，但保留接口）
        # self._highlight_strings(text)

        # 3. 高亮关键字
        self._highlight_keywords(text)

        # 4. 高亮类型
        self._highlight_types(text)

        # 5. 高亮数字
        self._highlight_numbers(text)

        # 6. 高亮运算符
        self._highlight_operators(text)

        # 恢复插入位置
        self.mark_set("insert", current_insert)

    def _highlight_comments(self, text):
        """高亮注释"""
        # 行注释 //
        for match in re.finditer(r"//[^\n]*", text):
            start, end = match.span()
            start_idx = f"1.0 + {start} chars"
            end_idx = f"1.0 + {end} chars"
            self.tag_add("comment", start_idx, end_idx)

        # 块注释 /* */
        for match in re.finditer(r"/\*.*?\*/", text, re.DOTALL):
            start, end = match.span()
            start_idx = f"1.0 + {start} chars"
            end_idx = f"1.0 + {end} chars"
            self.tag_add("comment", start_idx, end_idx)

    def _highlight_keywords(self, text):
        """高亮关键字"""
        # 使用单词边界确保只匹配完整的关键字
        for keyword in self.keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            for match in re.finditer(pattern, text):
                start, end = match.span()
                start_idx = f"1.0 + {start} chars"
                end_idx = f"1.0 + {end} chars"

                # 检查是否在注释中
                if not self._is_in_comment(start, text):
                    self.tag_add("keyword", start_idx, end_idx)

    def _highlight_types(self, text):
        """高亮类型关键字"""
        for type_name in self.types:
            pattern = r"\b" + re.escape(type_name) + r"\b"
            for match in re.finditer(pattern, text):
                start, end = match.span()
                start_idx = f"1.0 + {start} chars"
                end_idx = f"1.0 + {end} chars"

                # 检查是否在注释中
                if not self._is_in_comment(start, text):
                    self.tag_add("type", start_idx, end_idx)

    def _highlight_numbers(self, text):
        """高亮数字"""
        for match in re.finditer(r"\b\d+\b", text):
            start, end = match.span()
            start_idx = f"1.0 + {start} chars"
            end_idx = f"1.0 + {end} chars"

            # 检查是否在注释中
            if not self._is_in_comment(start, text):
                self.tag_add("number", start_idx, end_idx)

    def _highlight_operators(self, text):
        """高亮运算符"""
        # 合并所有运算符模式
        operator_pattern = "|".join(re.escape(op) for op in self.operators)

        for match in re.finditer(operator_pattern, text):
            start, end = match.span()
            start_idx = f"1.0 + {start} chars"
            end_idx = f"1.0 + {end} chars"

            # 检查是否在注释中
            if not self._is_in_comment(start, text):
                self.tag_add("operator", start_idx, end_idx)

    def _is_in_comment(self, pos, text):
        """检查位置是否在注释中"""
        # 检查行注释
        line_start = text.rfind("\n", 0, pos) + 1
        if "//" in text[line_start:pos]:
            return True

        # 检查块注释
        for match in re.finditer(r"/\*.*?\*/", text, re.DOTALL):
            if match.start() <= pos < match.end():
                return True

        return False

    def highlight_all(self):
        """手动触发全部高亮"""
        self._highlight_syntax()
