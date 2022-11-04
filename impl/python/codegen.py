from typing import Optional, TypeVar, Iterable
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

BAIL = 1             # Is bail
NO_BAIL = 0          # Is not bail
BAIL_FP_OFFSET = 2   # Offset from frame pointer that stores BAIL status
RA_FP_OFFSET = 0     # Offset from frame pointer that stores the return address
RET_FP_OFFSET = -1   # Offset from frame pointer that stores the return value
FP_CALLER_OFFSET = 1  # Offset from frame pointer that stores the caller's addr

T = TypeVar('T')


def flatten_list(list_iter: Iterable[Iterable[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(list_iter))


# This is the entry point for the visitor.
def generate(ast: asts.Program) -> list[Insn]:
    return _Program(ast)


def _Program(ast: asts.Program) -> list[Insn]:
    # for decl in ast.decls:
    #     f: list[Insn] = _FuncDecl(decl)
    main: Optional[asts.FuncDecl] = None
    for func_decl in ast.decls:
        if func_decl.id.token.value == "main":
            main = func_decl
    return flatten_list((
        callexpr_bare(main.id, [], cmt="call main") if main else [],
        [Halt()],
        *(_FuncDecl(decl) for decl in ast.decls),
    ))


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


def callexpr_bare(func_id: asts.Id, args: list[asts.Expr], cmt=None):
    fn_type = func_id.symbol.get_type()
    assert isinstance(fn_type, symbols.FuncType)
    param_size = fn_type.param_size
    func_name = func_id.token.value
    alloc_sz = 5 + param_size

    return flatten_list((
        _cmt(cmt),
        _cmt(f"-callexpr_bare: omega/{func_name}"),

        stack_malloc(
            alloc_sz, cmt=f"alloc sz:{alloc_sz}(psz:{param_size})")[1],
        [SaveEvalStack()],

        *(assign(-2-i, rval(arg), cmt="Assign arg to memstack")
          for i, arg in enumerate(args)),

        _cmt("Initialize FP and BAIL"),
        assign(BAIL_FP_OFFSET, [PushImmediate(NO_BAIL)], cmt="BAIL: NO_BAIL"),
        [PushFP(0, comment="Store our old FP")],

        _cmt("Assign this FP = SP - 4"),
        [
            PushSP(-4, "Set FP to new function scope memstack location"),
            PopFP(),
        ],

        _cmt("Finish storing the caller's FP to the callee's frame"), [
            *assign(FP_CALLER_OFFSET, [Swap()], "store caller's FP to FP_CALLER_OFFSET")
        ],

        _cmt(f"-Call {func_name}"),
        [
            PushLabel(func_label(func_id)),
            Call(f"call {func_name}"),
        ],

        _cmt("-Epilogue: Return FP to caller, and RET as rval"),
        _cmt("Retrieve ideal stack for processing"), [
            *retrieve(RET_FP_OFFSET, "stack push RET"),
        ],
        _cmt("Set FP to caller"), [
            *retrieve(FP_CALLER_OFFSET, "stack push FP_CALLER"),
            PopFP("FP = FP_CALLER"),
        ],

        _cmt(f"Dealloc fsize ({alloc_sz})"),
        [RestoreEvalStack()],
        stack_free(alloc_sz),

        _cmt("-RET as rval"), [
            # We have already put RET right after FP_CALLER
            # Since we popped FP_CALLER once, the thing left on the stack
            # is the return value
        ]

    ))


def rval_CallExpr(ast: asts.CallExpr) -> list[Insn]:
    assert isinstance(ast.fn, asts.IdExpr)
    return callexpr_bare(ast.fn.id, ast.args)


def _lval_offset(fp_offset: int) -> list[Insn]:
    return [PushFP(fp_offset, comment=f"lval_offset: {fp_offset}")]


def retrieve(fp_offset: int, cmt: Optional[str] = None) -> list[Insn]:
    return flatten_list((
        _cmt(cmt),
        [PushFP(fp_offset)],
        [Load()]
    ))


def assign(fp_offset: int, rval_insn: list[Insn], cmt: Optional[str] = None)\
        -> list[Insn]:
    return flatten_list((
        _cmt(cmt),
        _lval_offset(fp_offset),
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
        # _cmt("Print"),
        rval(ast.expr),
        [Print()],
    ))


def _IfStmt(ast: asts.IfStmt, parent_dealloc: str) -> list[Insn]:
    assert False, "IfStmt not yet supported"
    # handle ast.expr
    # handle ast.thenStmt
    # handle ast.elseStmt
    pass


def _WhileStmt(ast: asts.WhileStmt, parent_dealloc: str) -> list[Insn]:
    assert False, "WhileStmt not yet supported"
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
        case _:
            assert False, f"Missing handler for {e}"


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


def _ctrl_and(left: asts.Expr, right: asts.Expr, label: str, cond: bool,
              sense: bool) -> list[Insn]:
    match cond:
        case True:
            # Template of TRUE in and
            fall_label = control_label(
                [left, right], f"and-{label}-{cond}-{sense}")
            return flatten_list((
                control(left, fall_label, not sense),
                control(right, label, sense),
                [Label(fall_label)],
            ))
        case False:
            return flatten_list((
                control(left, label, not sense),
                control(right, label, not sense)
            ))


def _ctrl_bin(left: asts.Expr, right: asts.Expr, op_kind: str, label: str,
              sense: bool) -> list[Insn]:
    match op_kind:
        case "and":
            return _ctrl_and(left, right, label, sense, True)
        case "or":
            return _ctrl_and(left, right, label, not sense, False)
        case _:
            assert False, f"Unreachable: bad op_kind: {op_kind}"


def control_BinaryOp(e: asts.BinaryOp, label: str, sense: bool) -> list[Insn]:
    match (e.op.kind, sense):
        case "and":
            return _ctrl_bin(e.left, e.right, "and", label, sense)
        case "or":
            return _ctrl_bin(e.left, e.right, "or", label, sense)
        case ">":
            assert False, "Not yet supported"
        case ">=":
            assert False, "Not yet supported"
        case "<":
            assert False, "Not yet supported"
        case "<=":
            assert False, "Not yet supported"
        case _:
            assert False, f"Missing handler for {e.op.kind}"


def control_UnaryOp(e: asts.UnaryOp, label: str, sense: bool) -> list[Insn]:
    match e.op.kind:
        case "not":
            return control(e.expr, label, not sense)
        case _:
            assert False, f"control_UnaryOp() not implemented for {e.op.kind}"


def _CallStmt(ast: asts.CallStmt) -> list[Insn]:
    # handle ast.call
    return flatten_list((
        rval_CallExpr(ast.call),
        # Disregard return value
        [Pop("Disregard return value")],
    ))


def option_unwrap_or(opt: Optional[T], default: T) -> T:
    return opt if opt is not None else default


def stack_malloc(atomic_sz: int, cmt=None) -> tuple[int, list[Insn]]:
    return (atomic_sz, _cmt(cmt) + [PushImmediate(0)] * atomic_sz)


def stack_calloc(ty: symbols.Type, elem_cnt: int, imm: Optional[int] = None) \
        -> tuple[int, list[Insn]]:
    atomic_sz = (ty.size() * elem_cnt)
    return (atomic_sz, [PushImmediate(option_unwrap_or(imm, 0))] * atomic_sz)


def stack_free(atomic_sz: int, cmt=None) -> list[Insn]:
    return _cmt(cmt) + [Pop()] * atomic_sz


def _cmt(cmt: Optional[str]) -> list[Insn]:
    return [Noop(line.strip()) for line in cmt.strip().splitlines()] \
        if cmt else []


def _CompoundStmt(ast: asts.CompoundStmt, parent_dealloc: str, cmt=None) -> list[Insn]:
    # TODO: Revise to v2 func call
    my_dealloc_label = f"dealloc-{scope_label(ast.local_scope)}"

    stmts = (_Stmt(stmt, my_dealloc_label) for stmt in ast.stmts)
    isns_stmts = flatten_list(stmt for stmt in stmts)

    isns_return = _ReturnStmt(ast.return_stmt, my_dealloc_label) \
        if ast.return_stmt else []

    isns_bail = flatten_list((
        stack_peek("Peak BAIL"),
        [
            JumpIfNotZero(parent_dealloc)
        ]
    ))

    # TODO: func call allocate all space needed by all variables

    return flatten_list((
        _cmt("""
        +--------------+
        | Symbol table |
        +--------------+
        """),
        _cmt("\n".join(
            f"{s.id.token.value}: offset {s.id.symbol.offset}"
            for s in ast.decls)),
        _cmt("""
        +--------------+
        """),
        isns_stmts,
        isns_return,
        [Label(my_dealloc_label)],
        isns_bail
    ))


def _FuncDecl(ast: asts.FuncDecl) -> list[Insn]:
    # TODO: Revise to v2 func call

    # TODO: func decl allocate all the space necessary for all vars
    func_type = ast.id.symbol.get_type()
    assert isinstance(func_type, symbols.FuncType)
    frame_size = func_type.frame_size
    func_done = f"{func_label(ast.id)}-bail"
    # handle ast.body
    # ast.params is handled by callee
    ret_isns = [
        JumpIndirect()
    ]

    return flatten_list((
        [Label(func_label(ast.id))],
        _cmt("Store RA to memstack"),
        assign(RA_FP_OFFSET, [Swap()]),
        stack_malloc(frame_size, "allocate func vars")[1],
        [SaveEvalStack("Allocate func vars to memstack")],
        _CompoundStmt(ast.body, func_done, cmt="The main exec of func"),
        [
            Label(func_done),
        ],
        [RestoreEvalStack("Dealloc func vars from memstack")],
        stack_free(frame_size),
        retrieve(RA_FP_OFFSET),
        [
            JumpIndirect()
        ]
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


def stack_peek(cmt=None) -> list[Insn]:
    return flatten_list((
        _cmt(cmt),
        [
            PushSP(-1),
            Load()
        ],

    ))


def stack_pop_retrieve(cmt=None) -> list[Insn]:
    return [
        *_cmt(cmt),
        PushSP(-1),
        Load(),
        PushSP(-1, "Decrement SP to pop"),
        PopSP(),
    ]


def stack_pop(cmt: Optional[str] = None) -> list[Insn]:
    return [
        *_cmt(cmt),
        PushSP(-1, "Decrement SP"),
        PopSP()
    ]


def _ReturnStmt(ast: asts.ReturnStmt, dealloc_label: str) -> list[Insn]:
    isns_expr = _cmt("return"+("" if not ast.expr else " expr"))
    if ast.expr is not None:
        # rval and store return value
        isns_expr = []
        isns_expr.extend(assign(RET_FP_OFFSET, rval(ast.expr), "store RET"))

    # mark BAIL
    isns_expr.extend(assign(BAIL_FP_OFFSET, [PushImmediate(BAIL)], "set BAIL"))
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


def lval_id(e: asts.IdExpr, cmt=None) -> list[Insn]:
    return [
        *_cmt(cmt),
        PushFP(e.id.symbol.offset, comment=f"lval for: {e.id.token.value}")
    ]


def lval_array_cell(_: asts.ArrayCell) -> list[Insn]:
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
            return f"({params_s})->{_TypeString(ret_ty, coord)}"
        case _:
            error.error(f"Unsupported type: {ty.__class__.__name__}",
                        coord)


def func_label(e: asts.Id) -> str:
    return f"fn_{e.token.value}{_TypeString(e.symbol.get_type(), e.token.coord)}"


def scope_label(s: symbols.Scope) -> str:
    return f"scope_{hex(hash(id(s)))}"


def control_label(args: list[asts.Expr], keyword: Optional[str]) -> str:
    args_id = [hex(hash(id(e))) for e in args]
    args_fmt = "_".join(args_id)
    kw = "" if not keyword else f"_{keyword}"
    return f"control{kw}_{args_fmt}"


def rval(e: asts.Expr) -> list[Insn]:
    match e:
        case asts.BinaryOp():
            return rval_BinaryOp(e)
        case asts.UnaryOp():
            return rval_UnaryOp(e)
        case asts.CallExpr():
            return rval_CallExpr(e)
        case asts.IdExpr():
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
                    offset = e.id.symbol.offset
                    name = e.id.token.value
                    return [
                        PushFP(offset, f"Accessing {name}@{offset}"),
                        Load()
                    ]
        case asts.ArrayCell(arr=_, idx=_):
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
    rval_both = (rval(e.left), rval(e.right))
    match e.op.kind:
        case "+":
            return flatten_list((*rval_both, [Add()]))
        case "-":
            return flatten_list((*rval_both, [Sub()]))
        case "*":
            return flatten_list((*rval_both, [Mul()]))
        case "/":
            return flatten_list((*rval_both, [Div()]))
        case "<":
            return flatten_list((*rval_both, [LessThan()]))
        case "<=":
            return flatten_list((*rval_both, [LessThanEqual()]))
        case ">":
            return flatten_list((*rval_both, [GreaterThan()]))
        case ">=":
            return flatten_list((*rval_both, [GreaterThanEqual()]))
        case "==":
            return flatten_list((*rval_both, [Equal()]))
        case "!=":
            return flatten_list((*rval_both, [NotEqual()]))
        case "and":
            return rval_and(e)
        case "or":
            return rval_or(e)
        case _:
            assert False, f"rval_BinaryOp() not implemented for {e.op}"


def rval_UnaryOp(e: asts.UnaryOp) -> list[Insn]:
    match e.op.kind:
        case "-":
            return flatten_list((rval(e.expr), [Negate()]))
        case "not":
            return flatten_list((rval(e.expr), [Not()]))
        case _:
            assert False, f"rval_UnaryOp() not implemented for {e.op}"


def rval_and(e: asts.BinaryOp) -> list[Insn]:
    jump_label = control_label([e], "rval_and")
    return flatten_list((
        control_BinaryOp(e, jump_label, True),
        [
            PushImmediate(0),
            Jump(f"{jump_label}-end"),
            Label(jump_label),
            PushImmediate(1),
            Label(f"{jump_label}-end")
        ]
    ))


def rval_or(e: asts.BinaryOp) -> list[Insn]:
    jump_label = control_label([e], "rval_or")
    return flatten_list((
        control_BinaryOp(e, jump_label, True),
        [
            PushImmediate(0),
            Jump(f"{jump_label}-end"),
            Label(jump_label),
            PushImmediate(1),
            Label(f"{jump_label}-end")
        ]
    ))
