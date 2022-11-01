import asts
from dataclasses import dataclass

@dataclass
class PPrinter:
    def program(self, ast: asts.Program):
        self._Program(ast)


    def _Program(self, ast: asts.Program):
        # Assume that each Omega file is self-contained.
        # This means each file is a module/executable without any linking
        # just yet!
        # monofile repo
        for decl in ast.decls:
            self._FuncDecl(decl)


    def _Stmt(self, ast: asts.Stmt):
        if isinstance(ast, asts.AssignStmt):
            return self._AssignStmt(ast)
        elif isinstance(ast, asts.IfStmt):
            return self._IfStmt(ast)
        elif isinstance(ast, asts.WhileStmt):
            return self._WhileStmt(ast)
        elif isinstance(ast, asts.CallStmt):
            return self._CallStmt(ast)
        elif isinstance(ast, asts.CompoundStmt):
            return self._CompoundStmt(ast)
        elif isinstance(ast, asts.PrintStmt):
            return self._PrintStmt(ast)
        elif isinstance(ast, asts.ReturnStmt):
            return self._ReturnStmt(ast)
        else:
            assert False, f"self._Stmt() not implemented for {ast}"


    def _Expr(self, ast: asts.Expr):
        if isinstance(ast, asts.BinaryOp):
            self._BinaryOp(ast)
        elif isinstance(ast, asts.UnaryOp):
            self._UnaryOp(ast)
        elif isinstance(ast, asts.CallExpr):
            self._CallExpr(ast)
        elif isinstance(ast, asts.IdExpr):
            self._IdExpr(ast)
        elif isinstance(ast, asts.ArrayCell):
            self._ArrayCell(ast)
        elif isinstance(ast, asts.IntLiteral):
            self._IntLiteral(ast)
        elif isinstance(ast, asts.TrueLiteral):
            self._TrueLiteral(ast)
        elif isinstance(ast, asts.FalseLiteral):
            self._FalseLiteral(ast)
        else:
            assert False, f"self._Expr() not implemented for {type(ast)}"
        pass


    def _Type(self, ast: asts.Type):
        if isinstance(ast, asts.IntType):
            return self._IntType(ast)
        elif isinstance(ast, asts.BoolType):
            return self._BoolType(ast)
        elif isinstance(ast, asts.ArrayType):
            return self._ArrayType(ast)
        else:
            assert False, f"self._Type() not implemented for {type(ast)}"


    def _VarDecl(self, ast: asts.VarDecl):
        self._Id(ast.id)
        self._Type(ast.type_ast)
        pass


    def _ParamDecl(self, ast: asts.ParamDecl):
        self._Id(ast.id)
        self._Type(ast.type_ast)
        return ast


    def _IntType(self, ast: asts.IntType):
        pass


    def _BoolType(self, ast: asts.BoolType):
        pass

    def _ArrayType(self, ast: asts.ArrayType):
        self._Type(ast.element_type_ast)
        if ast.size is not None:
            self._Expr(ast.size)
        pass


    def _IdExpr(self, ast: asts.IdExpr):
        self._Id(ast.id)
        pass


    def _CallExpr(self, ast: asts.CallExpr):
        self._Expr(ast.fn)
        for arg in ast.args:
            self._Expr(arg)
        pass


    def _Id(self, ast: asts.Id):
        pass

    def _AssignStmt(self, ast: asts.AssignStmt):
        self._Expr(ast.lhs)
        self._Expr(ast.rhs)
        pass


    def _BinaryOp(self, ast: asts.BinaryOp):
        self._Expr(ast.left)
        self._Expr(ast.right)
        pass


    def _UnaryOp(self, ast: asts.UnaryOp):
        self._Expr(ast.expr)
        pass


    def _PrintStmt(self, ast: asts.PrintStmt):
        self._Expr(ast.expr)
        pass


    def _IfStmt(self, ast: asts.IfStmt):
        self._Expr(ast.expr)
        self._CompoundStmt(ast.thenStmt)
        if ast.elseStmt is not None:
            self._CompoundStmt(ast.elseStmt)
        pass

    def _WhileStmt(self, ast: asts.WhileStmt):
        self._Expr(ast.expr)
        self._CompoundStmt(ast.stmt)
        pass


    def _CallStmt(self, ast: asts.CallStmt):
        self._CallExpr(ast.call)
        pass


    def _CompoundStmt(self, ast: asts.CompoundStmt):
        for decl in ast.decls:
            self._VarDecl(decl)

        for stmt in ast.stmts:
            self._Stmt(stmt)

        if ast.return_stmt is not None:
            self._Stmt(ast.return_stmt)
        pass


    def _FuncDecl(self, ast: asts.FuncDecl):
        self._Id(ast.id)

        for param in ast.params:
            self._ParamDecl(param)
        if ast.ret_type_ast is not None:
            self._Type(ast.ret_type_ast)
        # assign function type of this function
        self._CompoundStmt(ast.body)
        


    def _ReturnStmt(self, ast: asts.ReturnStmt):
        if ast.expr is not None:
            self._Expr(ast.expr)


    def _ArrayCell(self, ast: asts.ArrayCell):
        self._Expr(ast.arr)
        self._Expr(ast.idx)


    def _IntLiteral(self, _ast: asts.IntLiteral):
        pass


    def _TrueLiteral(self, _ast: asts.TrueLiteral):
        pass


    def _FalseLiteral(self,_ast: asts.FalseLiteral):
        pass

