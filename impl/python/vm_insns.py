from typing import Optional


class Insn:
    comment: str


class Label(Insn):
    """
    Verbose asm:  Label <label:str>  [<comment:str>]
    Concise asm:  lab   <label:str>  [<comment:str>]

    Stack:
    |-----| <- TOS   |-----| <- TOS
    | ... |          | ... |
    Before            After
    """

    def __init__(self, label: str, comment: Optional[str] = None):
        self.label: str = label
        self.comment: Optional[str] = comment


class Jump(Insn):
    """
    Verbose asm:  Jump <label:str>  [<comment:str>]
    Concise asm:  j    <label:str>  [<comment:str>]

    Stack:
    |-----| <- TOS   |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: PC <- label
    """

    def __init__(self, label: str, comment: Optional[str] = None):
        self.label: str = label
        self.comment: Optional[str] = comment


class JumpIfZero(Insn):
    """
    Verbose asm:  JumpIfZero <label:str>  [<comment:str>]
    Concise asm:  jz         <label:str>  [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: PC <- label iff v == 0
    """

    def __init__(self, label: str, comment: Optional[str] = None):
        self.label: str = label
        self.comment: Optional[str] = comment


class JumpIfNotZero(Insn):
    """
    Verbose asm:  JumpIfNotZero <label:str>  [<comment:str>]
    Concise asm:  jnz           <label:str>  [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: PC <- label iff v != 0
    """

    def __init__(self, label: str, comment: Optional[str] = None):
        self.label: str = label
        self.comment: Optional[str] = comment


class JumpIndirect(Insn):
    """
    Verbose asm:  JumpIndirect  [<comment:str>]
    Concise asm:  ji            [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: PC <- v
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class PushImmediate(Insn):
    """
    Verbose asm:  PushImmediate <value:int>  [<comment:str>]
    Concise asm:  push          <value:int>  [<comment:str>]

    Stack:
                     |-----| <- TOS
                     | imm |
    |-----| <- TOS   |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, value: int, comment: Optional[str] = None):
        self.value: int = value
        self.comment: Optional[str] = comment


class PushLabel(Insn):
    """
    Verbose asm:  PushLabel <label:str>  [<comment:str>]
    Concise asm:  pushl     <label:str>  [<comment:str>]

    Stack:
                     |-------| <- TOS
                     | label |
    |-----| <- TOS   |-------|
    | ... |          | ...   |
    Before            After
    """

    def __init__(self, label: str, comment: Optional[str] = None):
        self.label: str = label
        self.comment: Optional[str] = comment


