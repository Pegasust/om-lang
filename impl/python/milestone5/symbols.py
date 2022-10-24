import typing


class Type:
    def __eq__(self, other: "Type") -> bool:
        assert False, "not implemented"
    def __repr__(self):
        return f"{self.__class__.__name__}()"


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
    
    def __repr__(self):
        return f"ArrayType({self.element_type})"


class PhonyType(Type):
    def __eq__(self, other: Type) -> bool:
        return isinstance(other, PhonyType)


class FuncType(Type):
    def __init__(self, params, ret):
        self.params: list[Type] = params
        self.ret: Type = ret

    def __eq__(self, other: Type) -> bool:
        return (
            isinstance(other, FuncType)
            and self.params == other.params
            and self.ret == other.ret
        )

    def __repr__(self):
        return f"FuncType({self.params}=>{self.ret})"


class Symbol:
    def __eq__(self, other: "Symbol") -> bool:
        assert False, f"not implemented for {type(self)}"

    def set_type(self, t: Type) -> None:
        assert False, f"not implemented for {type(self)}"

    def get_type(self) -> Type:
        assert False, f"not implemented for {type(self)}"


class IdSymbol(Symbol):
    def __init__(self, name: str, scope: "Scope"):
        self.name: str = name
        self.scope: Scope = scope
        self.semantic_type: Type = PhonyType()

    def set_type(self, t: Type):
        self.semantic_type = t

    def get_type(self) -> Type:
        return self.semantic_type

    def __eq__(self, other: "Symbol") -> bool:
        # print(f"IdSymbol.__eq__: {self}, {other}")
        # same_instance = isinstance(other, IdSymbol)
        # same_name = self.name == other.name
        # same_depth = self.scope.depth() == other.scope.depth()
        # print(f"{same_instance=} {same_name=} {same_depth=}")
        return (
            isinstance(other, IdSymbol)
            and self.name == other.name
            # and self.semantic_type == other.semantic_type
            and self.scope.depth() == other.scope.depth()
            # and self.scope == other.scope # not checked to avoid infinite recursion
        )

    def __repr__(self):
        return f"Symbol({self.name}, {self.semantic_type}, " + \
            f"({self.scope.depth()}): {self.scope})"


class PhonySymbol(Symbol):
    def __init__(self):
        pass

    def __eq__(self, other: "Symbol") -> bool:
        return isinstance(other, PhonySymbol)


class Scope:
    symtab: dict[str, Symbol]
    parent: typing.Optional["Scope"]

    def lookup(self, name: str) -> Symbol | None:
        if name in self.symtab:
            return self.symtab[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def set_return_type(self, t: Type) -> None:
        assert False, f"not implemented for {type(self)}"

    def get_return_type(self) -> Type:
        assert False, f"not implemented for {type(self)}"

    def __eq__(self, other: "Scope") -> bool:
        assert False, f"not implemented for {type(self)}"

    def depth(self) -> int:
        if self.parent:
            return self.parent.depth() + 1
        return 0

    def parent_fmt(self):
        def parent_gen():
            parent = self.parent
            while parent is not None:
                yield parent
                parent = parent.parent
        return f"({self.depth()}: {list((p.__class__.__name__, len(p.symtab)) for p in parent_gen())})"

    def __repr__(self):
        return f"{self.__class__.__name__}(syms: ({len(self.symtab)}), parent: {self.parent_fmt()})"


# holds parameters and return type
class FuncScope(Scope):
    def __init__(self, parent):
        self.symtab = {}
        self.parent = parent
        self.ret_type: Type = PhonyType()

    def get_return_type(self) -> Type:
        return self.ret_type

    def set_return_type(self, t: Type) -> None:
        self.ret_type = t

    def __eq__(self, other: Scope) -> bool:
        # print(f"FuncScope.__eq__: {self}, {other}")
        return (
            isinstance(other, FuncScope)
            and self.symtab == other.symtab
            and self.parent == other.parent
            and self.ret_type == other.ret_type
        )

    def __repr__(self):
        ret_type = f"{self.ret_type})"
        syms = f"syms: ({len(self.symtab)})"
        def parent_gen():
            parent = self.parent
            while parent is not None:
                yield parent
                parent = parent.parent
        return f"FuncScope({syms}, {self.parent_fmt()}; ->{ret_type}"

# holds symbols in compound statement
class LocalScope(Scope):
    def __init__(self, parent):
        self.parent: Scope = parent
        self.symtab: dict[str, Symbol] = {}

    def get_return_type(self) -> Type:
        return self.parent.get_return_type()

    def __eq__(self, other: Scope) -> bool:
        # print(f"LocalScope.__eq__: {self}, {other}")
        return (
            isinstance(other, LocalScope)
            and self.symtab == other.symtab
            and self.parent == other.parent
        )


# holds global symbols
class GlobalScope(Scope):
    def __init__(self):
        self.symtab: dict[str, Symbol] = {}
        self.parent = None

    def get_return_type(self) -> Type:  # should never be called
        assert False, "bad call to get_return_type()"

    def __eq__(self, other: Scope) -> bool:
        # print(f"GlobalScope.__eq__: {self}, {other}")
        return isinstance(other, GlobalScope) and self.symtab == other.symtab


class PhonyScope(Scope):
    def __init__(self):
        self.symtab: dict[str, Symbol] = {}
        self.parent = None

    def get_return_type(self) -> Type:  # should never be called
        assert False, "bad call to get_return_type()"

    def __eq__(self, other: Scope) -> bool:
        # print(f"PhonyScope.__eq__: {self}, {other}")
        return isinstance(other, PhonyScope) and self.symtab == other.symtab
