""" Lexical analyzer """

from . import kandyerrors as kerr
from .tokentype import TokenType, Token, RESERVED_KEYWORDS

# LexerAnalyzer


class Lexer():
    def __init__(self):
        self.pos = 0
        self.column = 0
        self.lineno = 1
        self.text = ""
        self.len_text = 0
        self.current_char = ""

    def load(self, text):
        self.pos = 0
        self.column = 0
        self.lineno = 1
        self.text = text
        self.len_text = len(text)
        self.current_char = ""
        self.advance()

    def error(self, chars):
        raise kerr.KandyLexerError(f"Unrecognized character at position {self.pos} (line {self.lineno} column {self.column})\nCharacter: {chars}")

    def back(self, new_pos):
        new_pos -= 1
        self.pos = new_pos

        self.lineno = 1
        self.column = 0
        for i in self.text[:new_pos]:
            if i == "\n":
                self.lineno += 1
                self.column = 0
            else:
                self.column += 1

        self.advance()

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

    def get_remaining_text(self):
        if self.pos >= self.len_text:
            return ""

        return self.text[self.pos:]

    def get_consumed_text(self):
        if (self.text) is not None:
            return self.text[:min(self.len_text, self.pos)]

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
            return ""
        elif (self.pos+chars) >= self.len_text:
            return self.text[self.pos:]
        else:
            return self.text[self.pos:self.pos + chars]

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char in (" ", "\r", "\n", "\t"):
                self.ignore_whitespaces()
                continue

            elif self.current_char == "#":
                self.comment()
                continue

            elif self.current_char.isdigit() or self.current_char == "." and self.peek().isdigit():
                return self.match_number()

            elif self.current_char.lower() in ("r", "p", "b", "n", "f") and self.peek() in ("'", '"'):
                return self.match_string()

            elif self.current_char in ("'", '"'):
                return self.match_string()

            elif self.current_char.isalpha() or self.current_char == "_":
                return self.match_id()

            elif self.current_char+self.peek() in ("==", "!=", ">=", "<=", "<<", ">>", "=>",
                                                   "**", "%%", "//", ":=", "?="):
                # match token of 2 len char in the list.
                try:
                    char = self.current_char+self.peek()
                    token_type = TokenType(char)
                    self.advance()
                    self.advance()

                except ValueError:
                    return self.error(char)

                return Token(
                    type_=token_type,
                    value=char,
                    pos=self.pos,
                    column=self.column,
                    lineno=self.lineno
                )

            else:
                # match token of 1 len char.
                try:
                    pos, column, lineno = self.pos, self.column, self.lineno
                    char = self.current_char
                    token_type = TokenType(self.current_char)
                    self.advance()

                except ValueError:
                    self.error(self.current_char)

                else:
                    return Token(
                        type_=token_type,
                        value=char,
                        pos=pos,
                        column=column,
                        lineno=lineno
                    )

        return Token(type_=TokenType.EOF, value=None, pos=self.pos, column=self.column, lineno=self.lineno)

    def ignore_whitespaces(self):
        while self.current_char in (" ", "\r", "\n", "\t"):
            self.advance()

    def comment(self):
        self.advance()
        if self.current_char == "*":
            while self.current_char is not None:
                self.advance()
                if self.current_char == "*":
                    if self.peek() == "#":
                        self.advance()
                        self.advance()
                        break

        else:
            while self.current_char not in (None, "\n"):
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

            while self.current_char in chars or self.current_char == "_":
                if self.current_char == "_":
                    self.advance()
                    continue

                number += self.current_char.upper()
                self.advance()

            return Token(
                type_=TokenType.INTEGER,
                value=(int(number, base=len(chars))),
                pos=pos_start,
                column=column_start,
                lineno=lineno_start
            )

        else:
            if self.current_char == ".":
                number += "0."
                self.advance()

            while self.current_char in ("0", "1", "2", "3", "4", "5", "6",
                                        "7", "8", "9", ".", "e", "E", "_"):
                if self.current_char == ".":
                    if "." in number or "E" in number:
                        break

                elif self.current_char in ("e", "E"):
                    if "E" in number:
                        break

                elif self.current_char == "_":
                    self.advance()
                    continue

                number += self.current_char.upper()
                self.advance()

            if "." in number or "E" in number:
                return Token(
                    type_=TokenType.FLOAT,
                    value=float(number),
                    pos=pos_start,
                    column=column_start,
                    lineno=lineno_start
                )

            else:
                return Token(
                    type_=TokenType.INTEGER,
                    value=int(number),
                    pos=pos_start,
                    column=column_start,
                    lineno=lineno_start
                )

    def match_string(self):
        pos_start, column_start, lineno_start = self.pos, self.column, self.lineno
        string_bytes = False
        string_type = "format"
        if self.current_char.lower() == "b":
            string_bytes = True
            self.advance()

        elif self.current_char.lower() in ("r", "p", "n", "f"):
            string_type = {"r": "raw", "p": "path", "n": "normal", "f": "format"}.get(
                self.current_char.lower(),
                string_type
            )
            self.advance()

        string_mode = None
        string_content = ""
        expressions = {}
        if self.current_char in ("'", '"'):
            string_mode = self.current_char
            self.advance()

            if self.current_char == string_mode and self.peek() == string_mode:
                string_mode = string_mode * 3
                self.advance()
                self.advance()

            while self.current_char is not None:
                # End String
                if self.current_char == string_mode[0]:
                    if len(string_mode) == 3:
                        if self.peek(2) == string_mode[1:3]:
                            self.advance()
                            self.advance()
                            self.advance()
                            break
                    else:
                        self.advance()
                        break

                # Special chars
                if self.current_char == "\\" and string_type not in ("path", "raw"):
                    peek = self.peek()
                    if peek == "x":
                        self.advance()
                        self.advance()
                        chars = self.current_char
                        self.advance()
                        chars += self.current_char
                        self.advance()

                        string_content += chr(int(chars, base=16))

                    elif peek == "u":
                        self.advance()
                        self.advance()
                        chars = self.current_char
                        self.advance()
                        for _ in range(3):
                            chars += self.current_char
                            self.advance()

                        string_content += chr(int(chars, base=16))

                    else:
                        chars = {"'": "'", '"': '"',
                                 'n': '\n', 't': '\t',
                                 'r': '\r', 'a': '\a',
                                 'b': '\b', 'v': '\v',
                                 '\\': '\\', '\r': "",
                                 '\n': "", '\t': '    ',
                                 '{': '{', '}': '}',
                                 '$': '$'
                                 }

                        string_content += chars.get(peek, "?")
                        self.advance()
                        self.advance()

                # NewLine on '' and "".
                elif self.current_char == "\n" and len(string_mode) == 1:
                    self.error("\n")

                # Insert simple-expression: $expr
                elif self.current_char == "$" and string_type not in ("raw", "normal"):
                    self.advance()
                    expression = ""
                    while self.current_char.isalnum() or self.current_char == "_":
                        if self.current_char == string_mode[0]:
                            if len(string_mode) == 3:
                                if self.peek(2) == string_mode[1:3]:
                                    break
                            else:
                                break

                        else:
                            expression += self.current_char
                            self.advance()

                    name = "expr"+str(len(expressions))
                    expressions[name] = expression
                    string_content += "{"+name+"}"

                # Insert expression: {expr}
                elif self.current_char == "{" and string_type not in ("raw", "normal", "path"):
                    self.advance()
                    expression = ""
                    opened = 1
                    while not (self.current_char == "}" and opened == 1):
                        if self.current_char == string_mode[0]:
                            if len(string_mode) == 3:
                                if self.peek(2) == string_mode[1:3]:
                                    break
                            else:
                                break

                        elif self.current_char == "\n" and len(string_mode) == 1:
                            self.error("\n")

                        else:
                            expression += self.current_char
                            if self.current_char == "{":
                                opened += 1
                            elif self.current_char == "}":
                                opened -= 1
                            self.advance()

                    if self.current_char == "}":
                        self.advance()

                    name = "expr"+str(len(expressions))
                    expressions[name] = expression
                    string_content += "{"+name+"}"

                # Default
                else:
                    string_content += self.current_char
                    self.advance()

            if not string_bytes:
                return Token(
                    type_=TokenType.STRING,
                    value=(string_type, string_mode, string_content, expressions),
                    pos=pos_start,
                    column=column_start,
                    lineno=lineno_start,
                )

            else:
                return Token(
                    type_=TokenType.BYTES,
                    value=(string_type, string_mode, string_content, expressions),
                    pos=pos_start,
                    column=column_start,
                    lineno=lineno_start,
                )

    def match_id(self):
        pos_start, column_start, lineno_start = self.pos, self.column, self.lineno

        name = ""
        if self.current_char.isalpha() or self.current_char == "_":
            name += self.current_char
            self.advance()

        while self.current_char is not None:
            if self.current_char.isalnum() or self.current_char == "_":
                name += self.current_char
                self.advance()
            else:
                break

        token_type = RESERVED_KEYWORDS.get(name, TokenType.ID)

        if name in ("None",):
            token_type = TokenType.NONE

        elif name in ("True", "False"):
            token_type = TokenType.BOOL

        elif name in ("Undefined",):
            token_type = TokenType.UNDEFINED

        return Token(
            type_=token_type,
            value=name,
            pos=pos_start,
            column=column_start,
            lineno=lineno_start
        )

    def get_line(self, line):
        lines = self.text.splitlines()
        if line >= len(lines):
            return None

        return lines[line]

    def is_next_newline(self):
        text = self.text
        pos = self.pos

        if pos >= len(text):
            return False

        while text[pos] in (" ", "#", "\t", "\r"):
            if text[pos] == "#":
                return True

            else:
                pos += 1
                if pos >= len(text):
                    return False

        print("IS_NEW_LINE?: ", repr(text[pos]))
        if text[pos] == "\n":
            return True

        return False
