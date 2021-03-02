str nombre;
str inp_edad;
int edad;

local proc PedirInformacion() begin
    nombre = nombre?? input("Ingrese su nombre: ") # Cargar el nombre, si es posible, o solicitarle al 
                                                   # usuario que lo ingrese.
    inp_edad = input("Ingrese su edad: ") 

    if inp_edad.isdigit() {
        edad = inp_edad
    } else {
        print("El valor ingresado en 'edad' es incorrecto.")
        PedirInformacion()
    }
end

PedirInformacion()

def Upper(str name) => {return name.upper()}

nombre = Upper(nombre)

print("\nPerfil:\n  Nombre: $nombre\n  Edad: $edad")
