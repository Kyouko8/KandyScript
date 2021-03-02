"""KandyScript main file"""
from enum import Enum

# kandymodules
from kandyitems.basics import (KandyTypeError, KandyObject, KandyInt, KandyFloat)


# Tokens Class
class TokenType(Enum):
    # Operations
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    POW = "**"
    DIV = "/"
    FLOORDIV = "//"
    MOD = "%"
    SUBMOD = "%%"

    LPARENT = "("
    RPARENT = ")"

    # Type
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"

    # Reserved keywords

    # Control
    EOF = "EOF"


class Token():
    def __init__(self, type_, value, pos, column, lineno):
        self.type = type_
        self.value = value
        self.pos = pos
        self.column = column
        self.lineno = lineno

    def __str__(self):
        return f"Token(type_={self.type}, value={self.value}, pos={self.pos}, column={self.column}, lineno={self.lineno})"

    def __repr__(self):
        return f"Token(type_={self.type}, value={self.value}, pos={self.pos}, column={self.column}, lineno={self.lineno})"


# LexerAnalyzer
class Lexer():
    def __init__(self):
        self.pos = 0
        self.column = 0
        self.lineno = 0
        self.text = ""
        self.len_text = 0
        self.current_char = ""

    def load(self, text):
        self.pos = 0
        self.column = 0
        self.lineno = 0
        self.text = text
        self.len_text = len(text)
        self.current_char = ""
        self.advance()

    def error(self, chars):
        print(f"LexerError: Unrecognized char at position {self.pos} (line {self.lineno} column {self.column})\nChar: {chars}")

    def advance(self):
        if self.pos >= self.len_text:
            self.current_char = None

        else:
            self.current_char = self.text[self.pos]
            self.pos += 1
            if self.current_char == "\n":
                self.lineno += 1
                self.column = 0
            else:
                self.column += 1

    def ignore(self, chars=1):
        if self.pos >= self.len_text:
            self.current_char = None

        else:
            text = self.text[self.pos:self.pos+abs(chars)-1]
            for i in text:
                if i == "\n":
                    self.lineno += 1
                    self.column = 0
                else:
                    self.column += 1

            self.current_char = self.text[self.pos+abs(chars)-1]
            self.pos += 1

    def peek(self, chars=1):
        if (self.pos) >= self.len_text:
            return None
        elif (self.pos+chars) >= self.len_text:
            return self.text[self.pos:]
        else:
            return self.text[self.pos:self.pos + chars]

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char in (" ", "\n", "\t"):
                self.ignore_whitespaces()

            elif self.current_char in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."):
                return self.match_number()

            elif self.current_char == "*" and self.peek() == "*":  # POW
                self.ignore()
                self.advance()
                return Token(
                    type_=TokenType.POW,
                    value="**",
                    pos=self.pos,
                    column=self.column,
                    lineno=self.lineno
                )

            elif self.current_char == "%" and self.peek() == "%":  # SUBMOD
                self.ignore()
                self.advance()
                return Token(
                    type_=TokenType.SUBMOD,
                    value="%%",
                    pos=self.pos,
                    column=self.column,
                    lineno=self.lineno
                )

            elif self.current_char == "/" and self.peek() == "/":  # FLOORDIV
                self.ignore()
                self.advance()
                return Token(
                    type_=TokenType.FLOORDIV,
                    value="//",
                    pos=self.pos,
                    column=self.column,
                    lineno=self.lineno
                )

            else:
                # match token of 1 len char.
                try:
                    token_type = TokenType(self.current_char)
                    self.advance()

                except ValueError:
                    return self.error(self.current_char)

                return Token(
                    type_=token_type,
                    value=self.current_char,
                    pos=self.pos,
                    column=self.column,
                    lineno=self.lineno
                )

        return Token(type_=TokenType.EOF, value=None, pos=self.pos, column=self.column, lineno=self.lineno)

    def ignore_whitespaces(self):
        while self.current_char in (" ", "\n", "\t"):
            self.advance()

    def match_number(self):
        pos_start, column_start, lineno_start = self.pos, self.column, self.lineno

        number = ""
        if self.current_char == "0" and self.peek() in ("x", "o", "b", "d", "X", "O", "B", "D"):
            number += "0"
            self.advance()
            chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")

            if self.current_char in ("x", "X"):
                number += self.current_char.upper()
                chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F")
                self.advance()

            elif self.current_char in ("o", "O",):
                number += self.current_char.upper()
                chars = ("0", "1", "2", "3", "4", "5", "6", "7")
                self.advance()

            elif self.current_char in ("b", "B",):
                number += self.current_char.upper()
                chars = ("0", "1")
                self.advance()

            while self.current_char in chars:
                number += self.current_char.upper()
                self.advance()

            return Token(
                type_=TokenType.INTEGER,
                value=KandyInt(int(number, base=len(chars))),
                pos=pos_start,
                column=column_start,
                lineno=lineno_start
            )

        else:
            if self.current_char == ".":
                number += "0."
                self.advance()

            while self.current_char in ("0", "1", "2", "3", "4", "5", "6",
                                        "7", "8", "9", ".", "e", "E"):
                if self.current_char == ".":
                    if "." in number or "E" in number:
                        break

                elif self.current_char in ("e", "E"):
                    if "E" in number:
                        break

                number += self.current_char.upper()
                self.advance()

            if "." in number or "E" in number:
                return Token(
                    type_=TokenType.FLOAT,
                    value=KandyFloat(float(number)),
                    pos=pos_start,
                    column=column_start,
                    lineno=lineno_start
                )

            else:
                return Token(
                    type_=TokenType.INTEGER,
                    value=KandyInt(int(number)),
                    pos=pos_start,
                    column=column_start,
                    lineno=lineno_start
                )


