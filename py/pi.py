for i in range(16):
    print(f'\
        Nand (a = sel[0], b = sel[0], out = n1o{i};\n\
        Nand (a = sel[0], b = sel[2], out = n2o{i};\n\
        Nand (a = n1o{i}, b = sel[2], out = n3o{i};\n\
        Nand (a = sel[0], b = n2o{i}, out = n4o{i};\n\
        Nand (a = n2o{i}, b = n2o{i}, out = n5o{i};\n\
        Nand (a = n1o{i}, b = n3o{i}, out = n6o{i};\n\
        Nand (a = n3o{i}, b = n3o{i}, out = n7o{i};\n\
        Nand (a = n4o{i}, b = n4o{i}, out = n8o{i};\n\
        Nand (a = sel[1], b = n5o{i}, out = n9o{i};\n\
        Nand (a = n6o{i}, b = n6o{i}, out = n10o{i};\n\
        Nand (a = n7o{i}, b = sel[1], out = n11o{i};\n\
        Nand (a = n8o{i}, b = sel[1], out = n12o{i};\n\
        Nand (a = n5o{i}, b = n9o{i}, out = n13o{i};\n\
        Nand (a = sel[1], b = n10o{i}, out = n14o{i};\n\
        Nand (a = n7o{i}, b = n11o{i}, out = n15o{i};\n\
        Nand (a = n8o{i}, b = n12o{i}, out = n16o{i};\n\
        Nand (a = n10o{i}, b = n14o{i}, out = n17o{i};\n\
        Nand (a = n17o{i}, b = n17o{i}, out = a[{i}];\n\
        Nand (a = n14o{i}, b = n14o{i}, out = c[{i}];\n\
        Nand (a = n15o{i}, b = n15o{i}, out = e[{i}];\n\
        Nand (a = n11o{i}, b = n11o{i}, out = g[{i}];\n\
        Nand (a = n16o{i}, b = n16o{i}, out = b[{i}];\n\
        Nand (a = n12o{i}, b = n12o{i}, out = d[{i}];\n\
        Nand (a = n13o{i}, b = n13o{i}, out = f[{i}];\n\
        Nand (a = n9o{i}, b = n9o{i}, out = h[{i}];\n')
