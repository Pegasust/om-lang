#!/usr/bin/env python3
import pprint
import argparse
from typing import List, Dict, Tuple, Set, Optional, Union

import vm_parser
import vm_scanner
import vm_insns
import vm_utils
import vm


def get_args():
    ap = argparse.ArgumentParser(description="Run VM files")
    ap.add_argument("args", nargs="*", type=int, help="Arguments to pass to VM")
    ap.add_argument("--file", type=str, required=True, help="The file to run")
    ap.add_argument("--verbose", action="store_true", help="verbose output")
    ap.add_argument("--debug-step", action="store_true", help="debug with step")
    return ap.parse_args()


def main():
    args = get_args()
    fname = args.file
    with open(fname) as f:
        input = f.read()

    lexer = vm_scanner.Scanner(input, reserved=vm_insns.reserved)
    psr = vm_parser.Parser(lexer)
    insns: List[vm.Insn] = psr.parse()

    if args.verbose:
        vm_utils.dump_insns(insns)

    params = list(reversed(args.args)) + [0]  # w/ space for return value
    exe = vm.Execution(
        insns,
        [],
        params + [0] * 100000,
        {"SP": len(params)},
    )
    exe.verbose = args.verbose
    exe.debug_step = args.debug_step
    exe.run()


if __name__ == "__main__":
    main()
