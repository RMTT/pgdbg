# pgdbg

`pgdbg` is a small GDB helper for pretty-printing PostgreSQL `Node` trees, including indexed PostgreSQL `List` elements, from a live debugging session.

## What It Does

- loads a custom `pgprint` command into GDB
- detects PostgreSQL node pointers and formats them recursively

## Requirements

- `gdb` with Python support
- a debug session where PostgreSQL types are available

This repository includes a Nix dev shell with `gdb` and `python3`:

```bash
nix develop
```

## Load In GDB

Do not run the Python files directly. Load them from inside GDB:

```gdb
source /path/to/pgdbg/pgdbg.py
```

That registers the `pgprint` command.

## Usage

```gdb
pgprint [--max-depth MAX_DEPTH] [--position POSITION] <expression>...
pgprint [--max-depth MAX_DEPTH] [--position POSITION] -- <expression>...
```

Examples:

```gdb
pgprint query
pgprint --max-depth 3 query
pgprint --position 0 query->targetList
pgprint --max-depth 2 --position 1 query->rtable
pgprint ((Node *) query)
pgprint --max-depth 2 -- ((Node *) query)
```

`max_depth` must be an integer greater than or equal to `1`.

`position` must be an integer greater than or equal to `0`.

Migration note:

- Trailing tokens such as `3` are treated as expression text by default. Use `--max-depth <max_depth>` when you want to set the depth explicitly.
- `--position <position>` selects a PostgreSQL list element after the expression is evaluated as a list.
- The canonical syntax documents `--max-depth` and `--position` before the expression, but this parser still recognizes those options until `--` ends option parsing.
- Use `--` only when the expression itself would otherwise be parsed as an option, such as an expression that starts with `--max-depth`, or when you need later tokens preserved as literal expression text.

## Supported Node Formatters

Current specialized formatters live under `nodes/`:

- `T_Query`
- `T_List`
- `T_IntList`
- `T_OidList`
- `T_XidList`

Other structs that look like PostgreSQL nodes still print through the generic base formatter.
