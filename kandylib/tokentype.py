""" KandyTokensClass """

from enum import Enum


# Tokens Class
class TokenType(Enum):
    """TokenType List"""
    # Operations
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    POW = "**"
    DIV = "/"
    FLOORDIV = "//"
    MOD = "%"
    SUBMOD = "%%"
    BIT_OR = "|"
    BIT_AND = "&"
    BIT_XOR = "^"
    SHIFT_L = "<<"
    SHIFT_R = ">>"
    BIT_NOT = "~"
    MATRIX_MUL = "@"

    # Comparations
    EQUALS = "=="
    LESSER = "<"
    LESSER_EQUALS = "<="
    GREATEN = ">"
    GREATEN_EQUALS = ">="
    NOT_EQUALS = "!="

    # Groups
    LPARENT = "("
    RPARENT = ")"
    LBRACKET = "["
    RBRACKET = "]"
    LBRACES = "{"
    RBRACES = "}"

    # Structure
    DOT = "."
    COMMA = ","
    SEMI = ";"
    COLON = ":"
    QUESTION = "?"
    EXCLAMATION = "!"
    DOLLAR = "$"
    ARROW = "=>"

    # Assigns
    ASSIGN = "="
    EXPR_ASSIGN = ":="
    QUESTION_ASSIGN = "?="

    # Type
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BYTES = "BYTES"
    BOOL = "BOOL"
    NONE = "NONE"
    UNDEFINED = "UNDEFINED"

    # Reserved keywords
    BEGIN = "begin"
    VAR = "var"
    DYNAMIC = "dynamic"
    MULTIPLE = "multiple"
    CONST = "const"
    STRICT = "strict"
    PRIVATE = "private"
    LOCAL = "local"
    IN = "in"
    AS = "as"
    IS = "is"
    NOT = "not"
    AND = "and"
    OR = "or"
    XOR = "xor"
    PASS = "pass"
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    UNLESS = "unless"
    REPEAT = "repeat"
    WHILE = "while"
    UNTIL = "until"
    DO = "do"
    FOR = "for"
    THEN = "then"
    TAKE = "take"
    FROM = "from"
    TO = "to"
    SWITCH = "switch"
    WHEN = "when"
    CASE = "case"
    DEFAULT = "default"
    CLASS = "class"
    PROCEDURE = "proc"
    DEF = "def"
    LAMBDA = "lambda"
    RETURN = "return"
    # YIELD = "yield"  # Not Supported yet
    CONTINUE = "continue"
    BREAK = "break"
    DELETE = "del"
    TRY = "try"
    EXCEPT = "except"
    FINALLY = "finally"
    RAISE = "raise"
    WITH = "with"
    USING = "using"
    EXPORT = "export"
    IMPORT = "import"
    PYTHON = "python"
    END = "end"

    # Control
    ID = "ID"
    EOF = "EOF"


class Token():
    """ Token object for Parser """

    def __init__(self, type_, value, pos, column, lineno):
        self.type = type_
        self.value = value
        self.pos = pos
        self.column = column
        self.lineno = lineno

    def __str__(self):
        return f"Token(type_={self.type}, value={self.value!r}, pos={self.pos}, lineno={self.lineno}, column={self.column})"

    def __repr__(self):
        return f"Token(type_={self.type}, value={self.value!r}, pos={self.pos}, lineno={self.lineno}, column={self.column})"


# Reserved keywords:
def _build_reserved_keywords():

    tt_list = list(TokenType)
    tt_begin = tt_list.index(TokenType.BEGIN)
    tt_end = tt_list.index(TokenType.END)

    _reserved_keyword = {
        token.value: token
        for token in tt_list[tt_begin:tt_end+1]
    }

    return _reserved_keyword


RESERVED_KEYWORDS = _build_reserved_keywords()
