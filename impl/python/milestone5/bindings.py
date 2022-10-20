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
        func_symb = _FuncDecl(decl)
        func_symb.scope = global_scope
        global_scope.symtab[func_symb.name] = func_symb


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
    id_symb.set_type(var_type)
    return id_symb


def _ParamDecl(ast: asts.ParamDecl):
    id_symb = _Id(ast.id)
    id_symb.set_type(_Type(ast.type_ast))
    return id_symb


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
    return _Id(ast.id)


def _CallExpr(ast: asts.CallExpr):
    _Expr(ast.fn)
    for arg in ast.args:
        _Expr(arg)


def _Id(ast: asts.Id):
    ast.symbol = symbols.IdSymbol(ast.token.value, symbols.PhonyScope())
    ast.symbol.name = ast.token.value
    return ast.symbol



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
    local_scope = ast.local_scope

    for decl in ast.decls:
        decl_id_symb = _VarDecl(decl)
        if decl_id_symb.name in local_scope.symtab.keys():
            error.error(f"Var \"{decl_id_symb.name}\" declared more than once",
                        decl.id.token.coord)
        local_scope.symtab[decl_id_symb.name] = decl_id_symb
        decl_id_symb.scope = local_scope

    for stmt in ast.stmts:
        stmt_symb = _Stmt(stmt)
        if stmt_symb:
            stmt_symb.parent = local_scope

    if ast.return_stmt is not None:
        ast.return_stmt.enclosing_scope = local_scope
        ret_symb = _Stmt(ast.return_stmt)
        if ret_symb:
            ret_symb.parent = local_scope

    return local_scope


def _FuncDecl(ast: asts.FuncDecl):
    id_symb = _Id(ast.id)
    func_scope = ast.func_scope

    param_symbs = [_ParamDecl(param) for param in ast.params]
    for param, param_symb in zip(ast.params,param_symbs):
        if param_symb.name in func_scope.symtab.keys():
            error.error(
                f"Param \"{param_symb.name}\" declared more than once",
                param.id.token.coord
            )
        func_scope.symtab[param_symb.name] = param_symb
        param_symb.scope = func_scope

    ret_type = None
    if ast.ret_type_ast is not None:
        ret_type = _Type(ast.ret_type_ast)
    # assign function type of this function
    id_symb.set_type(
        symbols.FuncType([p.get_type() for p in param_symbs], ret_type)
    )

    # parse the statements within the function
    ast.body.local_scope = symbols.LocalScope(func_scope)
    _CompoundStmt(ast.body)
    return id_symb


def _ReturnStmt(ast: asts.ReturnStmt):
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
