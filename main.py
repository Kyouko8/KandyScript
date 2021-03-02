"""KandyScript main file"""
from enum import Enum
import os
import sys

# Used by kandy:
import pathlib
import time
import math
import random
import _io
import importlib
import builtins

# kandymodules
from kandylib import kandyerrors as kerr
from kandylib.tokentype import TokenType, Token, RESERVED_KEYWORDS
from kandylib.parser import Parser
from kandylib.lexer import Lexer
from kandylib.undefined import UNDEFINED_TYPE
from kandylib.kandyclass import create_class_items
from kandylib.kandydefault import KandyInt, KandyFloat, KandyStr, KandyList, KandyTuple, KandyDict
from kandylib.actions import (ProcedureCall, FunctionCall, ModuleClass, SpaceClass, CurrentSpaceClass,
                              PrevSpaceClass, PrivateSpaceClass, Spaces, MultipleTypesClass, Numeric,
                              LoopControl, take_splitter)
from kandylib.callstack import CallStack, ARType, ActivationRecord, Record, RecordConstant, ClassObjectWithARC
from kandylib.ast import (AST, Empty, ValueAST, BinOp, UnaryOp, StarredTuple, StarredDict, Assign,
                          Var, TypeVar, Slicing, Attribute, IfExpr, UnlessExpr, IfNotNullExpr, Compound,
                          CompoundWithNoReturn, IfStatement, UnlessStatement, Number, Bool, NoneValue,
                          Undefined, String, Bytes, Tuple, List, Set, Dict, ProcedureDecl, FunctionDecl,
                          Param, Call, ScriptAction, WhileStatement, UntilStatement, ForInStatement,
                          ForFromToStatement, ForCStatement, RepeatStatement, SwitchCaseStatement,
                          SwitchCaseItem, WhenCaseStatement, WhenCaseItem, WithStatement, TryStatement,
                          ImportStatement, UsingStatement, ClassStatement, LambdaDecl, DeleteStatement)

KANDY_DIRECTORY = os.path.dirname(__file__)
KANDY_LIBRARY_DIRECTORY = f"{KANDY_DIRECTORY}\\lib"
KANDY_LIBRARY_DIRECTORY_PYTHON = f"{KANDY_DIRECTORY}\\lib_py"

if not os.path.exists(KANDY_LIBRARY_DIRECTORY):
    os.makedirs(KANDY_LIBRARY_DIRECTORY)

if not os.path.exists(KANDY_LIBRARY_DIRECTORY_PYTHON):
    os.makedirs(KANDY_LIBRARY_DIRECTORY_PYTHON)


# Node Visitor
class NodeVisitor():
    """ General visitor Class """

    def visit(self, node):
        """ Visit a node. """
        method_name = "visit_"+type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """ Raise exception if a node can't be visit """
        raise Exception('No visit_{} method'.format(type(node).__name__))

    def visit_and_print(self, node):
        """ Visit a node and print info about node """
        print("NODE: ", node)
        value = self.visit(node)
        print("VALUE OF NODE ", node, ":   ", value)
        return value


