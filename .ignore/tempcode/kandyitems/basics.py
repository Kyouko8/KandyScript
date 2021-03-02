# Medina Dylan
# 08:11 a.m. 26/11/2020
# KandyItems -> BasicObjects
from decimal import Decimal, getcontext


def kfloat(x):
    if isinstance(x, float):
        x = str(x)
    return Decimal(x)


def get_int(x) -> int:
    if isinstance(x, (KandyInt, KandyFloat)):
        return int(x.get())

    elif isinstance(x, KandyObject):
        new = x.g_int()
        if new is None:
            return new
        else:
            new = x.m_int()
            if new is not None:
                return new.value

    elif isinstance(x, (int, float, str, Decimal)):
        return int(x)


def get_float(x) -> int:
    if isinstance(x, (KandyInt, KandyFloat)):
        return kfloat(x.get())

    elif isinstance(x, KandyObject):
        new = x.g_float()
        if new is None:
            return new
        else:
            new = x.m_float()
            if new is not None:
                return new.value

    elif isinstance(x, (int, float, str, Decimal)):
        return kfloat(x)


class KandyTypeError(TypeError):
    pass


class KandyObject():
    def __init__(self, **kwargs):
        self.value = kwargs.get("DEFAULT_VALUE", None)
        self.class_var = {}
        self.methods = {}
        self.vars = {}

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}(value={self.value}, typevalue={type(self.value).__name__})"

    def get(self):
        return self.value

    def error_two_types(self, method, instance1, instance2):
        type1 = instance1.__class__.__name__
        type2 = instance2.__class__.__name__
        raise KandyTypeError(f"unsupported operand type(s) for {method}: '{type1}' and '{type2}'")

    def error_one_type(self, method, instance1):
        type1 = instance1.__class__.__name__
        raise TypeError(f"unsupported operand type(s) for {method}: '{type1}'")

    # Convert to Python object
    def g_int(self):
        return None

    def g_float(self):
        return None

    def g_str(self):
        return None

    def g_bytes(self):
        return None

    def g_bool(self):
        return None

    def g_iter(self):
        return None

    # Convert to KandyItem:
    def m_int(self):
        return None

    def m_float(self):
        return None

    def m_str(self):
        return "<Instance of KandyObject>"

    def m_repr(self):
        return "<Instance of KandyObject>"

    def m_bytes(self):
        return None

    def m_bool(self):
        return None

    def m_iter(self):
        return None

    # Operations: [one_member]
    def m_not(self):
        self.error_one_type("~", self)

    def m_negative(self):
        self.error_one_type("-", self)

    def m_positive(self):
        self.error_one_type("+", self)

    # Operations: [two_member]
    # normal-methods
    def m_add(self, other):
        self.error_two_types("+", self, other)
        return None

    def m_sub(self, other):
        self.error_two_types("-", self, other)
        return None

    def m_mult(self, other):
        self.error_two_types("*", self, other)
        return None

    def m_floordiv(self, other):
        self.error_two_types("//", self, other)
        return None

    def m_div(self, other):
        self.error_two_types("/", self, other)
        return None

    def m_mod(self, other):
        self.error_two_types("%", self, other)
        return None

    def m_submod(self, other):
        self.error_two_types("%%", self, other)
        return None

    def m_pow(self, other):
        self.error_two_types("**", self, other)
        return None

    def m_and(self, other):
        self.error_two_types("&", self, other)
        return None

    def m_or(self, other):
        self.error_two_types("|", self, other)

    def m_xor(self, other):
        self.error_two_types("^", self, other)

    # i-methods
    def m_iadd(self, other):
        self.value = self.m_add(other)

    def m_isub(self, other):
        self.value = self.m_sub(other)

    def m_imult(self, other):
        self.value = self.m_mult(other)

    def m_ifloordiv(self, other):
        self.value = self.m_floordiv(other)

    def m_idiv(self, other):
        self.value = self.m_div(other)

    def m_imod(self, other):
        self.value = self.m_mod(other)

    def m_isubmod(self, other):
        self.value = self.m_submod(other)

    def m_ipow(self, other):
        self.value = self.m_pow(other)

    def m_iand(self, other):
        self.value = self.m_and(other)

    def m_ior(self, other):
        self.value = self.m_floordiv(other)

    def m_ixor(self, other):
        self.value = self.m_xor(other)

    # r-methods
    def m_radd(self, other):
        other.error_two_types("+", other, self)
        return None

    def m_rsub(self, other):
        other.error_two_types("-", other, self)
        return None

    def m_rmult(self, other):
        other.error_two_types("*", other, self)
        return None

    def m_rfloordiv(self, other):
        other.error_two_types("//", other, self)
        return None

    def m_rdiv(self, other):
        other.error_two_types("/", other, self)
        return None

    def m_rmod(self, other):
        other.error_two_types("%", other, self)
        return None

    def m_rsubmod(self, other):
        other.error_two_types("%%", other, self)
        return None

    def m_rpow(self, other):
        other.error_two_types("**", other, self)
        return None

    def m_rand(self, other):
        other.error_two_types("&", other, self)
        return None

    def m_ror(self, other):
        other.error_two_types("|", other, self)

    def m_rxor(self, other):
        other.error_two_types("^", other, self)


