from enum import Enum
from .tokentype import TokenType
from .undefined import UNDEFINED_TYPE
from . import kandyerrors as kerr


# CallStack
class CallStack():
    def __init__(self):
        self._records = []

    def __str__(self):
        s = '\n\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'{" CALL-STACK ":-^80}\n{s}\n{"-"*80}\n'
        return s

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self._records)

    def push(self, ar):
        self._records.append(ar)

    def pop(self):
        return self._records.pop()

    def peek(self):
        return self._records[-1]

    def peek_prev(self, count=1):
        if count <= 0:
            raise ValueError("Invalid 'peek' value on CallStack.")

        if len(self._records) >= (1+count):
            return self._records[-1-count]

        elif len(self._records) >= 1 and len(self._records) <= count:
            return self._records[-1]

    def clear(self):
        self._records.clear()

    def copy(self, ar_src, index, ignore_read_only=False):
        ar_dst = self._records[min(len(self._records), index)]

        if ignore_read_only:
            rd_only = ar_dst.read_only
            ar_dst.set_read_only(False)

        for name, value in ar_src:
            ar_dst[name] = value

        if ignore_read_only:
            ar_dst.read_only = rd_only

    def get(self, index):
        return self._records[min(len(self._records), index)]


class ARType(Enum):
    BUILTIN = "BuiltIn"
    GLOBAL = "Global"
    PROCEDURE = "Procedure"
    FUNCTION = "Function"
    CLASS = "Class"
    INTERN_CLASS = "InternClass"
    MODULE = "Module"
    USER = "User"
    PRIVATE = "Private"


class ActivationRecord():
    def __init__(self, name, type_, nesting_level, nesting_record=None):
        self.name = name
        self.type = type_
        self.nesting_level = nesting_level
        self.nesting_record = nesting_record
        self.members = {}
        self.read_only = False

    def __iter__(self):
        for name, value in self.members.items():
            yield name, value

    def __contains__(self, value):
        return value in self.members

    def __setitem__(self, key, value):
        if self.read_only:
            print(self, key, value)
            raise kerr.KandyProtect("Access denied to edit values in this space.")
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def __delitem__(self, key):
        print("DELETE: ", repr(key))

    def __len__(self):
        return len(self.members)

    def get(self, key, local_only=False, *, private_are_allowed=True):
        if key in self.members:
            member = self.members.get(key, None)
            if isinstance(member, Record):
                if member.private:
                    if private_are_allowed:
                        return member
                else:
                    return member
            else:
                return member

        if (not local_only) and (self.nesting_record is not None):
            return self.nesting_record.get(key, private_are_allowed=False)

        else:
            message = f"{key!r} [On KandyScript]"
            raise NameError(message)

    def __str__(self):
        lines = [
            'AR in level {level}: [{type}] {name}'.format(
                level=self.nesting_level,
                type=self.type.value,
                name=self.name,
            )
        ]
        for name, val in self.members.items():
            lines.append(f'   {name:<20}: {val!r}')

        s = '\n'.join(lines)
        return s

    def __repr__(self):
        return self.__str__()

    def set_read_only(self, state):
        self.read_only = bool(state)

    def as_dict(self):
        return self.members.copy()

    def remove(self, key):
        self.members.pop(key)