# AST
class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = op
        self.right = right


class UnaryOp(AST):
    def __init__(self, op, value):
        self.token = op
        self.value = value


class Number(AST):
    def __init__(self, token):
        self.value = token.value
        self.token = token


# Parser/Interpreter
class Parser():
    def __init__(self, lexer: Lexer = None):
        if lexer is None:
            lexer = Lexer()

        self.lexer = lexer
        self.current_token = None

    def error(self, token, token_type):
        print(f"ParserError: Token Unrecognized.\nThe parser was waiting a '{token_type}', but found '{token}'.")

    def parse(self, text):
        self.lexer.load(text)
        self.current_token = self.lexer.get_next_token()
        return self.program()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()

        else:
            self.error(self.current_token, token_type)

    def program(self):
        """
        program: expr_plus
        """
        return self.expr_plus()

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
        expr_term -> expr_pow
                   | expr_pow ((MULT|DIV|FLOORDIV|MOD) expr_pow)*
        """
        node = self.expr_pow()

        while self.current_token.type in (TokenType.MULT, TokenType.DIV, TokenType.FLOORDIV,
                                          TokenType.MOD, TokenType.SUBMOD):
            token = self.current_token
            if token.type in (TokenType.MULT, TokenType.DIV, TokenType.FLOORDIV,
                              TokenType.MOD, TokenType.SUBMOD):
                self.eat(token.type)
                node = BinOp(left=node, op=token, right=self.expr_pow())

        return node

    def expr_pow(self):
        """
        expr_pow -> factor
                  | factor (POW factor)
        """
        node = self.factor()

        while self.current_token.type in (TokenType.POW,):
            token = self.current_token
            if token.type == TokenType.POW:
                self.eat(token.type)
                node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """
        factor : number
               | LPARENT expr RPARENT
               | variable
        """
        token = self.current_token

        if token.type in (TokenType.INTEGER, TokenType.FLOAT):
            return self.number()

        elif token.type == TokenType.LPARENT:
            self.eat(TokenType.LPARENT)
            node = self.expr_plus()
            self.eat(TokenType.RPARENT)
            return node

    def number(self):
        """
        number -> INTEGER | FLOAT
        """
        token = self.current_token
        if token.type in (TokenType.INTEGER, TokenType.FLOAT):
            token = self.current_token
            self.eat(token.type)
            return Number(token)


# Node Visitor
class NodeVisitor():
    def visit(self, node):
        method_name = "visit_"+type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


# Interpreter
class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        """ Apply operations and return the result """
        token = node.token
        left = self.visit(node.left)
        right = self.visit(node.right)

        if not isinstance(left, KandyObject) or not isinstance(right, KandyObject):
            raise KandyTypeError("The objects aren't KandyObjects or any sub-type.")

        if token.type == TokenType.PLUS:
            commands = (left.m_add, right.m_radd)

        elif token.type == TokenType.MINUS:
            commands = (left.m_sub, right.m_rsub)

        elif token.type == TokenType.MULT:
            commands = (left.m_mult, right.m_rmult)

        elif token.type == TokenType.POW:
            commands = (left.m_pow, right.m_rpow)

        elif token.type == TokenType.DIV:
            commands = (left.m_div, right.m_rdiv)

        elif token.type == TokenType.FLOORDIV:
            commands = (left.m_floordiv, right.m_rfloordiv)

        elif token.type == TokenType.MOD:
            commands = (left.m_mod, right.m_rmod)

        elif token.type == TokenType.SUBMOD:
            commands = (left.m_submod, right.m_rsubmod)

        # Apply command
        try:
            result = commands[0](right)

        except (KandyTypeError, NotImplementedError):
            result = commands[1](left)

        return result

    def visit_Number(self, node):
        return node.value


def parse(text):
    lexer = Lexer()
    parser = Parser(lexer)
    root_tree = parser.parse(text)
    interpreter = Interpreter(parser)
    result = interpreter.visit(root_tree)

    return dict(lexer=lexer, parser=parser, interpreter=interpreter, ast=root_tree, result=result)


if __name__ == "__main__":
    print(parse("7 + .0")['result'])
    print(parse("7 + 3 * ( 10/ ( 12 / ( 3 + 1 ) - 1 )) / ( 2 + 3 ) - 5 - 3 + ( 8.2 ) + 10.2 ** 2")['result'])
