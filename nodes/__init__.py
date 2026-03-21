"""NodeTag-specific pretty-printer implementations."""

from __future__ import annotations

import gdb

import nodes.list
import nodes.query
from nodes.base import BaseNode
from utils import is_char_type, is_node_struct, normalize_ptr, tag_name

TOTAL_NODES = nodes.list.NODES | nodes.query.NODES


class Printer:
    def __init__(self, max_depth: int | None = None, max_list_items: int = 6) -> None:
        self.max_depth = max_depth
        self.max_list_items = max_list_items
        self._visited: set[int] = set()

    def format(self, value: gdb.Value, depth: int = 0) -> str:
        current = normalize_ptr(value)
        # current may be int(0) or bool(false), so cannot just use not current
        if current is None:
            return "NULL"

        try:
            current_type = current.type.strip_typedefs()
        except Exception:
            return str(current)

        if current_type.code == gdb.TYPE_CODE_PTR:
            target = current_type.target().strip_typedefs()
            if is_char_type(target):
                return self._format_char_ptr(current)

        if current_type.code == gdb.TYPE_CODE_STRUCT and is_node_struct(current):
            return self._format_node(current, depth)

        return self._format_scalar(current)

    def indent(self, depth: int) -> str:
        return "  " * depth

    def list_item_limit(self) -> int:
        return self.max_list_items

    def _format_char_ptr(self, value: gdb.Value) -> str:
        try:
            return repr(value.string(errors="replace"))
        except Exception:
            return str(value)

    def _format_scalar(self, value: gdb.Value) -> str:
        try:
            value_type = value.type.strip_typedefs()
            if value_type.code == gdb.TYPE_CODE_BOOL:
                return "true" if int(value) else "false"
        except Exception:
            pass
        return str(value)

    def _format_node(self, node: gdb.Value, depth: int) -> str:
        if not node.address:
            return "NULL"

        addr = int(node.address)

        if self.max_depth is not None and depth >= self.max_depth:
            return f"<max-depth {self.max_depth} at 0x{addr:x}>"

        if addr in self._visited:
            return f"<cycle 0x{addr:x}>"

        self._visited.add(addr)
        try:
            tag = tag_name(node)
            return self.dispatch_node(node, tag, addr, depth)
        finally:
            self._visited.remove(addr)

    def dispatch_node(
        self, node_value: gdb.Value, tag: str, addr: int, depth: int
    ) -> str:
        return TOTAL_NODES.get(tag, BaseNode)(node_value, tag, addr, depth).format(self)
