import pprint
import argparse
import pickle
import contextlib
import io
import json
import pprint
from typing import Callable

from asts import AST, Id, Program, Type, Decl, Expr
import scanner
import parser
import typecheck
import bindings
import codegen
import vm_utils

import offsets
import ast_pprint
import os
    
OUT_DIR=os.getenv("TEST_OUTPUT") or "test_output"


def test(
    student: AST, expected: AST, fn: Callable[[AST, AST], bool], crash: bool
) -> bool:
    try:
        return student.assert_equal(expected, fn)
    except:
        if crash:
            raise
        return False


def test_bindings(student: AST, expected: AST, crash: bool) -> bool:
    def fn(a: AST, b: AST):
        if isinstance(a, Id) and isinstance(b, Id):
            assert a.symbol == b.symbol
        return True

    return test(student, expected, fn, crash)


def test_typecheck(student: AST, expected: AST, crash: bool) -> bool:
    def fn(a: AST, b: AST):
        if (isinstance(a, Type) or isinstance(a, Decl) or isinstance(a, Expr)) and (
            isinstance(b, Type) or isinstance(b, Decl) or isinstance(b, Expr)
        ):
            assert a.semantic_type == b.semantic_type
        return True

    return test(student, expected, fn, crash)


def test_offsets(student: AST, expected: AST, crash: bool) -> bool:
    def fn(a: AST, b: AST):
        if isinstance(a, Id) and isinstance(b, Id):
            assert a.symbol.offset == b.symbol.offset, \
            f"BAD: inequal offset {a.token.value} {a.symbol.offset} != {b.token.value} {b.symbol.offset}"
        return True

    return test(student, expected, fn, crash)

def nothing(student, expected, crash):
    return True


def log_test(test, retval):
    input_content_hash = hex(hash(test['input']))
    with open(f"{OUT_DIR}/test-{input_content_hash}.expect", "w") as f:
        print(f"input: {test['input']}", file=f)
        print(ast_pprint.SymbolCollector().output(test["output"]), file=f)

    with open(f"{OUT_DIR}/test-{input_content_hash}.actual", "w") as f:
        print(f"input: {test['input']}", file=f)
        print(ast_pprint.SymbolCollector().output(retval), file=f)


def print_test(test, retval, out, err):
    print(f"input: {test['input']}")
    print(f"==== expected return value ====")
    print(ast_pprint.SymbolCollector().output(test["output"]))
    print(f"==== actual return value ====")
    print(ast_pprint.SymbolCollector().output(retval))
    print(f"expected stdout: {test['stdout']}")
    print(f"stdout: {out.getvalue()}")
    print(f"expected stderr: {test['stderr']}")
    print(f"stderr: {err.getvalue()}")


def compile(input: str):
    lexer = scanner.Scanner(input)
    psr = parser.Parser(lexer)
    tree: Program = psr.parse()
    bindings.program(tree)
    typecheck.program(tree)
    offsets.program(tree)
    return tree

def compile_run(input: str):
    tree = compile(input)
    insns = codegen.generate(tree)
    vm_utils.invoke_omega(insns, [], False)
    return None


def run(inputs: list[str], verbose, crash) -> tuple[int, int]:
    if verbose:
        print("Running tests")
    correct = 0
    total = 0
    for input in inputs:
        if verbose:
            print(f"Reading {input}")
        with open(input, "rb") as f:
            tests = pickle.load(f)
        for test in tests:
            if verbose:
                pprint.pprint(test)
            fn = globals()[test["function"]]
            compare = globals()[test["compare"]]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    student = fn(test["input"])

            log_test(test, student)
            if (
                not compare(student, test["output"], crash)
                or out.getvalue() != test["stdout"]
                or err.getvalue() != test["stderr"]
            ):
                print_test(test, student, out, err)
                print("---")
            else:
                correct += 1
        total += len(tests)
    print(f"{correct} / {total} correct")
    return (correct, total)


def create(args):
    assert args.function in globals()
    fn = globals()[args.function]
    outputs = []
    for input in args.input:
        tests = read_input(args, input)
        output = process_test_inputs(args, fn, tests)
        outputs.extend(output)
    if args.verbose:
        print(f"Writing output.  {len(outputs)} tests")
    with open(args.output, "wb") as f:
        pickle.dump(outputs, f)


def process_test_inputs(args, fn, tests) -> list[dict]:
    output = []
    for test in tests:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            with contextlib.redirect_stderr(io.StringIO()) as err:
                retval = None
                error = None
                try:
                    retval = fn(test)
                except Exception as e:
                    error = e
                test = {
                    "function": args.function,
                    "compare": args.compare,
                    "input": test,
                    "output": retval,
                    "stdout": out.getvalue(),
                    "stderr": err.getvalue(),
                    "error": error,
                }
                output.append(test)
    return output


def read_input(args, input) -> list[str]:
    if args.verbose:
        print(f"Reading {input}")
    if args.pickle:
        with open(input, "rb") as f:
            tests = pickle.load(f)
    elif args.json:
        with open(input, "r") as f:
            tests = json.load(f)
    elif args.omega:
        with open(input, "r") as f:
            tests = [f.read()]
    else:
        assert False
    return tests


def main():
    args = parse_args()
    match args.command:
        case "create":
            create(args)
        case "run":
            run(args.input, args.verbose, args.crash)
        case _:
            assert False


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="create a test pickle")
    create.add_argument("input", type=str, nargs="+", help="input file(s)")
    create.add_argument("--output", type=str, required=True, help="output file")
    create.add_argument("--function", type=str, required=True, help="function to test")
    create.add_argument(
        "--compare", type=str, required=True, help="comparison function"
    )
    create.add_argument("--verbose", action="store_true", help="verbose output")

    format = create.add_mutually_exclusive_group(required=True)
    format.add_argument("--pickle", action="store_true", help="input is a pickle")
    format.add_argument("--json", action="store_true", help="input is a json")
    format.add_argument("--omega", action="store_true", help="input is a json")

    run = subparsers.add_parser("run", help="run tests in a pickle file")
    run.add_argument("input", nargs="+", help="input test pickle file(s)")
    run.add_argument("--verbose", action="store_true", help="enable verbose output")
    run.add_argument("--crash", action="store_true", help="crash on error")

    return parser.parse_args()


if __name__ == "__main__":
    main()
