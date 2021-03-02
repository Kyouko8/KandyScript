
def strict int sumar(int a, int b){
    return a + b
}

def str upper(str name) => name.upper()

print("Sumar: {sumar('8', 9.2)}")
print("Upper: {upper(8)}")

#for k in range(30) take 5 as loop:
#    print("$k")

int x = 8;
int z = 0;

hour = time.time()

switch (x, z){
    case (8, 0): {print("Match: 8, 0") break}
    case (3, 2): {print("Match: 3, 2") break}
    case (2, 0): {print("Match: 2, 0") break}
    default:
        print("No match")
}

int rand = random.randint(0, 8)
int y = when (1){
    case 0: 25
    case 1: 
    case 2: 28
    case 3: 
    case 5: 40
    case 6: 45
    case 8: 62
    default: 10
}

return True