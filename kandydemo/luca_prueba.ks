users = []
passwords = ${}

def crear_usuario(){
	str username = input("Nombre de usuario: ").lower()

	while username in users{
		print("")
		print("El nombre de usuario ya existe.")
		username = input("Nombre de usuario: ").lower()
	}


	str password = input("Contraseña: ")

	users.append(username)
	passwords[username] = password

	return True
}

def iniciar_sesion(){
	username = input("Nombre de usuario: ")

	if username not in users{
		print("El nombre de usuario no se encuentra registrado.")
		break

	}else{
		password = input("Contraseña: ")

		if passwords[username] == password: return True
		else: return False
	}
}

if not users{
	print("No hay usuarios añadidos.")
	print("Cree un usuario")

	crear_usuario()
}


while True as menu_loop{
	print("")
	print("+-------------------+")
	print("| 1. Iniciar Sesión |")
	print("| 2. Crear usuario  |")
	print("| 3. Salir          |")
	print("+-------------------+")
	op = input("> ")
	print("")

	switch op{
		case "1": {
			if iniciar_sesion(){
				print("Has iniciado sesión")
				break:menu_loop
			}
		}
		case "2": crear_usuario()
		case "3": break:menu_loop
	}
}