""" Syntactic analyzer """

from . import kandyerrors as kerr
from .lexer import Lexer
from .tokentype import TokenType, Token
from .ast import (AST, Empty, BinOp, UnaryOp, StarredTuple, StarredDict, Assign,
                  Var, TypeVar, Slicing, Attribute, IfExpr, UnlessExpr, IfNotNullExpr, Compound,
                  CompoundWithNoReturn, IfStatement, UnlessStatement, Number, Bool, NoneValue,
                  Undefined, String, Bytes, Tuple, List, Set, Dict, ProcedureDecl, FunctionDecl,
                  Param, Call, ScriptAction, WhileStatement, UntilStatement, ForInStatement,
                  ForFromToStatement, ForCStatement, RepeatStatement, SwitchCaseStatement,
                  SwitchCaseItem, WhenCaseStatement, WhenCaseItem, WithStatement, TryStatement,
                  ExceptBlock, ImportStatement, UsingStatement, ClassStatement, LambdaDecl,
                  DeleteStatement)


# Parser
class Parser():
    """ Parser-analyzer class: get tokens and convert it in AST nodes. """

    def __init__(self, lexer: Lexer = None):
        if lexer is None:
            lexer = Lexer()

        self.lexer = lexer
        self.current_token = None

    def error(self, token, token_type):
        """ Raise error with tokens """
        raise kerr.KandySyntaxError(f"Token Unrecognized.\nThe parser was waiting a '{token_type}', but found '{token}'.")

    def error_message(self, message):
        """ Raise Parser error """
        raise kerr.KandyParserError(message)

    def error_syntax(self, message="invalid syntax."):
        """ Raise syntax error """
        raise kerr.KandySyntaxError(message)

    def parse(self, text):
        """ Tokenize a program """
        self.lexer.load(text)
        self.current_token = self.lexer.get_next_token()
        return self.program()

    def parse_expr(self, text):
        """ Tokenize a expression """
        self.lexer.load(text)
        self.current_token = self.lexer.get_next_token()
        return self.expression()

    def eat(self, token_type):
        """ Get the next token and validate the current. """
        # print((self.current_token, token_type))

        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()

        else:
            self.error(self.current_token, token_type)

    def peek(self, tokens=1):
        """ Get the nexts tokens without eat them """
        current = self.lexer.pos
        next_token = []
        for _ in range(tokens):
            next_token.append(self.lexer.get_next_token())

        self.lexer.back(current)
        return next_token

    def back_to_token(self, token):
        """ Set lexer.pos to a prev token """
        pos = token.pos
        self.lexer.back(pos)
        self.current_token = self.lexer.get_next_token()

    def program(self):
        """
        program: statement_list
        """
        statement_list = self.statement_list()

        node = Compound()
        node.add_children(statement_list)

        self.eat(TokenType.EOF)
        return node

    def compound_statement(self, with_no_return=False, return_action=False):
        """
        compound_statement: LBRACES statement_list RBRACES
                          | BEGIN statement_list END
        """
        token = self.current_token
        if with_no_return:
            node = CompoundWithNoReturn()
        else:
            node = Compound(return_action)

        if token.type in (TokenType.BEGIN, TokenType.LBRACES):
            # Open compound
            if token.type == TokenType.BEGIN:
                self.eat(TokenType.BEGIN)

            elif token.type == TokenType.LBRACES:
                self.eat(TokenType.LBRACES)

            # Body compound
            statement_list = self.statement_list()
            node.add_children(statement_list)

            # Close compound
            if token.type == TokenType.BEGIN:
                self.eat(TokenType.END)

            elif token.type == TokenType.LBRACES:
                self.eat(TokenType.RBRACES)

        return node

    def statement_list(self):
        """
        statement_list: statement
                      | statement SEMI statement_list
        """
        nodes = []

        statement = self.statement()
        nodes.append(statement)

        while not isinstance(statement, Empty):
            if self.current_token.type in (TokenType.LBRACES, TokenType.END, TokenType.EOF):
                break

            if self.current_token.type == TokenType.SEMI:
                self.eat(TokenType.SEMI)

            statement = self.statement()
            nodes.append(statement)

        return nodes

    def statement(self, with_no_return=False, return_action=False):
        """
        statement: compound_statement
                 | assignment_statement
                 | procedure_declaration
                 | function_declaration
                 | class_statement
                 | if_statement
                 | unless_statement
                 | while_until_statement
                 | do_while_until_statement
                 | actions_statement
                 | repeat_statement
                 | for_statement
                 | switch_statement
                 | with_statement
                 | try_statement
                 | pass_statement
                 | using_statement
                 | import_statement
                 | delete_statement
                 | expression
                 | empty
        """

        token = self.current_token
        if token.type in (TokenType.BEGIN, TokenType.LBRACES):
            return self.compound_statement(with_no_return=with_no_return, return_action=return_action)

        elif token.type == TokenType.ID:
            return self.assignment_statement()

        elif token.type in (TokenType.CONST, TokenType.VAR, TokenType.DYNAMIC,
                            TokenType.STRICT, TokenType.PRIVATE, TokenType.MULTIPLE):
            return self.assignment_statement()

        elif token.type == TokenType.LOCAL:
            if self.peek()[0].type == TokenType.PROCEDURE:
                return self.procedure_declaration()

            elif self.peek()[0].type == TokenType.DEF:
                return self.function_declaration()

            elif self.peek()[0].type == TokenType.LAMBDA:
                return self.expr_lambda()

        elif token.type == TokenType.PROCEDURE:
            return self.procedure_declaration()

        elif token.type == TokenType.DEF:
            return self.function_declaration()

        elif token.type == TokenType.CLASS:
            return self.class_statement()

        elif token.type == TokenType.IF:
            return self.if_statement()

        elif token.type == TokenType.UNLESS:
            return self.unless_statement()

        elif token.type in (TokenType.WHILE, TokenType.UNTIL):
            return self.while_until_statement()

        elif token.type == TokenType.DO:
            return self.do_while_until_statement()

        elif token.type in (TokenType.RETURN, TokenType.BREAK,
                            TokenType.CONTINUE, TokenType.EXPORT):
            return self.actions_statement()

        elif token.type == TokenType.REPEAT:
            return self.repeat_statement()

        elif token.type == TokenType.FOR:
            return self.for_statement()

        elif token.type == TokenType.SWITCH:
            return self.switch_statement()

        elif token.type == TokenType.WITH:
            return self.with_statement()

        elif token.type == TokenType.TRY:
            return self.try_statement()

        elif token.type == TokenType.PASS:
            return self.pass_statement()

        elif token.type == TokenType.USING:
            return self.using_statement()

        elif token.type in (TokenType.PYTHON, TokenType.FROM, TokenType.IMPORT):
            return self.import_statement()

        elif token.type == TokenType.DELETE:
            return self.del_statement()

        else:
            expr = self.expression()

            if expr is not None:
                return expr
            else:
                return self.empty()

    # Basic-Statements:
    def pass_statement(self):
        """
        pass_statement: PASS
        """
        if self.current_token.type == TokenType.PASS:
            self.eat(TokenType.PASS)
            return Empty()

    def procedure_declaration(self):
        """
        procedure_declaration: (LOCAL)? PROCEDURE ID LPARENT
                                param_list_declaration
                                RPARENT (COLON statement|compound_statement)
        """
        local_type = False
        if self.current_token.type == TokenType.LOCAL:
            self.eat(TokenType.LOCAL)
            local_type = True

        self.eat(TokenType.PROCEDURE)
        variable = self.current_token
        self.eat(TokenType.ID)
        self.eat(TokenType.LPARENT)
        params = self.param_list_declaration()
        self.eat(TokenType.RPARENT)
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
            block = self.statement(with_no_return=True)
        else:
            block = self.compound_statement(with_no_return=True)

        if local_type:
            return ProcedureDecl(variable, params, block, is_local=True)

        else:
            return ProcedureDecl(variable, params, block)

    def function_declaration(self):
        """
        function_declaration: (LOCAL)? DEF function_variable_declaration LPARENT
                               param_list_declaration
                               RPARENT (COLON statement|arrow_statement|compound_statement)
        """
        local_type = False
        if self.current_token.type == TokenType.LOCAL:
            self.eat(TokenType.LOCAL)
            local_type = True

        self.eat(TokenType.DEF)
        type_, variable = self.function_variable_declaration()
        self.eat(TokenType.LPARENT)
        params = self.param_list_declaration()
        self.eat(TokenType.RPARENT)

        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
            block = self.statement()

        elif self.current_token.type == TokenType.ARROW:
            block = self.arrow_statement(return_action=True)

        else:
            block = self.compound_statement()

        if local_type:
            return FunctionDecl(variable, params, block, type_, is_local=True)

        else:
            return FunctionDecl(variable, params, block, type_)

    def function_type(self):
        """
        function_type: (STRICT)? ID
                     | (DYNAMIC)
                     | (STRICT)? MULTIPLE LPARENT ID (COMMA (ID)?)* RPARENT
        """
        strict = False
        if self.current_token.type == TokenType.STRICT:
            strict = True
            self.eat(TokenType.STRICT)

        token = self.current_token
        if token.type == TokenType.DYNAMIC:
            self.eat(token.type)
            if strict:
                self.error_syntax("The 'dynamic' variables can't be 'strict'.")

            return TypeVar("DYNAMIC", token)

        elif token.type == TokenType.MULTIPLE:
            self.eat(token.type)
            types = []
            self.eat(TokenType.LPARENT)
            if self.current_token.type == TokenType.ID:
                types.append(self.current_token)
                self.eat(TokenType.ID)

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if not self.current_token.type == TokenType.RPARENT:
                        types.append(self.current_token)
                        self.eat(TokenType.ID)

            self.eat(TokenType.RPARENT)
            return TypeVar("MULTIPLE", types, strict)

        elif token.type == TokenType.ID:
            # self.eat(token.type)
            variable = self.variable_with_attributes(can_use_call=False)
            return TypeVar("ID", token, strict, variable=variable)

        elif token.type == TokenType.CONST:
            self.eat(token.type)
            self.error_syntax("[CONST] Functions can't return an 'const' value.")
            return None

        elif token.type == TokenType.VAR:
            self.eat(token.type)
            self.error_syntax("[VAR] Functions can't return an 'auto-detect-type' value.")
            return None

    def function_variable_declaration(self):
        """
        function_variable_declaration: function_type variable
                                     | variable
        """
        type_ = self.function_type()

        if self.current_token.type == TokenType.ID:
            var = self.variable()

        else:
            if type_ is None:
                self.error_syntax()

            elif type_.token.type == TokenType.ID:
                var = (type_.variable)
                type_ = None

            else:
                self.error_syntax()

        return type_, var

    def param_list_declaration(self):
        """
        param_list_declaration: (param_declaration
                                (COMMA (param_declaration)?)*
                                (COMMA (param_declaration_starred))? )?
                              | param_declaration_starred
        """
        params = []
        can_be_positional = True
        starred = False
        if not self.current_token.type == TokenType.RPARENT:
            if self.current_token.type in (TokenType.MULT, TokenType.POW):
                can_be_positional = False
                params.extend(self.param_declaration_starred())
                starred = True
            else:
                param, can_be_positional = self.param_declaration(can_be_positional)
                params.append(param)

            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)

                if self.current_token.type in (TokenType.MULT, TokenType.POW):
                    can_be_positional = False
                    params.extend(self.param_declaration_starred())
                    starred = True

                elif not self.current_token.type == TokenType.RPARENT:
                    if starred:
                        self.error_syntax("Invalid syntax")

                    param, can_be_positional = self.param_declaration(can_be_positional)
                    params.append(param)

        return params

    def param_declaration(self, can_be_positional=True):
        """
        param_declaration: variable_declaration
                         | variable_declaration ASSIGN expression
        """
        vartype, var = self.variable_declaration()
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            value = self.expression()
            node = Param(vartype, var, value)
            can_be_positional = False

        elif can_be_positional:
            node = Param(vartype, var)

        else:
            self.error_message("non-default argument follows default argument.")

        return node, can_be_positional

    def param_declaration_starred(self):
        """
        param_declaration_starred: MULT variable_declaration
                                 | POW variable_declaration
        """
        params = []

        if self.current_token.type == TokenType.MULT:
            self.eat(self.current_token.type)
            vartype, var = self.variable_declaration()
            if vartype is not None:
                self.error_syntax("The Starred-syntax don't support 'variable-type' assignment.")

            params.append(Param(vartype, var, tuple_type=True))

        if self.current_token.type == TokenType.POW:
            self.eat(self.current_token.type)
            vartype, var = self.variable_declaration()
            if vartype is not None:
                self.error_syntax("The Starred-syntax don't support 'variable-type' assignment.")

            params.append(Param(vartype, var, dict_type=True))

        return params

    def assignment_statement(self):
        """
        assignment_statement: variable_declaration (ASSIGN|QUESTION_ASSIGN) expression
                            | variable_declaration (any_expression_tokens) (ASSIGN|QUESTION_ASSIGN) expression
                            | variable_declaration
        """
        master_token = self.current_token
        type_, left = self.variable_declaration()
        token = self.current_token
        if token.type in (TokenType.QUESTION_ASSIGN, TokenType.ASSIGN):
            self.eat(token.type)
            right = self.expression()
            node = Assign(type_, left, token, right)

        elif self.is_expression_token() and self.peek()[0].type in (TokenType.QUESTION_ASSIGN, TokenType.ASSIGN):
            token_op = token
            self.eat(token_op.type)
            token = self.current_token
            self.eat(token.type)
            right = self.expression()
            node = Assign(type_, left, token, right, op=token_op)

        elif type_ is None:
            self.back_to_token(master_token)
            return self.expression()

        elif token.type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            assign_token = Token(TokenType.ASSIGN, "=", pos=token.pos, lineno=token.lineno, column=token.column)  # FakeToken
            node = Assign(type_, left, assign_token, Undefined(None))

        else:
            self.error_syntax()

        return node

    def variable_declaration(self):
        """
        variable_declaration: variable_type variable (attributes)?
                            | variable (attributes)?
        """
        type_ = self.variable_type()

        if self.current_token.type == TokenType.ID:
            var = self.variable()

        else:
            if type_ is None:
                self.error_syntax()

            elif type_.token.type == TokenType.ID:
                if type_.private:
                    self.error_syntax("Invalid Private syntax. Example of use: private dynamic variable = value")

                var = (type_.variable)
                type_ = None

            else:
                self.error_syntax()

        var = self.attributes(var)

        return type_, var

    def variable_type(self):
        """
        variable_type: (PRIVATE)? (STRICT)? (VAR|ID)
                     | (PRIVATE)? (CONST|DYNAMIC)
                     | (PRIVATE)? (STRICT)? MULTIPLE LPARENT ID (COMMA (ID)?)* RPARENT
        """
        private = False
        if self.current_token.type == TokenType.PRIVATE:
            private = True
            self.eat(TokenType.PRIVATE)

        strict = False
        if self.current_token.type == TokenType.STRICT:
            strict = True
            self.eat(TokenType.STRICT)

        token = self.current_token
        if token.type == TokenType.VAR:
            self.eat(token.type)
            return TypeVar("VAR", token, strict=strict, private=private)

        elif token.type == TokenType.DYNAMIC:
            self.eat(token.type)
            if strict:
                self.error_syntax("The 'dynamic' variables can't be 'strict'.")

            return TypeVar("DYNAMIC", token, private=private)

        elif token.type == TokenType.MULTIPLE:
            self.eat(token.type)
            types = []
            self.eat(TokenType.LPARENT)
            if self.current_token.type == TokenType.ID:
                variable = self.variable_with_attributes(can_use_call=False)
                types.append(variable)

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if not self.current_token.type == TokenType.RPARENT:
                        variable = self.variable_with_attributes(can_use_call=False)
                        types.append(variable)

            self.eat(TokenType.RPARENT)
            return TypeVar("MULTIPLE", types, strict=strict, private=private)

        elif token.type == TokenType.ID:
            # self.eat(token.type)
            variable = self.variable_with_attributes(can_use_call=False)
            return TypeVar("ID", token, strict=strict, private=private, variable=variable)

        elif token.type == TokenType.CONST:
            self.eat(token.type)
            if strict:
                self.error_syntax("The 'const' variables can't be 'strict'.")

            return TypeVar("CONST", token, private=private)

    def variable(self):
        """
        variable: ID
        """
        token = self.current_token
        self.eat(TokenType.ID)
        return Var(token)

    def variable_with_attributes(self, can_use_call=True):
        """
        variable_with_attributes: variable (attributes)?
        """
        var = self.variable()
        var = self.attributes(var, can_use_call)
        return var

    def arrow_statement(self, return_action=False):
        """
        arrow_statement: ARROW expression
        """
        token = self.current_token
        self.eat(TokenType.ARROW)
        block = Compound(return_action=return_action)
        block.add_child(ScriptAction(
            token=Token(
                TokenType.RETURN,
                "return",
                pos=token.pos,
                lineno=token.lineno,
                column=token.column),
            expression=self.expression()
        ))
        return block

    # ScriptActions:
    def actions_statement(self):
        """
        actions_statement: RETURN (expression)
                         | EXPORT
                         | CONTINUE ((COLON)? expression)?
                         | BREAK  ((COLON)? expression)?
        """
        token = self.current_token
        expr = None

        if token.type == TokenType.RETURN:
            self.eat(TokenType.RETURN)
            expr = self.expression()

        elif token.type in (TokenType.CONTINUE, TokenType.BREAK):
            self.eat(token.type)
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)

            expr = self.expression()

        elif token.type == TokenType.EXPORT:
            self.eat(TokenType.EXPORT)

        return ScriptAction(token, expression=expr)

    def del_statement(self):
        """
        del_statement: DELETE expression
        """
        if self.current_token.type == TokenType.DELETE:
            self.eat(TokenType.DELETE)

            expression = self.expression()
            return DeleteStatement(expression)

    # Estructuras:
    def if_statement(self):
        """
        if_statement: IF (expression) then_block
                     [((ELIF|ELSE IF) (expression) then_block)*
                     [else_block]?]
        """
        token = self.current_token
        if token.type == TokenType.IF:
            self.eat(TokenType.IF)
            expressions = []
            else_statement = None

            condition = self.expression()
            then_block = self.then_block()

            expressions.append((condition, then_block))

            while self.current_token.type in (TokenType.ELIF, TokenType.ELSE):
                if self.current_token.type == TokenType.ELIF:
                    self.eat(TokenType.ELIF)
                    condition = self.expression()
                    then_block = self.then_block()

                    expressions.append((condition, then_block))

                elif self.current_token.type == TokenType.ELSE:
                    if self.peek()[0].type == TokenType.IF:
                        self.eat(TokenType.ELSE)
                        self.eat(TokenType.IF)
                        condition = self.expression()
                        then_block = self.then_block()

                        expressions.append((condition, then_block))

                    else:
                        else_statement = self.else_block()
                        break

            return IfStatement(tuple(expressions), else_statement)

    def unless_statement(self):
        """
        unless_statement: UNLESS (expression) then_block
                        [(ELSE UNLESS (expression) then_block)*
                        [ELSE (COLON)? statement]?]
        """
        token = self.current_token
        if token.type == TokenType.UNLESS:
            self.eat(TokenType.UNLESS)
            expressions = []
            else_statement = None

            condition = self.expression()
            then_block = self.then_block()

            expressions.append((condition, then_block))

            while self.current_token.type == TokenType.ELSE:
                if self.peek()[0].type == TokenType.UNLESS:
                    self.eat(TokenType.ELSE)
                    self.eat(TokenType.UNLESS)
                    condition = self.expression()
                    then_block = self.then_block()

                    expressions.append((condition, then_block))

                else:
                    else_statement = self.else_block()
                    break

            return UnlessStatement(tuple(expressions), else_statement)

    def then_block(self, return_action=True):
        """
        then_block: THEN statement
                  | COLON statement
                  | arrow_statement
                  | compound_statement
        """

        if self.current_token.type in (TokenType.THEN, TokenType.COLON):
            self.eat(self.current_token.type)
            return self.statement(return_action=return_action)

        elif self.current_token.type == TokenType.ARROW:
            return self.arrow_statement(return_action=return_action)

        else:
            return self.compound_statement(return_action=return_action)

    def else_block(self, return_action=True):
        """
        else_statement: ELSE (COLON)? (statement|arrow_statement)
        """
        self.eat(TokenType.ELSE)
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)

        if self.current_token.type == TokenType.ARROW:
            statement = self.arrow_statement(return_action=return_action)

        else:
            statement = self.statement(return_action=return_action)

        return statement

    def while_until_statement(self):
        """
        while_until_statement: (UNTIL|WHILE) (expression) [AS variable_with_attributes] do_block
                               [else_block]?]
        """
        token = self.current_token
        if token.type in (TokenType.WHILE, TokenType.UNTIL):
            self.eat(token.type)
            else_statement = None
            name = None

            condition = self.expression()

            if self.current_token.type == TokenType.AS:
                self.eat(TokenType.AS)
                name = self.variable_with_attributes()

            do_block = self.do_block()

            if self.current_token.type == TokenType.ELSE:
                else_statement = self.else_block()

            if token.type == TokenType.WHILE:
                return WhileStatement(condition, do_block, else_statement, name, do_first=False)

            elif token.type == TokenType.UNTIL:
                return UntilStatement(condition, do_block, else_statement, name, do_first=False)

    def do_while_until_statement(self):
        """
        do_while_until_statement: DO (COLON)? statement (WHILE|UNTIL) expression
                                [AS variable_with_attributes]? [else_block]?
        """
        if self.current_token.type == TokenType.DO:
            self.eat(TokenType.DO)

            else_statement = None
            name = None

            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)

            do_block = self.statement()
            token = self.current_token
            if token.type in (TokenType.UNTIL, TokenType.WHILE):
                self.eat(token.type)
                condition = self.expression()

                if self.current_token.type == TokenType.AS:
                    self.eat(TokenType.AS)
                    name = self.variable_with_attributes()

                if self.current_token.type == TokenType.ELSE:
                    else_statement = self.else_block()

                if token.type == TokenType.UNTIL:
                    return UntilStatement(condition, do_block, else_statement, name, do_first=True)

                elif token.type == TokenType.WHILE:
                    return WhileStatement(condition, do_block, else_statement, name, do_first=True)

    def do_block(self, return_action=True):
        """
        do_block: DO statement
                | COLON statement
                | arrow_statement
                | compound_statement
        """

        if self.current_token.type in (TokenType.DO, TokenType.COLON):
            self.eat(self.current_token.type)
            return self.statement(return_action=return_action)

        elif self.current_token.type == TokenType.ARROW:
            return self.arrow_statement(return_action=return_action)

        else:
            return self.compound_statement(return_action=return_action)

    def repeat_statement(self):
        """
        repeat_statement: REPEAT (expression) [AS variable_with_attributes] do_block
                          [else_block]?
        """
        token = self.current_token
        if token.type == TokenType.REPEAT:
            self.eat(TokenType.REPEAT)
            else_statement = None
            name = None

            value = self.expression()

            if self.current_token.type == TokenType.AS:
                self.eat(TokenType.AS)
                name = self.variable_with_attributes()

            do_block = self.do_block()

            if self.current_token.type == TokenType.ELSE:
                else_statement = self.else_block()

            return RepeatStatement(value, do_block, else_statement, name)

    def for_statement(self):
        """
        for_statement: (for_c|for_in|for_from_to) for_block

        for_c:  FOR LPARENT assignment_statement SEMI expression SEMI assignment_statement RPARENT
        for_in: FOR (variable_with_attributes (COMMA variable_with_attributes)*) IN expression [TAKE expression]
        for_from_to: FOR (variable_with_attributes) FROM expression TO expression

        for_block:  [AS variable_with_attributes] do_block [else_block]
        """

        if self.current_token.type == TokenType.FOR:
            self.eat(TokenType.FOR)
            name = None
            else_statement = None
            data = (None,)

            token = self.current_token
            # For-C
            if token.type == TokenType.LPARENT:
                self.eat(TokenType.LPARENT)
                assign = self.assignment_statement()
                self.eat(TokenType.SEMI)
                condition = self.expression()
                self.eat(TokenType.SEMI)
                increment = self.assignment_statement()
                self.eat(TokenType.RPARENT)

                data = (ForCStatement, assign, condition, increment)

            # For-From-To / For-In
            else:
                variables = [self.variable_with_attributes()]
                # For-From-To
                if self.current_token.type == TokenType.FROM:
                    self.eat(TokenType.FROM)
                    value_start = self.expression()
                    self.eat(TokenType.TO)
                    value_end = self.expression()
                    data = (ForFromToStatement, variables[0], value_start, value_end)

                # For-In
                else:
                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        variables.append(self.variable_with_attributes())

                    self.eat(TokenType.IN)
                    expression = self.expression()

                    take = None

                    if self.current_token.type == TokenType.TAKE:
                        self.eat(TokenType.TAKE)
                        take = self.expression()

                    data = (ForInStatement, variables, expression, take)

            if self.current_token.type == TokenType.AS:
                self.eat(TokenType.AS)
                name = self.variable_with_attributes()

            do_block = self.do_block()

            if self.current_token.type == TokenType.ELSE:
                else_statement = self.else_block()

            if data[0] == ForCStatement:
                return ForCStatement(data[1], data[2], data[3], do_block, else_statement, name)

            elif data[0] == ForFromToStatement:
                return ForFromToStatement(data[1], data[2], data[3], do_block, else_statement, name)

            elif data[0] == ForInStatement:
                return ForInStatement(data[1], data[2], data[3], do_block, else_statement, name)

            else:
                self.error_syntax("Invalid 'For Statement'.")

        return None

    def switch_statement(self):
        """
        switch_statement: SWITCH expression (COLON)? LBRACES
                         switch_cases_block
                         (DEFAULT COLON statement)? RBRACES
        """
        token = self.current_token
        if token.type == TokenType.SWITCH:
            self.eat(TokenType.SWITCH)
            expression = self.expression()

            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)

            self.eat(TokenType.LBRACES)

            cases = []
            while self.current_token.type == TokenType.CASE:
                cases.append(self.switch_cases_block())

            default_block = None
            if self.current_token.type == TokenType.DEFAULT:
                self.eat(TokenType.DEFAULT)
                self.eat(TokenType.COLON)
                default_block = self.statement()

            self.eat(TokenType.RBRACES)

            return SwitchCaseStatement(expression, cases, default_block)

    def switch_cases_block(self):
        """
        cases_block: (CASE expression COLON (statement (break_statement)?)?)*
        """
        cases = []

        while self.current_token.type == TokenType.CASE:
            self.eat(TokenType.CASE)
            cases.append(self.expression())

            self.eat(TokenType.COLON)

            if self.current_token.type == TokenType.CASE:
                continue

            else:
                statement = self.statement()
                if self.current_token.type == TokenType.BREAK:
                    break_statement = self.actions_statement()
                    if isinstance(statement, Compound):
                        statement.add_child(break_statement)
                    else:
                        compound = Compound(return_action=True)
                        compound.add_child(statement)
                        compound.add_child(break_statement)
                        statement = compound

                return SwitchCaseItem(cases, statement)

    def when_statement(self):
        """
        when_statement: WHEN expression (COLON)? LBRACES
                        when_cases_block
                        (DEFAULT COLON expression)? RBRACES
        """
        token = self.current_token
        if token.type == TokenType.WHEN:
            self.eat(TokenType.WHEN)
            expression = self.expression()

            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)

            self.eat(TokenType.LBRACES)

            cases = []
            while self.current_token.type == TokenType.CASE:
                cases.append(self.when_cases_block())

            default_block = None
            if self.current_token.type == TokenType.DEFAULT:
                self.eat(TokenType.DEFAULT)
                self.eat(TokenType.COLON)
                default_block = self.statement()

            self.eat(TokenType.RBRACES)

            return WhenCaseStatement(expression, cases, default_block)

    def when_cases_block(self):
        """
        when_cases_block: (CASE expression COLON (expression)?)*
        """
        cases = []

        while self.current_token.type == TokenType.CASE:
            self.eat(TokenType.CASE)
            cases.append(self.expression())

            self.eat(TokenType.COLON)

            if self.current_token.type == TokenType.CASE:
                continue

            else:
                expression = self.expression()

                return WhenCaseItem(cases, expression)

    def with_statement(self):
        """
        with_statement: WITH expression (AS variable_with_attributes) do_block
        """

        if self.current_token.type == TokenType.WITH:
            self.eat(TokenType.WITH)
            variable = None
            expression = self.expression()

            if self.current_token.type == TokenType.AS:
                self.eat(TokenType.AS)
                variable = self.variable_with_attributes()

            block = self.do_block()
            return WithStatement(expression, variable, block)

    def try_statement(self):
        """
        try_statement: TRY do_block (except_block)+  [else_block]? [FINALLY do_block]?
                     | TRY do_block [else_block]? FINALLY do_block
        """
        if self.current_token.type == TokenType.TRY:
            self.eat(TokenType.TRY)

            try_block = self.do_block()

            except_blocks = []
            while self.current_token.type == TokenType.EXCEPT:
                except_blocks.append(self.except_block())

            else_statement = None
            if self.current_token.type == TokenType.ELSE:
                else_statement = self.else_block()

            finally_block = None
            if self.current_token.type == TokenType.FINALLY:
                self.eat(TokenType.FINALLY)
                finally_block = self.do_block()

            if else_statement is None and self.current_token.type == TokenType.ELSE:
                else_statement = self.else_block()

            return TryStatement(try_block, except_blocks, finally_block, else_statement)

    def except_block(self):
        """
        except_block: EXCEPT expression (AS variable_with_attributes)? do_block
        """
        if self.current_token.type == TokenType.EXCEPT:
            self.eat(TokenType.EXCEPT)
            expression = self.expression()

            variable = None
            if self.current_token.type == TokenType.AS:
                self.eat(TokenType.AS)
                variable = self.variable_with_attributes()

            block = self.do_block()

            return ExceptBlock(expression, variable, block)

    def import_statement(self):
        """
        import_statement: [PYTHON]? [FROM variable (COMMA variable)*] IMPORT module_names
        """
        python_import = False
        package = None
        if self.current_token.type == TokenType.PYTHON:
            self.eat(TokenType.PYTHON)
            python_import = True

        if self.current_token.type == TokenType.FROM:
            self.eat(TokenType.FROM)
            package = [self.variable()]

            while self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                package.append(self.variable())

        if self.current_token.type == TokenType.IMPORT:
            self.eat(TokenType.IMPORT)
            import_module = [self.module_names()]

            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                import_module.append(self.module_names())

            return ImportStatement(import_module, package, python_import)

        else:
            self.error_syntax()

    def module_names(self):
        """
        module_name: variable (AS variable)?
        """
        variable = None
        module_name = self.variable()

        if self.current_token.type == TokenType.AS:
            self.eat(TokenType.AS)
            variable = self.variable_with_attributes()

        return [module_name, variable]

    def using_statement(self):
        """
        using_statement: USING variable_with_attributes do_block
        """
        if self.current_token.type == TokenType.USING:
            self.eat(TokenType.USING)
            variable = self.variable_with_attributes()

            block = self.do_block()

            return UsingStatement(variable, block)

    def class_statement(self):
        """
        class_statement: CLASS variable LPARENT (variable_with_attributes
                        (COMMA variable_with_attributes)*)? RPARENT
                        compound_statement
        """

        if self.current_token.type == TokenType.CLASS:
            self.eat(TokenType.CLASS)
            variable = self.variable()

            self.eat(TokenType.LPARENT)
            objects = []
            if not self.current_token.type == TokenType.RPARENT:
                objects.append(self.variable_with_attributes())

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current_token != TokenType.RPARENT:
                        objects.append(self.variable_with_attributes())

            self.eat(TokenType.RPARENT)

            block = self.compound_statement(with_no_return=True)

            return ClassStatement(variable, objects, block)

    # Expressions
    def empty(self):
        """
        empty:
        """
        return Empty()

    def is_expression_token(self):
        """
        Return True if the current token is in:
        BIT_OR, BIT_XOR, BIT_AND, SHIFT_L, SHIFT_R, PLUS, MINUS,
        MULT, DIV, FLOORDIV, MOD, SUBMOD, POW, MATRIX_MUL
        """
        return (self.current_token.type in (TokenType.BIT_OR, TokenType.BIT_XOR, TokenType.BIT_AND,
                                            TokenType.SHIFT_L, TokenType.SHIFT_R,
                                            TokenType.PLUS, TokenType.MINUS,
                                            TokenType.MULT, TokenType.DIV, TokenType.FLOORDIV,
                                            TokenType.MOD, TokenType.SUBMOD,
                                            TokenType.POW, TokenType.MATRIX_MUL))

    def expression(self):
        """
        expresion: expr_lambda
        """
        return self.expr_lambda()

    def expr_lambda(self):
        """
        expr_lambda: (LOCAL)? LAMBDA [LBRACKET function_type RBRACKET]? LPARENT param_list_declaration RPARENT
                    (COLON statement|arrow_statement|compound_statement)
        """

        token = self.current_token
        local_type = False
        if token.type == TokenType.LOCAL:
            self.eat(TokenType.LOCAL)
            local_type = True

        if self.current_token.type == TokenType.LAMBDA:
            self.eat(TokenType.LAMBDA)

            type_ = None
            if self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                type_ = self.function_type()
                self.eat(TokenType.RBRACKET)

            self.eat(TokenType.LPARENT)
            params = self.param_list_declaration()
            self.eat(TokenType.RPARENT)

            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
                block = self.statement()

            elif self.current_token.type == TokenType.ARROW:
                block = self.arrow_statement(return_action=True)

            else:
                block = self.compound_statement()

            if local_type:
                return LambdaDecl(params, block, type_, is_local=True)

            else:
                return LambdaDecl(params, block, type_)

        if local_type:
            self.error_syntax("Invalid Lambda declaration.")

        else:
            return self.expr_if_unless()

    def expr_if_unless(self):
        """
        expr_if_unless -> expr_or
                        | expr_or IF expr_or ELSE expr_or
                        | expr_or UNLESS expr_or ELSE expr_or
                        | expr_or QUESTION expr_or COLON expr_or
                        | expr_or QUESTION QUESTION expr_or
        """
        node = self.expr_or()

        while self.current_token.type in (TokenType.IF, TokenType.UNLESS, TokenType.QUESTION):
            token = self.current_token
            self.eat(token.type)
            if token.type == TokenType.QUESTION and self.current_token.type == TokenType.QUESTION:
                self.eat(token.type)
                node = IfNotNullExpr(expression=node, value_false=self.expr_or())

            elif token.type == TokenType.QUESTION:
                value_true = self.expr_or()
                self.eat(TokenType.COLON)
                value_false = self.expr_or()
                node = IfExpr(
                    condition=node,
                    value_true=value_true,
                    value_false=value_false
                )

            elif token.type == TokenType.IF:
                condition = self.expr_or()
                if not self.current_token.type == TokenType.ELSE:
                    self.back_to_token(token)
                    return node

                self.eat(TokenType.ELSE)
                value_false = self.expr_or()
                node = IfExpr(
                    condition=condition,
                    value_true=node,
                    value_false=value_false
                )

            elif token.type == TokenType.UNLESS:
                condition = self.expr_or()
                if not self.current_token.type == TokenType.ELSE:
                    self.back_to_token(token)
                    return node

                self.eat(TokenType.ELSE)
                value_false = self.expr_or()
                node = UnlessExpr(
                    condition=condition,
                    value_true=node,
                    value_false=value_false
                )

            else:
                break

        return node

    def expr_or(self):
        """
        expr_or -> expr_xor
                 | expr_xor (OR expr_xor)
        """
        node = self.expr_xor()

        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_xor())

        return node

    def expr_xor(self):
        """
        expr_xor -> expr_and
                  | expr_and (OR expr_and)
        """
        node = self.expr_and()

        while self.current_token.type == TokenType.XOR:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_and())

        return node

    def expr_and(self):
        """
        expr_and -> expr_not
                  | expr_not (AND expr_not)
        """
        node = self.expr_not()

        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_not())

        return node

    def expr_not(self):
        """
        expr_not -> expr_comparisons
                  | NOT expr_comparisons
        """
        if self.current_token.type == TokenType.NOT:
            token = self.current_token
            self.eat(token.type)
            node = UnaryOp(op=token, value=self.expr_not())

        else:
            node = self.expr_comparisons()

        return node

    def expr_comparisons(self):
        """
        expr_comparisons -> expr_bitwise_or
                          | expr_bitwise_or ((IS|IS NOT|IN|NOT IN|LESSER|LESSER_EQUALS|GREATEN|
                                            GREATEN_EQUALS|EQUALS|NOT_EQUALS) expr_bitwise_or)*
        """
        node = self.expr_bitwise_or()

        while self.current_token.type in (TokenType.IS, TokenType.IN, TokenType.NOT,
                                          TokenType.LESSER, TokenType.LESSER_EQUALS,
                                          TokenType.GREATEN, TokenType.GREATEN_EQUALS,
                                          TokenType.EQUALS, TokenType.NOT_EQUALS):
            token = self.current_token
            self.eat(token.type)
            if token.type == TokenType.NOT:
                if self.current_token.type == TokenType.IN:
                    in_token = self.current_token
                    self.eat(TokenType.IN)
                    node = UnaryOp(token, BinOp(left=node, op=in_token, right=self.expr_bitwise_or()))

            else:
                node = BinOp(left=node, op=token, right=self.expr_bitwise_or())
                if self.current_token.type == TokenType.NOT and token.type == TokenType.IS:
                    not_token = self.current_token
                    self.eat(TokenType.NOT)
                    node = UnaryOp(not_token, node)

        return node

    def expr_bitwise_or(self):
        """
        expr_bitwise_or -> expr_bitwise_xor
                         | expr_bitwise_xor (BIT_XOR expr_bitwise_xor)
        """
        node = self.expr_bitwise_xor()

        while self.current_token.type == TokenType.BIT_OR:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_bitwise_xor())

        return node

    def expr_bitwise_xor(self):
        """
        expr_bitwise_xor -> expr_bitwise_and
                          | expr_bitwise_and (BIT_XOR expr_bitwise_and)
        """
        node = self.expr_bitwise_and()

        while self.current_token.type == TokenType.BIT_XOR:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_bitwise_and())

        return node

    def expr_bitwise_and(self):
        """
        expr_bitwise_and -> expr_shifts
                          | expr_shifts (BIT_AND expr_shifts)
        """
        node = self.expr_shifts()

        while self.current_token.type == TokenType.BIT_AND:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_shifts())

        return node

    def expr_shifts(self):
        """
        expr_shifts -> expr_plus
                     | expr_plus ((PLUS|MINUS) expr_plus)*
        """
        node = self.expr_plus()

        while self.current_token.type in (TokenType.SHIFT_L, TokenType.SHIFT_R):
            token = self.current_token
            if token.type in (TokenType.SHIFT_L, TokenType.SHIFT_R):
                self.eat(token.type)
                node = BinOp(left=node, op=token, right=self.expr_plus())

        return node

    def expr_plus(self):
        """
        expr_plus -> expr_term
                   | expr_term ((PLUS|MINUS) expr_term)*
        """
        node = self.expr_term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type in (TokenType.PLUS, TokenType.MINUS):
                self.eat(token.type)
                node = BinOp(left=node, op=token, right=self.expr_term())

        return node

    def expr_term(self):
        """
        expr_term -> expr_unary
                   | expr_unary ((MULT|DIV|FLOORDIV|MOD|SUBMOD) expr_unary)*
        """
        node = self.expr_unary()

        while self.current_token.type in (TokenType.MULT, TokenType.DIV, TokenType.FLOORDIV,
                                          TokenType.MOD, TokenType.SUBMOD, TokenType.MATRIX_MUL):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.expr_unary())

        return node

    def expr_unary(self):
        """
        expr_unary: expr_pow
                  | (PLUS|MINUS|BIT_NOT|EXCLAMATION) expr_pow
        """
        token = self.current_token
        if token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.BIT_NOT, TokenType.EXCLAMATION):
            self.eat(token.type)
            return UnaryOp(token, self.expr_pow())

        else:
            return self.expr_pow()

    def expr_pow(self):
        """
        expr_pow -> expr_attr
                  | expr_attr (POW expr_attr)
        """
        node = self.expr_attr()

        while self.current_token.type == TokenType.POW:
            token = self.current_token
            if token.type == TokenType.POW:
                self.eat(token.type)
                node = BinOp(left=node, op=token, right=self.expr_attr())

        return node

    def expr_attr(self):
        """
        expr_attr: expr_value attributes
                 | expr_value
        """
        node = self.expr_value()
        return self.attributes(node)

    def expr_value(self):
        """
        expr_value : literal
                   | literal_tuple_expression
                   | literal_list
                   | literal_dict_set
                   | expr_variable
                   | compound_statement
                   | MULT expression
                   | POW expression
                   | when_statement
        """
        token = self.current_token

        if token.type in (TokenType.STRING, TokenType.BYTES, TokenType.INTEGER,
                          TokenType.FLOAT, TokenType.BOOL, TokenType.NONE,
                          TokenType.UNDEFINED):
            return self.literal()

        elif token.type == TokenType.LPARENT:
            return self.literal_tuple_expression()

        elif token.type == TokenType.LBRACKET:
            return self.literal_list()

        elif token.type == TokenType.DOLLAR:
            return self.literal_dict_set()

        elif token.type == TokenType.ID:
            return self.expr_variable()

        elif token.type in (TokenType.LBRACES, TokenType.BEGIN):
            return self.compound_statement()

        elif token.type == TokenType.MULT:
            self.eat(token.type)
            return StarredTuple(token, self.expression())

        elif token.type == TokenType.POW:
            self.eat(token.type)
            return StarredDict(token, self.expression())

        elif token.type == TokenType.WHEN:
            return self.when_statement()

    def expr_variable(self):
        """
        expr_variable: variable_with_attributes
                     | variable_with_attributes EXPR_ASSIGN expression
        """
        var = self.variable_with_attributes()
        token = self.current_token
        if token.type == TokenType.EXPR_ASSIGN:
            self.eat(TokenType.EXPR_ASSIGN)
            return Assign(None, var, token, self.expression())

        return var

    def attributes(self, node, can_use_call=True):
        """
        attributes: ... LBRACKET expression (COLON expression){0,2} RPARENT
                  | ... LPARENT argument_list kwargument_list RPARENT
                  | ... (DOT variable)*
                  | ...
        """
        while self.current_token.type in (TokenType.DOT, TokenType.LBRACKET, TokenType.LPARENT):
            token = self.current_token
            if token.type == TokenType.LPARENT:
                if not can_use_call:
                    break

                self.eat(TokenType.LPARENT)
                params = self.argument_list()
                kwparams = self.kw_argument_list()
                self.eat(TokenType.RPARENT)

                node = Call(node, params, kwparams)

            elif token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                node = Attribute(value=node, token=self.variable())

            # [::] don't match
            elif token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                slicing = [self.expression()]

                if self.current_token.type == TokenType.COLON:
                    self.eat(TokenType.COLON)
                    slicing.append(self.expression())

                    if self.current_token.type == TokenType.COLON:
                        self.eat(TokenType.COLON)
                        slicing.append(self.expression())

                node = Slicing(value=node, slicing=slicing)
                self.eat(TokenType.RBRACKET)

        return node

    def literal(self) -> AST:
        """
        literal: STRING
               | BYTES
               | INTEGER
               | FLOAT
               | BOOL
               | NONE
               | UNDEFINED
        """
        token = self.current_token
        if token.type in (TokenType.INTEGER, TokenType.FLOAT):
            self.eat(token.type)
            return Number(token)

        elif token.type == (TokenType.STRING):
            self.eat(token.type)
            return String(token)

        elif token.type == (TokenType.BYTES):
            self.eat(token.type)
            return Bytes(token)

        elif token.type == (TokenType.BOOL):
            self.eat(token.type)
            return Bool(token)

        elif token.type == (TokenType.NONE):
            self.eat(token.type)
            return NoneValue(token)

        elif token.type == (TokenType.UNDEFINED):
            self.eat(token.type)
            return Undefined(token)

    def literal_tuple_expression(self):
        """
        literal_tuple: LPARENT expression (COMMA (expression)?)+ RPARENT
                     | LPARENT RPARENT

        literal_expression: LPARENT expression RPARENT
        """
        self.eat(TokenType.LPARENT)
        if self.current_token.type == TokenType.RPARENT:
            self.eat(TokenType.RPARENT)
            return Tuple()

        node = self.expression()

        if self.current_token.type == TokenType.COMMA:
            node = Tuple(node)

            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                if not self.current_token.type == TokenType.RPARENT:
                    node.add_value(self.expression())

        self.eat(TokenType.RPARENT)
        return node

    def literal_list(self):
        """
        literal_list: LBRACKET expression (COMMA (expression)?)+ RBRACKET
                    | LBRACKET expression RBRACKET
                    | LBRACKET RBRACKET
        """
        node = List()
        self.eat(TokenType.LBRACKET)
        if self.current_token.type == TokenType.RBRACKET:
            self.eat(TokenType.RBRACKET)
            return node

        node.add_value(self.expression())

        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            if not self.current_token.type == TokenType.RBRACKET:
                node.add_value(self.expression())

        self.eat(TokenType.RBRACKET)
        return node

    def literal_dict_set(self):
        """
        literal_dict: DOLLAR LBRACES expression COLON expression (COMMA (literal_dict)?)+ RBRACES
                    : DOLLAR LBRACES RBRACES

        literal_set: DOLLAR LBRACES expression (COMMA (expression)?)+ RBRACES
        """
        self.eat(TokenType.DOLLAR)

        if self.current_token.type == TokenType.LBRACES:
            self.eat(TokenType.LBRACES)
            if self.current_token.type == TokenType.RBRACES:
                self.eat(TokenType.RBRACES)
                return Dict()

            node = self.expression()

            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
                key = node
                value = self.expression()
                node = Dict((key, value))

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if not self.current_token.type == TokenType.RBRACES:
                        # key: value
                        key = self.expression()
                        self.eat(TokenType.COLON)
                        value = self.expression()

                        node.add_value(key, value)

            else:
                node = Set(node)

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if not self.current_token.type == TokenType.RBRACES:
                        node.add_value(self.expression())

            self.eat(TokenType.RBRACES)
            return node

    def argument_list(self):
        """
        argument_list: expression (COMMA (argument_list)?)?
        """
        params = []
        if not self.current_token.type == TokenType.RPARENT:
            if not (self.current_token.type == TokenType.ID and self.peek(1)[0].type == TokenType.ASSIGN):
                params.append(self.expression())

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if (self.current_token.type == TokenType.ID and self.peek(1)[0].type == TokenType.ASSIGN):
                        break

                    if not self.current_token.type == TokenType.RPARENT:
                        params.append(self.expression())

        return params

    def kw_argument_list(self):
        """
        kw_argument_list: variable ASSIGN expression (COMMA (kw_argument_list)?)?
        """
        kwparams = {}
        if not self.current_token.type == TokenType.RPARENT:
            if self.current_token.type == TokenType.ID and self.peek(1)[0].type == TokenType.ASSIGN:
                name = self.variable().token.value
                self.eat(TokenType.ASSIGN)
                if name in kwparams:
                    raise TypeError(f"got multiple values for keyword argument {name!r}")

                kwparams[name] = self.expression()

                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if not self.current_token.type == TokenType.RPARENT:
                        if self.current_token.type in (TokenType.POW, TokenType.MULT):
                            kwparams[len(kwparams)+5] = self.expression()
                        else:
                            name = self.variable().token.value
                            self.eat(TokenType.ASSIGN)
                            if name in kwparams:
                                raise TypeError(f"got multiple values for keyword argument {name!r}")

                            kwparams[name] = self.expression()

        return kwparams
