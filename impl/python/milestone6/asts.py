# DO NOT EDIT THIS FILE

from typing import Optional, Callable

from tokens import Token, Coord
import symbols

i4 = " " * 4


class AST:
    def pprint(self, indent: str):
        assert False, f"AST.pprint() not implemented for {type(self)}"

    def __eq__(self, other) -> bool:
        return self.compare(other, lambda a, b: True)

    def __repr__(self) -> str:
        assert False, f"AST.__repr__() not implemented for {type(self)}"

    def compare(self, other: "AST", fn: Callable[["AST", "AST"], bool]) -> bool:
        assert False, f"AST.compare() not implemented for {type(self)}"

    def same_symbols(self, other: "AST") -> bool:
        def fn(a: AST, b: AST) -> bool:
            if isinstance(a, Id) and isinstance(b, Id):
                return a.symbol == b.symbol
            return True

        return self.compare(other, fn)

    def same_types(self, other: "AST") -> bool:
        def fn(a: AST, b: AST) -> bool:
            if (isinstance(a, Type) or isinstance(a, Decl) or isinstance(a, Expr)) and (
                isinstance(b, Type) or isinstance(b, Decl) or isinstance(b, Expr)
            ):
                return a.semantic_type == b.semantic_type
            return True

        return self.compare(other, fn)


class Program(AST):
    def __init__(self, decls: list["FuncDecl"]):
        self.decls: list["FuncDecl"] = decls

    def pprint(self, indent: str):
        print(indent + "Program")
        for decl in self.decls:
            decl.pprint(indent + i4)

    def __repr__(self):
        return f"Program({self.decls})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, Program)
            and fn(self, other)
            and len(self.decls) == len(other.decls)
            and all(
                self.decls[i].compare(other.decls[i], fn)
                for i in range(len(self.decls))
            )
        )


class Id(AST):
    def __init__(self, token: Token):
        self.token = token
        self.symbol: symbols.Symbol = symbols.PhonySymbol()
        self.semantic_type: symbols.Type = symbols.PhonyType()

    def pprint(self, indent: str):
        print(indent + f"Id({self.token}, {self.semantic_type})")

    def __repr__(self):
        return f"Id({self.token.__repr__()}, {self.symbol}, {self.semantic_type})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return isinstance(other, Id) and fn(self, other) and self.token == other.token


class Type(AST):
    semantic_type: symbols.Type = symbols.PhonyType()


class Decl(AST):
    semantic_type: symbols.Type = symbols.PhonyType()


class VarDecl(Decl):
    def __init__(self, id: Id, type: Type):
        self.id = id
        self.type_ast: Type = type

    def pprint(self, indent: str):
        print(indent + f"VarDecl {self.semantic_type}")
        self.id.pprint(indent + i4)
        self.type_ast.pprint(indent + i4)

    def __repr__(self):
        return f"VarDecl({self.id}, {self.type_ast})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, VarDecl)
            and fn(self, other)
            and self.id.compare(other.id, fn)
            and self.type_ast.compare(other.type_ast, fn)
        )


class ParamDecl(Decl):
    def __init__(self, id: Id, type: Type):
        self.id = id
        self.type_ast: Type = type

    def pprint(self, indent: str):
        print(indent + f"ParamDecl {self.semantic_type}")
        self.id.pprint(indent + i4)
        self.type_ast.pprint(indent + i4)

    def __repr__(self):
        return f"ParamDecl({self.id}, {self.type_ast})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, ParamDecl)
            and fn(self, other)
            and self.id.compare(other.id, fn)
            and self.type_ast.compare(other.type_ast, fn)
        )


class IntType(Type):
    def __init__(self, token: Token):
        self.token: Token = token

    def pprint(self, indent: str):
        print(indent + "IntType")

    def __repr__(self):
        return f"IntType({self.token.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, IntType) and fn(self, other) and self.token == other.token
        )


class BoolType(Type):
    def __init__(self, token: Token):
        self.token: Token = token

    def pprint(self, indent: str):
        print(indent + "BoolType")

    def __repr__(self):
        return f"BoolType({self.token.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, BoolType)
            and fn(self, other)
            and self.token == other.token
        )


