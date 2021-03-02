
import demo9

try:
    print(demo9.upper("hola mundo"))

except PyErrors.AttributeError:
    print("Solucionado.")

int a = 50
int b = 25

using Private{
    int b = 20

    def probando(x):{
        return x*2
    }
}

def normal_probando(y): {
    print("***: ", Private.probando(y*3))
    using Private {
        print("///: ", probando(Prev.y))
    }

}

normal_probando(7)