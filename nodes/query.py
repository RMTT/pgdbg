"""Formatter for PostgreSQL Query nodes."""

from __future__ import annotations

from nodes.base import BaseNode


class QueryNode(BaseNode):
    def field_width(self, field_names: list[str]) -> int:
        return max((len(name) for name in field_names), default=0)


NODES = {"T_Query": QueryNode}