class Record():
    def __init__(self, value, type_=None, strict=False, private=False, undefined=False):
        self.private = private
        self.type = type_
        self.strict = strict
        self.value = value

        if not undefined:
            self.validate()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        private = ""
        if self.private:
            private = " ~Private~"
        if isinstance(self.type, (tuple, list)):
            return f"<Record{private} [{', '.join(t.__name__ for t in self.type)}]: {self.value!r}>"
        elif self.type is None:
            return f"<Record Dynamic{private}: {self.value!r}>"
        else:
            return f"<Record{private} [{self.type.__name__}]: {self.value!r}>"

    def __eq__(self, other):
        if isinstance(other, Record):
            return self.value == other.value and self.is_valid_value(other.value)
        else:
            return self.value == other and self.is_valid_value(other)

    def check_multiple_types(self, *types):
        """ Return the type that match with any type inside this record. """
        for t in types:
            if self.is_valid_type(t):
                return t

        return None

    def is_valid_type(self, type_):
        if self.type is None:
            return True

        elif isinstance(self.type, (tuple, list)):
            return type_ in self.type

        elif isinstance(type_, type):
            return self.type == type_

        else:
            return False

    def is_valid_value(self, value):
        if value is None:
            return True

        return self.is_valid_type(type(value))

    def _set_value(self, newvalue, operation=None):
        if operation is None:
            self.value = newvalue

        # Tokens:
        # -     BIT_OR, BIT_XOR, BIT_AND, SHIFT_L, SHIFT_R, PLUS, MINUS,
        # -     MULT, DIV, FLOORDIV, MOD, SUBMOD, POW, MATRIX_MUL

        elif operation.type == TokenType.PLUS:
            self.value += newvalue

        elif operation.type == TokenType.MINUS:
            self.value -= newvalue

        elif operation.type == TokenType.MULT:
            self.value *= newvalue

        elif operation.type == TokenType.DIV:
            self.value /= newvalue

        elif operation.type == TokenType.FLOORDIV:
            self.value //= newvalue

        elif operation.type == TokenType.MOD:
            self.value %= newvalue

        elif operation.type == TokenType.SUBMOD:
            left = newvalue - (self.value % newvalue)
            self.value = left

        elif operation.type == TokenType.POW:
            self.value **= newvalue

        elif operation.type == TokenType.BIT_OR:
            self.value |= newvalue

        elif operation.type == TokenType.BIT_XOR:
            self.value ^= newvalue

        elif operation.type == TokenType.BIT_AND:
            self.value &= newvalue

        elif operation.type == TokenType.SHIFT_L:
            self.value <<= newvalue

        elif operation.type == TokenType.SHIFT_R:
            self.value >>= newvalue

        elif operation.type == TokenType.MATRIX_MUL:
            self.value @= newvalue

    def set_value(self, newvalue, operation=None):
        if self.is_valid_value(newvalue):
            self._set_value(newvalue, operation)

        elif newvalue is UNDEFINED_TYPE:
            raise TypeError("Can't assign again the 'Undefined' value. Use 'None' instead.")

        elif not self.strict:
            try:
                obj = self.get_type()
                newvalue2 = obj(newvalue)
                if self.is_valid_value(newvalue2):
                    self._set_value(newvalue2, operation)

            except Exception:
                message = f"Can't assign '{type(newvalue).__name__}' to '{self.get_type().__name__}'"
                raise TypeError(message)

        else:
            message = f"Can't assign '{type(newvalue).__name__}' to '{self.get_type().__name__}' (strict mode is enabled)."
            raise TypeError(message)

    def get_value(self):
        return self.value

    def validate(self):
        if not self.is_valid_value(self.value):
            self.set_value(self.value)

    def get_type(self):
        if isinstance(self.type, (tuple, list)):
            return self.type[0]

        else:
            return self.type


class RecordConstant(Record):
    def __init__(self, value, private=False):
        super().__init__(value=value, type_=None, strict=True, private=private, undefined=False)
        self.type = "Constant"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"<RecordConstant: {self.value!r}>"

    def set_value(self, newvalue, operation=None):
        raise TypeError("Can't reassign a value to 'Constant'.")


class RecordPrivate(Record):
    pass


# ClassObject With ActivationRecord Control
class ClassObjectWithARC():
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value

        elif name in self.__activationrecord:
            item = self.__activationrecord[name]
            if isinstance(item, Record):
                item.set_value(value)
            else:
                item = Record(item)
                item.set_value(value)
                self.__ar[name] = item

        else:
            self.__activationrecord[name] = value

    def __getattr__(self, name):
        if name in ("_ClassObjectWithARC__activationrecord"):
            if name in self.__dict__:
                return self.__dict__[name]

            elif "_ClassObjectWithARC__ar" in type(self).__dict__:
                class_ar = type(self).__dict__['_ClassObjectWithARC__ar']

                ar = ActivationRecord(
                    name="InternClassAR",
                    type_=ARType.INTERN_CLASS,
                    nesting_level=class_ar.nesting_level+1,
                    nesting_record=class_ar,
                )

                self.__dict__["_ClassObjectWithARC__activationrecord"] = ar
                return ar

        elif name in self.__dict__:
            return self.__dict__[name]

        elif name in type(self).__dict__:
            return type(self).__dict__[name]

        else:
            data = self.__activationrecord.get(name)
            if isinstance(data, Record):
                return data.value
            else:
                return data
