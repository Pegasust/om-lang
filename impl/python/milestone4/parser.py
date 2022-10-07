
from scanner import Scanner
from asts import *

class Parser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner

    def error(self, msg: str):
        raise Exception(msg + " at " + str(self.scanner.peek()))

    def parse(self) -> Program:
        program = self._program()
        self.scanner.match("EOF")
        return program
    # program -> { func_decl }
    def _program(self) -> Program:
        func_decls = []
        while self.scanner.peek().kind in {'func'}:
            func_decls.append(self._func_decl())
        return Program(func_decls)
    # var_decl -> "var" ":" ID type
    def _var_decl(self) -> VarDecl:
        self.scanner.match('var')
        var_id = self.scanner.match('ID')
        self.scanner.match(':')
        var_type = self._type()
        return VarDecl(Id(var_id), var_type)
    # func_decl -> "func" ID "(" [ ID ":" type { "," ID ":" type } ] ")" [ ":" type ] compound_stmt
    def _func_decl(self) -> FuncDecl:
        self.scanner.match('func')
        func_name = self.scanner.match('ID')
        self.scanner.match('(')
        params = []
        if self.scanner.peek().kind in {'ID'}:
            param_id = self.scanner.match('ID')
            self.scanner.match(':')
            param_type = self._type()
            params.append(ParamDecl(Id(param_id), param_type))
            while self.scanner.peek().kind in {','}:
                self.scanner.match(',')
                more_param_id = self.scanner.match('ID')
                self.scanner.match(':')
                more_param_type = self._type()
                params.append(ParamDecl(Id(more_param_id), more_param_type))
        self.scanner.match(')')
        ret_type = None
        if self.scanner.peek().kind in {':'}:
            self.scanner.match(':')
            ret_type = self._type()
        compound_stmt_node = self._compound_stmt()
        return FuncDecl(Id(func_name), params, ret_type, compound_stmt_node)
    # type -> "[" [ expr ] "]" type | "int" | "bool"
    def _type(self)->Type:
        primitive_type = None
        if self.scanner.peek().kind in {'['}:
            self.scanner.match('[')
            size = None
            if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
                size = self._expr()
            self.scanner.match(']')
            primitive_type = self._type()
            return ArrayType(size, primitive_type)
        elif self.scanner.peek().kind in {'int'}:
            tok = self.scanner.match('int')
            primitive_type = IntType(tok)
        elif self.scanner.peek().kind in {'bool'}:
            tok = self.scanner.match('bool')
            primitive_type = BoolType(tok)
        else:
            self.error('syntax error')
        return primitive_type
    # assign_stmt -> designator "=" expr
    def _assign_stmt(self) -> AssignStmt:
        lhs = self._designator()
        assignment_tok = self.scanner.match('=')
        rhs = self._expr()
        return AssignStmt(lhs, rhs, assignment_tok)
    # compound_stmt -> "{" { var_decl } { statement } [ return_stmt ] "}"
    def _compound_stmt(self)->CompoundStmt:
        var_decls = []
        stmts = []
        return_stmt = None
        self.scanner.match('{')
        while self.scanner.peek().kind in {'var'}:
            var_decls.append(self._var_decl())
        while self.scanner.peek().kind in {'call', 'if', 'print', 'while', '{', 'ID'}:
            stmts.append(self._statement())
        if self.scanner.peek().kind in {'return'}:
            return_stmt = self._return_stmt()
        self.scanner.match('}')
        return CompoundStmt(var_decls, stmts, return_stmt)
    # while_stmt -> "while" expr compound_stmt
    def _while_stmt(self) -> WhileStmt:
        while_tok = self.scanner.match('while')
        condition_expr = self._expr()
        while_body = self._compound_stmt()
        return WhileStmt(condition_expr, while_body, while_tok.coord)
    # if_stmt -> "if" expr compound_stmt [ "else" compound_stmt ]
    def _if_stmt(self) -> IfStmt:
        if_tok = self.scanner.match('if')
        cond_expr = self._expr()
        if_body = self._compound_stmt()
        else_body = None
        if self.scanner.peek().kind in {'else'}:
            self.scanner.match('else')
            else_body = self._compound_stmt()
        return IfStmt(cond_expr, if_body, else_body, if_tok.coord)
    # call_stmt -> "call" call
    def _call_stmt(self) -> CallStmt:
        self.scanner.match('call')
        call_expr = self._call()
        return CallStmt(call_expr)
    # call -> ID "(" [ expr { "," expr } ] ")"
    def _call(self) -> CallExpr:
        func_call_token = self.scanner.match('ID')
        self.scanner.match('(')
        params = []
        if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
            params.append(self._expr())
            while self.scanner.peek().kind in {','}:
                self.scanner.match(',')
                params.append(self._expr())
        self.scanner.match(')')
        return CallExpr(Expr(), params, func_call_token.coord)
    # return_stmt -> "return" [ expr ]
    def _return_stmt(self) -> ReturnStmt:
        return_tok = self.scanner.match('return')
        expr = None
        if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
            expr = self._expr()
        return ReturnStmt(expr, return_tok.coord)
    # print_stmt -> "print" expr
    def _print_stmt(self) -> PrintStmt:
        self.scanner.match('print')
        expr = self._expr()
        return PrintStmt(expr)
    # statement -> assign_stmt | while_stmt | if_stmt | call_stmt | compound_stmt | print_stmt
    def _statement(self) -> Stmt:
        stmt = None
        if self.scanner.peek().kind in {'ID'}:
            stmt = self._assign_stmt()
        elif self.scanner.peek().kind in {'while'}:
            stmt = self._while_stmt()
        elif self.scanner.peek().kind in {'if'}:
            stmt = self._if_stmt()
        elif self.scanner.peek().kind in {'call'}:
            stmt = self._call_stmt()
        elif self.scanner.peek().kind in {'{'}:
            stmt = self._compound_stmt()
        elif self.scanner.peek().kind in {'print'}:
            stmt = self._print_stmt()
        else:
            self.error('syntax error')
        return stmt
    # relation -> "<" | "<=" | ">" | ">=" | "==" | "!="
    def _relation(self) -> Token:
        if self.scanner.peek().kind in {'<'}:
            return self.scanner.match('<')
        elif self.scanner.peek().kind in {'<='}:
            return self.scanner.match('<=')
        elif self.scanner.peek().kind in {'>'}:
            return self.scanner.match('>')
        elif self.scanner.peek().kind in {'>='}:
            return self.scanner.match('>=')
        elif self.scanner.peek().kind in {'=='}:
            return self.scanner.match('==')
        elif self.scanner.peek().kind in {'!='}:
            return self.scanner.match('!=')
        else:
            self.error('syntax error')
    # addop -> "+" | "-"
    def _addop(self)->Token:
        if self.scanner.peek().kind in {'+'}:
            return self.scanner.match('+')
        elif self.scanner.peek().kind in {'-'}:
            return self.scanner.match('-')
        else:
            self.error('syntax error')
    # mulop -> "*" | "/"
    def _mulop(self)->Token:
        if self.scanner.peek().kind in {'*'}:
            return self.scanner.match('*')
        elif self.scanner.peek().kind in {'/'}:
            return self.scanner.match('/')
        else:
            self.error('syntax error')
    # expr -> and_bool_expr { "or" and_bool_expr }
    def _expr(self) -> BinaryOp | UnaryOp | IntLiteral | TrueLiteral | FalseLiteral | IdExpr:
        lhs_expr = self._and_bool_expr()
        ret_expr = lhs_expr
        while self.scanner.peek().kind in {'or'}:
            op = self.scanner.match('or')
            rhs_expr = self._and_bool_expr()
            ret_expr = BinaryOp(op, ret_expr, rhs_expr)
        return ret_expr
    # and_bool_expr -> relation_expr { "and" relation_expr }
    def _and_bool_expr(self) -> IdExpr | UnaryOp | BinaryOp | IntLiteral | TrueLiteral | FalseLiteral:
        lhs_expr = self._relation_expr()
        retval = lhs_expr
        while self.scanner.peek().kind in {'and'}:
            op = self.scanner.match('and')
            rhs_expr = self._relation_expr()
            retval = BinaryOp(op, retval, rhs_expr)
        return retval
    # relation_expr -> add_expr [ relation add_expr ]
    def _relation_expr(self) -> IntLiteral | BinaryOp | UnaryOp | IdExpr | TrueLiteral | FalseLiteral:
        lhs_expr = self._add_expr()
        retval = lhs_expr
        if self.scanner.peek().kind in {'!=', '<', '<=', '==', '>', '>='}:
            op = self._relation()
            rhs_expr = self._add_expr()
            retval = BinaryOp(op, retval, rhs_expr)
        return retval
    # add_expr -> mult_expr { addop mult_expr }
    def _add_expr(self) -> BinaryOp | IntLiteral | UnaryOp | IdExpr | TrueLiteral | FalseLiteral:
        lhs_expr = self._mult_expr()
        retval = lhs_expr
        while self.scanner.peek().kind in {'+', '-'}:
            op = self._addop()
            rhs_expr = self._mult_expr()
            retval = BinaryOp(op, retval, rhs_expr)
        return retval
    # mult_expr -> unary_expr { mulop unary_expr }
    def _mult_expr(self) -> TrueLiteral | FalseLiteral | BinaryOp | UnaryOp | IntLiteral | IdExpr:
        lhs_expr = self._unary_expr()
        ret_expr = lhs_expr
        while self.scanner.peek().kind in {'*', '/'}:
            op = self._mulop()
            rhs_expr = self._unary_expr()
            ret_expr = BinaryOp(op, ret_expr, rhs_expr)
        return ret_expr
    # unary_expr -> "(" expr ")" | integral_literal | "-" unary_expr | designator
    def _unary_expr(self) -> UnaryOp | IdExpr | IntLiteral | TrueLiteral | FalseLiteral:
        retval = None
        if self.scanner.peek().kind in {'('}:
            self.scanner.match('(')
            expr = self._expr()
            self.scanner.match(')')
            retval = expr
        elif self.scanner.peek().kind in {'false', 'true', 'INT'}:
            retval = self._integral_literal()
        elif self.scanner.peek().kind in {'-'}:
            op = self.scanner.match('-')
            retval = UnaryOp(op, self._unary_expr())
        elif self.scanner.peek().kind in {'not'}:
            op = self.scanner.match('not');
            retval = UnaryOp(op, self._unary_expr())
        elif self.scanner.peek().kind in {'ID'}:
            retval = self._designator()
        else:
            self.error('syntax error')
        return retval
    # integral_literal -> INT | "true" | "false"
    def _integral_literal(self) -> IntLiteral | TrueLiteral | FalseLiteral:
        int_token = None
        if self.scanner.peek().kind in {'INT'}:
            int_token = self.scanner.match('INT')
        elif self.scanner.peek().kind in {'true'}:
            int_token = self.scanner.match('true')
            return TrueLiteral(int_token)
        elif self.scanner.peek().kind in {'false'}:
            int_token = self.scanner.match('false')
            return FalseLiteral(int_token)
        else:
            self.error('syntax error')
        return IntLiteral(int_token)
    # designator -> ID [ arguments ] { selector }
    def _designator(self) -> IdExpr:
        id_tok = self.scanner.match('ID')
        if self.scanner.peek().kind in {'('}:
            self._arguments()
        while self.scanner.peek().kind in {'['}:
            self._selector()
        return IdExpr(Id(id_tok))
    # arguments -> "(" [ expr { "," expr } ] ")"
    def _arguments(self):
        self.scanner.match('(')
        if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
            self._expr()
            while self.scanner.peek().kind in {','}:
                self.scanner.match(',')
                self._expr()
        self.scanner.match(')')
    # selector -> "[" expr "]"
    def _selector(self):
        self.scanner.match('[')
        self._expr()
        self.scanner.match(']')

