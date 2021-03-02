int x;

do {
    x = loop1.get_count()
    if x == 5:
        loop1.ignore_next_iterations(5)

} until (x > 1000000) as loop1

print("Tiempo promedio de ejecución: ", loop1.get_time_average())

int y;

do {

    y = loop2.get_count()
    print("Y: $y")
    if y == 3:
        loop2.ignore_next_iterations(2)

} while (y <= 8) as loop2
