import vm


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner

    def error(self, msg: str):
        raise Exception(msg + " at " + str(self.scanner.peek()))

    def match(self, kind: str):
        if self.current() == kind:
            return self.scanner.consume()
        else:
            self.error(f"expected {kind}")

    def current(self):
        return self.scanner.peek().kind

    def parse(self):
        v = self._start()
        self.match("EOF")
        return v

    # start -> { operation }
    def _start(self):
        _start_ = []
        while self.current() in {
            "Add",
            "Call",
            "Div",
            "Equal",
            "GreaterThan",
            "GreaterThanEqual",
            "Halt",
            "Jump",
            "JumpIfNotZero",
            "JumpIfZero",
            "JumpIndirect",
            "Label",
            "LessThan",
            "LessThanEqual",
            "Load",
            "Mul",
            "Negate",
            "Noop",
            "Not",
            "NotEqual",
            "Pop",
            "PopFP",
            "PopSP",
            "Print",
            "PushFP",
            "PushImmediate",
            "PushLabel",
            "PushSP",
            "RestoreEvalStack",
            "SaveEvalStack",
            "Store",
            "Sub",
            "Swap",
            "add",
            "call",
            "div",
            "eq",
            "geq",
            "gt",
            "halt",
            "j",
            "ji",
            "jnz",
            "jz",
            "lab",
            "ld",
            "leq",
            "lt",
            "mul",
            "neg",
            "neq",
            "noop",
            "not",
            "pop",
            "popFP",
            "popSP",
            "print",
            "push",
            "pushFP",
            "pushSP",
            "pushl",
            "restore",
            "save",
            "st",
            "sub",
            "swap",
        }:
            _tmp__start__4432493968 = self._operation()
            _start_.append(_tmp__start__4432493968)
        return _start_

    # operation -> ("Label" | "lab") str [ str ] | ("Jump" | "j") str [ str ] | ("JumpIfZero" | "jz") str [ str ] | ("JumpIfNotZero" | "jnz") str [ str ] | ("JumpIndirect" | "ji") [ str ] | ("PushImmediate" | "push") int [ str ] | ("PushLabel" | "pushl") str [ str ] | ("Add" | "add") [ str ] | ("Sub" | "sub") [ str ] | ("Mul" | "mul") [ str ] | ("Div" | "div") [ str ] | ("Negate" | "neg") [ str ] | ("LessThan" | "lt") [ str ] | ("GreaterThan" | "gt") [ str ] | ("LessThanEqual" | "leq") [ str ] | ("GreaterThanEqual" | "geq") [ str ] | ("Equal" | "eq") [ str ] | ("NotEqual" | "neq") [ str ] | ("Not" | "not") [ str ] | ("Load" | "ld") [ str ] | ("Store" | "st") [ str ] | ("Print" | "print") [ str ] | ("PushFP" | "pushFP") int [ str ] | ("PopFP" | "popFP") [ str ] | ("PushSP" | "pushSP") int [ str ] | ("PopSP" | "popSP") [ str ] | ("Call" | "call") [ str ] | ("Halt" | "halt") [ str ] | ("Pop" | "pop") [ str ] | ("Swap" | "swap") [ str ] | ("SaveEvalStack" | "save") [ str ] | ("RestoreEvalStack" | "restore") [ str ] | ("Noop" | "noop") [ str ]
    def _operation(self):
        if self.current() in {"Label", "lab"}:
            if self.current() in {"Label"}:
                self.match("Label")
            elif self.current() in {"lab"}:
                self.match("lab")
            else:
                self.error("syntax error")
                assert False
            label = self._str()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Label(label, comment)
        elif self.current() in {"Jump", "j"}:
            if self.current() in {"Jump"}:
                self.match("Jump")
            elif self.current() in {"j"}:
                self.match("j")
            else:
                self.error("syntax error")
                assert False
            label = self._str()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Jump(label, comment)
        elif self.current() in {"JumpIfZero", "jz"}:
            if self.current() in {"JumpIfZero"}:
                self.match("JumpIfZero")
            elif self.current() in {"jz"}:
                self.match("jz")
            else:
                self.error("syntax error")
                assert False
            label = self._str()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.JumpIfZero(label, comment)
        elif self.current() in {"JumpIfNotZero", "jnz"}:
            if self.current() in {"JumpIfNotZero"}:
                self.match("JumpIfNotZero")
            elif self.current() in {"jnz"}:
                self.match("jnz")
            else:
                self.error("syntax error")
                assert False
            label = self._str()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.JumpIfNotZero(label, comment)
        elif self.current() in {"JumpIndirect", "ji"}:
            if self.current() in {"JumpIndirect"}:
                self.match("JumpIndirect")
            elif self.current() in {"ji"}:
                self.match("ji")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.JumpIndirect(comment)
        elif self.current() in {"PushImmediate", "push"}:
            if self.current() in {"PushImmediate"}:
                self.match("PushImmediate")
            elif self.current() in {"push"}:
                self.match("push")
            else:
                self.error("syntax error")
                assert False
            value = self._int()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.PushImmediate(value, comment)
        elif self.current() in {"PushLabel", "pushl"}:
            if self.current() in {"PushLabel"}:
                self.match("PushLabel")
            elif self.current() in {"pushl"}:
                self.match("pushl")
            else:
                self.error("syntax error")
                assert False
            label = self._str()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.PushLabel(label, comment)
        elif self.current() in {"Add", "add"}:
            if self.current() in {"Add"}:
                self.match("Add")
            elif self.current() in {"add"}:
                self.match("add")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Add(comment)
        elif self.current() in {"Sub", "sub"}:
            if self.current() in {"Sub"}:
                self.match("Sub")
            elif self.current() in {"sub"}:
                self.match("sub")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Sub(comment)
        elif self.current() in {"Mul", "mul"}:
            if self.current() in {"Mul"}:
                self.match("Mul")
            elif self.current() in {"mul"}:
                self.match("mul")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Mul(comment)
        elif self.current() in {"Div", "div"}:
            if self.current() in {"Div"}:
                self.match("Div")
            elif self.current() in {"div"}:
                self.match("div")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Div(comment)
        elif self.current() in {"Negate", "neg"}:
            if self.current() in {"Negate"}:
                self.match("Negate")
            elif self.current() in {"neg"}:
                self.match("neg")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Negate(comment)
        elif self.current() in {"LessThan", "lt"}:
            if self.current() in {"LessThan"}:
                self.match("LessThan")
            elif self.current() in {"lt"}:
                self.match("lt")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.LessThan(comment)
        elif self.current() in {"GreaterThan", "gt"}:
            if self.current() in {"GreaterThan"}:
                self.match("GreaterThan")
            elif self.current() in {"gt"}:
                self.match("gt")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.GreaterThan(comment)
        elif self.current() in {"LessThanEqual", "leq"}:
            if self.current() in {"LessThanEqual"}:
                self.match("LessThanEqual")
            elif self.current() in {"leq"}:
                self.match("leq")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.LessThanEqual(comment)
        elif self.current() in {"GreaterThanEqual", "geq"}:
            if self.current() in {"GreaterThanEqual"}:
                self.match("GreaterThanEqual")
            elif self.current() in {"geq"}:
                self.match("geq")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.GreaterThanEqual(comment)
        elif self.current() in {"Equal", "eq"}:
            if self.current() in {"Equal"}:
                self.match("Equal")
            elif self.current() in {"eq"}:
                self.match("eq")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Equal(comment)
        elif self.current() in {"NotEqual", "neq"}:
            if self.current() in {"NotEqual"}:
                self.match("NotEqual")
            elif self.current() in {"neq"}:
                self.match("neq")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.NotEqual(comment)
        elif self.current() in {"Not", "not"}:
            if self.current() in {"Not"}:
                self.match("Not")
            elif self.current() in {"not"}:
                self.match("not")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Not(comment)
        elif self.current() in {"Load", "ld"}:
            if self.current() in {"Load"}:
                self.match("Load")
            elif self.current() in {"ld"}:
                self.match("ld")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Load(comment)
        elif self.current() in {"Store", "st"}:
            if self.current() in {"Store"}:
                self.match("Store")
            elif self.current() in {"st"}:
                self.match("st")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Store(comment)
        elif self.current() in {"Print", "print"}:
            if self.current() in {"Print"}:
                self.match("Print")
            elif self.current() in {"print"}:
                self.match("print")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Print(comment)
        elif self.current() in {"PushFP", "pushFP"}:
            if self.current() in {"PushFP"}:
                self.match("PushFP")
            elif self.current() in {"pushFP"}:
                self.match("pushFP")
            else:
                self.error("syntax error")
                assert False
            offset = self._int()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.PushFP(offset, comment)
        elif self.current() in {"PopFP", "popFP"}:
            if self.current() in {"PopFP"}:
                self.match("PopFP")
            elif self.current() in {"popFP"}:
                self.match("popFP")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.PopFP(comment)
        elif self.current() in {"PushSP", "pushSP"}:
            if self.current() in {"PushSP"}:
                self.match("PushSP")
            elif self.current() in {"pushSP"}:
                self.match("pushSP")
            else:
                self.error("syntax error")
                assert False
            offset = self._int()
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.PushSP(offset, comment)
        elif self.current() in {"PopSP", "popSP"}:
            if self.current() in {"PopSP"}:
                self.match("PopSP")
            elif self.current() in {"popSP"}:
                self.match("popSP")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.PopSP(comment)
        elif self.current() in {"Call", "call"}:
            if self.current() in {"Call"}:
                self.match("Call")
            elif self.current() in {"call"}:
                self.match("call")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Call(comment)
        elif self.current() in {"Halt", "halt"}:
            if self.current() in {"Halt"}:
                self.match("Halt")
            elif self.current() in {"halt"}:
                self.match("halt")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Halt(comment)
        elif self.current() in {"Pop", "pop"}:
            if self.current() in {"Pop"}:
                self.match("Pop")
            elif self.current() in {"pop"}:
                self.match("pop")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Pop(comment)
        elif self.current() in {"Swap", "swap"}:
            if self.current() in {"Swap"}:
                self.match("Swap")
            elif self.current() in {"swap"}:
                self.match("swap")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Swap(comment)
        elif self.current() in {"SaveEvalStack", "save"}:
            if self.current() in {"SaveEvalStack"}:
                self.match("SaveEvalStack")
            elif self.current() in {"save"}:
                self.match("save")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.SaveEvalStack(comment)
        elif self.current() in {"RestoreEvalStack", "restore"}:
            if self.current() in {"RestoreEvalStack"}:
                self.match("RestoreEvalStack")
            elif self.current() in {"restore"}:
                self.match("restore")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.RestoreEvalStack(comment)
        elif self.current() in {"Noop", "noop"}:
            if self.current() in {"Noop"}:
                self.match("Noop")
            elif self.current() in {"noop"}:
                self.match("noop")
            else:
                self.error("syntax error")
                assert False
            comment = None
            if self.current() in {"STR"}:
                comment = self._str()
            _operation_ = vm.Noop(comment)
        else:
            self.error("syntax error")
            assert False
        return _operation_

    # str -> STR
    def _str(self):
        tok = self.match("STR")
        _str_ = tok.value
        return _str_

    # int -> INT
    def _int(self):
        tok = self.match("INT")
        _int_ = int(tok.value)
        return _int_