# Interpreter
class Interpreter(NodeVisitor):
    """ KandyInterpreter Class """

    def __init__(self, parser: Parser = None, log_stack=False, print_call_stack=False):
        if parser is None:
            parser = Parser()

        # Interpreter main objects
        self.parser = parser
        self.ast = None
        self.call_stack = CallStack()
        self.main_ar = None
        self.module_ar = None
        self.user_ar = None
        self.global_ar = None
        self.private_ar = None
        self.id = id(self)

        # Interpreter control:
        self._inside_class = None

        # Kandy Import
        self.modules_imported = {}
        self.modules = {}

        # Kandy Spaces:
        self.spaces = {}

        # Kandy Special attributes:
        self.special_attributes = {
            int: KandyInt,
            float: KandyFloat,
            str: KandyStr,
            # list: KandyList,
            dict: KandyDict,
            tuple: KandyTuple,
        }

        # Log
        self.log_stack = log_stack
        self.print_call_stack = print_call_stack

        # Kandy Data
        self.filename = "<VirtualFile>"

        # Kandy Variables:
        self.__version = 1.0

        # Prepare the interpreter:
        self.reset()

    def reset(self, user_variables=None, start_variables=None):
        """ Reset the interpreter """
        self.call_stack.clear()
        self.init_components(
            user_variables=user_variables,
            start_variables=start_variables
        )

    def error(self, message):
        """ Generate a basic error. """
        raise Exception(f"InterpreterError: {message}")

    def get_var_name_assign(self, node):
        """ Get a var name for assignment """
        if isinstance(node, Var):
            return None, node.value

        elif isinstance(node, Attribute):
            return self.visit(node.value), self.get_var_name_assign(node.token)[1]

        elif isinstance(node, Call):
            self.error("Can't assign to a call function result directly.")

        elif isinstance(node, Slicing):
            slicing = slice(*tuple(map(self.visit, node.slicing)))
            return self.visit(node.value), slicing

    def init_components(self, name=None, user_variables=None, start_variables=None):
        """ Start the required components for the interpreter. """
        ar0 = ActivationRecord(
            name=(name if name is not None else "Kandy-Script-Stack (KSS)"),
            type_=ARType.BUILTIN,
            nesting_level=0,
        )
        ar1 = ActivationRecord(
            name="Module",
            type_=ARType.MODULE,
            nesting_level=1,
            nesting_record=ar0
        )
        ar2 = ActivationRecord(
            name="User",
            type_=ARType.USER,
            nesting_level=2,
            nesting_record=ar1
        )
        ar3 = ActivationRecord(
            name="Global",
            type_=ARType.GLOBAL,
            nesting_level=3,
            nesting_record=ar2
        )
        ar4 = ActivationRecord(
            name="Private",
            type_=ARType.PRIVATE,
            nesting_level=4,
            nesting_record=ar3
        )

        self.call_stack.push(ar0)
        self.call_stack.push(ar1)
        self.call_stack.push(ar2)
        self.call_stack.push(ar3)

        self.main_ar = ar0
        self.module_ar = ar1
        self.user_ar = ar2
        self.global_ar = ar3
        self.private_ar = ar4

        python_classes = [bool, bytes, complex, dict, float, frozenset, int,
                          list, object, property, set, slice, str, tuple,
                          type, super]

        for pc in python_classes:
            ar0[pc.__name__] = RecordConstant(pc)

        python_functions = [abs, all, any, ascii, bin, callable, chr, delattr,
                            divmod, enumerate, filter, format, getattr,
                            hasattr, hex, id, input, isinstance, issubclass,
                            iter, len, locals, map, max, memoryview, min, next,
                            oct, open, ord, pow, print, range, repr, reversed,
                            round, setattr, sorted, sum, vars, zip]

        for pc in python_functions:
            ar0[pc.__name__] = RecordConstant(pc)

        python_default_modules = [pathlib, time, os, math, random]
        for pc in python_default_modules:
            ar0[pc.__name__] = RecordConstant(pc)

        # Modify functions:
        ar0['dir'] = RecordConstant(self.dir)

        # Special clases:
        ar0['MultipleTypesClass'] = RecordConstant(MultipleTypesClass)
        ar0['numeric'] = RecordConstant(Numeric())
        ar0['Iterable'] = RecordConstant(MultipleTypesClass(list, tuple, dict))
        ar0['Text'] = RecordConstant(MultipleTypesClass(str, bytes))

        # Spaces and python-objects required:
        ar0['Errors'] = RecordConstant(kerr.AllPythonErrorInstance)
        ar0['Python'] = RecordConstant(builtins)
        ar0['Global'] = SpaceClass(self, ar3, "Global")
        ar0['User'] = SpaceClass(self, ar2, "User")
        ar0['BuiltIn'] = SpaceClass(self, ar0, "BuiltIn")
        ar0['Now'] = CurrentSpaceClass(self)
        ar0['Prev'] = PrevSpaceClass(self)
        ar0['Private'] = PrivateSpaceClass(self)

        # Kandy-Vars:
        ar0['KANDY_VERSION'] = RecordConstant(self.__version)
        ar0['KANDY_AUTHOR'] = RecordConstant("Medina Dylan")
        ar0['KANDY_FILE'] = RecordConstant(self.filename)
        ar0['KANDY_MAIN'] = RecordConstant(True)
        ar0['KANDY_TYPE'] = RecordConstant("program")
        ar2['PROGRAM_START'] = RecordConstant(time.time())

        # Add Values:
        if user_variables is not None:
            for key, value in user_variables.items():
                ar2[key] = value

        if start_variables is not None:
            for key, value in start_variables.items():
                ar3[key] = value

        # Add Protect:
        ar0.set_read_only(True)
        ar2.set_read_only(True)

    def copy_ar(self, ar, index, ignore_read_only=False):
        """ Copy AR to a specific position in AR """
        self.call_stack.copy(ar, index, ignore_read_only)

    def get_variable(self, name):
        """ Get a variable from current AR. """
        ar = self.call_stack.peek()

        return ar.get(name)

    def set_variable(self, name, record):
        """ Set a new var on the current AR. """
        ar = self.call_stack.peek()
        ar[name] = record

    def load_variable_from(self, name, ar):
        """ Load variable value from AR objects. """
        variable = ar.get(name)
        if isinstance(variable, Record):
            return variable.value

        else:
            return variable

    def get_ar_from_object(self, obj):
        """ Get the AR from Space objects. """
        if isinstance(obj, ModuleClass):
            value = self.modules[obj]
            if isinstance(value, ActivationRecord):
                return value

            elif isinstance(value, Interpreter):
                return value.get_ar_from_object(obj)

            else:
                message = f"Invalid type of module-class ({obj!r})."
                raise ValueError(message)

        elif isinstance(obj, SpaceClass):
            return self.spaces[obj]

        elif isinstance(obj, CurrentSpaceClass):
            return self.call_stack.peek()

        elif isinstance(obj, PrevSpaceClass):
            return self.call_stack.peek_prev()

        elif isinstance(obj, PrivateSpaceClass):
            if obj.verifyID(self.id):
                return self.get_private_AR()
            else:
                raise ValueError("Can't enter into this private area. Use the 'Private' builtin object to access to private area of this code.")

        elif isinstance(obj, ClassObjectWithARC):
            return obj._ClassObjectWithARC__activationrecord

        else:
            raise TypeError("Invalid access to space class.")

    def assign(self, value, name: str, var_type: TypeVar, operation=None):
        ar = self.call_stack.peek()
        if name in ar:
            if var_type is not None:
                raise TypeError("Can't reassign the 'variable-type'.")

            rec = ar.get(name)
            if isinstance(rec, Record):
                rec.set_value(value, operation=operation)

            else:
                rec = Record(rec)
                rec.set_value(value, operation=operation)
                ar[name] = rec

        elif operation is not None:
            message = f"{value} [On KandyScript]"
            raise NameError(message)

        else:
            undef = (value is UNDEFINED_TYPE)
            vtype = None
            strict = False
            const = False
            private = False

            if isinstance(var_type, TypeVar):
                private = var_type.private

            if var_type is None:
                pass

            elif not isinstance(var_type, TypeVar):
                vtype = var_type

            elif var_type.name == "DYNAMIC":
                pass

            elif var_type.name == "VAR":
                if value is None or value is UNDEFINED_TYPE:
                    pass
                else:
                    vtype = type(value)
                    strict = var_type.strict

            elif var_type.name == "ID":
                vtype = self.visit(var_type.variable)
                strict = var_type.strict

                if isinstance(vtype, MultipleTypesClass):
                    vtype = vtype.get_valid_types()

            elif var_type.name == "MULTIPLE":
                vtype = []
                for variables in var_type.token:
                    value_type = self.visit(variables)
                    if isinstance(value_type, MultipleTypesClass):
                        value_type = value_type.get_valid_types()
                        vtype.extend(value_type)
                    else:
                        vtype.append(value_type)

                strict = var_type.strict

            elif var_type.name == "CONST":
                const = True

            else:
                raise TypeError("The 'variable-type' is invalid.")

            if const:
                rec = RecordConstant(value=value, private=private)
            else:
                rec = Record(value=value, type_=vtype, strict=strict, private=private, undefined=undef)

            ar[name] = rec

        return rec

    def general_assign(self, value, var_ast: Var, var_type: TypeVar, operation=None):
        obj, var_name = self.get_var_name_assign(var_ast)

        if obj is not None:
            if isinstance(var_name, slice):
                if operation is None:
                    obj[var_name.stop] = value

                elif operation.type == TokenType.PLUS:
                    obj[var_name.stop] += value

                elif operation.type == TokenType.MINUS:
                    obj[var_name.stop] -= value

                elif operation.type == TokenType.MULT:
                    obj[var_name.stop] *= value

                elif operation.type == TokenType.DIV:
                    obj[var_name.stop] /= value

                elif operation.type == TokenType.FLOORDIV:
                    obj[var_name.stop] //= value

                elif operation.type == TokenType.MOD:
                    obj[var_name.stop] %= value

                elif operation.type == TokenType.SUBMOD:
                    left = value - (obj[var_name.stop] % value)
                    obj[var_name.stop] = left

                elif operation.type == TokenType.POW:
                    obj[var_name.stop] **= value

                elif operation.type == TokenType.BIT_OR:
                    obj[var_name.stop] |= value

                elif operation.type == TokenType.BIT_XOR:
                    obj[var_name.stop] ^= value

                elif operation.type == TokenType.BIT_AND:
                    obj[var_name.stop] &= value

                elif operation.type == TokenType.SHIFT_L:
                    obj[var_name.stop] <<= value

                elif operation.type == TokenType.SHIFT_R:
                    obj[var_name.stop] >>= value

                elif operation.type == TokenType.MATRIX_MUL:
                    obj[var_name.stop] @= value

                return obj[var_name.stop]

            elif isinstance(obj, (Spaces, ClassObjectWithARC)):
                ar = self.get_ar_from_object(obj)
                self.call_stack.push(ar)
                self.assign(value=value, name=var_name, var_type=var_type, operation=operation)
                self.call_stack.pop()

                return ar.get(var_name)

            else:
                if operation is None:
                    setattr(obj, var_name, value)

                elif operation.type == TokenType.PLUS:
                    obj.__dict__[var_name] += value

                elif operation.type == TokenType.MINUS:
                    obj.__dict__[var_name] -= value

                elif operation.type == TokenType.MULT:
                    obj.__dict__[var_name] *= value

                elif operation.type == TokenType.DIV:
                    obj.__dict__[var_name] /= value

                elif operation.type == TokenType.FLOORDIV:
                    obj.__dict__[var_name] //= value

                elif operation.type == TokenType.MOD:
                    obj.__dict__[var_name] %= value

                elif operation.type == TokenType.SUBMOD:
                    left = value - (obj.__dict__[var_name] % value)
                    obj.__dict__[var_name] = left

                elif operation.type == TokenType.POW:
                    obj.__dict__[var_name] **= value

                elif operation.type == TokenType.BIT_OR:
                    obj.__dict__[var_name] |= value

                elif operation.type == TokenType.BIT_XOR:
                    obj.__dict__[var_name] ^= value

                elif operation.type == TokenType.BIT_AND:
                    obj.__dict__[var_name] &= value

                elif operation.type == TokenType.SHIFT_L:
                    obj.__dict__[var_name] <<= value

                elif operation.type == TokenType.SHIFT_R:
                    obj.__dict__[var_name] >>= value

                elif operation.type == TokenType.MATRIX_MUL:
                    obj.__dict__[var_name] @= value

                return getattr(obj, var_name)

        else:
            return self.assign(value=value, name=var_name, var_type=var_type, operation=operation)

    def get_main_AR(self):
        return self.main_ar

    def get_module_AR(self):
        return self.module_ar

    def get_user_AR(self):
        return self.user_ar

    def get_global_AR(self):
        return self.global_ar

    def get_private_AR(self):
        return self.private_ar

    def _invalid_script_action(self):
        raise SyntaxError("Invalid script-action.")

    def get_special_attribute(self, obj, value):
        class_ = self.special_attributes.get(type(obj))
        if class_ is not None:
            item = class_(obj)
            return getattr(item, value)

        else:
            class_ = self.special_attributes.get(obj)
            if class_ is not None:
                return getattr(class_, value)

            else:
                return getattr(obj, value)

    def is_inside_class(self):
        return (self._inside_class is not None)

    # Functions:
    def dir(self, obj):
        if type(obj) in self.special_attributes:
            class_ = self.special_attributes.get(type(obj))
            return dir(class_(obj))

        elif obj in self.special_attributes:
            return dir(self.special_attributes.get(obj))

        else:
            return dir(obj)

    # Visitors:
    # Blocks:
    def visit_Compound(self, node: Compound):
        """ Visit all children inside the parent node. """
        for child in node.children:
            # print(type(child).__name__,self.visit(child))
            result = self.visit(child)
            if isinstance(result, ScriptAction):
                if result.action == "return":
                    if node.return_action:
                        return result

                    return (result.data)

                elif result.action in ("continue", "break"):
                    return result

                else:
                    self._invalid_script_action()

    def visit_CompoundWithNoReturn(self, node: CompoundWithNoReturn):
        """ Visit all children inside the parent node. """
        for child in node.children:
            # print(type(child).__name__,self.visit(child))
            result = self.visit(child)
            if isinstance(result, ScriptAction):
                if result.action == "return":
                    raise SyntaxError("The 'return' statement can't be used here.")

                else:
                    self._invalid_script_action()

    # Operations
    def visit_Assign(self, node: Assign):
        """ Create o re-assign a variable """
        var_type = node.type
        value = self.visit(node.right)

        if node.token.type == TokenType.QUESTION_ASSIGN:
            if not value:
                return None

        if node.token.type in (TokenType.ASSIGN, TokenType.EXPR_ASSIGN, TokenType.QUESTION_ASSIGN):
            value_assigned = self.general_assign(value=value, var_ast=node.left, var_type=var_type, operation=node.op)

            if node.token.type == (TokenType.EXPR_ASSIGN):
                if isinstance(value_assigned, Record):
                    return value_assigned.value
                else:
                    return value_assigned

    def visit_Var(self, node: Var):
        """ Get the value of the variable """
        var_name = node.value
        ar = self.call_stack.peek()

        return self.load_variable_from(var_name, ar)

    def visit_BinOp(self, node: BinOp):
        """ Apply operations and return the result """
        token = node.token

        if token.type == TokenType.AND:
            return self.visit(node.left) and self.visit(node.right)

        elif token.type == TokenType.OR:
            return self.visit(node.left) or self.visit(node.right)

        elif token.type == TokenType.EQUALS:
            return self.visit(node.left) == self.visit(node.right)

        elif token.type == TokenType.NOT_EQUALS:
            return self.visit(node.left) != self.visit(node.right)

        elif token.type == TokenType.GREATEN:
            return self.visit(node.left) > self.visit(node.right)

        elif token.type == TokenType.GREATEN_EQUALS:
            return self.visit(node.left) >= self.visit(node.right)

        elif token.type == TokenType.LESSER:
            return self.visit(node.left) < self.visit(node.right)

        elif token.type == TokenType.LESSER_EQUALS:
            return self.visit(node.left) <= self.visit(node.right)

        elif token.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)

        elif token.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)

        elif token.type == TokenType.MULT:
            return self.visit(node.left) * self.visit(node.right)

        elif token.type == TokenType.POW:
            return self.visit(node.left) ** self.visit(node.right)

        elif token.type == TokenType.DIV:
            return self.visit(node.left) / self.visit(node.right)

        elif token.type == TokenType.FLOORDIV:
            return self.visit(node.left) // self.visit(node.right)

        elif token.type == TokenType.MOD:
            return self.visit(node.left) % self.visit(node.right)

        elif token.type == TokenType.SUBMOD:
            left = self.visit(node.left)
            right = self.visit(node.right)
            return right - (left % right)

        elif token.type == TokenType.MATRIX_MUL:
            return self.visit(node.left) @ self.visit(node.right)

        elif token.type == TokenType.IS:
            return self.visit(node.left) is self.visit(node.right)

        elif token.type == TokenType.IN:
            return self.visit(node.left) in self.visit(node.right)

        elif token.type == TokenType.SHIFT_L:
            return self.visit(node.left) << self.visit(node.right)

        elif token.type == TokenType.SHIFT_R:
            return self.visit(node.left) >> self.visit(node.right)

        elif token.type == TokenType.BIT_AND:
            return self.visit(node.left) & self.visit(node.right)

        elif token.type == TokenType.BIT_OR:
            return self.visit(node.left) | self.visit(node.right)

        elif token.type == TokenType.BIT_XOR:
            return self.visit(node.left) ^ self.visit(node.right)

        elif token.type == TokenType.XOR:
            left = self.visit(node.left)
            right = self.visit(node.right)
            return (left and not right) or (right and not left)

    def visit_UnaryOp(self, node: UnaryOp):
        """ Apply unary operations and return the result. """
        token = node.token
        if token.type == TokenType.MINUS:
            return -self.visit(node.value)

        elif token.type == TokenType.PLUS:
            return +self.visit(node.value)

        elif token.type == TokenType.BIT_NOT:
            return ~self.visit(node.value)

        elif token.type == TokenType.NOT:  # lower precedence
            return not self.visit(node.value)

        elif token.type == TokenType.EXCLAMATION:  # highest precedence
            return not self.visit(node.value)

    def visit_ValueAST(self, node: ValueAST):
        """ Return the value inside the AST. """
        return node.value

    def visit_ScriptAction(self, node: ScriptAction):
        """ ScriptActions like 'RETURN', 'CONTINUE', 'BREAK', 'EXPORT', etc. """
        if node.token.type == TokenType.EXPORT:
            ar = self.call_stack.peek()
            expr = ValueAST(
                SpaceClass(
                    interpreter=self, ar=ar, name=f"Space-Exported-{ar.name}"
                )
            )
            token = Token(
                TokenType.RETURN,
                "return",
                pos=node.token.pos,
                column=node.token.column,
                lineno=node.token.lineno
            )

            return ScriptAction(token=token, expression=expr)

        elif node.token.type in (TokenType.RETURN, TokenType.CONTINUE, TokenType.BREAK):
            if isinstance(node.expression, AST):
                node.data = self.visit(node.expression)

                if isinstance(node.data, ScriptAction):
                    raise SyntaxError("Invalid {node.token.value} statement.")

        return node

    # Data:
    def visit_Empty(self, _: Empty):
        """ Empty block: no actions required """
        return None

    def visit_Number(self, node: Number):
        """ Return the value of the number class. """
        return node.value

    def visit_Bool(self, node: Bool):
        """ Return the bool value (True/False). """
        return node.value

    def visit_String(self, node: String):
        """ Return the content of the string class. """
        if node.type == "path":
            if len(node.expr) >= 1:
                content = node.content
                path = content.format(**node.evaluate_expressions(self))
            else:
                path = node.content

            return pathlib.Path(path)

        elif len(node.expr) >= 1:
            content = node.content
            return content.format(**node.evaluate_expressions(self))
        else:
            return node.content

    def visit_Bytes(self, node: Bytes):
        """ Return the content of the bytes class. """
        if node.type == "path":
            if len(node.expr) >= 1:
                content = node.content
                path = content.format(**node.evaluate_expressions(self))
            else:
                path = node.content

            return pathlib.Path(path.encode())

        elif len(node.expr) >= 1:
            content = node.content
            return content.format(**node.evaluate_expressions(self)).encode()

        else:
            return node.content.encode()

    def visit_NoneValue(self, _: NoneValue):
        """ Return the null value. """
        return None

    def visit_Undefined(self, _: Undefined):
        """ Return the undefined value. """
        return UNDEFINED_TYPE

    def visit_Tuple(self, node: Tuple):
        """ Return a tuple object. """
        return tuple(self.visit(i) for i in node.values)

    def visit_List(self, node: Tuple):
        """ Return a list object. """
        return list(self.visit(i) for i in node.values)

    def visit_Set(self, node: Tuple):
        """ Return a set object. """
        return set(self.visit(i) for i in node.values)

    def visit_Dict(self, node: Tuple):
        """ Return a dict object. """
        dic = {}
        for key, value in node.values:
            dic[self.visit(key)] = self.visit(value)

        return dic

    # Expressions:
    def visit_IfExpr(self, node: IfExpr):
        """ Test condition, if this is True return the left value, else the right value. """

        if self.visit(node.condition):
            return self.visit(node.on_true)

        elif node.on_false is not None:
            return self.visit(node.on_false)

    def visit_UnlessExpr(self, node: UnlessExpr):
        """ Test condition, if this is not True return the left value, else the right value. """

        if not self.visit(node.condition):
            return self.visit(node.on_true)

        elif node.on_false is not None:
            return self.visit(node.on_false)

    def visit_IfNotNullExpr(self, node: IfNotNullExpr):
        """ Test value, if this is not Null (None) return the left value, else the right value. """

        value = self.visit(node.expression)
        if value is not None and value is not UNDEFINED_TYPE:
            return value

        elif node.on_false is not None:
            return self.visit(node.on_false)

    def visit_Attribute(self, node: Attribute):
        obj = self.visit(node.value)
        if isinstance(obj, Record):
            obj = obj.value

        if isinstance(obj, Spaces):
            return self.load_variable_from(
                name=node.token.value,
                ar=self.get_ar_from_object(obj)
            )

        elif (type(obj) in self.special_attributes) or ((type(obj) == type) and obj in self.special_attributes):
            return self.get_special_attribute(obj, node.token.value)

        return getattr(obj, node.token.value)

    def visit_Slicing(self, node: Slicing):
        if len(node.slicing) == 3:
            index1, index2, index3 = node.slicing
            return self.visit(node.value)[self.visit(index1):self.visit(index2):self.visit(index3)]

        elif len(node.slicing) == 2:
            index1, index2 = node.slicing
            return self.visit(node.value)[self.visit(index1):self.visit(index2)]

        elif len(node.slicing) == 1:
            index1 = node.slicing[0]
            return self.visit(node.value)[self.visit(index1)]

    def visit_Call(self, node: Call):
        """ Call a function/procedure. """
        function = self.visit(node.value)
        params = []
        kwparams = {}
        for p in node.params:
            if isinstance(p, StarredTuple):
                params.extend(self.visit(p))

            elif isinstance(p, StarredDict):
                for k, v in (self.visit(p)).items():
                    if k in kwparams:
                        raise TypeError(f"got multiple values for keyword argument {k!r}")

                    kwparams[k] = v

            else:
                params.append(self.visit(p))

        for k, v in node.kwparams.items():
            if isinstance(v, StarredDict):
                for k2, v2 in (self.visit(v)).items():
                    if k2 in kwparams:
                        raise TypeError(f"got multiple values for keyword argument {k2!r}")

                    kwparams[k2] = v2
            else:
                if k in kwparams:
                    raise TypeError(f"got multiple values for keyword argument {k!r}")

                kwparams[k] = self.visit(v)

        return function(*params, **kwparams)

    def visit_StarredTuple(self, node: StarredTuple):
        """ Return the value of '*list' syntax. """
        return tuple((i for i in self.visit(node.value)))

    def visit_StarredDict(self, node: StarredDict):
        """ Return the value of '**dict' syntax. """
        return dict((k, v) for k, v in self.visit(node.value).items())

    # Functions and Procedures:
    def visit_ProcedureDecl(self, node: ProcedureDecl):
        """
        Define a new procedure (global)
        """
        name = node.name.value
        block = node.block
        params = node.params
        is_local = node.is_local

        for p in params:
            if p.value is not UNDEFINED_TYPE:
                p.value = self.visit(p.value)

        self.assign(
            name=name,
            value=ProcedureCall(
                self, name, block, params, is_local
            ),
            var_type=None
        )

    def visit_FunctionDecl(self, node: FunctionDecl):
        """
        Define a new function (global)
        """
        name = node.name.value
        block = node.block
        params = node.params
        is_local = node.is_local
        type_return = node.type

        strict = False
        if type_return is not None:
            if type_return.strict:
                strict = True

        for p in params:
            if p.value is not UNDEFINED_TYPE:
                p.value = self.visit(p.value)

        self.assign(
            name=name,
            value=FunctionCall(
                self, name, block, params, type_return, strict, is_local
            ),
            var_type=None
        )

    def visit_LambdaDecl(self, node: FunctionDecl):
        """
        Define a new lambda function
        """
        block = node.block
        params = node.params
        is_local = node.is_local
        type_return = node.type

        strict = False
        if type_return is not None:
            if type_return.strict:
                strict = True

        for p in params:
            if p.value is not UNDEFINED_TYPE:
                p.value = self.visit(p.value)

        return FunctionCall(
            self, "kandy_lambda_function", block, params, type_return, strict, is_local
        )

    # Statements:
    def visit_IfStatement(self, node: IfStatement):
        """ Execute an if statement. """
        for condition, statement in node.expressions:
            if self.visit(condition):
                return self.visit(statement)

        if node.else_statement is not None:
            return self.visit(node.else_statement)

    def visit_UnlessStatement(self, node: UnlessStatement):
        """ Execute an unless (if not) statement. """
        for condition, statement in node.expressions:
            if not self.visit(condition):
                return self.visit(statement)

        if node.else_statement is not None:
            return self.visit(node.else_statement)

    def visit_WhileStatement(self, node: WhileStatement):
        """ Execute a while statement. """
        name = None
        loop = LoopControl()
        if node.variable is not None:
            name = self.general_assign(value=loop, var_ast=node.variable, var_type=None)

        if node.do_first:
            loop._count()
            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        pass
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        while self.visit(node.condition):
            loop._count()
            if loop.get_remaining_ignore_count():
                loop._ignore()
                loop._count_finished()
                continue

            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        continue
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        loop._finish()

        if node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_UntilStatement(self, node: UntilStatement):
        """ Execute an until (while not) statement. """
        name = None
        loop = LoopControl()
        if node.variable is not None:
            name = self.general_assign(value=loop, var_ast=node.variable, var_type=None)

        if node.do_first:
            loop._count()
            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        pass
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        while not self.visit(node.condition):
            loop._count()
            if loop.get_remaining_ignore_count():
                loop._ignore()
                loop._count_finished()
                continue

            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        continue
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        loop._finish()

        if node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_RepeatStatement(self, node: RepeatStatement):
        """ Execute a repeat statement. """
        name = None
        loop = LoopControl()
        if node.variable is not None:
            name = self.general_assign(value=loop, var_ast=node.variable, var_type=None)

        value = self.visit(node.value)
        for _ in range(value):
            loop._count()
            if loop.get_remaining_ignore_count():
                loop._ignore()
                loop._count_finished()
                continue

            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        continue
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        loop._finish()

        if node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_ForCStatement(self, node: ForCStatement):
        """ Execute a for-c statement. """
        name = None
        loop = LoopControl()
        if node.variable is not None:
            name = self.general_assign(value=loop, var_ast=node.variable, var_type=None)

        self.visit(node.assign)
        while self.visit(node.condition):
            loop._count()
            if loop.get_remaining_ignore_count():
                loop._ignore()
                loop._count_finished()
                continue

            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        continue
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()
            self.visit(node.increment)

        loop._finish()

        if node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_ForFromToStatement(self, node: ForFromToStatement):
        """ Execute a for-from-to statement. """
        name = None
        loop = LoopControl()
        if node.variable is not None:
            name = self.general_assign(value=loop, var_ast=node.variable, var_type=None)

        start = self.visit(node.value_start)
        end = self.visit(node.value_end)
        step = (1 if end > start else -1)

        for current in range(start, end+step, step):
            loop._count()
            if loop.get_remaining_ignore_count():
                loop._ignore()
                loop._count_finished()
                continue

            self.general_assign(value=current, var_ast=node.assign, var_type=None)
            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        continue
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        loop._finish()

        if node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_ForInStatement(self, node: ForInStatement):
        """ Execute a for-in statement. """
        name = None
        loop = LoopControl()
        if node.variable is not None:
            name = self.general_assign(value=loop, var_ast=node.variable, var_type=None)

        expression = self.visit(node.expression)
        n_variables = len(node.assigns)
        first_var = node.assigns[0]

        if node.take is not None:
            expression = take_splitter(
                expression=expression,
                count=self.visit(node.take),
                values_to_unpack=n_variables
            )

        for current in expression:
            loop._count()
            if loop.get_remaining_ignore_count():
                loop._ignore()
                loop._count_finished()
                continue

            if n_variables == 1:
                self.general_assign(value=current, var_ast=first_var, var_type=None)

            elif n_variables >= 2:
                n = 0
                for current_value, current_variable in zip(current, node.assigns):
                    self.general_assign(value=current_value, var_ast=current_variable, var_type=None)
                    n += 1

                if not n == n_variables:
                    message = f"too many values to unpack (expected {n_variables}, found {n})"
                    raise ValueError(message)

            result = self.visit(node.block)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    if result.data is None or result.data == loop or self.visit(result.data) == loop:
                        continue
                    else:
                        loop._finish()
                        return result

                elif result.action == "break":
                    if result.data is None or result.data == loop or self.visit(result.data) == name:
                        loop._finish()
                        return None
                    else:
                        loop._finish()
                        return result

                elif result.action == "return":
                    loop._finish()
                    return result

            loop._count_finished()

        loop._finish()

        if node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_SwitchCaseItem(self, node: SwitchCaseItem):
        """ Execute a switch-case control. """
        if not isinstance(node, SwitchCaseItem):
            return None

        for expression in node.cases:
            if node.compare_expression == self.visit(expression):
                return self.visit(node.block)

    def visit_SwitchCaseStatement(self, node: SwitchCaseStatement):
        """ Execute a switch-case statement. """

        compare_expression = self.visit(node.compare_expression)
        for expression in node.cases:
            expression.compare_expression = compare_expression
            result = self.visit(expression)
            if isinstance(result, ScriptAction):
                if result.action == "continue":
                    continue

                elif result.action == "break":
                    if result.data is None:
                        return None

                return result

        if node.default_block is not None:
            return self.visit(node.default_block)

    def visit_WhenCaseItem(self, node: WhenCaseItem):
        """ Execute a when-case-item control. """

        if not isinstance(node, WhenCaseItem):
            return None

        for expression in node.cases:
            if node.compare_expression == self.visit(expression):
                return (True, self.visit(node.block))

    def visit_WhenCaseStatement(self, node: WhenCaseStatement):
        """ Execute a when-case statement. """

        compare_expression = self.visit(node.compare_expression)
        for expression in node.cases:
            expression.compare_expression = compare_expression
            result = self.visit(expression)
            if result is None:
                continue

            if result[0]:
                return result[1]

        if node.default_block is not None:
            return self.visit(node.default_block)

    def visit_WithStatement(self, node: WithStatement):
        """ Execute a with statement. """
        expression = self.visit(node.expression)

        with expression as value:
            if not node.variable is None:
                self.general_assign(value=value, var_ast=node.variable, var_type=None)

            return self.visit(node.block)

    def visit_TryStatement(self, node: TryStatement):
        """ Execute a try-except-finally-else statement. """

        error = False
        try:
            return self.visit(node.try_block)

        except BaseException as exception:
            error = True
            for exc in node.except_blocks:
                class_ = self.visit(exc.expression)
                if isinstance(exception, class_):
                    if exc.variable is not None:
                        self.general_assign(
                            value=exception,
                            var_ast=exc.variable,
                            var_type=None
                        )

                    return self.visit(exc.block)

            raise exception

        finally:
            if node.finally_block is not None:
                self.visit(node.finally_block)

            if not error:
                if node.else_statement is not None:
                    return self.visit(node.else_statement)

    def visit_ImportStatement(self, node: ImportStatement):
        """ Execute a try-except-finally-else statement. """
        package = ""
        if node.is_python_file:
            if node.package is not None:
                for module in node.package:
                    package = f"{package}.{module.value}"

            for module in node.module_names:
                name = module[0].value
                if module[1] is not None:
                    import_as = module[1].value
                else:
                    import_as = name

            module_class = importlib.import_module(name=name, package=package)
            ar = self.get_module_AR()
            ar[import_as] = RecordConstant(module_class)

        else:
            if node.package is not None:
                for module in node.package:
                    package = os.path.join(package, module.value)

            for module in node.module_names:
                name = module[0].value
                if module[1] is not None:
                    import_as = module[1].value
                else:
                    import_as = name

                ks_file = os.path.join(package, name) + ".ks"
                filename = _search_import_module(ks_file, self.filename)
                module_class = self._module(filename, name)
                ar = self.get_module_AR()
                ar[import_as] = RecordConstant(module_class)

    def visit_UsingStatement(self, node: UsingStatement):
        """ Change the current AR temporally """
        value = self.visit(node.variable)

        if isinstance(value, (Spaces, ClassObjectWithARC)):
            ar = self.get_ar_from_object(value)
            self.call_stack.push(ar)
            result = self.visit(node.block)
            self.call_stack.pop()

            if isinstance(result, ScriptAction):
                return result

        else:
            message = ("Invalid Space, you only can use SpaceClass (like: modules and exported spaces;"
                       "or the builtin spaces objects: Global, BuiltIn, User, Now, Prev, Private)")
            raise ValueError(message)

    def visit_ClassStatement(self, node: ClassStatement):
        """ Create a new class """
        name = node.variable.value
        objects = []
        required = True
        for x in tuple((self.visit(i) for i in node.objects)):
            if issubclass(x, ClassObjectWithARC):
                required = False

            objects.append(x)

        if required:
            objects.append(ClassObjectWithARC)

        current_ar = self.call_stack.peek()
        new_ar = ActivationRecord(
            name=name,
            type_=ARType.CLASS,
            nesting_level=current_ar.nesting_level,
            nesting_record=current_ar
        )

        self.call_stack.push(new_ar)
        self._inside_class = name
        self.visit(node.block)
        self._inside_class = None
        self.call_stack.pop()

        data_dict = {"_ClassObjectWithARC__ar": new_ar}
        for key, record in new_ar:
            if key in ("__getattr__", "__setattr__"):
                continue

            if isinstance(record, Record):
                if isinstance(record.value, (FunctionCall, ProcedureCall)):
                    data_dict[key] = lambda *args, _ClassObjectWithARC__record__=record, \
                        **kwargs: _ClassObjectWithARC__record__.value(*args, **kwargs)
                    continue

        new_class = create_class_items(name, tuple(objects), data_dict)
        current_ar[name] = RecordConstant(new_class)

    def visit_DeleteStatement(self, node: DeleteStatement):
        """ Execute a del statement. """
        expression = self.visit(node.expression)
        pass

    # Start the Interpreter:
    def _interpret(self, text):
        tree = self._generate_ast(text)
        return self._visit_ast(tree)

    def _generate_ast(self, text):
        try:
            self.ast = tree = self.parser.parse(text)

        except BaseException:
            token = self.parser.current_token
            line = self.parser.lexer.get_line(token.lineno-1)
            note = "{0:>{1}}".format("^", token.column)
            print("\n\n")
            if self.filename:
                print(f"Filename:\n\t{os.path.basename(self.filename)}")

            print(f"Position:\n\tpos={token.pos}; lineno={token.lineno}; column={token.column};"
                  f"\nLine:\n\t{line}\n\t{note}\n")

            raise

        return tree

    def _visit_ast(self, tree):
        try:
            result = self.visit(tree)

        except BaseException:
            print("InterpreterError!")
            raise

        return result

    def _test(self, tree, times=5, user_variables=None, start_variables=None):
        results = []
        for i in range(times):
            self.reset(user_variables=user_variables, start_variables=start_variables)
            start = time.time()
            output = self.visit(tree)
            end = time.time()
            results.append((output, end-start))

        return results

    def _module(self, filename, name):
        if os.path.abspath(filename) == os.path.abspath(self.filename):
            return RecordConstant(SpaceClass(self, self.get_global_AR(), "RecursionImportedModule"))

        if filename in self.modules_imported:
            return self.modules_imported[filename]

        return ModuleClass(self, filename, name)

    def interpret(self, text, reset=True, *, filename=None, user_variables=None, start_variables=None):
        """ Interpret a text or file with KandyScript """
        self.filename = "<VirtualFile>"

        if filename is not None:
            self.filename = os.path.abspath(filename)
            with open(filename, "rb") as f:
                text = f.read()
                text = text.decode("utf-8")

        if reset:
            self.reset(user_variables=user_variables, start_variables=start_variables)

        result = self._interpret(text)

        if self.print_call_stack:
            print(self.call_stack)

        return result

    def interpret_from_filename(self, filename, reset=True, *, user_variables=None, start_variables=None):
        """ Alias to Interpret.interpret(filename=FILE)"""
        return self.interpret(
            text="",
            reset=reset,
            filename=filename,
            user_variables=user_variables,
            start_variables=start_variables
        )

    def test(self, text, times=5, *, filename=None, user_variables=None, start_variables=None):
        self.filename = "<VirtualFile>"

        if filename is not None:
            self.filename = os.path.abspath(filename)
            with open(filename, "rb") as f:
                text = f.read()
                text = text.decode("utf-8")

        tree = self._generate_ast(text)
        return self._test(tree, times, user_variables=user_variables, start_variables=start_variables)

    def test_from_filename(self, filename=None, times=5, *, user_variables=None, start_variables=None):
        return self.test(
            "",
            times,
            filename=filename,
            user_variables=user_variables,
            start_variables=start_variables
        )

    def console_mode(self, reset=False, user_variables=None, start_variables=None):
        if reset:
            self.reset(
                user_variables=user_variables,
                start_variables=start_variables
            )

        print("\nKandyConsole\nUse $end para finalizar.\n\n")
        while True:
            program = input("Kandy >>  ")
            if program == "$end":
                break

            elif program:
                try:
                    ast = self._generate_ast(program)
                    result = self._visit_ast(ast)
                    if result is not None:
                        print("Result>> ", result)

                except BaseException as exc:
                    print("Error >> "+type(exc).__name__+":", exc, "\n")

        print("\n\n")


