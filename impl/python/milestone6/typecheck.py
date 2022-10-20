# This file is a template for implementing a visitor for the ASTs.
# Copy and edit it as needed.

import asts
import error
import symbols


# This is the entry point for the visitor.
def program(ast: asts.Program):
    _Program(ast)


def _Program(ast: asts.Program):
    for decl in ast.decls:
        _FuncDecl(decl)


def _Stmt(ast: asts.Stmt):
    if isinstance(ast, asts.AssignStmt):
        _AssignStmt(ast)
    elif isinstance(ast, asts.IfStmt):
        _IfStmt(ast)
    elif isinstance(ast, asts.WhileStmt):
        _WhileStmt(ast)
    elif isinstance(ast, asts.CallStmt):
        _CallStmt(ast)
    elif isinstance(ast, asts.CompoundStmt):
        _CompoundStmt(ast)
    elif isinstance(ast, asts.PrintStmt):
        _PrintStmt(ast)
    elif isinstance(ast, asts.ReturnStmt):
        _ReturnStmt(ast)
    else:
        assert False, f"_Stmt() not implemented for {type(ast)}"


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


def _VarDecl(ast: asts.VarDecl):
    assert not isinstance(ast.semantic_type, symbols.PhonyType)
    _Id(ast.id)
    _Type(ast.type_ast)


def _ParamDecl(ast: asts.ParamDecl):
    assert not isinstance(ast.semantic_type, symbols.PhonyType)
    _Id(ast.id)
    _Type(ast.type_ast)


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


def _IfStmt(ast: asts.IfStmt):
    _Expr(ast.expr)
    _CompoundStmt(ast.thenStmt)
    if ast.elseStmt is not None:
        _CompoundStmt(ast.elseStmt)


def _WhileStmt(ast: asts.WhileStmt):
    _Expr(ast.expr)
    _CompoundStmt(ast.stmt)


def _CallStmt(ast: asts.CallStmt):
    _CallExpr(ast.call)


def _CompoundStmt(ast: asts.CompoundStmt):
    assert not isinstance(ast.local_scope, symbols.PhonyScope)
    for decl in ast.decls:
        _VarDecl(decl)
    for stmt in ast.stmts:
        _Stmt(stmt)
    if ast.return_stmt is not None:
        _Stmt(ast.return_stmt)


def _FuncDecl(ast: asts.FuncDecl):
    assert not isinstance(ast.func_scope, symbols.PhonyScope)
    _Id(ast.id)
    for param in ast.params:
        _ParamDecl(param)
    if ast.ret_type_ast is not None:
        _Type(ast.ret_type_ast)
    _CompoundStmt(ast.body)


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
