const APELLIDO = "Rodriguez"

class Name(){
    def __init__(self, str name){
        strict str self.name = name
        int self.x = 0
    }

    def str get_name(self) => "{self.name} {APELLIDO}"

    def count(self): self.x += 1

    def upper(self) => self.name.upper()
    
    def add(self, strict str name): self.name += name

}

class UpperName(Name){
    def __init__(self, name){
        super(UpperName, self).__init__(name)
        self.name = self.upper()
    }

    def add(self, name){
        super(UpperName, self).add(name)
        self.name = self.upper()
    }

}

class lista(list){}

UpperName name = UpperName("Dylan")

for i from 1 to 25:
    name.count()

name.add("Medina")
print(repr(name.get_name()))
print(repr(name.upper()))
print(name.x)

lista ls = lista([])
ls.append("Hola")

print(ls.__class__, ls)

return Name