class ArrayType(Type):
    def __init__(self, size: Optional["Expr"], type: Type):
        self.size: Optional["Expr"] = size
        self.element_type_ast: Type = type

    def pprint(self, indent: str):
        print(indent + "ArrayType")
        if self.size is not None:
            self.size.pprint(indent + i4)
        self.element_type_ast.pprint(indent + i4)

    def __repr__(self):
        return f"ArrayType({self.size}, {self.element_type_ast})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, ArrayType)
            and fn(self, other)
            and (
                (self.size is None and other.size is None)
                or (
                    self.size is not None
                    and other.size is not None
                    and self.size.compare(other.size, fn)
                )
            )
            and self.element_type_ast.compare(other.element_type_ast, fn)
        )


class Stmt(AST):
    pass


class PrintStmt(Stmt):
    def __init__(self, expr: "Expr"):
        self.expr: Expr = expr

    def pprint(self, indent: str):
        print(indent + "Print")
        self.expr.pprint(indent + i4)

    def __repr__(self):
        return f"PrintStmt({self.expr})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, PrintStmt)
            and fn(self, other)
            and self.expr.compare(other.expr, fn)
        )


class CompoundStmt(Stmt):
    def __init__(
        self,
        decls: list[VarDecl],
        stmts: list[Stmt],
        return_stmt: Optional["ReturnStmt"],
    ):
        self.decls: list[VarDecl] = decls
        self.stmts: list[Stmt] = stmts
        self.return_stmt: Optional[ReturnStmt] = return_stmt
        self.local_scope: symbols.Scope = symbols.PhonyScope()

    def pprint(self, indent: str):
        ret_type = self.return_stmt.expr.semantic_type if self.return_stmt and \
            self.return_stmt.expr else symbols.VoidType()
        print(indent + f"CompoundStmt [{self.local_scope}]>{ret_type}")
        for decl in self.decls:
            decl.pprint(indent + i4)
        for stmt in self.stmts:
            stmt.pprint(indent + i4)
        if self.return_stmt is not None:
            self.return_stmt.pprint(indent + i4)

    def __repr__(self):
        return f"CompoundStmt({self.decls}, {self.stmts}, {self.return_stmt}, {self.local_scope})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, CompoundStmt)
            and fn(self, other)
            and len(self.decls) == len(other.decls)
            and all(
                self.decls[i].compare(other.decls[i], fn)
                for i in range(len(self.decls))
            )
            and len(self.stmts) == len(other.stmts)
            and all(
                self.stmts[i].compare(other.stmts[i], fn)
                for i in range(len(self.stmts))
            )
            and (
                (self.return_stmt is None and other.return_stmt is None)
                or (
                    self.return_stmt is not None
                    and other.return_stmt is not None
                    and self.return_stmt.compare(other.return_stmt, fn)
                )
            )
        )


class FuncDecl(AST):
    def __init__(
        self,
        id: Id,
        params: list[ParamDecl],
        ret_type_ast: Optional[Type],
        body: CompoundStmt,
    ):
        self.id = id
        self.params: list[ParamDecl] = params
        self.ret_type_ast: Optional[Type] = ret_type_ast
        self.body: CompoundStmt = body
        self.func_scope: symbols.Scope = symbols.PhonyScope()

    def pprint(self, indent: str):
        print(indent + f"FuncDecl [{self.func_scope}]")
        self.id.pprint(indent + i4)
        for param in self.params:
            param.pprint(indent + i4)
        if self.ret_type_ast is not None:
            self.ret_type_ast.pprint(indent + i4)
        self.body.pprint(indent + i4)

    def __repr__(self):
        return f"FuncDecl({self.id}, {self.params}, {self.ret_type_ast}, {self.body}, {self.func_scope})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, FuncDecl)
            and fn(self, other)
            and self.id.compare(other.id, fn)
            and len(self.params) == len(other.params)
            and all(
                self.params[i].compare(other.params[i], fn)
                for i in range(len(self.params))
            )
            and (
                (self.ret_type_ast is None and other.ret_type_ast is None)
                or (
                    self.ret_type_ast is not None
                    and other.ret_type_ast is not None
                    and self.ret_type_ast.compare(other.ret_type_ast, fn)
                )
            )
            and self.body.compare(other.body, fn)
        )


