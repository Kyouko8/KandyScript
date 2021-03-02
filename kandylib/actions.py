import time
import os

from .undefined import UNDEFINED_TYPE
from .callstack import ActivationRecord, ARType, Record, RecordConstant
from .ast import ScriptAction, Var, Param, TypeVar
from .tokentype import TokenType, Token


# Actions Class
class ProcedureCall():
    def __init__(self, interpreter, name, block, params, is_local=False):
        # Information:
        self.name = name
        self.__interpreter = interpreter
        self.__ar = self.__interpreter.call_stack.peek()
        self.__block = block
        self.__params = params
        self.__is_local = is_local
        self._inside_class = interpreter.is_inside_class()

        # Arguments:
        self.__args = []
        self.__kwargs = {}

        self.__process_params()

    def __process_params(self):
        if self._inside_class:
            add_self = True
            if len(self.__params) >= 1:
                p = self.__params[0]
                if p.name == "self":
                    add_self = False

            if add_self:
                token = Token(TokenType.ID, "self", pos=None, lineno=None, column=None)
                var = Var(token)
                self.__params.insert(0, Param(None, var))

        for param in self.__params:
            if param.name == "self" and self._inside_class:
                continue

            if param.mode == "normal":
                self.__kwargs[param.variable.value] = param

            if param.value is UNDEFINED_TYPE:
                self.__args.append(param)

            if param.mode == "dict":
                self.__kwargs['$$$KWDICT$$$'] = param

    def __prepare_params(self, args, kwargs):
        pos = 0
        len_args = len(args)
        used_names = []

        # Load Values from: default_values
        for param in self.__params:
            if param.mode == "tuple":
                self.__interpreter.assign(value=None, name=param.variable.value, var_type=None)
            elif param.mode == "dict":
                self.__interpreter.assign(value=None, name=param.variable.value, var_type=None)
            else:
                self.__interpreter.assign(value=param.value, name=param.variable.value, var_type=param.type)

        # Load Values from: kwargs
        kwdict = {}
        for name, value in kwargs.items():
            try:
                param = self.__kwargs[name]
            except KeyError as exc_ke:
                try:
                    param = self.__kwargs['$$$KWDICT$$$']
                    kwdict[name] = value
                    self.__interpreter.assign(value=kwdict, name=param.variable.value, var_type=None)
                    continue

                except KeyError:
                    raise exc_ke

            if name in used_names:
                message = f"{self.name}() got multiple values for keyword argument '{name}'"
                raise TypeError(message)

            self.__interpreter.assign(value=value, name=name, var_type=None)
            used_names.append(name)

        # Load Value from: args
        no_more_params = False
        for param in self.__params:
            name = param.variable.value
            if param.mode == "tuple":
                self.__interpreter.assign(value=args[pos:], name=name, var_type=None)
                pos += len(args[pos:])
                used_names.append(name)

            elif param.mode == "dict":
                continue

            elif pos < len_args and not no_more_params:
                if name in used_names:
                    message = f"{self.name}() got multiple values for keyword argument '{name}'"
                    raise TypeError(message)

                self.__interpreter.assign(value=args[pos], name=name, var_type=None)
                used_names.append(name)

            elif param.value is not UNDEFINED_TYPE and name not in used_names:
                self.__interpreter.assign(value=param.value, name=name, var_type=None)
                used_names.append(name)

            elif name in used_names:
                no_more_params = True

            else:
                message = f"{self.name} expected {len(self.__args)}, got {len_args}."
                raise TypeError(message)

            pos += 1

        if len_args > pos:
            message = f"{self.name}() takes {pos} positional arguments but {len_args} were given"
            raise TypeError(message)

    def __call__(self, *args, **kwargs):
        # ActivationRecords:
        if not self.__is_local:
            current_ar = self.__interpreter.call_stack.peek()
            new_ar = ActivationRecord(
                name=self.name,
                type_=ARType.PROCEDURE,
                nesting_level=current_ar.nesting_level+1,
                nesting_record=self.__ar  # interpreter.get_global_AR()
            )
            self.__interpreter.call_stack.push(new_ar)

        # Prepare Real-Params and Interpret the body (block):
        self.__prepare_params(args, kwargs)
        self.__interpreter.visit(self.__block)

        # Restore AR:
        if not self.__is_local:
            self.__interpreter.call_stack.pop()


