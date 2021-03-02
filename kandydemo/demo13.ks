class Persona(){
    proc __init__(Persona self, str name, str last_name, int age){
        self.name = name
        self.last_name = last_name
        self.age = age
    }

    def str get_name() => self.name
    
    def str get_last_name(self) => self.last_name

    def int get_age() => self.age

    def int get_aage() => get_age(self)

    def str __repr__(): using self => "Persona({name!r=}, {last_name!r=}, {age!r=})"

    def str __str__(): using self => "Persona({name!r=}, {last_name!r=}, {age!r=})" 

    def Persona copy(){
        return Persona(self.name, self.last_name, self.age)
    }
}

Persona p = Persona("Dylan", "Medina", 12)

print(p)
print(p.get_name())
print(p.get_last_name())
print(Persona.get_name(p))
print(Persona.get_last_name(p))
print(p.get_aage())
print("Datos: ", {using p => (name, last_name, age)})

return p #Send 'p' instance to python.