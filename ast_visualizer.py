"""
AST可视化器 - 将JSON格式的AST转换为可视化的树状结构
"""
from __future__ import annotations

from typing import Any, Dict, List


class ASTVisualizer:
    """AST树状结构可视化器"""

    def __init__(self, use_unicode: bool = True):
        """
        初始化可视化器

        Args:
            use_unicode: 是否使用Unicode字符绘制树状结构
        """
        self.use_unicode = use_unicode
        # Unicode树形字符
        self.chars = {
            'vertical': '│',
            'horizontal': '─',
            'branch': '├',
            'last_branch': '└',
            'corner': '└'
        } if use_unicode else {
            'vertical': '|',
            'horizontal': '-',
            'branch': '|--',
            'last_branch': '`--',
            'corner': '`--'
        }

    def visualize(self, ast: Dict[str, Any]) -> str:
        """
        将AST转换为可视化的树状结构字符串

        Args:
            ast: AST字典

        Returns:
            可视化的树状结构字符串
        """
        if not ast or 'type' not in ast:
            return "Empty AST"

        lines = []
        self._build_tree(ast, "", lines, is_last=True)
        return '\n'.join(lines)

    def _build_tree(
        self,
        node: Any,
        prefix: str,
        lines: List[str],
        is_last: bool
    ) -> None:
        """
        递归构建树状结构

        Args:
            node: 当前节点
            prefix: 当前行前缀
            lines: 输出行的列表
            is_last: 是否是最后一个子节点
        """
        if isinstance(node, dict):
            self._build_dict_node(node, prefix, lines, is_last)
        elif isinstance(node, list):
            self._build_list_node(node, prefix, lines, is_last)
        else:
            # 基本类型值
            connector = self.chars['last_branch'] if is_last else self.chars['branch']
            lines.append(f"{prefix}{connector} {self._format_value(node)}")

    def _build_dict_node(
        self,
        node: Dict[str, Any],
        prefix: str,
        lines: List[str],
        is_last: bool
    ) -> None:
        """构建字典类型的节点"""
        node_type = node.get('type', 'Unknown')
        connector = self.chars['last_branch'] if is_last else self.chars['branch']

        # 构建节点标题
        title_parts = [node_type]
        if 'name' in node:
            title_parts.append(f"name={self._format_value(node['name'])}")
        elif 'op' in node:
            title_parts.append(f"op={self._format_value(node['op'])}")
        elif 'value' in node:
            title_parts.append(f"value={self._format_value(node['value'])}")

        lines.append(f"{prefix}{connector} {' '.join(title_parts)}")

        # 处理子节点
        children = self._get_children(node)
        if children:
            # 更新前缀
            extension = self.chars['vertical'] + "   " if not is_last else "    "
            new_prefix = prefix + extension

            # 递归处理子节点
            for i, (key, child) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                if key:  # 如果有键名，显示键名
                    child_prefix = new_prefix
                    child_connector = self.chars['last_branch'] if is_last_child else self.chars['branch']
                    lines.append(f"{child_prefix}{child_connector} {key}:")

                    # 为子节点添加额外缩进
                    child_extension = self.chars['vertical'] + "   " if not is_last_child else "    "
                    child_new_prefix = child_prefix + child_extension
                    self._build_tree(child, child_new_prefix, lines, is_last_child)
                else:
                    self._build_tree(child, new_prefix, lines, is_last_child)

    def _build_list_node(
        self,
        node: List[Any],
        prefix: str,
        lines: List[str],
        is_last: bool
    ) -> None:
        """构建列表类型的节点"""
        connector = self.chars['last_branch'] if is_last else self.chars['branch']
        lines.append(f"{prefix}{connector} [{len(node)} items]")

        if node:
            extension = self.chars['vertical'] + "   " if not is_last else "    "
            new_prefix = prefix + extension

            for i, item in enumerate(node):
                is_last_child = (i == len(node) - 1)
                self._build_tree(item, new_prefix, lines, is_last_child)

    def _get_children(self, node: Dict[str, Any]) -> List[tuple[str | None, Any]]:
        """
        获取节点的子节点，按照期望的顺序排列

        Returns:
            List of (key, value) tuples，key为None表示无键名
        """
        # 定义子字段的优先级顺序
        priority_fields = [
            'functions', 'params', 'body', 'statements',
            'cond', 'then', 'else',
            'name', 'mut', 'ty', 'return_type', 'init',
            'target', 'expr', 'left', 'right', 'args',
            'callee', 'elements', 'index', 'var', 'start', 'end'
        ]

        children = []
        added_fields = set()

        # 首先按优先级添加字段
        for field in priority_fields:
            if field in node and field not in ['type', 'name', 'op', 'value']:
                value = node[field]
                if value is not None and value != [] and value != {}:
                    children.append((field, value))
                    added_fields.add(field)

        # 添加其他字段
        for key, value in node.items():
            if key not in ['type', 'name', 'op', 'value'] and key not in added_fields:
                if value is not None and value != [] and value != {}:
                    children.append((key, value))

        return children

    def _format_value(self, value: Any) -> str:
        """格式化值用于显示"""
        if isinstance(value, str):
            return f'"{value}"'
        return str(value)


def create_text_tree(ast: Dict[str, Any], use_unicode: bool = True) -> str:
    """
    便捷函数：创建AST的文本树状结构

    Args:
        ast: AST字典
        use_unicode: 是否使用Unicode字符

    Returns:
        可视化的树状结构字符串
    """
    visualizer = ASTVisualizer(use_unicode=use_unicode)
    return visualizer.visualize(ast)


# 简化版的树状结构生成器（用于向后兼容）
def generate_simple_tree(ast: Dict[str, Any], indent: int = 0, prefix: str = "") -> str:
    """
    生成简化的树状结构（使用缩进）

    Args:
        ast: AST字典
        indent: 当前缩进级别
        prefix: 行前缀

    Returns:
        树状结构字符串
    """
    if not isinstance(ast, dict):
        return f"{prefix}└─ {ast}\n"

    result = ""
    node_type = ast.get('type', 'Unknown')

    # 构建当前节点的表示
    node_info = node_type
    if 'name' in ast:
        node_info += f" [{ast['name']}]"
    elif 'op' in ast:
        node_info += f" [{ast['op']}]"
    elif 'value' in ast:
        node_info += f" [{ast['value']}]"

    result += f"{prefix}└─ {node_info}\n"

    # 递归处理子节点
    for key, value in ast.items():
        if key not in ['type', 'name', 'op', 'value'] and value is not None:
            if isinstance(value, dict):
                result += generate_simple_tree(value, indent + 1, prefix + "   ")
            elif isinstance(value, list) and value:
                result += f"{prefix}   ├─ {key}:\n"
                for item in value:
                    if isinstance(item, dict):
                        result += generate_simple_tree(item, indent + 2, prefix + "   │  ")
                    else:
                        result += f"{prefix}   │  └─ {item}\n"
            elif value not in [[], {}]:
                result += f"{prefix}   ├─ {key}: {value}\n"

    return result