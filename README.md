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
pgprint [--depth MAX_DEPTH] [--position POSITION] <expression>...
pgprint [--depth MAX_DEPTH] [--position POSITION] -- <expression>...
```

Examples:

```gdb
pgprint query
pgprint --depth 3 query
pgprint --position 0 query->targetList
pgprint --depth 2 --position 1 query->rtable
pgprint ((Node *) query)
pgprint --depth 2 -- ((Node *) query)
```

`depth` must be an integer greater than or equal to `1`.

`position` must be an integer greater than or equal to `0`.

## Supported Node Formatters

Current specialized formatters live under `nodes/`:

- `T_Query`
- `T_List`
- `T_IntList`
- `T_OidList`
- `T_XidList`

Other structs that look like PostgreSQL nodes still print through the generic base formatter.
