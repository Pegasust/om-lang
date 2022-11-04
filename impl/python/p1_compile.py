#!/usr/bin/env python3
import vm_insns
import scanner
import parser
import bindings
import typecheck
import offsets
import codegen


def emit_code(insns: list[vm_insns.Insn]) -> str:
    return "\n".join(
        f"[{i+1:3}] {vm_insns.dis(insn, False, 4)}"
        for i, insn in enumerate(insns))


def compile_source(inp: str) -> list[vm_insns.Insn]:
    s = scanner.Scanner(inp)
    tree = parser.Parser(s).parse()

    # decorate AST with bindings
    bindings.program(tree)
    typecheck.program(tree)
    offsets.program(tree)

    # generate assembly for our PyVM
    instructions = codegen.generate(tree)
    return instructions


def test(tests: list[str]):
    for i, test in enumerate(tests):
        print(f"========= Test {i:3} =========")
        print("\n".join(f"[{i+1:3}] {line}"
                        for i, line in enumerate(test.splitlines())))
        insns = compile_source(test)
        print("=========  Output  =========")
        source = emit_code(insns)
        print(source)


if __name__ == "__main__":
    tests = [
        """
        func main() {
            print 17
        }
        """,
        """
        func f() {
            print 2
            call g()
            print 3
            call g()
        }
        func g() {
            print 1
        }
        func main() {
            call f()
            print 17
            call g()
        }
        """,
        """

        """
    ]
    test(tests)
