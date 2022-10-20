from asts import *
from tokens import *
import scanner
import parser
from ast_tests_data import tests


def main():
    failed = 0
    for i, p, tree in tests:
        lexer = scanner.Scanner(p)
        psr = parser.Parser(lexer)
        computed: asts.Program = psr.parse()
        if tree != computed:
            failed += 1
            print(f"Test {i} failed")
            print(f"Expected: {tree}")
            print(f"Computed: {computed}")
            print("---")
    print(f'total {len(tests)}, correct {len(tests)-failed}, failed {failed}')



if __name__ == "__main__":
    main()
