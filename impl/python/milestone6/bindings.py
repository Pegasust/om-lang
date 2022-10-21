# General idea: for each type of token, we return the unbounded IdSymbol
# The tokens that owns some scope will then resolve it to the symbolic table.
from os import wait
import asts
import error
import symbols

# This is the entry point for the visitor.
def program(ast: asts.Program):
    _Program(ast)


def _Program(ast: asts.Program):
    # Assume that each Omega file is self-contained.
    # This means each file is a module/executable without any linking
    # just yet!
    # monofile repo
    global_scope = symbols.GlobalScope()
    for decl in ast.decls:
        decl.func_scope = symbols.FuncScope(global_scope)
        (_func_symb, unscoped) = _FuncDecl(decl)
        func_symb = _func_symb.id.symbol
        assert isinstance(func_symb, symbols.IdSymbol)
        func_symb.scope = global_scope
        global_scope.symtab[func_symb.name] = func_symb
        for symb_id in unscoped:
            symb = symb_id.symbol
            assert isinstance(symb, symbols.IdSymbol)
            func_symb = global_scope.lookup(symb.name)
            if not func_symb:
                # warning?
                # print(f"WARNING: symbol {symb} not found on global scope")
                continue
            symb.set_type(func_symb.get_type())
            symb.scope = global_scope
            symb_id.semantic_type = symb.get_type()


def _Stmt(ast: asts.Stmt):
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
        assert False, f"_Stmt() not implemented for {ast}"


def _Expr(ast: asts.Expr):
    retval: list[asts.Id] = []
    if isinstance(ast, asts.BinaryOp):
        retval.extend(_BinaryOp(ast))
    elif isinstance(ast, asts.UnaryOp):
        retval.extend(_UnaryOp(ast))
    elif isinstance(ast, asts.CallExpr):
        retval.extend(_CallExpr(ast))
    elif isinstance(ast, asts.IdExpr):
        retval.extend(_IdExpr(ast))
    elif isinstance(ast, asts.ArrayCell):
        retval.extend(_ArrayCell(ast))
    elif isinstance(ast, asts.IntLiteral):
        _IntLiteral(ast)
    elif isinstance(ast, asts.TrueLiteral):
        _TrueLiteral(ast)
    elif isinstance(ast, asts.FalseLiteral):
        _FalseLiteral(ast)
    else:
        assert False, f"_Expr() not implemented for {type(ast)}"
    return retval


def _Type(ast: asts.Type):
    if isinstance(ast, asts.IntType):
        return _IntType(ast)
    elif isinstance(ast, asts.BoolType):
        return _BoolType(ast)
    elif isinstance(ast, asts.ArrayType):
        return _ArrayType(ast)
    else:
        assert False, f"_Type() not implemented for {type(ast)}"


def _VarDecl(ast: asts.VarDecl):
    id_symb = _Id(ast.id)
    var_type = _Type(ast.type_ast)
    id_symb.semantic_type = var_type
    id_symb.symbol.set_type(var_type)
    # TODO: Might want to change this to VoidType
    ast.semantic_type = var_type
    return ast


def _ParamDecl(ast: asts.ParamDecl):
    id_symb = _Id(ast.id)
    id_symb.semantic_type = _Type(ast.type_ast)
    id_symb.symbol.set_type(id_symb.semantic_type)
    ast.id.semantic_type = id_symb.semantic_type
    # TODO: Might want to change this to VoidType
    ast.semantic_type = ast.id.semantic_type
    return ast


def _IntType(ast: asts.IntType):
    return symbols.IntType()


def _BoolType(ast: asts.BoolType):
    return symbols.BoolType()


def _ArrayType(ast: asts.ArrayType):
    elem_type = _Type(ast.element_type_ast)
    if ast.size is not None:
        _Expr(ast.size)
    return symbols.ArrayType(elem_type)


def _IdExpr(ast: asts.IdExpr):
    return [_Id(ast.id)]


def _CallExpr(ast: asts.CallExpr):
    symbs = _Expr(ast.fn)
    for arg in ast.args:
        symbs.extend(_Expr(arg))
    ast.semantic_type = ast.fn.semantic_type
    return symbs


def _Id(ast: asts.Id):
    ast.symbol = symbols.IdSymbol(ast.token.value, symbols.PhonyScope())
    ast.symbol.name = ast.token.value
    return ast

def _AssignStmt(ast: asts.AssignStmt):
    symbs = _Expr(ast.lhs)
    symbs.extend(_Expr(ast.rhs))
    return symbs


def _BinaryOp(ast: asts.BinaryOp):
    symbs = _Expr(ast.left)
    symbs.extend(_Expr(ast.right))
    if ast.op.kind in {'<=', '==', '!=', '>=', '<', '>', 'and', 'or'}:
        ast.semantic_type = symbols.BoolType()
    elif ast.op.kind in {'+', '-', '*', '/'}:
        ast.semantic_type = symbols.IntType()
    else:
        error.error(f"BinaryOp: Unexpected op: {ast.op.kind}", ast.op.coord)
    return symbs


