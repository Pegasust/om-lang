from typing import List, Dict, Tuple, Optional

from vm_insns import *


class Execution:
    def __init__(
        self,
        insns: List[Insn],
        stack: List[int],
        memory: List[int],
        regs: Dict[str, int],
    ):
        self.insns: List[Insn] = insns
        self.stack: List[int] = stack
        self.memory: List[int] = memory
        self.regs: Dict[str, int] = regs
        if "FP" not in self.regs:
            self.regs["FP"] = 0
        if "SP" not in self.regs:
            self.regs["SP"] = 0
        if "PC" not in self.regs:
            self.regs["PC"] = 0
        self.labels: dict[str, int] = {}
        for i, insn in enumerate(self.insns):
            match insn:
                case Label(label=label):
                    assert label not in self.labels, f"Duplicate label: {label}"
                    self.labels[label] = i

        for insn in self.insns:
            if hasattr(insn, "label"):
                lab = getattr(insn, "label")
                assert lab in self.labels, f"Undefined label: {lab}"

        self.verbose = False

    def __repr__(self):
        return f"Execution({self.insns}, {self.stack}, {self.regs})"

    def dump_state(self):
        insn = self.insns[self.regs["PC"]]
        if self.regs["FP"] == 0:
            caller = "N/A"
        else:
            start = self.memory[self.regs["FP"] + 1]
            caller = self.memory[start : self.regs["FP"]]
        print(f"      stack ={self.stack}")
        print(f"      regs  ={self.regs}")
        print(f'      frame ={self.memory[self.regs["FP"] : self.regs["SP"]]}')
        print(f"      caller={caller}")
        print(f"[{self.regs['PC']:4}] {dis(insn)}")

    def step(self) -> Optional["Execution"]:
        insn = self.insns[self.regs["PC"]]
        match insn:
            case Label():
                self.regs["PC"] += 1
            case Noop():
                self.regs["PC"] += 1
            case Jump(label=label):
                self.regs["PC"] = self.labels[label]
            case JumpIfZero(label=label):
                if self.stack.pop() == 0:
                    self.regs["PC"] = self.labels[label]
                else:
                    self.regs["PC"] += 1
            case JumpIfNotZero(label=label):
                if self.stack.pop() != 0:
                    self.regs["PC"] = self.labels[label]
                else:
                    self.regs["PC"] += 1
            case JumpIndirect():
                self.regs["PC"] = self.stack.pop()
            case PushImmediate(value=value):
                self.stack.append(value)
                self.regs["PC"] += 1
            case PushLabel(label=label):
                self.stack.append(self.labels[label])
                self.regs["PC"] += 1
            case Load():
                lval = self.stack.pop()
                rval = self.memory[lval]
                self.stack.append(rval)
                self.regs["PC"] += 1
            case Store():
                rval = self.stack.pop()
                lval = self.stack.pop()
                self.memory[lval] = rval
                self.regs["PC"] += 1
            case Add():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(penultimate + top)
                self.regs["PC"] += 1
            case Sub():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(penultimate - top)
                self.regs["PC"] += 1
            case Mul():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(penultimate * top)
                self.regs["PC"] += 1
            case Div():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(penultimate // top)
                self.regs["PC"] += 1
            case Negate():
                self.stack.append(-self.stack.pop())
                self.regs["PC"] += 1
            case LessThan():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(int(penultimate < top))
                self.regs["PC"] += 1
            case GreaterThan():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(int(penultimate > top))
                self.regs["PC"] += 1
            case LessThanEqual():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(int(penultimate <= top))
                self.regs["PC"] += 1
            case GreaterThanEqual():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(int(penultimate >= top))
                self.regs["PC"] += 1
            case Equal():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(int(penultimate == top))
                self.regs["PC"] += 1
            case NotEqual():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(int(penultimate != top))
                self.regs["PC"] += 1
            case Not():
                self.stack.append(int(self.stack.pop() == 0))
                self.regs["PC"] += 1
            case Print():
                print(self.stack.pop())
                self.regs["PC"] += 1
            case PushFP(offset=offset):
                self.stack.append(self.regs["FP"] + offset)
                self.regs["PC"] += 1
            case PopFP():
                self.regs["FP"] = self.stack.pop()
                self.regs["PC"] += 1
            case PushSP(offset=offset):
                self.stack.append(self.regs["SP"] + offset)
                self.regs["PC"] += 1
            case PopSP():
                self.regs["SP"] = self.stack.pop()
                self.regs["PC"] += 1
            case Pop():
                self.stack.pop()
                self.regs["PC"] += 1
            case Swap():
                top = self.stack.pop()
                penultimate = self.stack.pop()
                self.stack.append(top)
                self.stack.append(penultimate)
                self.regs["PC"] += 1
            case Call():
                # assert len(self.stack) == 1, "Call must have only destination on stack"
                retattr = self.regs["PC"] + 1
                self.regs["PC"] = self.stack.pop()
                self.stack.append(retattr)
            case SaveEvalStack():
                sp = self.regs["SP"]
                size = len(self.stack)
                self.memory[sp : sp + size + 1] = self.stack + [size]
                self.regs["SP"] += size + 1
                self.stack = []
                self.regs["PC"] += 1
            case RestoreEvalStack():
                sp = self.regs["SP"]
                size = self.memory[sp - 1]
                tmp = self.memory[sp - size - 1 : sp - 1]
                self.regs["SP"] -= size + 1
                self.stack = tmp + self.stack
                self.regs["PC"] += 1
            case Halt():
                return None
            case _:
                raise Exception(f"Unknown instruction: {insn}")
        return self

    def run(self):
        if self.verbose:
            print("Begin Execution")
            self.dump_state()
        o = self
        while o is not None:
            o = self.step()
            if self.verbose:
                self.dump_state()
        if self.verbose:
            print("End Execution")
