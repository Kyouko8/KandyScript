# ArchTemp

TokenType.BIT_OR, TokenType.BIT_XOR, TokenType.BIT_AND,
TokenType.SHIFT_L, TokenType.SHIFT_R,
TokenType.PLUS, TokenType.MINUS,
TokenType.MULT, TokenType.DIV, TokenType.FLOORDIV,
TokenType.MOD, TokenType.SUBMOD,
TokenType.BIT_NOT, TokenType.EXCLAMATION, TokenType.POW,


elif var_name in self.GLOBAL_SCOPE:
                if var_type is not None:
                    return self.error("Can't reassign variable type.")

                else:
                    current_type = self.GLOBAL_SCOPE[var_name][0]
                    if current_type == "CONST":
                        self.error("Can't reassign a constant.")

                    if current_type is None or type(value) == current_type:
                        self.GLOBAL_SCOPE[var_name][1] = value

                    elif value is None:
                        self.GLOBAL_SCOPE[var_name][1] = value

                    else:
                        convert = current_type(value)
                        if type(convert) == current_type:
                            self.GLOBAL_SCOPE[var_name][1] = convert
                        else:
                            self.error(f"Can't assign a {type(value).__name__} to an object of type {current_value}")

            else:
                if value == UNDEFINED_TYPE:
                    if node.right.token is None:
                        self.GLOBAL_SCOPE[var_name] = [None, value]
                    else:
                        raise SyntaxError()

                elif var_type is None:
                    self.GLOBAL_SCOPE[var_name] = [None, value]

                elif var_type.name == "DYNAMIC":
                    self.GLOBAL_SCOPE[var_name] = [None, value]

                elif var_type.name == "VAR":
                    if value is None:
                        self.GLOBAL_SCOPE[var_name] = [None, value]  # Impossible get type of NoneVar
                    else:
                        self.GLOBAL_SCOPE[var_name] = [type(value), value]

                elif var_type.name == "ID":
                    used_type = self.visit(Var(var_type.token))
                    if isinstance(used_type, type):
                        if type(value) == used_type:
                            self.GLOBAL_SCOPE[var_name] = [used_type, value]
                        else:
                            convert = used_type(value)
                            if type(convert) == used_type:
                                self.GLOBAL_SCOPE[var_name] = [used_type, convert]
                            else:
                                self.error(f"The value given is {type(value).__name__} and the variable is defined as {used_type}.")
                    else:
                        return self.error("Invalid TypeVariable.")

                elif var_type.name == "CONST":
                    self.GLOBAL_SCOPE[var_name] = ["CONST", value]

                else:
                    return self.error("Unrecognized TypeVariable.")
