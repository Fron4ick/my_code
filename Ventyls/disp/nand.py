'''
for i in range(1,16):print(f'\
	Nand (a = x[{i}], b = nox, out = m1X{i});\n\
	Nand (a = y[{i}], b = noy, out = m2X{i});\n\
	Not (in = m1X{i}, out = m3X{i});\n\
	Not (in = m2X{i}, out = m4X{i});\n\
	Xor (a = m3X{i}, b = nx, out = cxX{i});\n\
	Xor (a = m4X{i}, b = ny, out = cyX{i});\n')
'''
'''
for i in range(1,16):print(f'\
    Nand (a = cxX{i}, b = cyX{i}, out = b1X{i});\n\
    Not (in = b1X{i}, out = b2X{i});\n\
    Nand (a = cxX{i}, b = b1X{i}, out = b3X{i});\n\
    Nand (a = b1X{i}, b = cyX{i}, out = b4X{i});\n\
    Nand (a = b3X{i}, b = b4X{i}, out = b5X{i});\n\
    Nand (a = b2X{i}, b = nf, out = b6X{i});\n\
    Nand (a = b5X{i}, b = bR{i-1}, out = b7X{i});\n\
    Nand (a = b1X{i}, b = b7X{i}, out = b8X{i});\n\
    Nand (a = b5X{i}, b = b7X{i}, out = b9X{i});\n\
    Nand (a = b7X{i}, b = bR{i-1}, out = b10X{i});\n\
    Nand (a = f, b = b8X{i}, out = b11X{i});\n\
    Nand (a = b9X{i}, b = b10X{i}, out = b12X{i});\n\
    Not (in = b11X{i}, out = bR{i});\n\
    Nand (a = b12X{i}, b = f, out = b13X{i});\n\
    Nand (a = b13X{i}, b = b6X{i}, out = b14X{i});\n\
    Xor (a = b14X{i}, b = no, out = out[{i}], out = zrX{i});\n')
'''
'''
for k in range(7):
    print(f'\
    Mux (a = mux3wave{k}X1, b = mux3wave{k}X2, sel = in[3], out = mux3wave{k}X1);')
'''

'''for i in range(4):
    for j in range(4):
        if i > j:  # чтобы избежать дубликатов (n3n2 и n2n3)
            print(f"Nand(a=in[{i}], b=in[{j}], out=i{i}i{j});")


# Только комбинации in[i] и n[j] (как в примере i3n2)
print("// Комбинации in[i] и n[j]")
for i in range(4):
    for j in range(4):
        if i != j:
            print(f"Nand(a=in[{i}], b=n{j}, out=i{i}n{j});")

print()

# Только комбинации n[i] и n[j] (как в примере n3n2)
print("// Комбинации n[i] и n[j]")
for i in range(4):
    for j in range(4):
        if i > j:  # чтобы избежать дубликатов (n3n2 и n2n3)
            print(f"Nand(a=n{i}, b=n{j}, out=n{i}n{j});")'''

def v(s):return 'i' if s==1 else 'n'
i = 0
for a in 0,1:
    for b in 0,1:
        for c in 0,1:
            for d in 0,1:
                q1 = 'i[3]' if a else 'n3'
                q2 = 'i[2]' if b else 'n2'
                q3 = 'i[1]' if c else 'n1'
                q4 = 'i[0]' if d else 'n0'
                p = int(str(a)+str(b)+str(c)+str(d),2)
                print(f'	Nand(a={'i[3]' if a else 'n3'}, b={'i[2]' if b else 'n2'}, out=x{p}ch1)')
                print(f'	Nand(a={'i[1]' if c else 'n1'}, b={'i[0]' if d else 'n0'}, out=x{p}ch2)')
                print(f'	Or(a=x{p}ch1, b=x{p}ch2, out=ch{p})\n')
print(input())
