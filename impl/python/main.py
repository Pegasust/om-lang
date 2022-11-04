#!/usr/bin/env python3
import argparse
from sys import stdout
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
import vm_insns


def main():
    args = get_args()
    fname = args.file
    compiled_source = None
    with open(fname) as f:
        input = f.read()
        compiled_source = compile(input)

    if not compiled_source:
        raise RuntimeError(f"Compiling {fname} yields None for some reason")

    with open(args.output, "w") as f:
        # stdout.writelines(
        #     (vm_insns.dis(isns)+"\n" for isns in compiled_source))
        f.writelines((vm_insns.dis(isns)+"\n" for isns in compiled_source))

    if args.run:
        interpret(compiled_source, args.args, args.verbose)


def compile(input):
    lexer = Scanner(input)
    psr = Parser(lexer)
    tree: Program = psr.parse()
    bindings.program(tree)
    typecheck.program(tree)
    offsets.program(tree)
    insns: List[Insn] = codegen.generate(tree)
    return insns


def interpret(insns: list[Insn], args, verbose):
    vm_utils.invoke_omega(insns, args, verbose)


def get_args():
    ap: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Compile Omega files"
    )
    ap.add_argument("--file", help="The file to compile")
    ap.add_argument("--output", help="Output filename", default="a.omega")
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Cause the interpreter to be more verbose",
    )
    ap.add_argument(
        "args", nargs="*", help="Arguments to pass to the program as integers"
    )
    ap.add_argument("--run", action="store_true",
                    help="Run the program after compilation")
    return ap.parse_args()


if __name__ == "__main__":
    main()
