
from .undefined import UNDEFINED_TYPE
from .tokentype import TokenType

__all__ = ['AST', 'Empty', 'ValueAST', 'BinOp', 'UnaryOp', 'StarredTuple', 'StarredDict', 'Assign',
           'Var', 'TypeVar', 'Slicing', 'Attribute', 'IfExpr', 'UnlessExpr', 'IfNotNullExpr', 'Compound',
           'CompoundWithNoReturn', 'IfStatement', 'UnlessStatement', 'Number', 'Bool', 'NoneValue',
           'Undefined', 'String', 'Bytes', 'Tuple', 'List', 'Set', 'Dict', 'ProcedureDecl', 'FunctionDecl',
           'Param', 'Call', 'ScriptAction', 'WhileStatement', 'UntilStatement', 'ForInStatement',
           'ForFromToStatement', 'ForCStatement', 'RepeatStatement', 'SwitchCaseStatement',
           'SwitchCaseItem', 'WhenCaseStatement', 'WhenCaseItem', 'WithStatement', 'TryStatement',
           'ExceptBlock', 'ImportStatement', 'UsingStatement', 'ClassStatement']


# AST
class AST(object):
    def __repr__(self):
        return type(self).__name__ + "(" + ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items()) + ")"

    __str__ = __repr__


class Empty(AST):
    pass


class ValueAST(AST):
    def __init__(self, value):
        self.value = value


# AST: Expressiones
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = op
        self.right = right


class UnaryOp(AST):
    def __init__(self, op, value):
        self.token = op
        self.value = value


class StarredTuple(UnaryOp):
    pass


class StarredDict(UnaryOp):
    pass


class Assign(AST):
    def __init__(self, type_, left, assign_type, right, op=None):
        self.type = type_
        self.left = left
        self.token = assign_type
        self.right = right
        self.op = op


class Var(AST):
    def __init__(self, token):
        self.value = token.value
        self.token = token


class TypeVar(AST):
    def __init__(self, name, token, strict=False, private=False, variable=None):
        self.name = name
        self.token = token
        self.strict = strict
        self.private = private
        self.variable = variable


class Slicing(AST):
    def __init__(self, value, slicing):
        self.slicing = slicing
        self.value = value


class Attribute(AST):
    def __init__(self, value, token):
        self.token = token
        self.value = value


class IfExpr(AST):
    def __init__(self, condition, value_true, value_false):
        self.condition = condition
        self.on_true = value_true
        self.on_false = value_false


class UnlessExpr(IfExpr):
    pass


class IfNotNullExpr(AST):
    def __init__(self, expression, value_false):
        self.expression = expression
        self.on_false = value_false


# AST: Estructuras
class Compound(AST):
    def __init__(self, return_action=False):
        self.children = []
        self.return_action = return_action  # True: Return action; False: Return value.

    def add_child(self, child):
        self.children.append(child)

    def add_children(self, children_list):
        self.children.extend(children_list)


class CompoundWithNoReturn(Compound):
    pass


class IfStatement(AST):
    def __init__(self, expressions: tuple, else_statement: AST):
        """
        expressions: tuple
            ((AST_expression, AST_statement))

        else_statement:
            AST_statement
        """

        self.expressions = expressions
        self.else_statement = else_statement


class UnlessStatement(IfStatement):
    pass


class WhileStatement(AST):
    def __init__(self, condition: AST, do_block: AST, else_statement: AST, var_name: AST, do_first=False):
        self.condition = condition
        self.block = do_block
        self.else_statement = else_statement
        self.variable = var_name
        self.do_first = do_first


class UntilStatement(WhileStatement):
    pass


class ForInStatement(AST):
    def __init__(self, assigns: tuple, expression: AST, take: AST, do_block: AST, else_statement: AST, var_name: AST):
        self.assigns = assigns  # Tuple of AST
        self.expression = expression
        self.take = take
        self.block = do_block
        self.else_statement = else_statement
        self.variable = var_name


class ForFromToStatement(AST):
    def __init__(self, assign: AST, value_start: AST, value_end: AST, do_block: AST, else_statement: AST, var_name: AST):
        self.assign = assign
        self.value_start = value_start
        self.value_end = value_end
        self.block = do_block
        self.else_statement = else_statement
        self.variable = var_name


class ForCStatement(AST):
    def __init__(self, assign: AST, condition: AST, increment: AST, do_block: AST, else_statement: AST, var_name: AST):
        self.assign = assign
        self.condition = condition
        self.increment = increment
        self.block = do_block
        self.else_statement = else_statement
        self.variable = var_name


class RepeatStatement(AST):
    def __init__(self, value: AST, do_block: AST, else_statement: AST, var_name: AST):
        self.value = value
        self.block = do_block
        self.else_statement = else_statement
        self.variable = var_name


class SwitchCaseStatement(AST):
    def __init__(self, compare_expression, cases, default_block):
        self.cases = cases
        self.default_block = default_block
        self.compare_expression = compare_expression


