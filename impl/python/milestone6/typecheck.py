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


def _VarDecl(ast: asts.VarDecl):
    # assert not isinstance(ast.semantic_type, symbols.PhonyType)
    _Id(ast.id)
    _Type(ast.type_ast)
    ast.id.semantic_type = ast.type_ast.semantic_type
    


def _ParamDecl(ast: asts.ParamDecl):
    # assert not isinstance(ast.semantic_type, symbols.PhonyType)
    _Id(ast.id)
    _Type(ast.type_ast)
    ast.id.semantic_type = ast.type_ast.semantic_type


def _IntType(ast: asts.IntType):
    ast.semantic_type = symbols.IntType()
    return ast


def _BoolType(ast: asts.BoolType):
    ast.semantic_type = symbols.BoolType()
    return ast


def _ArrayType(ast: asts.ArrayType):
    _Type(ast.element_type_ast)
    ast.semantic_type = symbols.ArrayType(ast.element_type_ast.semantic_type)
    if ast.size is not None:
        _Expr(ast.size)
        # TODO: # assert that the size_expr resolves to integral value
        if not isinstance(ast.size.semantic_type, symbols.IntType):
            # warning
            print(f"array size ({ast.size})'s semantic_type is not IntType")
    return ast


def _IdExpr(ast: asts.IdExpr):
    _Id(ast.id)
    ast.semantic_type = ast.id.semantic_type
    return ast



def _CallExpr(ast: asts.CallExpr):
    _Expr(ast.fn)
    if not isinstance(ast.fn.semantic_type, symbols.FuncType):
        error.error(f"Expect call expr but type ({ast.fn.semantic_type}) "+
                        "is not FuncType", ast.coord)
    for i, (expect, arg) in enumerate(zip(ast.fn.semantic_type.params, ast.args)):
        _Expr(arg)
        # TODO: Add arg type check for non literal type using symbol table
        if expect != arg.semantic_type:
            error.error(f"Positional arg {i}: expect {expect}, got {arg.semantic_type}",
                        ast.coord)
    if not isinstance(ast.fn.semantic_type, symbols.FuncType):
        error.error(f"Expect call expr but type ({ast.fn.semantic_type}) "+
                        "is not FuncType", ast.coord)
    ast.semantic_type = ast.fn.semantic_type.ret


def _Id(ast: asts.Id):
    # assert not isinstance(ast.symbol, symbols.PhonySymbol)
    # assert not isinstance(ast.semantic_type, symbols.PhonyType)
    return ast


def _AssignStmt(ast: asts.AssignStmt):
    _Expr(ast.lhs)
    _Expr(ast.rhs)
    return ast


def _BinaryOp(ast: asts.BinaryOp):
    _Expr(ast.left)
    _Expr(ast.right)
    if ast.left.semantic_type != ast.right.semantic_type:
        # warning
        error.error(f"lhs's type({ast.left.semantic_type}) != "+\
                  f"rhs's type ({ast.right.semantic_type})", ast.op.coord)
    if ast.op.kind in {'==', '!='}:
        assert(isinstance(ast.left.semantic_type, symbols.IntType) or 
            isinstance(ast.left.semantic_type, symbols.BoolType))
    elif ast.op.kind in {'<=', '>=', '<', '>', '+', '-', '*', '/'}:
        assert(isinstance(ast.left.semantic_type, symbols.IntType))
    elif ast.op.kind in {'and', 'or'}:
        assert(isinstance(ast.left.semantic_type, symbols.BoolType))
    else:
        error.error(f"BinaryOp: Unexpected op: {ast.op.kind}", ast.op.coord)
    return ast


def _UnaryOp(ast: asts.UnaryOp):
    _Expr(ast.expr)
    ast.semantic_type = ast.expr.semantic_type
    return ast


def _PrintStmt(ast: asts.PrintStmt):
    _Expr(ast.expr)
    return ast


def _IfStmt(ast: asts.IfStmt):
    _Expr(ast.expr)

    if not isinstance(ast.expr.semantic_type, symbols.BoolType):
        # TODO: Warning
        semtype = ast.expr.semantic_type
        error.error(f"If expr: semantic_type ({semtype}) not bool", ast.coord)

    _CompoundStmt(ast.thenStmt)

    if ast.elseStmt is not None:
        _CompoundStmt(ast.elseStmt)

    return ast


