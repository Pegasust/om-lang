#!/usr/bin/env python3
import vm_insns
import scanner
import parser
import bindings
import typecheck
import offsets
import codegen
import vm
import io


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
        print("=========  Interp  =========")
        stack = []
        memory = [0] * 100000
        regs = {
            "PC": 0,
            "FP": 0,
            "SP": 1,
        }
        machine_stdout = io.StringIO()
        exec = vm.Execution(insns, stack, memory, regs,
                            max_insns=200, vm_stdout=machine_stdout)
        o = exec
        insn_last = None
        ra_lookup = {i+1: insn for i, insn in enumerate(insns)
                     if isinstance(insn, vm_insns.Call)}
        nolabel = vm_insns.Call("?")
        while o is not None:
            if exec.debug_step:
                input("Enter>>")
            o = exec.step()
            insn = exec.insns[exec.regs["PC"]]
            if not isinstance(insn, vm_insns.Noop) and insn != insn_last and\
                    not isinstance(insn, vm_insns.Label):
                frame = exec.memory[exec.regs["FP"]: exec.regs["SP"]]
                pseudo_regs = {
                    "RET": exec.memory[exec.regs["FP"]-1],
                    "RA": f"{frame[0]}: " +
                    f"{ra_lookup.get(frame[0], nolabel).comment}",
                    "CallerFP": frame[1] if len(frame) >= 2 else -1,
                    "BAIL": frame[2] if len(frame) >= 3 else -1,
                    "THROW": frame[3] if len(frame) >= 4 else -1,
                }
                print(f"      stack ={exec.stack}")
                print(f"      regs  ={exec.regs};{pseudo_regs}")
                print(
                    f'      frame ={frame}')
                print(f'      mem   ={exec.memory[:exec.regs["SP"]]}')
                exec.max_insns -= 1
                if exec.max_insns == 0:
                    break
            print(f"[{exec.regs['PC']:4}] {vm_insns.dis(insn)}")
            insn_last = insn
        print("=========  stdout  =========")
        print(machine_stdout.getvalue())


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
        }
        func g() {
            print 1
        }
        func main() {
            print 3
            call f()
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
    ]
    test(tests)
