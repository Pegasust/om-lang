import typing


class Type:
    def __eq__(self, other: "Type") -> bool:
        assert False, "not implemented"


class VoidType(Type):
    def __eq__(self, other: Type) -> bool:
        return isinstance(other, VoidType)


class IntType(Type):
    def __eq__(self, other: Type) -> bool:
        return isinstance(other, IntType)


class BoolType(Type):
    def __eq__(self, other: Type) -> bool:
        return isinstance(other, BoolType)


class ArrayType(Type):
    def __init__(self, element_type: Type):
        self.element_type: Type = element_type

    def __eq__(self, other: Type) -> bool:
        if isinstance(other, ArrayType):
            return self.element_type == other.element_type
        return False


class PhonyType(Type):
    def __eq__(self, other: Type) -> bool:
        assert False, "not implemented"


class FuncType(Type):
    def __init__(self, params, ret):
        self.params: list[Type] = params
        self.ret: Type = ret

    def __eq__(self, other: Type) -> bool:
        if isinstance(other, FuncType):
            if len(self.params) != len(other.params):
                return False
            for i in range(len(self.params)):
                if not self.params[i] == other.params[i]:
                    return False
            return self.ret == other.ret
        return False


class Symbol:
    def __init__(self, name: str, type: Type, scope: "Scope"):
        self.name: str = name
        self.semantic_type: Type = type
        self.scope: Scope = scope

    def __repr__(self):
        return "Symbol(%r, %r)" % (self.name, self.semantic_type)


class Scope:
    symtab: dict[str, Symbol]
    parent: typing.Optional["Scope"]

    def lookup(self, name: str) -> Symbol | None:
        if name in self.symtab:
            return self.symtab[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def get_return_type(self) -> Type:
        assert False, "not implemented"


# holds parameters and return type
class FuncScope(Scope):
    def __init__(self, parent):
        self.symtab = {}
        self.parent = parent
        self.ret_type: Type = PhonyType()

    def get_return_type(self) -> Type:
        return self.ret_type


# holds symbols in compound statement
class LocalScope(Scope):
    def __init__(self, parent):
        self.parent: Scope = parent
        self.symtab: dict[str, Symbol] = {}

    def get_return_type(self) -> Type:
        return self.parent.get_return_type()


# holds global symbols
class GlobalScope(Scope):
    def __init__(self):
        self.symtab: dict[str, Symbol] = {}
        self.parent = None

    def get_return_type(self) -> Type:  # should never be called
        assert False, "bad call to get_return_type()"


class PhonyScope(Scope):
    def __init__(self):
        self.symtab: dict[str, Symbol] = {}
        self.parent = None

    def get_return_type(self) -> Type:  # should never be called
        assert False, "bad call to get_return_type()"