def _WhileStmt(ast: asts.WhileStmt):
    _Expr(ast.expr)
    
    if not isinstance(ast.expr.semantic_type, symbols.BoolType):
        # TODO: Warning
        semtype = ast.expr.semantic_type
        error.error(f"while expr: semantic_type ({semtype}) not bool", ast.coord)
    _CompoundStmt(ast.stmt)

    return ast


def _CallStmt(ast: asts.CallStmt):
    _CallExpr(ast.call)
    return ast


def _CompoundStmt(ast: asts.CompoundStmt):
    # assert not isinstance(ast.local_scope, symbols.PhonyScope)
    for decl in ast.decls:
        _VarDecl(decl)
    for stmt in ast.stmts:
        _Stmt(stmt)
    if ast.return_stmt is not None:
        assert not isinstance(ast.return_stmt.enclosing_scope, symbols.PhonyScope)
        _Stmt(ast.return_stmt)


def _FuncDecl(ast: asts.FuncDecl):
    # assert not isinstance(ast.func_scope, symbols.PhonyScope)
    _Id(ast.id)

    for param in ast.params:
        _ParamDecl(param)

    # Declared return value
    decl_ret_type = symbols.VoidType()
    if ast.ret_type_ast is not None:
        _Type(ast.ret_type_ast)
        decl_ret_type = ast.ret_type_ast.semantic_type

    # Actual return value
    _CompoundStmt(ast.body)
    ret_type = symbols.VoidType()
    if ast.body.return_stmt and ast.body.return_stmt.expr:
        ret_type = ast.body.return_stmt.expr.semantic_type

    if ret_type != decl_ret_type:
        # warning instead
        coord = ast.body.return_stmt.coord if ast.body.return_stmt\
            else ast.id.token.coord
        message = (f"Function \"{ast.id.token.value}\": "+\
                        f"Expect {decl_ret_type} but returns {ret_type}", 
                    coord)
        print(*message)
    # ast.func_scope.set_return_type(ret_type)
    return ast


def _ReturnStmt(ast: asts.ReturnStmt):
    # assert not isinstance(ast.enclosing_scope, symbols.PhonyScope)
    if ast.expr is not None:
        _Expr(ast.expr)


def _ArrayCell(ast: asts.ArrayCell):
    _Expr(ast.arr)
    if not isinstance(ast.arr.semantic_type, symbols.ArrayType):
        error.error(f"Attempting to access non-array ({ast.arr}) by indexing",
              ast.coord)
    ast.semantic_type = ast.arr.semantic_type.element_type
    _Expr(ast.idx)
    if not isinstance(ast.idx.semantic_type, symbols.IntType):
        # TODO: Warning instead
        semtype = ast.idx.semantic_type 
        error.error(f"Array access semantic_type ({semtype}) is not int",
                    ast.coord)
    return ast
    


def _IntLiteral(ast: asts.IntLiteral):
    pass


def _TrueLiteral(ast: asts.TrueLiteral):
    pass


def _FalseLiteral(ast: asts.FalseLiteral):
    pass
    
    
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
        # assert False, f"_Stmt() not implemented for {type(ast)}"
        pass


def _Expr(ast: asts.Expr):
    # assert not isinstance(ast.semantic_type, symbols.PhonyType), ast
    if isinstance(ast, asts.BinaryOp):
        return _BinaryOp(ast)
    elif isinstance(ast, asts.UnaryOp):
        return _UnaryOp(ast)
    elif isinstance(ast, asts.CallExpr):
        return _CallExpr(ast)
    elif isinstance(ast, asts.IdExpr):
        return _IdExpr(ast)
    elif isinstance(ast, asts.ArrayCell):
        return _ArrayCell(ast)
    elif isinstance(ast, asts.IntLiteral):
        return _IntLiteral(ast)
    elif isinstance(ast, asts.TrueLiteral):
        return _TrueLiteral(ast)
    elif isinstance(ast, asts.FalseLiteral):
        return _FalseLiteral(ast)
    else:
        # assert False, f"_Expr() not implemented for {type(ast)}"
        pass


def _Type(ast: asts.Type):
    # assert not isinstance(ast.semantic_type, symbols.PhonyType)
    if isinstance(ast, asts.IntType):
        return _IntType(ast)
    elif isinstance(ast, asts.BoolType):
        return _BoolType(ast)
    elif isinstance(ast, asts.ArrayType):
        return _ArrayType(ast)
    else:
        # assert False, f"_Type() not implemented for {type(ast)}"
        pass


