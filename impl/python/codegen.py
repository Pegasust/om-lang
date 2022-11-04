from typing import Optional, TypeVar, Iterable, Union
import error
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

BAIL = 1
NO_BAIL = 0


T = TypeVar('T')


def flatten_list(list_iter: Iterable[Iterable[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(list_iter))


# This is the entry point for the visitor.
def generate(ast: asts.Program) -> list[Insn]:
    return _Program(ast)


def _Program(ast: asts.Program) -> list[Insn]:
    # for decl in ast.decls:
    #     f: list[Insn] = _FuncDecl(decl)
    return flatten_list(_FuncDecl(decl) for decl in ast.decls)


def _Stmt(ast: asts.Stmt, dealloc_label: str) -> list[Insn]:
    if isinstance(ast, asts.AssignStmt):
        return _AssignStmt(ast)
    elif isinstance(ast, asts.IfStmt):
        return _IfStmt(ast, dealloc_label)
    elif isinstance(ast, asts.WhileStmt):
        return _WhileStmt(ast, dealloc_label)
    elif isinstance(ast, asts.CallStmt):
        return _CallStmt(ast)
    elif isinstance(ast, asts.CompoundStmt):
        return _CompoundStmt(ast, dealloc_label)
    elif isinstance(ast, asts.PrintStmt):
        return _PrintStmt(ast)
    elif isinstance(ast, asts.ReturnStmt):
        error.error("ReturnStmt should be handled separately by CompoundStmt",
                    ast.coord)
        # return _ReturnStmt(ast)
    else:
        assert False, f"_Stmt() not implemented for {type(ast)}"


def rval_CallExpr(ast: asts.CallExpr) -> list[Insn]:
    assert isinstance(ast.fn, asts.IdExpr)
    retval = flatten_list(
        rval(arg) for arg in reversed(ast.args)
    )
    # TODO: for register-based machines, maybe call SaveEvalStack on full
    # or allocate the space for the whole program first
    retval.extend(stack_malloc(1)[1])  # ret
    # , SP', FP'. Note that SP not changed
    retval.extend([PushSP(0, "Back up SP"), PushFP(0, "Back up FP")])
    retval.extend(stack_malloc(2)[1])  # the 2 reserving spaces
    retval.append(SaveEvalStack())

    # Assign this FP
    retval.extend([
        PushSP(-4, "Set FP to be at offset 0"),
        PopFP(),
    ])

    # Call the function
    retval.extend(rval(ast.fn))
    retval.append(Call(f"Call {ast.fn.id.token.value}"))

    # Epilogue:
    retval.extend(flatten_list((
        [RestoreEvalStack()],
        # pop the empty elements
        stack_free(3),
        [PopFP("Restore the old FP")],
        # retain the return value as offset-1 from the original stack pointer
        # TODO: This must later be popped out to serve as rval
        stack_emplace(),
        # dealloc all args
        stack_free(len(ast.args)),
        # return value as rval
        stack_pop_retrieve(),
    )))

    return retval


def _lval_offset(sp_offset: int) -> list[Insn]:
    return [PushSP(sp_offset)]


def assign(sp_offset: int, rval_insn: list[Insn]) -> list[Insn]:
    return flatten_list((
        _lval_offset(sp_offset),
        rval_insn,
        [Store()],
    ))


def _AssignStmt(ast: asts.AssignStmt) -> list[Insn]:
    # TODO: Basically this becomes lval
    return flatten_list((
        lval(ast.lhs),
        rval(ast.rhs),
        [Store()],
    ))


def _PrintStmt(ast: asts.PrintStmt) -> list[Insn]:
    # handle ast.expr
    return flatten_list((
        rval(ast.expr),
        [Print()],
    ))


def _IfStmt(ast: asts.IfStmt, parent_dealloc: str) -> list[Insn]:
    # handle ast.expr
    # handle ast.thenStmt
    # handle ast.elseStmt
    pass


def _WhileStmt(ast: asts.WhileStmt, parent_dealloc: str) -> list[Insn]:
    # handle ast.expr
    # handle ast.stmt
    pass


def _ctrl_lit(literal: bool, label: str, sense: bool) -> list[Insn]:
    if literal == sense:
        return [Jump(label)]
    else:
        return []


def control(e: asts.Expr, label: str, sense: bool) -> list[Insn]:
    match e:
        case asts.BinaryOp():
            return control_BinaryOp(e, label, sense)
        case asts.UnaryOp():
            return control_UnaryOp(e, label, sense)
        case asts.TrueLiteral():
            return _ctrl_lit(True, label, sense)
        case asts.FalseLiteral():
            return _ctrl_lit(False, label, sense)
        case asts.IdExpr():
            return control_IdExpr(e, label, sense)
    pass


def control_IdExpr(e: asts.IdExpr, label: str, sense: bool) -> list[Insn]:
    if sense:
        return flatten_list((
            rval(e),
            [JumpIfNotZero(label)]
        ))
    else:
        return flatten_list((
            rval(e),
            [JumpIfZero(label)]
        ))


def _ctrl_bin(left: asts.Expr, right: asts.Expr, op_kind: str, label: str, sense: bool) -> list[Insn]:
    match (op_kind, sense):
        case "and", True:
            return flatten_list((
                ,
            ))
        case "or", True:
            return flatten_list((
                ,
            ))
        case "and", False:
            return _ctrl_bin(left, right, "or", True)
        case "or", False:
            return flatten_list((
                ,
            ))


def control_BinaryOp(e: asts.BinaryOp, label: str, sense: bool) -> list[Insn]:
    match (e.op.kind, sense):
        case "and", False:
            return flatten_list((
                control(e.left, label, False),
            ))
        case "or":
            pass
        case ">":
            pass
        case ">=":
            pass
        case "<":
            pass
        case "<=":
            pass

    pass


def control_UnaryOp(e: asts.UnaryOp, label: str, sense: bool) -> list[Insn]:
    match e.op.kind:
        case "not":
            return control(e.expr, label, not sense)
        case _:
            assert False, f"control_UnaryOp() not implemented for {e.op.kind}"


def _CallStmt(ast: asts.CallStmt) -> list[Insn]:
    # handle ast.call
    # TODO: Disregard return optimization
    return flatten_list((
        rval_CallExpr(ast.call),
        # Disregard return value
        stack_pop()
    ))


def option_unwrap_or(opt: Optional[T], default: T) -> T:
    return opt if opt is not None else default


def stack_malloc(atomic_sz: int) -> tuple[int, list[Insn]]:
    return (atomic_sz, [PushImmediate(0)] * atomic_sz)


def stack_calloc(ty: symbols.Type, elem_cnt: int, imm: Optional[int] = None) \
        -> tuple[int, list[Insn]]:
    atomic_sz = (ty.size() * elem_cnt)
    return (atomic_sz, [PushImmediate(option_unwrap_or(imm, 0))] * atomic_sz)


def stack_free(atomic_sz: int) -> list[Insn]:
    return [Pop()] * atomic_sz


def _CompoundStmt(ast: asts.CompoundStmt, parent_dealloc: str) -> list[Insn]:
    my_dealloc_label = scope_label(ast.local_scope)
    args_size, isns_calloc = stack_malloc(len(ast.decls))

    stmts = (_Stmt(stmt, my_dealloc_label) for stmt in ast.stmts)
    isns_stmts = flatten_list(stmt for stmt in stmts)

    isns_return = _ReturnStmt(ast.return_stmt, my_dealloc_label) \
        if ast.return_stmt else stack_emplace(NO_BAIL)

    isns_dealloc_lab = [Label(my_dealloc_label)]
    isns_dealloc = stack_free(args_size)

    isns_bail = flatten_list((
        stack_pop_retrieve(),
        [
            JumpIfNotZero(parent_dealloc)
        ]
    ))

    return flatten_list((
        isns_calloc,
        isns_stmts,
        isns_return,
        isns_dealloc_lab,
        isns_dealloc,
        isns_bail
    ))


def _FuncDecl(ast: asts.FuncDecl):
    # handle ast.id
    label_instructions = [Label(func_label(ast.id))]
    # handle ast.body
    # ast.params is handled by callee
    func_done = f"{func_label(ast.id)}-bail"
    body_instructions = _CompoundStmt(ast.body, func_done)
    bail_isns = [
        Label(func_done),
        # consume the BAIL status. Guaranteed to have this status
        stack_pop()
    ]
    # Now we're guaranteed to have FP, SP, RA; [[RET]]
    ret_isns = [
        JumpIndirect()
    ]

    return flatten_list((
        label_instructions,
        bail_isns,
        body_instructions,
        ret_isns
    ))


def stack_emplace(imm: Optional[int] = None) -> list[Insn]:
    """
    Moves the value of TOS to SP and increase SP by one
    The original value at TOS is popped by the end of this call
    """

    return flatten_list((
        [] if imm is None else [PushImmediate(imm)],
        [
            PushSP(0, "Push retval to stack"),
            Swap(),
            Store("Assign value of retval to stack"),
            PushSP(1, "Move stack pointer forward to preserve RET"),
            PopSP(),
        ],
    ))


def stack_push() -> list[Insn]:
    """
    Copies the value of TOS to SP and increase SP by one.
    The value of TOS at the end of this call remains the same
    """
    return [
        PushSP(0, "Push retval to stack"),
        Swap(),
        Store("Assign value of retval to stack"),
        PushSP(0, "Prepare to duplicate"),
        Load("Duplicate value back"),
        PushSP(1, "Move stack pointer forward to preserve RET"),
        PopSP()
    ]


def stack_pop_retrieve() -> list[Insn]:
    return [
        PushSP(-1, "Restore RET"),
        Load(),
        PushSP(-1, "Decrement SP to pop RET"),
        PopSP(),
    ]


def stack_pop() -> list[Insn]:
    return [PushSP(-1, "Decrement SP"), PopSP()]


def _ReturnStmt(ast: asts.ReturnStmt, dealloc_label: str) -> list[Insn]:
    if ast.expr is None:
        isns_expr = []
    else:
        # rval and store return value
        isns_expr = rval(ast.expr)
        isns_expr.extend(stack_emplace())

    # mark BAIL
    isns_expr.extend(stack_emplace(BAIL))
    # jump to the dealloc section of the enclosing scope
    isns_expr.extend([
        PushLabel(dealloc_label),
        JumpIndirect()
    ])
    return isns_expr


def lval(e: asts.Expr) -> list[Insn]:
    match e:
        case asts.IdExpr():
            return lval_id(e)
        case asts.ArrayCell():
            return lval_array_cell(e)
        case _:
            assert False, f"lval() not implemented for {type(e)}"


def lval_id(e: asts.IdExpr) -> list[Insn]:
    return [
        PushFP(0),
        PushImmediate(e.id.symbol.offset),
        Add(),
    ]


def lval_array_cell(e: asts.ArrayCell) -> list[Insn]:
    assert False, "Arrays are not part of codegen in CSC 453"
    # find the base pointer of array cell
    # then find the extracted value of the expr
    # if apply negative syntactic sugar, then we need to know length
    # return the addition of base and the extracted offset


def _TypeString(ty: symbols.Type, coord: asts.Coord):
    match ty:
        case symbols.ArrayType(element_type=e_ty):
            return f"Array__{_TypeString(e_ty, coord)}__"
        case symbols.BoolType():
            return "bool"
        case symbols.IntType():
            return "int"
        case symbols.VoidType():
            return "void"
        case symbols.FuncType(params=params, ret=ret_ty):
            params_s = "_".join(_TypeString(p, coord) for p in params)
            return f"__{params_s}__ret__{_TypeString(ret_ty, coord)}__"
        case _:
            error.error(f"Unsupported type: {ty.__class__.__name__}",
                        coord)


def func_label(e: asts.Id) -> str:
    return _TypeString(e.symbol.get_type(), e.token.coord)


def scope_label(s: symbols.Scope) -> str:
    return f"scope_${hex(hash(id(s)))}"


def rval(e: asts.Expr) -> list[Insn]:
    match e:
        case asts.BinaryOp():
            return rval_BinaryOp(e)
        case asts.UnaryOp():
            return rval_UnaryOp(e)
        case asts.CallExpr():
            return rval_CallExpr(e)
        case asts.IdExpr():
            # if move, then have to swap all the way up
            match e.semantic_type:
                case symbols.FuncType():
                    # rval: function "pointer"
                    return [PushLabel(func_label(e.id))]
                case symbols.ArrayType():
                    error.error("rval(IdExpr as Array) not yet supported",
                                e.id.token.coord)
                case symbols.VoidType():
                    error.error("rval(IdExpr as VoidType) unknown behavior",
                                e.id.token.coord)
                case symbols.PhonyType():
                    error.error("PhonyType encountered.", e.id.token.coord)
                case _:
                    return [
                        SaveEvalStack(),

                        RestoreEvalStack()
                    ]

        case asts.ArrayCell(arr, idx):
            error.error("rval(ArrayCell) is currently not supported.", e.coord)
        case asts.IntLiteral(token=token):
            return [PushImmediate(int(token.value))]
        case asts.TrueLiteral():
            return [PushImmediate(1, "true")]
        case asts.FalseLiteral():
            return [PushImmediate(0, "false")]
        case _:
            assert False, f"rval() not implemented for {type(e)}"


def rval_BinaryOp(e: asts.BinaryOp) -> list[Insn]:
    assert False, "rval not supported yet"
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
    assert False, "rval not supported yet"
    match e.op.kind:
        case "-":
            pass
        case "not":
            pass
        case _:
            assert False, f"rval_UnaryOp() not implemented for {e.op}"
    pass


def rval_and(e: asts.BinaryOp) -> list[Insn]:
    assert False, "rval not supported yet"
    pass


def rval_or(e: asts.BinaryOp) -> list[Insn]:
    assert False, "rval not supported yet"
    pass