class Add(Insn):
    """
    Verbose asm:  Add  [<comment:str>]
    Concise asm:  add  [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-----| <- TOS
    | x   |          | x+y |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Sub(Insn):
    """
    Verbose asm:  Sub  [<comment:str>]
    Concise asm:  sub  [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-----| <- TOS
    | x   |          | x-y |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Mul(Insn):
    """
    Verbose asm:  Mul  [<comment:str>]
    Concise asm:  mul  [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-----| <- TOS
    | x   |          | x*y |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Div(Insn):
    """
    Verbose asm:  Div  [<comment:str>]
    Concise asm:  div  [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-----| <- TOS
    | x   |          | x/y |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Negate(Insn):
    """
    Verbose asm:  Negate  [<comment:str>]
    Concise asm:  neg     [<comment:str>]

    Stack:
    |-----| <- TOS   |-----| <- TOS
    | v   |          | -v  |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class LessThan(Insn):
    """
    Verbose asm:  LessThan  [<comment:str>]
    Concise asm:  lt        [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-----| <- TOS
    | x   |          | x<y |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class GreaterThan(Insn):
    """
    Verbose asm:  GreaterThan  [<comment:str>]
    Concise asm:  gt           [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-----| <- TOS
    | x   |          | x>y |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class LessThanEqual(Insn):
    """
    Verbose asm:  LessThanEqual  [<comment:str>]
    Concise asm:  leq            [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-------| <- TOS
    | x   |          | x<=y  |
    |-----|          |-------|
    | ... |          | ...   |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class GreaterThanEqual(Insn):
    """
    Verbose asm:  GreaterThanEqual  [<comment:str>]
    Concise asm:  geq               [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-------| <- TOS
    | x   |          | x>=y  |
    |-----|          |-------|
    | ... |          | ...   |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Equal(Insn):
    """
    Verbose asm:  Equal  [<comment:str>]
    Concise asm:  eq     [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-------| <- TOS
    | x   |          | x==y  |
    |-----|          |-------|
    | ... |          | ...   |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class NotEqual(Insn):
    """
    Verbose asm:  NotEqual  [<comment:str>]
    Concise asm:  neq       [<comment:str>]

    Stack:
    |-----| <- TOS
    | y   |
    |-----|          |-------| <- TOS
    | x   |          | x!=y  |
    |-----|          |-------|
    | ... |          | ...   |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Not(Insn):
    """
    Verbose asm:  Not  [<comment:str>]
    Concise asm:  not  [<comment:str>]

    Stack:
    |-----| <- TOS   |-------| <- TOS
    | v   |          | not v |
    |-----|          |-------|
    | ... |          | ...   |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Load(Insn):
    """
    Verbose asm:  Load  [<comment:str>]
    Concise asm:  ld    [<comment:str>]

    Stack:
    |---------| <- TOS   |---------------| <- TOS
    | address |          | mem[address]  |
    |---------|          |---------------|
    | ...     |          | ...           |
    Before                After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Store(Insn):
    """
    Verbose asm:  Store  [<comment:str>]
    Concise asm:  st     [<comment:str>]

    Stack:
    |---------| <- TOS
    | v       |
    |---------|
    | address |
    |---------|          |-----| <- TOS
    | ...     |          | ... |
    Before                After

    Side Effects: mem[address] <- v
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Print(Insn):
    """
    Verbose asm:  Print  [<comment:str>]
    Concise asm:  print  [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: print v to stdout
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class PushFP(Insn):
    """
    Verbose asm:  PushFP <offset:int>  [<comment:str>]
    Concise asm:  pushFP <offset:int>  [<comment:str>]

    Stack:
                     |-----------| <- TOS
                     | FP+offset |
    |-----| <- TOS   |-----------|
    | ... |          | ...       |
    Before            After
    """

    def __init__(self, offset: int, comment: Optional[str] = None):
        self.offset: int = offset
        self.comment: Optional[str] = comment


class PopFP(Insn):
    """
    Verbose asm:  PopFP  [<comment:str>]
    Concise asm:  popFP  [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: FP <- v
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class PushSP(Insn):
    """
    Verbose asm:  PushSP <offset:int>  [<comment:str>]
    Concise asm:  pushSP <offset:int>  [<comment:str>]

    Stack:
                     |-----------| <- TOS
                     | SP+offset |
    |-----| <- TOS   |-----------|
    | ... |          | ...       |
    Before            After
    """

    def __init__(self, offset: int, comment: Optional[str] = None):
        self.offset: int = offset
        self.comment: Optional[str] = comment


class PopSP(Insn):
    """
    Verbose asm:  PopSP  [<comment:str>]
    Concise asm:  popSP  [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: SP <- v
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Call(Insn):
    """
    Verbose asm:  Call  [<comment:str>]
    Concise asm:  call  [<comment:str>]

    Stack:
    |-----| <- TOS   |---------| <- TOS
    | v   |          | retaddr |
    |-----|          |---------|
    | ... |          | ...     |
    Before            After

    Side Effects: PC <- v
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Halt(Insn):
    """
    Verbose asm:  Halt  [<comment:str>]
    Concise asm:  halt  [<comment:str>]

    Stack:
    |-----| <- TOS   |-----| <- TOS
    | ... |          | ... |
    Before            After

    Side Effects: halt execution
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Pop(Insn):
    """
    Verbose asm:  Pop  [<comment:str>]
    Concise asm:  pop  [<comment:str>]

    Stack:
    |-----| <- TOS
    | v   |
    |-----|          |-----| <- TOS
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Swap(Insn):
    """
    Verbose asm:  Swap  [<comment:str>]
    Concise asm:  swap  [<comment:str>]

    Stack:
    |-----| <- TOS   |-----| <- TOS
    | y   |          | x   |
    |-----|          |-----|
    | x   |          | y   |
    |-----|          |-----|
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class SaveEvalStack(Insn):
    """
    Verbose asm:  SaveEvalStack  [<comment:str>]
    Concise asm:  save           [<comment:str>]

    Stack:
    |-----| <- TOS
    | vN  |
    |-----|
    | ... |
    |-----|
    | v0  |
    |=====|          |=====| <- TOS
    Before            After

    Memory:
                    |-----| <- SP
                    | N   |
                    |-----|
                    | vN  |
                    |-----|
                    | ... |
                    |-----|
                    | v0  |
    |-----| <- SP   |-----|
    | ... |         | ... |
    Before           After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class RestoreEvalStack(Insn):
    """
    Verbose asm:  RestoreEvalStack  [<comment:str>]
    Concise asm:  restore           [<comment:str>]

    Stack:
                     |-----| <- TOS
                     | ... |
                     |-----|
                     | vN  |
                     |-----|
                     | ... |
    |-----| <- TOS   |-----|
    | ... |          | v0  |
    |=====|          |=====|
    Before            After

    Memory:
    |-----| <- SP
    | N   |
    |-----|
    | vN  |
    |-----|
    | ... |
    |-----|
    | v0  |
    |-----|         |-----| <- SP
    | ... |         | ... |
    Before           After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


class Noop(Insn):
    """
    Verbose asm:  Noop  [<comment:str>]
    Concise asm:  noop  [<comment:str>]

    Stack:
    |-----| <- TOS   |-----| <- TOS
    | ... |          | ... |
    Before            After
    """

    def __init__(self, comment: Optional[str] = None):
        self.comment: Optional[str] = comment


def dis(insn: Insn, long=True, indent=0):
    args = ""
    indentation = " " * indent
    op = "<op>"
    match insn:
        case Label():
            op = "Label" if long else "lab"
            indentation = ""
            args += insn.label.__repr__()
        case Jump():
            op = "Jump" if long else "j"
            args += insn.label.__repr__()
        case JumpIfZero():
            op = "JumpIfZero" if long else "jz"
            args += insn.label.__repr__()
        case JumpIfNotZero():
            op = "JumpIfNotZero" if long else "jnz"
            args += insn.label.__repr__()
        case JumpIndirect():
            op = "JumpIndirect" if long else "ji"
        case PushImmediate():
            op = "PushImmediate" if long else "push"
            args += insn.value.__repr__()
        case PushLabel():
            op = "PushLabel" if long else "pushl"
            args += insn.label.__repr__()
        case Add():
            op = "Add" if long else "add"
        case Sub():
            op = "Sub" if long else "sub"
        case Mul():
            op = "Mul" if long else "mul"
        case Div():
            op = "Div" if long else "div"
        case Negate():
            op = "Negate" if long else "neg"
        case LessThan():
            op = "LessThan" if long else "lt"
        case GreaterThan():
            op = "GreaterThan" if long else "gt"
        case LessThanEqual():
            op = "LessThanEqual" if long else "leq"
        case GreaterThanEqual():
            op = "GreaterThanEqual" if long else "geq"
        case Equal():
            op = "Equal" if long else "eq"
        case NotEqual():
            op = "NotEqual" if long else "neq"
        case Not():
            op = "Not" if long else "not"
        case Load():
            op = "Load" if long else "ld"
        case Store():
            op = "Store" if long else "st"
        case Print():
            op = "Print" if long else "print"
        case PushFP():
            op = "PushFP" if long else "pushFP"
            args += insn.offset.__repr__()
        case PopFP():
            op = "PopFP" if long else "popFP"
        case PushSP():
            op = "PushSP" if long else "pushSP"
            args += insn.offset.__repr__()
        case PopSP():
            op = "PopSP" if long else "popSP"
        case Call():
            op = "Call" if long else "call"
        case Halt():
            op = "Halt" if long else "halt"
        case Pop():
            op = "Pop" if long else "pop"
        case Swap():
            op = "Swap" if long else "swap"
        case SaveEvalStack():
            op = "SaveEvalStack" if long else "save"
        case RestoreEvalStack():
            op = "RestoreEvalStack" if long else "restore"
        case Noop():
            op = "Noop" if long else "noop"
    args += insn.comment.__repr__() if insn.comment else ""
    return f"{indentation}{op} {args}"


reserved = [
    "Label",
    "lab",
    "Jump",
    "j",
    "JumpIfZero",
    "jz",
    "JumpIfNotZero",
    "jnz",
    "JumpIndirect",
    "ji",
    "PushImmediate",
    "push",
    "PushLabel",
    "pushl",
    "Add",
    "add",
    "Sub",
    "sub",
    "Mul",
    "mul",
    "Div",
    "div",
    "Negate",
    "neg",
    "LessThan",
    "lt",
    "GreaterThan",
    "gt",
    "LessThanEqual",
    "leq",
    "GreaterThanEqual",
    "geq",
    "Equal",
    "eq",
    "NotEqual",
    "neq",
    "Not",
    "not",
    "Load",
    "ld",
    "Store",
    "st",
    "Print",
    "print",
    "PushFP",
    "pushFP",
    "PopFP",
    "popFP",
    "PushSP",
    "pushSP",
    "PopSP",
    "popSP",
    "Call",
    "call",
    "Halt",
    "halt",
    "Pop",
    "pop",
    "Swap",
    "swap",
    "SaveEvalStack",
    "save",
    "RestoreEvalStack",
    "restore",
    "Noop",
    "noop",
]
