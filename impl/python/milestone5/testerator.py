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
    typecheck.program(tree)
    return tree


def test_bindings(student: asts.AST, expected: asts.AST):
    return student.same_symbols(expected)


def print_test(test, retval, out, err):
    print(f"input: {test['input']}")
    print(f"expected return value: {test['output']}")
    print(f"actual return value: {retval}")
    print(f"expected stdout: {test['stdout']}")
    print(f"stdout: {out.getvalue()}")
    print(f"expected stderr: {test['stderr']}")
    print(f"stderr: {err.getvalue()}")


def run(args):
    if args.verbose:
        print("Running tests")
    with open(args.input, "rb") as f:
        tests = pickle.load(f)
    correct = 0
    for test in tests:
        if args.verbose:
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
            print_test(test, student, out, err)
            print("---")
        else:
            correct += 1
    print(f"{correct} / {len(tests)} correct")
    return (correct, len(tests))


def create(args):
    assert args.function in globals()
    fn = globals()[args.function]
    if args.pickle:
        with open(args.input, "rb") as f:
            tests = pickle.load(f)
    elif args.json:
        with open(args.input, "r") as f:
            tests = json.load(f)
    elif args.omega:
        with open(args.input, "r") as f:
            tests = [f.read()]
    else:
        assert False
    output = []
    for test in tests:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            with contextlib.redirect_stderr(io.StringIO()) as err:
                retval = fn(test)
        test = {
            "function": args.function,
            "compare": args.compare,
            "input": test,
            "output": retval,
            "stdout": out.getvalue(),
            "stderr": err.getvalue(),
        }
        output.append(test)

    with open(args.output, "wb") as f:
        pickle.dump(output, f)


def main():
    args = parse_args()
    match args.command:
        case "create":
            create(args)
        case "run":
            run(args)
        case _:
            assert False


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="create a test pickle")
    create.add_argument("--input", type=str, required=True, help="input file")
    create.add_argument("--output", type=str, required=True, help="output file")
    create.add_argument("--function", type=str, required=True, help="function to test")
    create.add_argument(
        "--compare", type=str, required=True, help="comparison function"
    )
    format = create.add_mutually_exclusive_group(required=True)
    format.add_argument("--pickle", action="store_true", help="input is a pickle")
    format.add_argument("--json", action="store_true", help="input is a json")
    format.add_argument("--omega", action="store_true", help="input is a json")

    run = subparsers.add_parser("run", help="create a JSON file with example sentences")
    run.add_argument("--input", type=str, help="input test pickle file")
    run.add_argument("--verbose", action="store_true", help="enable verbose output")

    return parser.parse_args()


if __name__ == "__main__":
    main()
