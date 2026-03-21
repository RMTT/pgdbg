"""Formatters for PostgreSQL list node tags."""

from __future__ import annotations

import gdb

from nodes.base import BaseNode, Printer
from utils import (
    possible_node_type_names,
    safe_int,
    tag_name,
)


LIST_TAGS = {"T_List", "T_IntList", "T_OidList", "T_XidList"}


def _normalize_list_value(value: gdb.Value) -> tuple[gdb.Value, str]:
    current = value

    while True:
        try:
            current_type = current.type.strip_typedefs()
        except Exception as exc:
            raise gdb.GdbError("expression must evaluate to a PostgreSQL List") from exc

        if current_type.code != gdb.TYPE_CODE_PTR:
            break

        if int(current) == 0:
            raise gdb.GdbError("list pointer is NULL")

        try:
            current = current.dereference()
        except Exception as exc:
            raise gdb.GdbError("expression must evaluate to a PostgreSQL List") from exc

    tag = tag_name(current)
    if tag not in LIST_TAGS:
        raise gdb.GdbError("expression must evaluate to a PostgreSQL List")

    return current, tag


def _list_length(list_value: gdb.Value) -> int:
    return safe_int(list_value["length"])


def _list_cell(list_value: gdb.Value, position: int) -> gdb.Value:
    if position < 0:
        raise gdb.GdbError("position must be >= 0")

    length = _list_length(list_value)
    if position >= length:
        raise gdb.GdbError(
            f"position {position} out of range for list of length {length}"
        )
    return list_value["elements"][position]


def _describe_scalar_cell(cell: gdb.Value, tag: str) -> str:
    if tag == "T_IntList":
        return str(safe_int(cell["int_value"]))
    if tag == "T_OidList":
        return str(safe_int(cell["oid_value"]))
    return str(safe_int(cell["xid_value"]))


def _describe_ptr_cell(
    ptr_val: gdb.Value, printer: Printer | None = None
) -> tuple[str, gdb.Value | None]:
    addr = int(ptr_val)
    if addr == 0:
        return "NULL", None

    child_tag = tag_name(ptr_val)
    if child_tag == "<unknown-tag>":
        return f"0x{addr:x}", None

    if printer is None:
        return f"{child_tag} @0x{addr:x}", None

    for type_name in possible_node_type_names(child_tag):
        try:
            node_ptr = ptr_val.cast(gdb.lookup_type(type_name).pointer())
            return printer.format(node_ptr), node_ptr
        except Exception:
            continue

    return f"0x{addr:x}", None


def _describe_list_cell(
    cell: gdb.Value,
    tag: str,
    printer: Printer | None,
    *,
    detailed: bool = False,
) -> str:
    if tag != "T_List":
        return _describe_scalar_cell(cell, tag)

    rendered, _ = _describe_ptr_cell(cell["ptr_value"], printer if detailed else None)
    return rendered


def describe_list_element(value: gdb.Value, position: int, printer: Printer) -> str:
    list_value, tag = _normalize_list_value(value)
    cell = _list_cell(list_value, position)
    return _describe_list_cell(cell, tag, printer, detailed=True)


class ListNode(BaseNode):
    def format(self, printer: Printer) -> str:
        length = _list_length(self.node_value)

        lines = [f"{self.tag}(len={length}) ["]
        limit = min(length, printer.list_item_limit())

        for i in range(limit):
            item = _describe_list_cell(
                _list_cell(self.node_value, i), self.tag, printer, detailed=False
            )
            lines.append(f"{printer.indent(self.depth + 1)}[{i}] {item}")

        if length > limit:
            lines.append(f"{printer.indent(self.depth + 1)}... ({length - limit} more)")

        lines.append(f"{printer.indent(self.depth)}]")
        return "\n".join(lines)


NODES = {
    "T_List": ListNode,
    "T_IntList": ListNode,
    "T_OidList": ListNode,
    "T_XidList": ListNode,
}
