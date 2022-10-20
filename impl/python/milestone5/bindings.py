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
        func_symb = _FuncDecl(decl)
        func_symb.scope.parent = global_scope
        global_scope.symtab[func_symb.name] = func_symb
        # print(f"func_decl: {decl}, func_symb: {func_symb}")
    print(f"===  AST  ===\n{ast}")


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
        _IntType(ast)
    elif isinstance(ast, asts.BoolType):
        _BoolType(ast)
    elif isinstance(ast, asts.ArrayType):
        _ArrayType(ast)
    else:
        assert False, f"_Type() not implemented for {type(ast)}"


def _VarDecl(ast: asts.VarDecl):
    id_symb = _Id(ast.id)
    _Type(ast.type_ast)
    return id_symb


def _ParamDecl(ast: asts.ParamDecl):
    id_symb = _Id(ast.id)
    _Type(ast.type_ast)
    return id_symb


def _IntType(ast: asts.IntType):
    pass


def _BoolType(ast: asts.BoolType):
    pass


def _ArrayType(ast: asts.ArrayType):
    _Type(ast.element_type_ast)
    if ast.size is not None:
        _Expr(ast.size)


def _IdExpr(ast: asts.IdExpr):
    return _Id(ast.id)


def _CallExpr(ast: asts.CallExpr):
    _Expr(ast.fn)
    for arg in ast.args:
        _Expr(arg)


def _Id(ast: asts.Id):
    ast.symbol = symbols.IdSymbol(ast.token.value, symbols.PhonyScope())
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
    local_scope = symbols.LocalScope(symbols.PhonyScope())
    for decl in ast.decls:
        decl_id_symb = _VarDecl(decl)
        decl_id_symb.scope = local_scope
        local_scope.symtab[decl_id_symb.name] = decl_id_symb
        print(f"_CompoundStmt: decl: {decl_id_symb}")
    for stmt in ast.stmts:
        # How do we handle compound stmt within compound stmt?
        stmt_symb = _Stmt(stmt)
        if stmt_symb:
            stmt_symb.parent = local_scope
    if ast.return_stmt is not None:
        ret_symb = _Stmt(ast.return_stmt)
        if ret_symb:
            ret_symb.parent = local_scope
    ast.local_scope = local_scope
    return local_scope


def _FuncDecl(ast: asts.FuncDecl):
    id_symb = _Id(ast.id)
    id_symb.scope = symbols.FuncScope(None)
    func_scope = id_symb.scope
    for param in ast.params:
        param_symb = _ParamDecl(param)
        param_symb.scope = func_scope
        func_scope.symtab[param_symb.name] = param_symb
    if ast.ret_type_ast is not None:
        _Type(ast.ret_type_ast)
    compound_scope = _CompoundStmt(ast.body)
    compound_scope.parent = func_scope
    ast.func_scope = func_scope
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
