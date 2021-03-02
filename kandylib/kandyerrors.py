"""
KandyErrors module.

Tree of Exceptions:

Exception (python Exceptions Class)
+-- KandyBaseException
    +-- KandySystemExit
    +-- KandyKeyboardInterrupt
    +-- KandyException
        +-- KandyLexerError
        +-- KandyParserError
        |   +-- KandySyntaxError
        +-- KandySemanticError
        +-- KandyInterpreterError

"""
from enum import Enum


# Error codes:
class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'


# BaseClass from all exceptions and errors.
class KandyBaseException(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'


class KandySystemExit(KandyBaseException):
    pass


class KandyKeyboardInterrupt(KandyBaseException):
    pass


# Exception is an important class that contains a big variety of sub-exceptions class.
class KandyException(KandyBaseException):
    pass


# Errors:
class KandyLexerError(KandyException):
    pass


class KandyParserError(KandyException):
    pass


class KandySyntaxError(KandyParserError):
    pass


class KandySemanticError(KandyException):
    pass


class KandyInterpreterError(KandyException):
    pass


class KandyProtect(KandyException):
    pass


class AllPythonErrors():
    def __init__(self):
        for k, v in dict(globals()['__builtins__']).items():
            if k.endswith("Error") or k.endswith("Exception"):
                self.__dict__[k] = v

AllPythonErrorInstance = AllPythonErrors()