class FunctionCall():
    def __init__(self, interpreter, name, block, params, type_=None, strict=False, is_local=False):
        # Information:
        self.name = name
        self.__interpreter = interpreter
        self.__ar = interpreter.call_stack.peek()
        self.__block = block
        self.__params = params
        self.__is_local = is_local
        self._inside_class = interpreter.is_inside_class()

        # Type
        self.__type = type_
        self.__strict = strict

        # Args:
        self.__args = []
        self.__kwargs = {}

        self.__process_params()

    def __process_params(self):
        if self._inside_class:
            add_self = True
            if len(self.__params) >= 1:
                param = self.__params[0]
                if param.name == "self":
                    add_self = False

            if add_self:
                token = Token(TokenType.ID, "self", pos=None, lineno=None, column=None)
                var = Var(token)
                self.__params.insert(0, Param(None, var))

        for param in self.__params:
            if param.mode == "normal":
                self.__kwargs[param.variable.value] = param

            if param.value is UNDEFINED_TYPE:
                self.__args.append(param)

            if param.mode == "dict":
                self.__kwargs['$$$KWDICT$$$'] = param

    def __prepare_params(self, args, kwargs):
        pos = 0
        len_args = len(args)
        used_names = []

        # Load Values from: default_values
        # Prepare all params and params-type.
        for param in self.__params:
            if param.mode == "tuple":
                self.__interpreter.assign(value=None, name=param.variable.value, var_type=None)
            elif param.mode == "dict":
                self.__interpreter.assign(value=None, name=param.variable.value, var_type=None)
            else:
                self.__interpreter.assign(value=param.value, name=param.variable.value, var_type=param.type)

        # Load Values from: kwargs
        kwdict = {}
        for name, value in kwargs.items():
            try:
                param = self.__kwargs[name]

            except KeyError as exc_ke:
                try:
                    param = self.__kwargs['$$$KWDICT$$$']
                    kwdict[name] = value
                    self.__interpreter.assign(value=kwdict, name=param.variable.value, var_type=None)
                    continue

                except KeyError:
                    raise exc_ke

            if name in used_names:
                message = f"{self.name}() got multiple values for keyword argument '{name}'"
                raise TypeError(message)

            self.__interpreter.assign(value=value, name=name, var_type=None)
            used_names.append(name)

        # Load Value from: args
        no_more_params = False
        for param in self.__params:
            name = param.variable.value

            if param.mode == "tuple":
                self.__interpreter.assign(value=args[pos:], name=name, var_type=None)
                pos += len(args[pos:])
                used_names.append(name)

            elif param.mode == "dict":
                continue

            elif pos < len_args and not no_more_params:
                if name in used_names:
                    message = f"{self.name}() got multiple values for keyword argument '{name}'"
                    raise TypeError(message)

                self.__interpreter.assign(value=args[pos], name=name, var_type=None)
                used_names.append(name)

            elif param.value is not UNDEFINED_TYPE and name not in used_names:
                self.__interpreter.assign(value=param.value, name=name, var_type=None)
                used_names.append(name)

            elif name in used_names:
                no_more_params = True

            else:
                message = f"{self.name} expected {len(self.__args)}, got {len_args}."
                raise TypeError(message)

            pos += 1

        if len_args > pos:
            message = f"{self.name}() takes {pos} positional arguments but {len_args} were given"
            raise TypeError(message)

    def __get_type(self):
        if isinstance(self.__type, TypeVar):
            self.__interpreter.call_stack.push(self.__ar)
            type_ = self.__type

            if type_ is not None:
                if type_.name == "ID":
                    self.__type = self.__interpreter.visit(Var(type_.token))

                elif type_.name == "DYNAMIC":
                    self.__type = None

                elif type_.name == "MULTIPLE":
                    type_return = []
                    for token in type_.token:
                        type_return.append(self.__interpreter.visit(Var(token)))

                    self.__type = type_return

            self.__interpreter.call_stack.pop()

        return self.__type

    def __call__(self, *args, **kwargs):
        # ActivationRecords:
        if not self.__is_local:
            current_ar = self.__interpreter.call_stack.peek()
            new_ar = ActivationRecord(
                name=self.name,
                type_=ARType.PROCEDURE,
                nesting_level=current_ar.nesting_level+1,
                nesting_record=self.__ar  # interpreter.get_global_AR()
            )
            self.__interpreter.call_stack.push(new_ar)

        # Prepare Real-Params and Interpret the body (block):
        self.__prepare_params(args, kwargs)
        result = self.__interpreter.visit(self.__block)

        # Restore AR:
        if not self.__is_local:
            self.__interpreter.call_stack.pop()

        # Verify the result type data:
        if isinstance(result, ScriptAction):
            if result.token.type == TokenType.RETURN:
                result = result.data
            else:
                return result

        if (result is not None) and (self.__type is not None):
            rec = Record(result, self.__get_type(), self.__strict)
            result = rec.value

        return result


