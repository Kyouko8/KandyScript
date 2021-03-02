# AuxiliarClass
class UndefinedType:
    def __str__(self):
        return "Undefined"

    def __repr__(self):
        return "Undefined"

    def __bool__(self):
        return False

    def __setattr__(self, name, value):
        raise AttributeError("Can't assign an attribute to UndefinedType.")

    def __setitem__(self, index, value):
        raise IndexError("Can't assign an index to UndefinedType.")

    def __eq__(self, other):
        return isinstance(other, UndefinedType)


UNDEFINED_TYPE = UndefinedType()
