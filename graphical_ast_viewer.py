"""
图形化AST树状结构查看器
使用tkinter Canvas绘制真正的树状图
"""
from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext
from typing import Any, Dict, List, Tuple
import math


class GraphicalASTViewer:
    """图形化AST查看器"""

    def __init__(self, parent: tk.Widget):
        """
        初始化图形化AST查看器

        Args:
            parent: 父容器
        """
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 配置
        self.node_width = 130
        self.node_height = 50
        self.horizontal_spacing = 20
        self.vertical_spacing = 90
        self.node_bg_color = "#E8F4FD"
        self.node_border_color = "#2196F3"
        self.text_color = "#333333"
        self.line_color = "#666666"

        # 存储节点信息
        self.nodes_to_draw: List[Dict] = []
        self.connections_to_draw: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

        # 滚动和缩放相关
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_zoom)
        self.canvas.bind("<Control-Button-4>", self._on_zoom)
        self.canvas.bind("<Control-Button-5>", self._on_zoom)

        # 拖拽相关
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_release)

        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.scale = 1.0  # 当前缩放比例
        self.original_nodes = []  # 存储原始节点数据用于缩放

    def display_ast(self, ast: Dict[str, Any]):
        """
        显示AST的图形化树状结构

        Args:
            ast: AST字典
        """
        self.canvas.delete("all")
        self.nodes_to_draw.clear()
        self.connections_to_draw.clear()
        self.scale = 1.0  # 重置缩放比例

        if not ast or 'type' not in ast:
            self._draw_centered_text("Empty AST or invalid format")
            return

        try:
            # 计算树的布局（先使用一个较大的初始x值）
            self._build_tree_layout(ast, x=1000, y=50, level=0)

            if not self.nodes_to_draw:
                self._draw_centered_text("No nodes to display")
                return

            # 延迟适应窗口大小（等待canvas完全显示）
            self.canvas.after(100, self._delayed_fit_and_draw)

        except Exception as e:
            self._draw_centered_text(f"Error: {str(e)}")

    def _delayed_fit_and_draw(self):
        """延迟适应和绘制"""
        try:
            # 自动适应窗口大小
            self._fit_to_window()

            # 绘制所有内容
            self._redraw_all()

            # 确保滚动到合适位置，使整个树可见
            self.canvas.update()

            # 滚动到左上角
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)

        except Exception as e:
            self._draw_centered_text(f"Error in delayed draw: {str(e)}")

    def _fit_to_window(self):
        """自动缩放以适应窗口大小"""
        if not self.nodes_to_draw:
            return

        # 计算当前树的实际边界
        min_x = min(node['x'] - self.node_width // 2 for node in self.nodes_to_draw)
        max_x = max(node['x'] + self.node_width // 2 for node in self.nodes_to_draw)
        min_y = min(node['y'] for node in self.nodes_to_draw)
        max_y = max(node['y'] + self.node_height for node in self.nodes_to_draw)

        # 添加边距
        padding = 50
        tree_width = max_x - min_x + 2 * padding
        tree_height = max_y - min_y + 2 * padding

        # 获取canvas可见区域大小
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 如果canvas还没有显示，使用默认值
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600

        # 计算合适的缩放比例，留一些边距
        scale_x = canvas_width / tree_width
        scale_y = canvas_height / tree_height
        new_scale = min(scale_x, scale_y) * 0.95  # 留5%边距

        self.scale = max(0.1, min(new_scale, 1.0))  # 限制在0.1到1.0之间

        # 保存树的边界信息用于滚动定位
        self.tree_bounds = {
            'min_x': min_x - padding,
            'min_y': min_y - padding,
            'max_x': max_x + padding,
            'max_y': max_y + padding
        }

    def _redraw_all(self):
        """重新绘制所有内容（考虑缩放）"""
        self.canvas.delete("all")

        if not self.nodes_to_draw:
            return

        # 计算缩放后的画布大小
        if hasattr(self, 'tree_bounds') and self.tree_bounds:
            # 使用保存的边界信息
            bounds = self.tree_bounds
            scroll_region = (
                bounds['min_x'] * self.scale,
                bounds['min_y'] * self.scale,
                bounds['max_x'] * self.scale,
                bounds['max_y'] * self.scale
            )
        else:
            # 重新计算边界
            min_x = min(node['x'] - self.node_width // 2 for node in self.nodes_to_draw)
            max_x = max(node['x'] + self.node_width // 2 for node in self.nodes_to_draw)
            min_y = min(node['y'] for node in self.nodes_to_draw)
            max_y = max(node['y'] + self.node_height for node in self.nodes_to_draw)

            scroll_region = (
                min_x * self.scale,
                min_y * self.scale,
                max_x * self.scale,
                max_y * self.scale
            )

        self.canvas.config(scrollregion=scroll_region)

        # 先绘制连接线
        for start_pos, end_pos in self.connections_to_draw:
            scaled_start = (start_pos[0] * self.scale, start_pos[1] * self.scale)
            scaled_end = (end_pos[0] * self.scale, end_pos[1] * self.scale)
            line_width = max(1, 2 * self.scale)
            self.canvas.create_line(
                scaled_start[0], scaled_start[1],
                scaled_end[0], scaled_end[1],
                fill=self.line_color,
                width=line_width,
                tags="connection"
            )

        # 再绘制节点
        for node_info in self.nodes_to_draw:
            self._draw_single_node_scaled(node_info)

    def _draw_centered_text(self, text: str):
        """在canvas中心绘制文本"""
        self.canvas.create_text(
            400, 300,
            text=text,
            font=("Arial", 12),
            fill="#FF0000" if "Error" in text else "#999999"
        )

    def _build_tree_layout(self, node: Any, x: int, y: int, level: int):
        """
        递归构建树布局

        Args:
            node: 当前节点
            x: 当前节点x坐标
            y: 当前节点y坐标
            level: 层级深度
        """
        if not isinstance(node, dict):
            return

        node_type = node.get('type', 'Unknown')
        node_info = self._get_node_info(node)

        # 存储当前节点信息
        current_node = {
            'x': x,
            'y': y,
            'type': node_type,
            'info': node_info,
            'node': node
        }
        self.nodes_to_draw.append(current_node)

        # 获取子节点
        children = self._get_important_children(node)

        if not children:
            return

        # 计算子节点的布局
        child_y = y + self.node_height + self.vertical_spacing

        # 计算每个子树需要的宽度
        subtree_widths = []
        for child in children:
            width = self._calculate_subtree_width(child)
            subtree_widths.append(width)

        total_width = sum(subtree_widths) + (len(children) - 1) * self.horizontal_spacing

        # 当前节点居中
        start_x = x - total_width // 2

        # 布局子节点
        current_child_x = start_x
        for i, (child, width) in enumerate(zip(children, subtree_widths)):
            child_center_x = current_child_x + width // 2

            # 递归处理子节点
            child_node_count_before = len(self.nodes_to_draw)
            self._build_tree_layout(child, child_center_x, child_y, level + 1)
            child_node_count_after = len(self.nodes_to_draw)

            # 只有当子节点确实生成了节点时，才绘制连接线
            if child_node_count_after > child_node_count_before:
                self.connections_to_draw.append(
                    ((x, y + self.node_height), (child_center_x, child_y))
                )

            current_child_x += width + self.horizontal_spacing

    def _calculate_subtree_width(self, node: Any) -> int:
        """计算子树需要的宽度"""
        if not isinstance(node, dict):
            return self.node_width

        children = self._get_important_children(node)

        if not children:
            return self.node_width

        # 如果只有一个子节点，直接返回节点宽度
        if len(children) == 1:
            return max(self.node_width, self._calculate_subtree_width(children[0]))

        # 多个子节点，累加宽度
        total_width = 0
        for i, child in enumerate(children):
            child_width = self._calculate_subtree_width(child)
            total_width += child_width
            if i < len(children) - 1:
                total_width += self.horizontal_spacing

        return max(total_width, self.node_width)

    def _get_important_children(self, node: Dict[str, Any]) -> List[Any]:
        """获取重要的子节点（只返回会生成节点的子节点）"""
        priority_fields = [
            'functions',
            'params',
            'body',
            'statements',
            'cond',
            'then',
            'else',
            'expr',
            'left',
            'right',
            'args',
            'callee',
            'elements',
            'init',
            'target',
            'index',
            'var',
            'start',
            'end'
        ]

        children = []
        for field in priority_fields:
            if field in node:
                value = node[field]
                if value is not None and value != [] and value != {}:
                    if isinstance(value, list):
                        # 只添加字典类型的元素
                        for item in value:
                            if isinstance(item, dict):
                                children.append(item)
                    elif isinstance(value, dict):
                        children.append(value)

        return children

    def _get_node_info(self, node: Dict[str, Any]) -> str:
        """获取节点信息文本"""
        info_parts = []

        if 'name' in node:
            name = str(node['name'])
            if len(name) > 12:
                name = name[:9] + "..."
            info_parts.append(f"name: {name}")

        elif 'op' in node:
            info_parts.append(f"op: {node['op']}")

        elif 'value' in node:
            value = str(node['value'])
            if len(value) > 12:
                value = value[:9] + "..."
            info_parts.append(f"value: {value}")

        return " | ".join(info_parts) if info_parts else ""

    def _draw_single_node(self, node_info: Dict):
        """绘制单个节点（不缩放）"""
        x = node_info['x']
        y = node_info['y']
        node_type = node_info['type']
        node_info_text = node_info['info']

        # 绘制节点背景
        self.canvas.create_rectangle(
            x - self.node_width // 2, y,
            x + self.node_width // 2, y + self.node_height,
            fill=self.node_bg_color,
            outline=self.node_border_color,
            width=2,
            tags="node"
        )

        # 绘制节点类型
        self.canvas.create_text(
            x, y + 15,
            text=node_type,
            font=("Arial", 10, "bold"),
            fill=self.text_color,
            tags="node"
        )

        # 绘制节点信息
        if node_info_text:
            self.canvas.create_text(
                x, y + 35,
                text=node_info_text,
                font=("Arial", 8),
                fill="#666666",
                tags="node"
            )

    def _draw_single_node_scaled(self, node_info: Dict):
        """绘制缩放后的单个节点"""
        scale = self.scale
        x = node_info['x'] * scale
        y = node_info['y'] * scale
        node_width = self.node_width * scale
        node_height = self.node_height * scale
        node_type = node_info['type']
        node_info_text = node_info['info']

        # 绘制节点背景
        self.canvas.create_rectangle(
            x - node_width // 2, y,
            x + node_width // 2, y + node_height,
            fill=self.node_bg_color,
            outline=self.node_border_color,
            width=max(1, 2 * scale),
            tags="node"
        )

        # 根据缩放比例调整字体大小
        font_size = max(6, int(10 * scale))
        info_font_size = max(5, int(8 * scale))

        # 绘制节点类型
        self.canvas.create_text(
            x, y + node_height * 0.3,
            text=node_type,
            font=("Arial", font_size, "bold"),
            fill=self.text_color,
            tags="node"
        )

        # 绘制节点信息
        if node_info_text and scale > 0.5:  # 缩放太小时不显示详细信息
            self.canvas.create_text(
                x, y + node_height * 0.7,
                text=node_info_text,
                font=("Arial", info_font_size),
                fill="#666666",
                tags="node"
            )

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件（滚动）"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _on_zoom(self, event):
        """处理缩放事件（Ctrl+滚轮）"""
        if event.num == 5 or event.delta < 0:
            # 缩小
            new_scale = max(0.1, self.scale * 0.9)
        else:
            # 放大
            new_scale = min(3.0, self.scale * 1.1)

        if new_scale != self.scale:
            self.scale = new_scale
            self._redraw_all()

    def zoom_in(self):
        """放大"""
        new_scale = min(3.0, self.scale * 1.2)
        if new_scale != self.scale:
            self.scale = new_scale
            self._redraw_all()

    def zoom_out(self):
        """缩小"""
        new_scale = max(0.1, self.scale * 0.8)
        if new_scale != self.scale:
            self.scale = new_scale
            self._redraw_all()

    def reset_zoom(self):
        """重置缩放"""
        self.scale = 1.0
        self._redraw_all()

    def fit_to_window(self):
        """适应窗口大小"""
        self._fit_to_window()
        self._redraw_all()

        # 确保滚动到左上角，使整个树可见
        self.canvas.update()

        # 等待一小段时间确保canvas完全更新
        self.canvas.after(50, lambda: (
            self.canvas.xview_moveto(0),
            self.canvas.yview_moveto(0)
        ))

    def _on_drag_start(self, event):
        """开始拖拽"""
        self.drag_data["start_x"] = event.x
        self.drag_data["start_y"] = event.y
        self.drag_data["last_x"] = event.x
        self.drag_data["last_y"] = event.y
        self.drag_data["dragging"] = True
        self.canvas.config(cursor="fleur")  # 改变鼠标样式

    def _on_drag_motion(self, event):
        """拖拽移动"""
        if self.drag_data["dragging"]:
            # 计算自上次移动以来的增量
            dx = event.x - self.drag_data["last_x"]
            dy = event.y - self.drag_data["last_y"]

            # 更新最后位置
            self.drag_data["last_x"] = event.x
            self.drag_data["last_y"] = event.y

            # 使用合适的滚动系数，让拖动既灵敏又可控
            scroll_factor = 0.5  # 调整这个值来改变灵敏度：0.5=很平滑，0.6=平滑，1=适中
            self.canvas.xview_scroll(int(-dx * scroll_factor), "units")
            self.canvas.yview_scroll(int(-dy * scroll_factor), "units")

    def _on_drag_release(self, event):
        """结束拖拽"""
        self.drag_data["dragging"] = False
        self.canvas.config(cursor="")  # 恢复鼠标样式


class ASTViewerWindow:
    """AST查看器窗口"""

    def __init__(self, root: tk.Tk, ast: Dict[str, Any]):
        """
        初始化AST查看器窗口

        Args:
            root: 根窗口
            ast: AST字典
        """
        self.window = tk.Toplevel(root)
        self.window.title("AST 图形化树状结构查看器")
        self.window.geometry("1000x700")

        # 创建工具栏
        toolbar = tk.Frame(self.window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(toolbar, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(toolbar, text="适应窗口", command=self._fit_to_window).pack(side=tk.RIGHT, padx=5)

        # 创建查看器
        self.viewer = GraphicalASTViewer(self.window)

        # 显示AST
        self.viewer.display_ast(ast)

    def _fit_to_window(self):
        """适应窗口大小"""
        pass


def show_graphical_ast(root: tk.Tk, ast: Dict[str, Any]):
    """
    显示图形化AST查看器

    Args:
        root: 根窗口
        ast: AST字典
    """
    ASTViewerWindow(root, ast)