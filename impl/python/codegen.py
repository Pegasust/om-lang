import asts
import symbols
import itertools
from vm import (
    Equal,
    Insn,
    NotEqual,
    RestoreEvalStack,
    SaveEvalStack,
    Store,
    Print,
    Label,
    Jump,
    Add,
    Mul,
    Sub,
    Div,
    LessThan,
    LessThanEqual,
    GreaterThan,
    GreaterThanEqual,
    JumpIfNotZero,
    JumpIfZero,
    Load,
    PushFP,
    PushImmediate,
    PushSP,
    PushLabel,
    Negate,
    Not,
    Pop,
    PopFP,
    PopSP,
    JumpIndirect,
    Call,
    Halt,
    Noop,
    Swap,
)


# This is the entry point for the visitor.
def generate(ast: asts.Program) -> list[Insn]:
    return _Program(ast)


def _Program(ast: asts.Program) -> list[Insn]:
    return list(itertools.chain.from_iterable(_FuncDecl(decl)
                                              for decl in ast.decls))
    # for decl in ast.decls:
    #     f: list[Insn] = _FuncDecl(decl)
    # pass


def _Stmt(ast: asts.Stmt) -> list[Insn]:
    if isinstance(ast, asts.AssignStmt):
        return _AssignStmt(ast)
    elif isinstance(ast, asts.IfStmt):
        return _IfStmt(ast)
    elif isinstance(ast, asts.WhileStmt):
        return _WhileStmt(ast)
    elif isinstance(ast, asts.CallStmt):
        return _CallStmt(ast)
    elif isinstance(ast, asts.CompoundStmt):
        return _CompoundStmt(ast)
    elif isinstance(ast, asts.PrintStmt):
        return _PrintStmt(ast)
    elif isinstance(ast, asts.ReturnStmt):
        return _ReturnStmt(ast)
    else:
        assert False, f"_Stmt() not implemented for {type(ast)}"


def rval_CallExpr(ast: asts.CallExpr) -> list[Insn]:
    assert isinstance(ast.fn, asts.IdExpr)
    for i, arg in enumerate(ast.args):
        pass  # handle arg
    # handle return value


def _AssignStmt(ast: asts.AssignStmt) -> list[Insn]:
    # handle ast.lhs
    # handle ast.rhs
    pass


def _PrintStmt(ast: asts.PrintStmt) -> list[Insn]:
    # handle ast.expr
    pass


def _IfStmt(ast: asts.IfStmt) -> list[Insn]:
    # handle ast.expr
    # handle ast.thenStmt
    # handle ast.elseStmt
    pass


def _WhileStmt(ast: asts.WhileStmt) -> list[Insn]:
    # handle ast.expr
    # handle ast.stmt
    pass


def control(e: asts.Expr, label: str, sense: bool) -> list[Insn]:
    match e:
        case asts.BinaryOp():
            return control_BinaryOp(e, label, sense)
        case asts.UnaryOp():
            return control_UnaryOp(e, label, sense)
        case asts.TrueLiteral():
            pass
        case asts.FalseLiteral():
            pass
        case _:
            # handle other control expressions
            pass
    pass


def control_BinaryOp(e: asts.BinaryOp, label: str, sense: bool) -> list[Insn]:
    match e.op.kind:
        case "and":
            pass
        case "or":
            pass
        case _:
            # handle other control binary operators
            pass
    pass


def control_UnaryOp(e: asts.UnaryOp, label: str, sense: bool) -> list[Insn]:
    match e.op.kind:
        case "not":
            pass
        case _:
            assert False, f"control_UnaryOp() not implemented for {e.op.kind}"
    pass


def _CallStmt(ast: asts.CallStmt) -> list[Insn]:
    # handle ast.call
    pass


def _CompoundStmt(ast: asts.CompoundStmt) -> list[Insn]:
    for stmt in ast.stmts:
        pass
    if ast.return_stmt is not None:
        pass
    pass


def _FuncDecl(ast: asts.FuncDecl):
    # handle ast.id
    # handle ast.body
    pass


def _ReturnStmt(ast: asts.ReturnStmt) -> list[Insn]:
    # handle ast.expr
    pass


def lval(e: asts.Expr) -> list[Insn]:
    match e:
        case asts.IdExpr():
            return lval_id(e)
        case asts.ArrayCell():
            return lval_array_cell(e)
        case _:
            assert False, f"lval() not implemented for {type(e)}"
    pass


def lval_id(e: asts.IdExpr) -> list[Insn]:
    # handle e.id
    pass


def lval_array_cell(e: asts.ArrayCell) -> list[Insn]:
    assert False, "Arrays are not part of codegen in CSC 453"


def rval(e: asts.Expr) -> list[Insn]:
    match e:
        case asts.BinaryOp():
            return rval_BinaryOp(e)
        case asts.UnaryOp():
            return rval_UnaryOp(e)
        case asts.CallExpr():
            return rval_CallExpr(e)
        case asts.IdExpr():
            pass
        case asts.ArrayCell(arr, idx):
            pass
        case asts.IntLiteral():
            pass
        case asts.TrueLiteral():
            pass
        case asts.FalseLiteral():
            pass
        case _:
            assert False, f"rval() not implemented for {type(e)}"


def rval_BinaryOp(e: asts.BinaryOp) -> list[Insn]:
    match e.op.kind:
        case "+":
            pass
        case "-":
            pass
        case "*":
            pass
        case "/":
            pass
        case "<":
            pass
        case "<=":
            pass
        case ">":
            pass
        case ">=":
            pass
        case "==":
            pass
        case "!=":
            pass
        case "and":
            return rval_and(e)
        case "or":
            return rval_or(e)
        case _:
            assert False, f"rval_BinaryOp() not implemented for {e.op}"
    pass


def rval_UnaryOp(e: asts.UnaryOp) -> list[Insn]:
    match e.op.kind:
        case "-":
            pass
        case "not":
            pass
        case _:
            assert False, f"rval_UnaryOp() not implemented for {e.op}"
    pass


def rval_and(e: asts.BinaryOp) -> list[Insn]:
    pass


def rval_or(e: asts.BinaryOp) -> list[Insn]:
    pass
