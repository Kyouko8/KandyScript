
print("\n")
str normal_text = "Hola mundo, mi casa es blanca con rejas negras."
normal_text ?= "nunca dire eso que fue"
str encrypt_text = normal_text.simple_encrypt("password")
str decrypt_text = "" #= encrypt_text.simple_decrypt("password")
str decrypt_text_wrong_password = encrypt_text.simple_decrypt("Password")

str password = "password"
until decrypt_text == normal_text as loop{
    random.seed(time.time())
    password = password.unsort()
    decrypt_text = encrypt_text.simple_decrypt(password)
}
print("{loop.get_count():04d}) Desencriptar con {password:<12}:  {decrypt_text}")

print(Global)
