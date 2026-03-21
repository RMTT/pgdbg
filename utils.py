from typing import Any, cast

import gdb


def safe_int(value: gdb.Value, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def tag_name(node_value: gdb.Value) -> str:
    try:
        node_type = gdb.lookup_type("Node")
        if node_value.type.strip_typedefs().code == gdb.TYPE_CODE_PTR:
            node_value = node_value.cast(node_type.pointer()).dereference()
        else:
            node_value = node_value.cast(node_type)
        return str(node_value["type"])
    except Exception:
        return "<unknown-tag>"


def is_char_type(value_type: gdb.Type) -> bool:
    try:
        target = value_type.strip_typedefs()
        return target.code == gdb.TYPE_CODE_CHAR or target.name == "char"
    except Exception:
        return False


def normalize_ptr(value: gdb.Value) -> gdb.Value | None:
    """Get base type from pointer.

    Possible return Value:
        + scalar
        + struct
        + None
        + void *
        + char *
    """
    while True:
        current_type = value.type.strip_typedefs()
        code = current_type.code

        if code != gdb.TYPE_CODE_PTR:
            return value

        if int(value) == 0:
            return None

        target = current_type.target().strip_typedefs()
        if target.code == gdb.TYPE_CODE_VOID or is_char_type(target):
            return value

        value = value.dereference()


def is_node_struct(value_or_type: gdb.Value | gdb.Type) -> bool:
    try:
        if hasattr(value_or_type, "cast"):
            node_value = cast(Any, value_or_type).cast(gdb.lookup_type("Node"))
            stype = node_value.type.strip_typedefs()
        else:
            stype = value_or_type
        fields = cast(Any, stype).fields()
        return bool(fields and fields[0].name == "type")
    except Exception:
        return False


def possible_node_type_names(tag: str) -> tuple[str, ...]:
    if not tag.startswith("T_"):
        return ("Node",)
    return (tag.removeprefix("T_"), "Node")
