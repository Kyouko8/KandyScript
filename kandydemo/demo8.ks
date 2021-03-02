
# -----------------------------------------------------------------------------
dict loops = ${}

# ------------------------ repeat [value] (as [alias]) ------------------------
print("Repeat")
repeat(8) as loops['rep']:
    print(loops['rep'])

# ------------ for ([init]; [condition]; [increment]) (as [alias]) ------------
print("ForC")
for (int x = 0; x < 20; x += 1) as loops['forC'] {
    print(x, loops['forC'])
}

# ------------------ for [var] in [expression] (as [alias]) -------------------
print("ForIn")
str k;
int v;
dict demo = ${'a': 0, 'b': 2, 'c': 5, 'd': 7, 'e': 9}

for k, v in demo.items() as loops['forIn']:
    print("$k: $v", loops['forIn'])


# ------------- for [var] from [value1] to [value2] (as [alias]) --------------
print("ForFromTo")
for z from 10 to 15 as loops['forFrom']:
    print(z, loops['forFrom'])
    