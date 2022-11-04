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
    interps = []
    source = []
    output = []
    for i, test in enumerate(tests):
        print(f"========= Test {i:3} =========")
        print("\n".join(f"[{i+1:3}] {line}"
                        for i, line in enumerate(test.splitlines())))
        insns = compile_source(test)
        src = emit_code(insns)
        source.append(src)

        stack = []
        memory = [0] * 100000
        regs = {
            "PC": 0,
            "FP": 0,
            "SP": 1,
        }
        machine_stdout = io.StringIO()
        MAX_INS = 200
        exec = vm.Execution(insns, stack, memory, regs,
                            max_insns=MAX_INS, vm_stdout=machine_stdout)
        o = exec
        insn_last = None
        ra_lookup = {i+1: insn for i, insn in enumerate(insns)
                     if isinstance(insn, vm_insns.Call)}
        nolabel = vm_insns.Call("?")
        machine_trace = io.StringIO()
        interps.append(machine_trace)
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
                print(f"      stack ={exec.stack}", file=machine_trace)
                print(
                    f"      regs  ={exec.regs};{pseudo_regs}",
                    file=machine_trace)
                print(
                    f'      frame ={frame}', file=machine_trace)
                print(
                    f'      mem   ={exec.memory[:exec.regs["SP"]]}',
                    file=machine_trace)
                exec.max_insns -= 1
                if exec.max_insns == 0:
                    break
            print(f"[{exec.regs['PC']:4}] {vm_insns.dis(insn)}",
                  file=machine_trace)
            insn_last = insn
        output.append([
            "=========  stdout  =========",
            f"Ins taken: {MAX_INS - exec.max_insns}/{MAX_INS}",
            machine_stdout.getvalue(),
        ])
    for i, src in enumerate(source):
        print(f"========= Test {i:3} =========")
        print("=========   Source   =========")
        print(src)
    for i, interp in enumerate(interps):
        print(f"========= Test {i:3} =========")
        print("=========   Interp   =========")
        print(interp.getvalue())
    for i, out in enumerate(output):
        print(f"========= Test {i:3} =========")
        print("\n".join(out))


if __name__ == "__main__":
    tests_m8 = [
        """
        func g() {
            print 1
        }
        func f() {
            print 2
            call g()
            print 3
            call g()
        }
        func main() {
            print 4
            call f()
            call g()
            print 5
        }
        """,
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
    # test(tests_m8)
    tests = [
        """
func foo1(x1:int , x2: int, x3:int, a: bool):int{
    var sum : int 
    sum = 100
    {
        var sum : int 
        sum = 0
        x1 = 20 
        x2 = 20
        x3 = 20
        if (x1 == x2){
            x3 = 40
            if (x3 == x1 + x2){
                sum = x3 + x2 + x1 
            }
            else{
                var a : bool
                sum = x3 + x2 
                a = false
            }
            print sum
            print a
        }
        else{
            sum = x1 + x2 - x3
            print sum
        }
    }
    print sum
    return 0
}  
func main(){
    var x : int
    var y : int
    var z : int 
    var a : bool
    var b : bool
    x = 10
    y = 20
    z = 30 
    a = true
    b = false
    call foo1(x, y, z, a)
}
"""
    ]
    # test(tests)
    tests_m9 = [
        """
        func main() {
            var foo: int
            foo = 3
            var bar: int
            bar = 8
            print 2
            print bar
            print foo
        }
        """
    ]
    test(tests_m9)
