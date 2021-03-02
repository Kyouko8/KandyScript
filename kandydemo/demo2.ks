def Name(name1, str name2, strict str name3="Med"){
    return (name1, name2, name3)
}

proc Sumar(*numeros){
    print(numeros)
    r = sum(numeros)
    print(r)
}

proc Show(value){print(value)}

proc XD(x, dylan=70, **kw)
{
    print(x, dylan, kw)
}

int num1 = 14
int num2 = 13
int resultado = 27
print("[F-s] La suma de $num1 + $num2 es {num1+num2}")
print(f"[F-s] El resultado es $resultado")
print(r"[Raw] El resultado es $resultado\nLa suma es mágica.")
print(n"[Nor] El resultado es $resultado\nLa suma es mágica.")

dirname = p".\homework"
str ruta = p"$dirname\ruta1"

tuple t = ("Dyl",)
dict d = ${'name3': "Dylan",}

print("NAME: ", *Name(*t, name2="hola mundo", **d))

Sumar(2, 3, 4)

XD(15, 180, hola=25, mundo=30)


return "-".join(Name("Dylan", "Joel", "Medina"))