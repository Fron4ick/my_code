for k in range(8):
    for i in range(16):
        print(
            f"\
        Nand(a=in[{i}],  b=load{k},  out=in{i}load{k});\n\
        Nand(a=dffout{k}X{i}, b=nload{k}, out=out{k}X{i}nload{k});\n\
        Nand(a=in{i}load{k},   b=out{k}X{i}nload{k},  out=in{i}load{k}out{k}X{i}nload{k});\n\
        DFF(in=in{i}load{k}out{k}X{i}nload{k}, out = dffout{k}X{i}, out=out{k}X{i});\n\
        "
        )
for i in range(16):
    print(
        f"\
        Nand (a = out{1}X{i}, b = address[0], out = out1l{i});\n\
        Nand (a = out{0}X{i}, b = ns{i}, out = out2l{i});\n\
        Nand (a = out{3}X{i}, b = address[0], out = out3l{i});\n\
        Nand (a = out{2}X{i}, b = ns{i}, out = out4l{i});\n\
        Nand (a = out{5}X{i}, b = address[0], out = out5l{i});\n\
        Nand (a = out{4}X{i}, b = ns{i}, out = out6l{i});\n\
        Nand (a = out{7}X{i}, b = address[0], out = out7l{i});\n\
        Nand (a = out{6}X{i}, b = ns{i}, out = out8l{i});\n\
        Nand (a = out1l{i}, b = out2l{i}, out = out9l{i});\n\
        Nand (a = out3l{i}, b = out4l{i}, out = out10l{i});\n\
        Nand (a = out5l{i}, b = out6l{i}, out = out11l{i});\n\
        Nand (a = out7l{i}, b = out8l{i}, out = out12l{i});\n\
        Nand (a = out9l{i}, b = ns1, out = out13l{i});\n\
        Nand (a = out10l{i}, b = address[1], out = out14l{i});\n\
        Nand (a = out11l{i}, b = ns1, out = out15l{i});\n\
        Nand (a = out12l{i}, b = address[1], out = out16l{i});\n\
        Nand (a = out13l{i}, b = out14l{i}, out = out17l{i});\n\
        Nand (a = out15l{i}, b = out16l{i}, out = out18l{i});\n\
        Nand (a = out17l{i}, b = ns2, out = out19l{i});\n\
        Nand (a = out18l{i}, b = address[2], out = out20l{i});\n\
        Nand (a = out19l{i}, b = out20l{i}, out = out[{i}]);\n\
        "
    )
