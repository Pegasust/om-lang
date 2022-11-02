from typing import List

import vm
import vm_insns


def invoke_omega(insns, params, verbose):
    if verbose:
        dump_insns(insns)

    params = []
    for arg in reversed(params):
        if arg.isnumeric():
            params.append(int(arg))
        else:
            raise Exception(f"Invalid argument: {arg}")

    stack: List[int] = []
    memory: List[int] = params + [0] * 100000
    regs = {
        "PC": 0,
        "FP": 0,
        "SP": len(params) + 1,
    }
    exe = vm.Execution(insns, stack, memory, regs)
    exe.verbose = verbose
    exe.run()
    assert exe.regs["SP"] == len(params) + 1


def dump_insns(insns):
    print("Instructions:")
    for i, insn in enumerate(insns):
        print(f"[{i:5}]", vm_insns.dis(insn, indent=8, long=False))
