import json
import argparse
from scanner import Scanner
from parser import Parser


def main():
    args = get_args()
    if args.correct:
        with open(args.correct) as f:
            correct = json.load(f)
            for x in correct:
                do_correct(x)

    if args.incorrect:
        with open(args.incorrect) as f:
            incorrect = json.load(f)
            for x in incorrect:
                do_incorrect(x)


def do_incorrect(x: str):
    scanner = Scanner(x)
    parser = Parser(scanner)
    try:
        parser.parse()
        print("Incorrect input was accepted: " + x)
        print("---")
    except Exception as e:
        pass


def do_correct(x: str):
    scanner = Scanner(x)
    parser = Parser(scanner)
    try:
        parser.parse()
    except Exception as e:
        print("Incorrectly rejected: " + x)
        print("Exception: " + str(e))
        print("---")


def get_args():
    parser = argparse.ArgumentParser(description="Test a JSON file.")
    parser.add_argument(
        "--correct", type=str, help="The JSON file with list of correct inputs."
    )
    parser.add_argument(
        "--incorrect", type=str, help="The JSON file with list of incorrect inputs."
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
