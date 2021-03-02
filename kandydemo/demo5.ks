
int x = 0;
int y = 1;

until (x > 5) as loop1: {
    x += 1
    print("Tabla del: $x")
    y = 1
    while (y <= 10) as loop2: {
        print("\t $x * $y = {y*x}")
        y += 1

        if y == 6 and x == 2:
            break:loop1
    }
}
print("Iteraciones de LOOP1: ", loop1.get_count())
print("Iteraciones de LOOP2: ", loop2.get_count())
print("Iteraciones Finalizadas de LOOP1: ", loop1.get_count_finished())
print("Iteraciones Finalizadas de LOOP2: ", loop2.get_count_finished())