def _UnaryOp(ast: asts.UnaryOp):
    symbs = _Expr(ast.expr)
    ast.semantic_type = ast.expr.semantic_type
    return symbs


def _PrintStmt(ast: asts.PrintStmt):
    symbs = _Expr(ast.expr)
    return symbs


def _IfStmt(ast: asts.IfStmt):
    symbs = _Expr(ast.expr)
    symbs.extend(_CompoundStmt(ast.thenStmt))
    if ast.elseStmt is not None:
        symbs.extend(_CompoundStmt(ast.elseStmt))
    return symbs


def _WhileStmt(ast: asts.WhileStmt):
    symbs = _Expr(ast.expr)
    symbs.extend(_CompoundStmt(ast.stmt))
    return symbs


def _CallStmt(ast: asts.CallStmt):
    return _CallExpr(ast.call)


def _CompoundStmt(ast: asts.CompoundStmt):
    local_scope = ast.local_scope

    for decl in ast.decls:
        _decl = _VarDecl(decl)
        decl_id_symb = _decl.id.symbol
        assert isinstance(decl_id_symb, symbols.IdSymbol)
        if decl_id_symb.name in local_scope.symtab.keys():
            error.error(f"Var \"{decl_id_symb.name}\" declared more than once",
                        decl.id.token.coord)
        local_scope.symtab[decl_id_symb.name] = decl_id_symb
        decl_id_symb.scope = local_scope

    unscoped_symbs: list[asts.Id] = []
    for stmt in ast.stmts:
        # how to handle compound statements?
        # TODO: Add more nodes that may create new scopes here!
        if isinstance(stmt, asts.AssignStmt):
            pass
        elif isinstance(stmt, asts.IfStmt):
            stmt.thenStmt.local_scope = symbols.LocalScope(local_scope)
            if stmt.elseStmt:
                stmt.elseStmt.local_scope = symbols.LocalScope(local_scope)
        elif isinstance(stmt, asts.WhileStmt):
            stmt.stmt.local_scope = symbols.LocalScope(local_scope)
        elif isinstance(stmt, asts.CallStmt):
            pass
        elif isinstance(stmt, asts.CompoundStmt):
            stmt.local_scope = symbols.LocalScope(local_scope)
        elif isinstance(stmt, asts.PrintStmt):
            pass
        elif isinstance(stmt, asts.ReturnStmt):
            pass

        unscoped_symbs.extend(_Stmt(stmt))

    if ast.return_stmt is not None:
        ast.return_stmt.enclosing_scope = local_scope
        unscoped_symbs.extend(_Stmt(ast.return_stmt))

    # drain filter would be ideal here
    _unscoped = list(unscoped_symbs) * 0 # borrow type with empty list
    for id in unscoped_symbs:
        symb = id.symbol
        assert isinstance(symb, symbols.IdSymbol)
        decl = local_scope.lookup(symb.name)
        # print(f"{symb=}, {decl=}")
        if not decl:
            _unscoped.append(id)
            continue
        if not isinstance(decl, symbols.IdSymbol):
            # print(f"WARNING: {decl} is not IdSymbol")
            continue

        symb.set_type(decl.get_type())
        symb.scope = decl.scope
        id.semantic_type = symb.get_type()

    return _unscoped # Since we have processed all unscoped symbols


def _FuncDecl(ast: asts.FuncDecl):
    id_symb = _Id(ast.id)
    func_scope = ast.func_scope

    param_symbs = [_ParamDecl(param) for param in ast.params]
    for param in ast.params:
        param_symb = param.id.symbol
        assert isinstance(param_symb, symbols.IdSymbol)
        if param_symb.name in func_scope.symtab.keys():
            error.error(
                f"Param \"{param_symb.name}\" declared more than once",
                param.id.token.coord
            )
        func_scope.symtab[param_symb.name] = param_symb
        param_symb.scope = func_scope

    ret_type = symbols.VoidType()
    if ast.ret_type_ast is not None:
        ret_type = _Type(ast.ret_type_ast)
    # assign function type of this function
    id_symb.symbol.set_type(
        symbols.FuncType([p.id.symbol.get_type() for p in param_symbs], ret_type)
    )
    ast.func_scope.set_return_type(id_symb.symbol.get_type())
    func_scope.set_return_type(ret_type)

    # parse the statements within the function
    ast.body.local_scope = symbols.LocalScope(func_scope)
    unscoped_symbs = _CompoundStmt(ast.body)
    ast.id.semantic_type = func_scope.get_return_type()
    
    return (ast, unscoped_symbs)


def _ReturnStmt(ast: asts.ReturnStmt):
    if ast.expr is not None:
        return _Expr(ast.expr)
    return []


def _ArrayCell(ast: asts.ArrayCell):
    symbs = _Expr(ast.arr)
    symbs.extend(_Expr(ast.idx))
    return symbs


def _IntLiteral(_ast: asts.IntLiteral):
    _ast.semantic_type = symbols.IntType()
    pass


def _TrueLiteral(_ast: asts.TrueLiteral):
    _ast.semantic_type = symbols.BoolType()
    pass


def _FalseLiteral(_ast: asts.FalseLiteral):
    _ast.semantic_type = symbols.BoolType()
    pass
