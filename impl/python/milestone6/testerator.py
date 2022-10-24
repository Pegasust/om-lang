import pprint
import argparse
import pickle
import contextlib
import io
import json
import pprint

import asts
import scanner
import parser
import typecheck
import bindings


def compile(input: str):
    lexer = scanner.Scanner(input)
    psr = parser.Parser(lexer)
    tree: asts.Program = psr.program()
    bindings.program(tree)
    # print(f"Tree after bindings: {tree}")
    typecheck.program(tree)
    return tree


def test_bindings(student: asts.AST, expected: asts.AST):
    return student.same_symbols(expected)


def test_typecheck(student: asts.AST, expected: asts.AST):
    return student.same_types(expected)


def print_test(test, retval, out, err):
    print(f"=== input ===\n{test['input']}")
    print(f"=== expected return value ===\n{test['output']}")
    print(f"=== actual return value ===\n{retval}")
    print(f"=== expected stdout ===\n{test['stdout']}")
    print(f"=== stdout ===\n{out.getvalue()}")
    print(f"=== expected stderr ===\n{test['stderr']}")
    print(f"=== stderr ===\n{err.getvalue()}")


def run(inputs: list[str], verbose) -> tuple[int, int]:
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
            if (
                not compare(student, test["output"])
                or out.getvalue() != test["stdout"]
                or err.getvalue() != test["stderr"]
            ):
                print("===== Failed =====")
                print_test(test, student, out, err)
                print("---")
            else:
                print_test(test, student, out, err)
                print("---")
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
            run(args.input, args.verbose)
        case _:
            assert False


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="create a test pickle")
    create.add_argument("--input", type=str, nargs="+", help="input file(s)")
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
    run.add_argument("--input", nargs="+", help="input test pickle file(s)")
    run.add_argument("--verbose", action="store_true", help="enable verbose output")

    return parser.parse_args()


if __name__ == "__main__":
    main()
