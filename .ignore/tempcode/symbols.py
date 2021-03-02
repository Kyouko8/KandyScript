
# Symbol
class Symbol():
    def __init__(self, name, type_=None):
        self.name = name
        self.type = type_


class BuiltInTypeSymbol(Symbol):
    def __init__(self, function, name=None):
        super().__init__(None, None)
        self.function = function
        if name is not None:
            self.name = type(self.function).__name__
        else:
            self.name = name

    def __str__(self):
        return f"<BuiltInType {self.name!r}>"

    __repr__ = __str__


class VarSymbol(Symbol):
    def __str__(self):
        return f"<VarSymbol {self.type!r}: {self.name!r}>"

    __repr__ = __str__


class ScopeSymbolTable():
    def __init__(self, scope_name, scope_level):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltInTypeSymbol(int))
        self.define(BuiltInTypeSymbol(float))
        self.define(BuiltInTypeSymbol(str))
        self.define(BuiltInTypeSymbol(bool))
        self.define(BuiltInTypeSymbol(bytes))
        self.define(BuiltInTypeSymbol(list))
        self.define(BuiltInTypeSymbol(tuple))
        self.define(BuiltInTypeSymbol(dict))

    def __str__(self):
        "Symbol:\n{symbols}".format(
            symbols="\n".join((value for value in self._symbols.values()))
        )

    __repr__ = __str__

    def define(self, symbol):
        print(f"Define {symbol.name} as {symbol}")
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print(f"Lookup for {name}")
        symbol = self._symbols.get(name)
        return symbol