class KandyInt(KandyObject):
    def __init__(self, x):
        super().__init__()
        self.value = get_int(x)

    def repr(self):
        return f"KandyFloat({self.value})"

    # Python methods
    def g_int(self):
        return int(self.value)

    def g_float(self):
        return kfloat(self.value)

    # Kandy Items methods
    def m_int(self):
        return KandyInt(self.value)

    def m_float(self):
        return KandyFloat(self.value)

    def m_str(self):
        return str(self.value)

    def m_bytes(self):
        return bytes(self.value)

    def m_bool(self):
        return bool(self.value)

    def m_iter(self):
        return iter(self.value)

    # Control:
    def _get_value(self, instance):
        if isinstance(instance, KandyInt):
            return instance.value

        elif isinstance(instance, int):
            return instance

        else:
            raise KandyTypeError("Try apply reverse_method")

    def verify_type(self, data):
        if isinstance(data, int):
            return KandyInt(data)

        elif isinstance(data, Decimal):
            return KandyFloat(data)

    # Operations [one_member]
    def m_not(self):
        return self.verify_type(~self.value)

    def m_negative(self):
        return self.verify_type(-self.value)

    def m_positive(self):
        return self.verify_type(+self.value)

    # Operations [two_members]
    def m_add(self, other):
        return self.verify_type(self.value + self._get_value(other))

    def m_sub(self, other):
        return self.verify_type(self.value - self._get_value(other))

    def m_mult(self, other):
        return self.verify_type(self.value * self._get_value(other))

    def m_floordiv(self, other):
        return self.verify_type(self.value // self._get_value(other))

    def m_div(self, other):
        value = self.value / self._get_value(other)
        if value == int(value):
            return KandyInt(value)
        else:
            return self.verify_type(value)

    def m_mod(self, other):
        return self.verify_type(self.value % self._get_value(other))

    def m_submod(self, other):
        value2 = self._get_value(other)
        return self.verify_type(value2 - (self.value % value2))

    def m_pow(self, other):
        return self.verify_type(self.value ** self._get_value(other))

    def m_and(self, other):
        return self.verify_type(self.value & self._get_value(other))

    def m_or(self, other):
        return self.verify_type(self.value | self._get_value(other))

    def m_xor(self, other):
        return self.verify_type(self.value ^ self._get_value(other))

    # Functions:
    def f_count(self, value):
        self.value += self._get_value(value)
        return self

    def f_percent_of(self, totalvalue=100):
        total = self._get_value(totalvalue)
        return self.verify_type(kfloat(self.value * 100) / total)

    def f_percent(self, percent=100):
        percent = kfloat(self._get_value(percent)) / 100
        return self.verify_type(self.value * percent)


class KandyFloat(KandyObject):
    def __init__(self, x):
        super().__init__()
        self.value = get_float(x)

    def repr(self):
        return f"KandyFloat({self.value})"

    # Python Methods
    def g_int(self):
        return int(self.value)

    def g_float(self):
        return kfloat(self.value)

    # KandyMethods
    def m_int(self):
        return KandyInt(self.value)

    def m_float(self):
        return KandyFloat(self.value)

    def _get_value(self, instance):
        if isinstance(instance, (KandyFloat, KandyInt)):
            return kfloat(instance.value)

        elif isinstance(instance, (float, int, Decimal)):
            return kfloat(instance)

        else:
            raise KandyTypeError("Try apply reverse_method")

    def verify_type(self, data):
        if isinstance(data, (float, int, Decimal)):
            return KandyFloat(data)

    # Operations [one_member]
    def m_not(self):
        return self.verify_type(~self.value)

    def m_negative(self):
        return self.verify_type(-self.value)

    def m_positive(self):
        return self.verify_type(+self.value)

    # Operations [two_members]
    def m_add(self, other):
        return self.verify_type(self.value + self._get_value(other))

    def m_sub(self, other):
        return self.verify_type(self.value - self._get_value(other))

    def m_mult(self, other):
        return self.verify_type(self.value * self._get_value(other))

    def m_floordiv(self, other):
        return self.verify_type(self.value // self._get_value(other))

    def m_div(self, other):
        return self.verify_type(self.value / self._get_value(other))

    def m_mod(self, other):
        return self.verify_type(self.value % self._get_value(other))

    def m_submod(self, other):
        value2 = self._get_value(other)
        return self.verify_type(value2 - (self.value % value2))

    def m_pow(self, other):
        return self.verify_type(self.value ** self._get_value(other))

    def m_and(self, other):
        return self.verify_type(self.value & self._get_value(other))

    def m_or(self, other):
        return self.verify_type(self.value | self._get_value(other))

    def m_xor(self, other):
        return self.verify_type(self.value ^ self._get_value(other))

    def m_iadd(self, other):
        self.value += self._get_value(other)

    def m_isub(self, other):
        self.value -= self._get_value(other)

    def m_imult(self, other):
        self.value *= self._get_value(other)

    def m_ifloordiv(self, other):
        self.value //= self._get_value(other)

    def m_idiv(self, other):
        self.value /= self._get_value(other)

    def m_imod(self, other):
        self.value %= self._get_value(other)

    def m_isubmod(self, other):
        value2 = self._get_value(other)
        self.value = value2 - (self.value % value2)

    def m_ipow(self, other):
        self.value **= self._get_value(other)

    def m_iand(self, other):
        self.value &= self._get_value(other)

    def m_ior(self, other):
        self.value |= self._get_value(other)

    def m_ixor(self, other):
        self.value ^= self._get_value(other)

    def m_radd(self, other):
        return self.verify_type(self._get_value(other) + self.value)

    def m_rsub(self, other):
        return self.verify_type(self._get_value(other) - self.value)

    def m_rmult(self, other):
        return self.verify_type(self._get_value(other) * self.value)

    def m_rfloordiv(self, other):
        return self.verify_type(self._get_value(other) // self.value)

    def m_rdiv(self, other):
        return self.verify_type(self._get_value(other) / self.value)

    def m_rmod(self, other):
        return self.verify_type(self._get_value(other) % self.value)

    def m_rsubmod(self, other):
        return self.verify_type(self.value - (self._get_value(other) % self.value))

    def m_rpow(self, other):
        return self.verify_type(self._get_value(other) ** self.value)

    def m_rand(self, other):
        return self.verify_type(self._get_value(other) & self.value)

    def m_ror(self, other):
        return self.verify_type(self._get_value(other) | self.value)

    def m_rxor(self, other):
        return self.verify_type(self._get_value(other) ^ self.value)

    # Functions
    def f_count(self, value):
        self.value += self._get_value(value)
        return self

    def f_percent_of(self, totalvalue=100):
        total = self._get_value(totalvalue)
        return self.verify_type(kfloat(self.value * 100) / total)

    def f_percent(self, percent=100):
        percent = kfloat(self._get_value(percent)) / 100
        return self.verify_type(self.value * percent)
