
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
    # var_decl -> "var" ID type
    def _var_decl(self) -> VarDecl:
        self.scanner.match('var')
        var_id = self.scanner.match('ID')
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
        retval = Type()
        if self.scanner.peek().kind in {'['}:
            self.scanner.match('[')
            if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
                self._expr()
            self.scanner.match(']')
            self._type()
        elif self.scanner.peek().kind in {'int'}:
            self.scanner.match('int')
        elif self.scanner.peek().kind in {'bool'}:
            self.scanner.match('bool')
        else:
            self.error('syntax error')
        return retval
    # assign_stmt -> designator "=" expr
    def _assign_stmt(self) -> AssignStmt:
        self._designator()
        self.scanner.match('=')
        self._expr()
    # compound_stmt -> "{" { var_decl } { statement } [ return_stmt ] "}"
    def _compound_stmt(self)->CompoundStmt:
        self.scanner.match('{')
        while self.scanner.peek().kind in {'var'}:
            self._var_decl()
        while self.scanner.peek().kind in {'call', 'if', 'print', 'while', '{', 'ID'}:
            self._statement()
        if self.scanner.peek().kind in {'return'}:
            self._return_stmt()
        self.scanner.match('}')
    # while_stmt -> "while" expr compound_stmt
    def _while_stmt(self) -> WhileStmt:
        self.scanner.match('while')
        self._expr()
        self._compound_stmt()
    # if_stmt -> "if" expr compound_stmt [ "else" compound_stmt ]
    def _if_stmt(self) -> IfStmt:
        self.scanner.match('if')
        self._expr()
        self._compound_stmt()
        if self.scanner.peek().kind in {'else'}:
            self.scanner.match('else')
            self._compound_stmt()
    # call_stmt -> "call" call
    def _call_stmt(self) -> CallStmt:
        self.scanner.match('call')
        self._call()
    # call -> ID "(" [ expr { "," expr } ] ")"
    def _call(self) -> CallExpr:
        self.scanner.match('ID')
        self.scanner.match('(')
        if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
            self._expr()
            while self.scanner.peek().kind in {','}:
                self.scanner.match(',')
                self._expr()
        self.scanner.match(')')
    # return_stmt -> "return" [ expr ]
    def _return_stmt(self) -> ReturnStmt:
        self.scanner.match('return')
        if self.scanner.peek().kind in {'(', '-', 'false', 'true', 'ID', 'INT'}:
            self._expr()
    # print_stmt -> "print" expr
    def _print_stmt(self) -> PrintStmt:
        self.scanner.match('print')
        self._expr()
    # statement -> assign_stmt | while_stmt | if_stmt | call_stmt | compound_stmt | print_stmt
    def _statement(self) -> Stmt:
        if self.scanner.peek().kind in {'ID'}:
            self._assign_stmt()
        elif self.scanner.peek().kind in {'while'}:
            self._while_stmt()
        elif self.scanner.peek().kind in {'if'}:
            self._if_stmt()
        elif self.scanner.peek().kind in {'call'}:
            self._call_stmt()
        elif self.scanner.peek().kind in {'{'}:
            self._compound_stmt()
        elif self.scanner.peek().kind in {'print'}:
            self._print_stmt()
        else:
            self.error('syntax error')
    # relation -> "<" | "<=" | ">" | ">=" | "==" | "!="
    def _relation(self):
        if self.scanner.peek().kind in {'<'}:
            self.scanner.match('<')
        elif self.scanner.peek().kind in {'<='}:
            self.scanner.match('<=')
        elif self.scanner.peek().kind in {'>'}:
            self.scanner.match('>')
        elif self.scanner.peek().kind in {'>='}:
            self.scanner.match('>=')
        elif self.scanner.peek().kind in {'=='}:
            self.scanner.match('==')
        elif self.scanner.peek().kind in {'!='}:
            self.scanner.match('!=')
        else:
            self.error('syntax error')
    # addop -> "+" | "-"
    def _addop(self):
        if self.scanner.peek().kind in {'+'}:
            self.scanner.match('+')
        elif self.scanner.peek().kind in {'-'}:
            self.scanner.match('-')
        else:
            self.error('syntax error')
    # mulop -> "*" | "/"
    def _mulop(self):
        if self.scanner.peek().kind in {'*'}:
            self.scanner.match('*')
        elif self.scanner.peek().kind in {'/'}:
            self.scanner.match('/')
        else:
            self.error('syntax error')
    # expr -> and_bool_expr { "or" and_bool_expr }
    def _expr(self) -> Expr:
        self._and_bool_expr()
        while self.scanner.peek().kind in {'or'}:
            self.scanner.match('or')
            self._and_bool_expr()
    # and_bool_expr -> relation_expr { "and" relation_expr }
    def _and_bool_expr(self) -> Expr:
        self._relation_expr()
        while self.scanner.peek().kind in {'and'}:
            self.scanner.match('and')
            self._relation_expr()
    # relation_expr -> add_expr [ relation add_expr ]
    def _relation_expr(self) -> Expr:
        self._add_expr()
        if self.scanner.peek().kind in {'!=', '<', '<=', '==', '>', '>='}:
            self._relation()
            self._add_expr()
    # add_expr -> mult_expr { addop mult_expr }
    def _add_expr(self) -> Expr:
        self._mult_expr()
        while self.scanner.peek().kind in {'+', '-'}:
            self._addop()
            self._mult_expr()
    # mult_expr -> unary_expr { mulop unary_expr }
    def _mult_expr(self) -> Expr:
        self._unary_expr()
        while self.scanner.peek().kind in {'*', '/'}:
            self._mulop()
            self._unary_expr()
    # unary_expr -> "(" expr ")" | integral_literal | "-" unary_expr | designator
    def _unary_expr(self) -> Expr:
        if self.scanner.peek().kind in {'('}:
            self.scanner.match('(')
            self._expr()
            self.scanner.match(')')
        elif self.scanner.peek().kind in {'false', 'true', 'INT'}:
            self._integral_literal()
        elif self.scanner.peek().kind in {'-'}:
            self.scanner.match('-')
            self._unary_expr()
        elif self.scanner.peek().kind in {'ID'}:
            self._designator()
        else:
            self.error('syntax error')
    # integral_literal -> INT | "true" | "false"
    def _integral_literal(self) -> IntLiteral:
        int_token = None
        if self.scanner.peek().kind in {'INT'}:
            int_token = self.scanner.match('INT')
        elif self.scanner.peek().kind in {'true'}:
            int_token = self.scanner.match('true')
        elif self.scanner.peek().kind in {'false'}:
            int_token = self.scanner.match('false')
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