class Expr(AST):
    semantic_type: symbols.Type = symbols.PhonyType()


class CallExpr(Expr):
    def __init__(self, fn: Expr, args: list[Expr], coord: Coord):
        self.fn: Expr = fn
        self.args: list[Expr] = args
        self.coord: Coord = coord

    def pprint(self, indent: str):
        print(indent + f"CallExpr->{self.semantic_type}")
        self.fn.pprint(indent + i4)
        for arg in self.args:
            arg.pprint(indent + i4)

    def __repr__(self):
        return f"CallExpr({self.fn}, {self.args}, {self.coord.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, CallExpr)
            and fn(self, other)
            and self.fn.compare(other.fn, fn)
            and len(self.args) == len(other.args)
            and all(
                self.args[i].compare(other.args[i], fn) for i in range(len(self.args))
            )
        )


class AssignStmt(Stmt):
    def __init__(self, lhs: Expr, rhs: Expr, token):
        self.lhs: Expr = lhs
        self.rhs: Expr = rhs
        self.token: Token = token

    def pprint(self, indent: str):
        print(indent + "AssignStmt")
        self.lhs.pprint(indent + i4)
        self.rhs.pprint(indent + i4)

    def __repr__(self):
        return f"AssignStmt({self.lhs}, {self.rhs}, {self.token.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, AssignStmt)
            and fn(self, other)
            and self.lhs.compare(other.lhs, fn)
            and self.rhs.compare(other.rhs, fn)
        )


class IfStmt(Stmt):
    def __init__(
        self,
        expr: Expr,
        thenStmt: CompoundStmt,
        elseStmt: Optional[CompoundStmt],
        coord: Coord,
    ):
        self.expr: Expr = expr
        self.thenStmt: CompoundStmt = thenStmt
        self.elseStmt: Optional[CompoundStmt] = elseStmt
        self.coord: Coord = coord

    def pprint(self, indent: str):
        print(indent + "IfStmt")
        self.expr.pprint(indent + i4)
        self.thenStmt.pprint(indent + i4)
        if self.elseStmt is not None:
            self.elseStmt.pprint(indent + i4)

    def __repr__(self):
        return f"IfStmt({self.expr}, {self.thenStmt}, {self.elseStmt}, {self.coord.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, IfStmt)
            and fn(self, other)
            and self.expr.compare(other.expr, fn)
            and self.thenStmt.compare(other.thenStmt, fn)
            and (
                (self.elseStmt is None and other.elseStmt is None)
                or (
                    self.elseStmt is not None
                    and other.elseStmt is not None
                    and self.elseStmt.compare(other.elseStmt, fn)
                )
            )
        )


class WhileStmt(Stmt):
    def __init__(self, expr: Expr, stmt: CompoundStmt, coord: Coord):
        self.expr: Expr = expr
        self.stmt: CompoundStmt = stmt
        self.coord: Coord = coord

    def pprint(self, indent: str):
        print(indent + "WhileStmt")
        self.expr.pprint(indent + i4)
        self.stmt.pprint(indent + i4)

    def __repr__(self):
        return f"WhileStmt({self.expr}, {self.stmt}, {self.coord.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, WhileStmt)
            and fn(self, other)
            and self.expr.compare(other.expr, fn)
            and self.stmt.compare(other.stmt, fn)
        )


class CallStmt(Stmt):
    def __init__(self, call: CallExpr):
        self.call: CallExpr = call

    def pprint(self, indent: str):
        print(indent + "CallStmt")
        self.call.pprint(indent + i4)

    def __repr__(self):
        return f"CallStmt({self.call})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return isinstance(other, CallStmt) and self.call.compare(other.call, fn)


