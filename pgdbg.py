"""GDB command for pretty-printing PostgreSQL Node trees.

Load inside gdb with:
  source /home/mt/Projects/pgdbg/pgdbg.py

Then use:
  pgprint [--max-depth MAX_DEPTH] [--position POSITION] <expression>...
  pgprint [--max-depth MAX_DEPTH] [--position POSITION] -- <expression>...
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from typing import Any, NamedTuple, NoReturn, Sequence

import gdb


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from nodes import Printer
from nodes.list import describe_list_element


class PgPrintCommand(gdb.Command):
    def __init__(self) -> None:
        super().__init__("pgprint", gdb.COMMAND_DATA)
        parser = argparse.ArgumentParser(
            prog="pgprint", add_help=True, allow_abbrev=True, exit_on_error=False
        )
        parser.add_argument(
            "-p",
            "--position",
            type=int,
            help="print the PostgreSQL list element at POSITION",
        )
        parser.add_argument(
            "-d",
            "--depth",
            type=int,
            help="limit recursive formatting depth to MAX_DEPTH",
        )
        parser.add_argument(
            "expr",
            type=str,
            help="expression text to evaluate; trailing tokens remain part of it",
        )

        self._parser = parser

    def validate_pgprint_args(self, args: argparse.Namespace) -> bool:
        if args.depth is not None and args.depth < 1:
            gdb.write("depth must be >= 1\n")
            return False

        if args.position is not None and args.position < 0:
            gdb.write("position must be >= 0\n")
            return False
        return True

    def invoke(self, argument: str, from_tty: bool) -> None:
        argv = gdb.string_to_argv(argument)
        try:
            args = self._parser.parse_args(argv)
        except Exception:
            gdb.write(self._parser.format_help())
            return

        if not self.validate_pgprint_args(args):
            gdb.write(self._parser.format_help())
            return

        value = gdb.parse_and_eval(args.expr)
        printer = Printer(max_depth=args.depth)
        if args.position is not None:
            gdb.write(describe_list_element(value, args.position, printer) + "\n")
            return

        gdb.write(printer.format(value) + "\n")


PgPrintCommand()
