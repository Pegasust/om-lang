# This file is a template for implementing a visitor for the ASTs.
# Copy and edit it as needed.

import asts
import error
import symbols

INT_SIZE=1
BOOL_SIZE=1

def type_size(t: symbols.Type):
    return t.size()

# This is the entry point for the visitor.
def program(ast: asts.Program):
    _Program(ast)


def _Program(ast: asts.Program):
    for decl in ast.decls:
        (param_size, stack_size) = _FuncDecl(decl, 0)


def _Stmt(ast: asts.Stmt, offset: int):
    if isinstance(ast, asts.AssignStmt):
        _AssignStmt(ast)
    elif isinstance(ast, asts.IfStmt):
        return _IfStmt(ast, offset)
    elif isinstance(ast, asts.WhileStmt):
         return _WhileStmt(ast, offset)
    elif isinstance(ast, asts.CallStmt):
        _CallStmt(ast)
    elif isinstance(ast, asts.CompoundStmt):
        return _CompoundStmt(ast, offset)
    elif isinstance(ast, asts.PrintStmt):
        _PrintStmt(ast)
    elif isinstance(ast, asts.ReturnStmt):
        _ReturnStmt(ast)
    else:
        assert False, f"_Stmt() not implemented for {type(ast)}"
    return offset


def _Expr(ast: asts.Expr):
    assert not isinstance(ast.semantic_type, symbols.PhonyType), ast
    if isinstance(ast, asts.BinaryOp):
        _BinaryOp(ast)
    elif isinstance(ast, asts.UnaryOp):
        _UnaryOp(ast)
    elif isinstance(ast, asts.CallExpr):
        _CallExpr(ast)
    elif isinstance(ast, asts.IdExpr):
        _IdExpr(ast)
    elif isinstance(ast, asts.ArrayCell):
        _ArrayCell(ast)
    elif isinstance(ast, asts.IntLiteral):
        _IntLiteral(ast)
    elif isinstance(ast, asts.TrueLiteral):
        _TrueLiteral(ast)
    elif isinstance(ast, asts.FalseLiteral):
        _FalseLiteral(ast)
    else:
        assert False, f"_Expr() not implemented for {type(ast)}"


def _Type(ast: asts.Type):
    assert not isinstance(ast.semantic_type, symbols.PhonyType)
    if isinstance(ast, asts.IntType):
        _IntType(ast)
    elif isinstance(ast, asts.BoolType):
        _BoolType(ast)
    elif isinstance(ast, asts.ArrayType):
        _ArrayType(ast)
    else:
        assert False, f"_Type() not implemented for {type(ast)}"


def _VarDecl(ast: asts.VarDecl, offset: int):
    assert not isinstance(ast.semantic_type, symbols.PhonyType)
    _Id(ast.id)
    ast.id.symbol.offset = offset
    sym_sz = type_size(ast.id.symbol.get_type())
    _Type(ast.type_ast)
    return offset + sym_sz


def _ParamDecl(ast: asts.ParamDecl, offset: int):
    assert not isinstance(ast.semantic_type, symbols.PhonyType)
    _Id(ast.id)
    _Type(ast.type_ast)
    ast.id.symbol.offset = offset
    # params decrease by size
    return offset - type_size(ast.id.symbol.get_type())


def _IntType(ast: asts.IntType):
    pass


def _BoolType(ast: asts.BoolType):
    pass


def _ArrayType(ast: asts.ArrayType):
    _Type(ast.element_type_ast)
    if ast.size is not None:
        _Expr(ast.size)


def _IdExpr(ast: asts.IdExpr):
    _Id(ast.id)


def _CallExpr(ast: asts.CallExpr):
    _Expr(ast.fn)
    for arg in ast.args:
        _Expr(arg)


def _Id(ast: asts.Id):
    assert not isinstance(ast.symbol, symbols.PhonySymbol)
    assert not isinstance(ast.semantic_type, symbols.PhonyType)



def _AssignStmt(ast: asts.AssignStmt):
    _Expr(ast.lhs)
    _Expr(ast.rhs)


def _BinaryOp(ast: asts.BinaryOp):
    _Expr(ast.left)
    _Expr(ast.right)


def _UnaryOp(ast: asts.UnaryOp):
    _Expr(ast.expr)


def _PrintStmt(ast: asts.PrintStmt):
    _Expr(ast.expr)


def _IfStmt(ast: asts.IfStmt, offset: int):
    _Expr(ast.expr)
    max_offset = _CompoundStmt(ast.thenStmt, offset)
    if ast.elseStmt is not None:
        max_offset = max(max_offset, _CompoundStmt(ast.elseStmt, offset))
    return max_offset


def _WhileStmt(ast: asts.WhileStmt, offset: int):
    _Expr(ast.expr)
    return _CompoundStmt(ast.stmt, offset)


def _CallStmt(ast: asts.CallStmt):
    _CallExpr(ast.call)


def _CompoundStmt(ast: asts.CompoundStmt, offset: int):
    assert not isinstance(ast.local_scope, symbols.PhonyScope)
    for decl in ast.decls:
        offset = _VarDecl(decl, offset)

    max_offset = offset
    for stmt in ast.stmts:
        max_offset = max(max_offset, _Stmt(stmt, offset))
    if ast.return_stmt is not None:
        _ReturnStmt(ast.return_stmt)
    return max_offset


def _FuncDecl(ast: asts.FuncDecl, offset: int):
    assert not isinstance(ast.func_scope, symbols.PhonyScope)
    _Id(ast.id)
    param_offset = offset - 2
    for param in ast.params:
        param_offset = _ParamDecl(param, param_offset)
    if ast.ret_type_ast is not None:
        _Type(ast.ret_type_ast)
    ret_offset = _CompoundStmt(ast.body, offset + 4)
    func_type = ast.id.symbol.get_type()
    assert isinstance(func_type, symbols.FuncType), f"semantic_type: {ast.id.semantic_type}"
    # func_type.frame_size = ret_offset - 3 - offset + 1
    func_type.frame_size = ret_offset - 3 - offset
    func_type.param_size = offset - 2 - param_offset + 1
    return (func_type.param_size, func_type.frame_size)


def _ReturnStmt(ast: asts.ReturnStmt):
    assert not isinstance(ast.enclosing_scope, symbols.PhonyScope)
    if ast.expr is not None:
        _Expr(ast.expr)


def _ArrayCell(ast: asts.ArrayCell):
    _Expr(ast.arr)
    _Expr(ast.idx)


def _IntLiteral(ast: asts.IntLiteral):
    pass


def _TrueLiteral(ast: asts.TrueLiteral):
    pass


def _FalseLiteral(ast: asts.FalseLiteral):
    pass