def _search_import_module(name, current_filename=""):
    if not name.lower().endswith(".ks"):
        name = f"{name}.ks"

    if os.path.exists(current_filename):
        dirname = os.path.dirname(os.path.abspath(current_filename))

    else:
        dirname = os.path.abspath(".")

    file_test = os.path.join(dirname, name)
    if os.path.exists(file_test):
        return file_test

    file_test = os.path.join(KANDY_LIBRARY_DIRECTORY, name)
    if os.path.exists(file_test):
        return file_test

    message = "Impossible to load KandyModule."
    raise ModuleNotFoundError(message)


def parse(text):
    """ Fast use of Interpreter-class """
    lexer = Lexer()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.reset()
    result = interpreter.interpret(text)

    return dict(lexer=lexer, parser=parser, interpreter=interpreter, ast=interpreter.ast, result=result)


if __name__ == "__main__":
    inter = Interpreter(print_call_stack=False)
    if len(sys.argv) == 1:
        resultado = inter.interpret_from_filename(".\\kandydemo\\luca_prueba.ks", 15)
        #resultado = inter.console_mode()
    else:
        print("\nRunning KandyScript: \n")
        resultado = inter.interpret_from_filename(sys.argv[1])

    if resultado is not None:
        print("\nResultado obtenido por el interprete: ", repr(resultado))
