# Using spaces
import demo9
import demo10

int x = 25
print("{(Global.x := 27)}")

str Now.o = "Holiiiii"
print(demo9.upper(o))

name = "Julian"
def Demo(str name){
    name_upper = name.upper()
    name_lower = name.lower()
    export
}

space = Demo("Dylan")

using space {
    print(name_lower)
    print(name)
    print(Prev.name)
}

using Private{
    int a = 1
    int b = 2
    def str Lower(str value) => value.lower()
    def int Power(int value, int power = 8) => (value ** power)
}

demo10.normal_probando(Private.b)

using Private{
    demo10.normal_probando(
        Power(
            random.randint(
                2,
                10
            ),
            2
        )
    )
}


print(demo10.demo9.upper("Uf, I'll test it."))
print(space.name_upper)