class Spaces():
    pass


class ModuleClass(Spaces):
    def __init__(self, interpreter, filename, name):
        self.__filename = os.path.abspath(filename)
        self.__name = name
        self.__ar = None
        self.make(interpreter)

    def make(self, interpreter):
        module_inter = interpreter.__class__()
        module_inter.init_components(self.__name)
        # Set Main = False
        main = module_inter.get_main_AR()
        main.set_read_only(False)
        main['KANDY_MAIN'] = RecordConstant(False)
        main['KANDY_TYPE'] = RecordConstant("module")
        main.set_read_only(True)
        # Copy user objects:
        module_inter.copy_ar(interpreter.get_user_AR(), 2, ignore_read_only=True)
        # GetCurrentModulesImported
        module_inter.modules_imported.update(interpreter.modules_imported)
        # Interpret
        module_inter.interpret_from_filename(self.__filename, reset=False)
        self.__ar = module_inter.get_global_AR()
        # Add Protect:
        self.__ar.set_read_only(True)

        interpreter.modules_imported[self.__filename] = self
        interpreter.modules[self] = self.__ar

        for k in module_inter.modules:
            if k in interpreter.modules:
                continue

            interpreter.modules[k] = module_inter

    def __getattr__(self, name):
        if name.startswith("_"):
            return self.__dict__[name]

        else:
            return self.__ar.get(name)

    def __repr__(self):
        return f"Module(<Name: {self.__name!r}, File: {self.__filename}>)"

    def __str__(self):
        return f"Module(<Name: {self.__name!r}, File: {self.__filename}>)"


class SpaceClass(Spaces):
    def __init__(self, interpreter, ar, name):
        self.__ar = ar
        self.__name = name
        interpreter.spaces[self] = ar

    def __repr__(self):
        return f"Space(<Name: {self.__name!r}, Space: {self.__ar.name}, Values: {len(self.__ar)}>)"

    def __str__(self):
        return (f"Space(<Name: {self.__name!r}, Space: {self.__ar.name}, "
                f"Values: {len(self.__ar)}>, <Data: \n{self.__ar}\n>)")


class CurrentSpaceClass(Spaces):
    def __init__(self, interpreter):
        self.__interpreter = interpreter

    def __repr__(self):
        ar = self.__interpreter.call_stack.peek()
        return f"Space(<Name: CurrentSpace, Space: {ar.name}, Values: {len(ar)}>)"

    def __str__(self):
        ar = self.__interpreter.call_stack.peek()
        return (f"Space(<Name: CurrentSpace, Space: {ar.name}>, "
                f"Values: {len(ar)}>, <Data: \n{ar}\n>)")


class PrevSpaceClass(Spaces):
    def __init__(self, interpreter):
        self.__interpreter = interpreter

    def __repr__(self):
        ar = self.__interpreter.call_stack.peek_prev()
        return f"Space(<Name: PrevSpace, Space: {ar.name}, Values: {len(ar)}>)"

    def __str__(self):
        ar = self.__interpreter.call_stack.peek_prev()
        return (f"Space(<Name: PrevSpace, Space: {ar.name}>, "
                f"Values: {len(ar)}>, <Data: \n{ar}\n>)")


