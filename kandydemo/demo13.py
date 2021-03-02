def verify_type(object_, type_):
    if isinstance(object_, type_) or object_ is None:
        return object_
    else:
        raise TypeError("Unexpected data-type.")

class Persona():
    def __init__(self, name, last_name, age):
        self.name = verify_type(name, str)
        self.last_name = verify_type(last_name, str)
        self.age = verify_type(age, str)

    def get_name(self):
        return self.name
    
    def get_last_name(self):
        return self.last_name

    def get_age(self):
        return self.age

    def __repr__(self):
        return f"Persona(name={self.name!r}, last_name={self.last_name!r}, age={self.age!r})"

    def __str__(self):
        return f"Persona(name={self.name!r}, last_name={self.last_name!r}, age={self.age!r})"

p = Persona("Dylan", "Medina", 0)

print(p)
print("Datos: ", (p.name, p.last_name, p.age))

#return p  # Send 'p' instance to "C"? F, I can't do it.