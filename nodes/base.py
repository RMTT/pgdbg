from collections.abc import Iterator
import gdb
from typing import Protocol


class Printer(Protocol):
    def format(self, value: gdb.Value, depth: int = 0) -> str: ...

    def indent(self, depth: int) -> str: ...

    def list_item_limit(self) -> int: ...


class BaseNode:
    def __init__(self, node_value: gdb.Value, tag: str, addr: int, depth: int):
        self.node_value = node_value
        self.tag = tag
        self.addr = addr
        self.depth = depth

    def iter_fields(self) -> Iterator[str]:
        for field in self.node_value.type.strip_typedefs().fields():
            if field.name and not field.is_base_class:
                yield field.name

    def render_field(self, printer: Printer, name: str, width: int = 0) -> list[str]:
        label = f"{name:<{width}}" if width else name
        prefix = f"{printer.indent(self.depth + 1)}{label}:"

        try:
            rendered = printer.format(self.node_value[name], self.depth + 1)
        except Exception:
            return [f"{prefix} <unavailable>"]

        if "\n" not in rendered:
            return [f"{prefix} {rendered}"]

        rendered_lines = rendered.splitlines()
        first_line = rendered_lines[0].removeprefix(printer.indent(self.depth + 1))
        return [
            f"{prefix} {first_line}",
            *rendered_lines[1:],
        ]

    def field_width(self, field_names: list[str]) -> int:
        del field_names
        return 0

    def format(self, printer: Printer) -> str:
        stype = self.node_value.type.strip_typedefs()
        lines = [
            f"{printer.indent(self.depth)}{stype.tag or stype.name or '<anon>'} ({self.tag}) @0x{self.addr:x} {{"
        ]

        field_names = list(self.iter_fields())
        width = self.field_width(field_names)

        for name in field_names:
            lines.extend(self.render_field(printer, name, width))

        lines.append(f"{printer.indent(self.depth)}}}")
        return "\n".join(lines)
