from typing import Literal, Optional
import asts
from dataclasses import dataclass, field
import symbols


@dataclass
class ScopePrintOpts:
    id: bool = False
    symtab: Optional[Literal["full", "short"]] = "short"
    parent: Optional[Literal["full", "short", "tiny"]] = "short"
    depth: bool = True
    return_type: bool = True


@dataclass
class SymbolPrintOpts:
    type: bool = False
    offset: bool = False
    id: bool = False
    scope: ScopePrintOpts = field(default_factory=ScopePrintOpts)


@dataclass
class PrettyPrintOpts:
    coord: bool = True
    symbol: SymbolPrintOpts = field(default_factory=SymbolPrintOpts)


# General idea: for each type of token, we return the unbounded IdSymbol
# The tokens that owns some scope will then resolve it to the symbolic table.

# This is the entry point for the visitor.

@dataclass
class SymbolCollector:
    symlist: list[tuple[str, str]] = field(default_factory=list)
    config: PrettyPrintOpts = field(default_factory=lambda: PrettyPrintOpts())
    virtual_id: dict[int, int] = field(default_factory=dict)

    def output(self, ast: asts.Program) -> str:
        self.program(ast)
        return "\n".join(f"{id}: {sym}" for id, sym in self.symlist)

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

    def _IntType(self, _: asts.IntType):
        pass

    def _BoolType(self, _: asts.BoolType):
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
        self.symlist.append((ast.token.value, self._Symbol(ast.symbol)))
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

    def _IntLiteral(self, _: asts.IntLiteral):
        pass

    def _TrueLiteral(self, _: asts.TrueLiteral):
        pass

    def _FalseLiteral(self, _: asts.FalseLiteral):
        pass

    def _id_of(self, o: object) -> str:
        idx = id(o)
        virt_idx = self.virtual_id.get(idx, len(self.virtual_id))
        self.virtual_id[idx] = virt_idx
        return hex(virt_idx)

    def _SymbolType(self, sym: symbols.Symbol) -> str:
        match sym:
            case symbols.IdSymbol():
                return "IdSymbol"
            case symbols.PhonySymbol():
                return "PhonySymbol"
            case symbols.Symbol():
                return "Symbol"
            case _:
                raise AssertionError(
                    f"Not valid symbol {sym.__class__.__name__}")

    def _Symtab(self, symtab: dict[str, symbols.Symbol], is_parent=False):
        if is_parent:
            return f"Symtab(id:{self._id_of(symtab)})"

        def symbol_fmt(sym: symbols.Symbol):
            return f"{self._SymbolType(sym)}(@{self._id_of(sym)})"

        symbols_str = ",".join(
            f"{ident}:{symbol_fmt(sym)}" for ident, sym in symtab.items())
        return f"Symtab(syms: [{len(symtab)}]({symbols_str}))"

    def _ScopeType(self, scope: symbols.Scope):
        match scope:
            case symbols.FuncScope():
                return "FuncScope"
            case symbols.GlobalScope():
                return "GlobalScope"
            case symbols.LocalScope():
                return "LocalScope"
            case symbols.PhonyScope():
                return "PhonyScope"
            case symbols.Scope():
                return "Scope"
        pass

    def _TypeString(self, ty: symbols.Type):
        match ty:
            case symbols.ArrayType(element_type=e_ty):
                return f"Array<{self._TypeString(e_ty)}>"
            case symbols.BoolType():
                return "bool"
            case symbols.IntType():
                return "int"
            case symbols.VoidType():
                return "void"
            case symbols.FuncType(params=params, ret=ret_ty, frame_size=fsize,
                                  param_size=psize):
                params_s = ",".join(self._TypeString(p) for p in params)
                return f"({params_s})=>{self._TypeString(ret_ty)} " +\
                    f"[{fsize=},{psize=}]"

    def _Scope(self, scope: symbols.Scope, is_parent=False):
        sym = self._Symtab(scope.symtab, is_parent)
        # print parent
        # just name, id, and depth

        def parents_gen(parent: symbols.Scope | None):
            while parent is not None:
                yield parent
                parent = parent.parent

        parents: list[symbols.Scope] = list(parents_gen(scope.parent))
        parents_str = ",".join(f"{self._ScopeType(parent)}(id:" +
                               f"{self._id_of(parent)},depth:{parent.depth()})"
                               for parent in parents)
        ret_type = f"ret:{self._TypeString(scope.get_return_type())}" \
            if isinstance(scope, symbols.FuncScope) else ""
        return f"{self._ScopeType(scope)}(@{self._id_of(scope)},sym:{sym}," +\
            f"p:[{parents_str}],{ret_type})"

    def _Symbol(self, sym: symbols.Symbol):
        type_name = self._SymbolType(sym)
        match sym:
            case symbols.IdSymbol(name=name, scope=scope, semantic_type=ty,
                                  offset=off):
                return f"{type_name}(@{self._id_of(sym)},off:{off}," +\
                    f"{self._TypeString(ty)},{self._Scope(scope)},\"{name}\")"
            case _:
                return f"{type_name}(@{self._id_of(sym)},off:{sym.offset})"
