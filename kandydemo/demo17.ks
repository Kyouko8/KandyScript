# KandyScript:
# Ejemplo 3

hello = lambda [str] (str name="world") => "Hello $name"
say = lambda [str] (str what_say="Hello world") => {
    print(what_say)
    return what_say
}

string = MultipleTypesClass(str, bytes)
numeric y = 3
y = 3.4
multiple (Global.int, Global.str, Global.float) i = 80

private var z = 20
private int x = 20

print(x, b'hola')
print(numeric, int)

def pr(s, x=7) => s*x

print(pr(2, x))