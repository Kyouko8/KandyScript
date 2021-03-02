# IF-Unless Structures
#* Aquí estoy probando mi
extensión de vscode *#

var x = 7;
strict int y = 7;
const z = 9;
strict multiple (int, float) m = 20;

x += 4;

KANDY = 1

if x >= 10 and x <= 20: {
    print(x)
}

y = KANDY*2 if z == 9 else KANDY*4

if x >= 10: print("O1")
else unless (x == 0): print("O2")
else: print("O3")

if x {
    print("=x")
} else {
    print("!x")
}

local proc Upper(str string){
    string = string.upper()
}

proc Name(name){
    Upper(name)
    print(string)
}

unless x {
    print("!x")
} else {
    print("=x")
}

if x >= 10:
    Name("Carlitos")
else:
    Name("José")