class PrivateSpaceClass(Spaces):
    def __init__(self, interpreter):
        self.__interpreter = interpreter
        self.__id = interpreter.id

    def __repr__(self):
        ar = self.__interpreter.get_private_AR()
        return f"Space(<Name: PrivateSpace, Space: {ar.name}, Values: {len(ar)}>)"

    def __str__(self):
        ar = self.__interpreter.get_private_AR()
        return (f"Space(<Name: Private, Space: {ar.name}>, "
                f"Values: {len(ar)}>, <Data: \n{ar}\n>)")

    def verifyID(self, id_):
        return (self.__id == id_)


class MultipleTypesClass():
    def __init__(self, *tuple_cls):
        self._valid_types = tuple(filter(lambda x: isinstance(x, type), tuple_cls))

    def get_valid_types(self):
        return self._valid_types

    def __repr__(self):
        return f"MultipleTypesClass({', '.join(map(lambda x: x.__name__, self._valid_types))})"

    def __str__(self):
        return f"MultipleTypesClass({', '.join(map(lambda x: x.__name__, self._valid_types))})"

    get = property(get_valid_types, None, None, "Get the valid types")


class Numeric(MultipleTypesClass):
    def __init__(self):
        super().__init__(int, float)

# LoopControl for: While, Until, Do-While, Do-Until, For
class LoopControl():
    def __init__(self):
        self.__count = 0  # Iterations started
        self.__finished = 0  # Iterations finished
        self.__remaining_ignore = 0  # Will be ignore
        self.__ignored = 0  # Was ignored
        self.__time_start = time.time()  # Start time
        self.__time_end = None  # End time for average information
        self.__last_count_time = None  # Record time.
        self.__is_running = True  # Flag

    def __repr__(self):
        return f"<LoopControl count={self.__count}, finished={self.__finished}>"

    def __str__(self):
        return f"<LoopControl count={self.__count}, finished={self.__finished}>"

    def _finish(self):
        self.__is_running = False
        self.__time_end = time.time()

    def _count(self):
        self.__count += 1
        self.__last_count_time = time.time()

    def _count_finished(self):
        self.__finished += 1

    def _ignore(self):
        self.__ignored += 1

    def reset_ignore(self):
        self.__remaining_ignore = self.__ignored

    def ignore_next_iterations(self, count):
        self.__remaining_ignore += count

    def get_count(self):
        return self.__count

    def get_count_finished(self):
        return self.__finished

    def get_remaining_ignore_count(self):
        return max(0, self.__remaining_ignore - self.__ignored)

    def get_ignored(self):
        return self.__ignored

    def get_time_start(self):
        return self.__time_start

    def get_time_end(self):
        return self.__time_end

    def get_time_total(self):
        if self.__time_end is None:
            return time.time() - self.__time_start
        else:
            return self.__time_end - self.__time_start

    def get_time_of_last_iteration(self):
        if self.__last_count_time is None:
            return 0

        return self.__last_count_time - self.__time_start

    def get_time_average(self):
        if self.__count <= 0:
            return 0

        if self.__time_end is None:
            return (time.time() - self.__time_start) / self.__count
        else:
            return (self.__time_end - self.__time_start) / self.__count

    def is_running(self):
        return self.__is_running


# Take:
# Function for the reserverd keyword "take" (ForInStatement)
def take_splitter(expression, count=2, values_to_unpack=1):
    take = []
    if values_to_unpack == 1:
        for i in expression:
            take.append(i)
            if len(take) == count:
                yield tuple(take)
                take.clear()

        if len(take) >= 1:
            yield tuple(take)
            take.clear()

    elif values_to_unpack >= 2:
        for i in expression:
            take.append(i)
            if len(take) == count:
                yield tuple(zip(*take))
                take.clear()

        if len(take) >= 1:
            yield tuple(zip(*take))
            take.clear()