class ReturnStmt(Stmt):
    def __init__(self, expr: Optional[Expr], coord: Coord):
        self.expr: Optional[Expr] = expr
        self.coord: Coord = coord
        self.enclosing_scope: symbols.Scope = symbols.PhonyScope()

    def pprint(self, indent: str):
        semtype = symbols.VoidType() if not self.expr else self.expr.semantic_type
        print(indent + f"ReturnStmt -> {semtype}")
        if self.expr is not None:
            self.expr.pprint(indent + i4)

    def __repr__(self):
        return f"ReturnStmt({self.expr}, {self.coord.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, ReturnStmt)
            and fn(self, other)
            and (
                (self.expr is None and other.expr is None)
                or (
                    self.expr is not None
                    and other.expr is not None
                    and self.expr.compare(other.expr, fn)
                )
            )
        )


class BinaryOp(Expr):
    def __init__(self, op: Token, left: Expr, right: Expr):
        self.op: Token = op
        self.left: Expr = left
        self.right: Expr = right

    def pprint(self, indent: str):
        print(indent + f"BinaryOp({self.op}) ->{self.semantic_type}")
        self.left.pprint(indent + i4)
        self.right.pprint(indent + i4)

    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, BinaryOp)
            and fn(self, other)
            and self.op == other.op
            and self.left.compare(other.left, fn)
            and self.right.compare(other.right, fn)
        )


class UnaryOp(Expr):
    def __init__(self, op: Token, expr: Expr):
        self.op: Token = op
        self.expr: Expr = expr

    def pprint(self, indent: str):
        print(indent + f"UnaryOp({self.op}) -> {self.semantic_type}")
        self.expr.pprint(indent + i4)

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.expr} ->{self.semantic_type})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, UnaryOp)
            and fn(self, other)
            and self.op == other.op
            and self.expr.compare(other.expr, fn)
        )


class ArrayCell(Expr):
    def __init__(self, arr: Expr, idx: Expr, coord: Coord):
        self.arr: Expr = arr
        self.idx: Expr = idx
        self.coord: Coord = coord

    def pprint(self, indent: str):
        print(indent + f"ArrayCell -> {self.semantic_type}")
        self.arr.pprint(indent + i4)
        self.idx.pprint(indent + i4)

    def __repr__(self):
        return f"ArrayCell({self.arr}, {self.idx}, {self.coord.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, ArrayCell)
            and fn(self, other)
            and self.arr.compare(other.arr, fn)
            and self.idx.compare(other.idx, fn)
        )


class IntLiteral(Expr):
    def __init__(self, token: Token):
        self.token: Token = token

    def pprint(self, indent: str):
        print(indent + f"IntLiteral({self.token}) -> {self.semantic_type}")

    def __repr__(self):
        return f"IntLiteral({self.token.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, IntLiteral)
            and fn(self, other)
            and self.token == other.token
        )


class TrueLiteral(Expr):
    def __init__(self, token: Token):
        self.token: Token = token

    def pprint(self, indent: str):
        print(indent + f"TrueLiteral -> {self.semantic_type}")

    def __repr__(self):
        return f"TrueLiteral({self.token.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, TrueLiteral)
            and fn(self, other)
            and self.token == other.token
        )


class FalseLiteral(Expr):
    def __init__(self, token: Token):
        self.token: Token = token

    def pprint(self, indent: str):
        print(indent + f"FalseLiteral -> {self.semantic_type}")

    def __repr__(self):
        return f"FalseLiteral({self.token.__repr__()})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, FalseLiteral)
            and fn(self, other)
            and self.token == other.token
        )


class IdExpr(Expr):
    def __init__(self, id: Id):
        self.id = id

    def pprint(self, indent: str):
        print(indent + f"IdExpr->{self.semantic_type}")
        self.id.pprint(indent + i4)

    def __repr__(self):
        return f"IdExpr({self.id}: {self.semantic_type})"

    def compare(self, other: AST, fn: Callable[[AST, AST], bool]) -> bool:
        return (
            isinstance(other, IdExpr)
            and fn(self, other)
            and self.id.compare(other.id, fn)
        )
