from typing import Any, cast

import gdb


def safe_int(value: gdb.Value, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def tag_name(node_value: gdb.Value) -> str:
    try:
        return str(node_value["type"])
    except Exception:
        return "<unknown-tag>"


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
        current_type = value.type
        code = current_type.code

        if code != gdb.TYPE_CODE_PTR:
            return value

        if int(value) == 0:
            return None

        target = current_type.target().strip_typedefs()
        if target.code == gdb.TYPE_CODE_VOID or target.code == gdb.TYPE_CODE_CHAR:
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


def node_tag_from_ptr(ptr_val: gdb.Value) -> str | None:
    addr = int(ptr_val)
    if addr == 0:
        return None

    try:
        node_ptr = ptr_val.cast(gdb.lookup_type("Node").pointer())
        tag = tag_name(node_ptr.dereference())
    except Exception:
        return None

    return tag if tag.startswith("T_") else None
