'''
for i in range(1,16):print(f'\
	Nand (a = x[{i}], b = nox, out = m1X{i});\n\
	Nand (a = y[{i}], b = noy, out = m2X{i});\n\
	Not (in = m1X{i}, out = m3X{i});\n\
	Not (in = m2X{i}, out = m4X{i});\n\
	Xor (a = m3X{i}, b = nx, out = cxX{i});\n\
	Xor (a = m4X{i}, b = ny, out = cyX{i});\n')
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