class SwitchCaseItem(AST):
    def __init__(self, cases, block):
        self.cases = cases
        self.block = block
        self.compare_expression = None


class WhenCaseStatement(AST):
    def __init__(self, compare_expression, cases, default_block):
        self.cases = cases
        self.default_block = default_block
        self.compare_expression = compare_expression


class WhenCaseItem(AST):
    def __init__(self, cases, block):
        self.cases = cases
        self.block = block
        self.compare_expression = None


class WithStatement(AST):
    def __init__(self, expression, variable, block):
        self.expression = expression
        self.variable = variable
        self.block = block


class TryStatement(AST):
    def __init__(self, try_block, except_blocks, finally_block=None, else_statement=None):
        self.try_block = try_block
        self.except_blocks = except_blocks
        self.finally_block = finally_block
        self.else_statement = else_statement


class ExceptBlock(AST):
    def __init__(self, expression, variable, block):
        self.expression = expression
        self.variable = variable
        self.block = block


class ImportStatement(AST):
    def __init__(self, modules=None, package=None, is_python_file=False):
        self.module_names = modules
        self.package = package
        self.is_python_file = is_python_file


class UsingStatement(AST):
    def __init__(self, variable, block):
        self.variable = variable
        self.block = block


class ClassStatement(AST):
    def __init__(self, variable, objects, block):
        self.variable = variable
        self.objects = objects
        self.block = block


class DeleteStatement(AST):
    def __init__(self, expression):
        self.expression = expression

# AST: TypeValue
class Number(AST):
    def __init__(self, token):
        self.value = token.value
        self.token = token


class Bool(AST):
    def __init__(self, token):
        self.value = {'True': True, 'False': False}.get(token.value, None)
        self.token = token


class NoneValue(AST):
    def __init__(self, token):
        self.token = token


class Undefined(AST):
    def __init__(self, token):
        self.token = token


class String(AST):
    def __init__(self, token):
        self.token = token
        self.type = token.value[0]
        self.mode = token.value[1]
        self.content = token.value[2]
        self.expr = token.value[3]
        self.expr_ast = {}
        self.expr_form = {}

    def evaluate_expressions(self, interpreter):
        output = {}
        if len(self.expr) >= 1:
            if not len(self.expr_ast) == len(self.expr):
                self.generate_ast(interpreter.parser)

            for name, ast in self.expr_ast.items():
                form = self.expr_form.get(name, None)
                if form:
                    output[name] = form.format(interpreter.visit(ast))
                else:
                    output[name] = interpreter.visit(ast)

        return output

    def generate_ast(self, parser):
        if len(self.expr) >= 1:
            self.expr_ast.clear()
            for name, expr in self.expr.items():
                self.expr_ast[name] = parser.parse_expr(expr)

                if not parser.current_token.type == TokenType.EOF:
                    parser.lexer.back(parser.current_token.pos-1)
                    remaining = parser.lexer.get_remaining_text()
                    if remaining.endswith("="):
                        remaining = remaining[:-1]
                        consume_text = parser.lexer.get_consumed_text()
                        self.expr_form[name] = consume_text+"={0"+remaining+"}"

                    else:
                        self.expr_form[name] = "{0"+remaining+"}"


class Bytes(String):
    pass


class Tuple(AST):
    def __init__(self, *initial_values):
        self.values = []
        for value in initial_values:
            self.add_value(value)

    def add_value(self, new_value: AST):
        self.values.append(new_value)


class List(Tuple):
    pass


class Set(Tuple):
    pass


class Dict(AST):
    def __init__(self, *initial_values):
        self.values = []
        for key, value in initial_values:
            self.add_value(key, value)

    def add_value(self, new_key: AST, new_value: AST):
        self.values.append((new_key, new_value))


# AST: Procedimientos, Funciones y Lambda (funciones anónimas)
class ProcedureDecl(AST):
    def __init__(self, name, params, block, is_local=False):
        self.name = name
        self.params = params
        self.block = block
        self.is_local = is_local


class FunctionDecl(AST):
    def __init__(self, name, params, block, type_=None, is_local=False):
        self.name = name
        self.params = params
        self.block = block
        self.type = type_  # Data-Type of return statement.
        self.is_local = is_local


class LambdaDecl(AST):
    def __init__(self, params, block, type_=None, is_local=False):
        self.params = params
        self.block = block
        self.type = type_  # Data-Type of return statement.
        self.is_local = is_local


class Param(AST):
    def __init__(self, type_, variable, default_value=UNDEFINED_TYPE, tuple_type=False, dict_type=False):
        self.type = type_
        self.variable = variable
        self.name = variable.token.value
        self.value = default_value
        self.mode = "normal"
        if tuple_type:
            self.mode = "tuple"

        elif dict_type:
            self.mode = "dict"


class Call(AST):
    def __init__(self, value, params, kwparams):
        self.value = value
        self.params = params
        self.kwparams = kwparams


class ScriptAction(AST):
    def __init__(self, token, expression):
        self.token = token
        self.action = token.value
        self.data = None
        self.expression = expression
