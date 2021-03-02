#KandyScript File

# Crear procedures
proc Name(str my_name = "Dylan"){
    x = "Nameeeeeeeeeeeeeeeeee"
    print(x)
}

# Crear variables

const CONSTANTE = 250
strict int num3 = 260
var o = None
int num1 = 28
int num2 = 38 if (num4:=27) == 27 else 20
int num88 = ['8'][0]
bool boo = 17
bool true = True
bool false = False
tuple t1 = (num1,)
tuple t2 = (num1, num2)
tuple t3 = (num1, num2, boo)
tuple t4 = (t1, t2, (num1, boo, true))
x = t1[0]
dict d = ${'a': 65, 'b': 70}
set s = ${20, 40, 50}
var b = ${}
var b[20] = 60
var z = "hola mundo".upper()
list lis = [20, 40, 60]
lis.append(80)
Token token = Token(TokenType.ID, 'CONSTANTE', pos=45, lineno=5, column=7)
token.hola = token.type
print(token)
print(Name("Jose")?? "Sin Salida")

num3 = "35"
7
# Sumar los números y guardar el resultado.
int resultado = num1 + num2

# Actualizar la variable.
resultado = resultado + num1 * 2

resultado += 1

resultado = None

int testThis;

print(testThis)
print("Resultado:", resultado)


# Question assignment
numero = 8

# Si el valor retornado por la funcion es considerado True (bool(output) == True),
# entonces el valor es asignado, de lo contrario, el valor no cambia.

#numero ?= function1()


# Multiple var_type
# multiple (int, float, str)