#!/usr/bin/env python3
import argparse
from typing import List

from asts import Program
from scanner import Scanner
from parser import Parser
import typecheck
import bindings
import codegen
import offsets
from vm_insns import Insn
import vm_utils


def main():
    args = get_args()
    fname = args.file
    with open(fname) as f:
        input = f.read()
    interpret(input, args.args, args.verbose)


def interpret(input, args, verbose):
    lexer = Scanner(input)
    psr = Parser(lexer)
    tree: Program = psr.parse()
    bindings.program(tree)
    typecheck.program(tree)
    offsets.program(tree)
    insns: List[Insn] = codegen.generate(tree)
    vm_utils.invoke_omega(insns, args, verbose)


def get_args():
    ap: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Compile Omega files"
    )
    ap.add_argument("--file", help="The file to compile")
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Cause the interpreter to be more verbose",
    )
    ap.add_argument(
        "args", nargs="*", help="Arguments to pass to the program as integers"
    )
    return ap.parse_args()


if __name__ == "__main__":
    main()
