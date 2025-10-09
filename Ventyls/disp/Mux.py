def Mux(s):
    a, b, sel, out = map(str, s.replace('Mux(a=', '').replace(', b=', ' ').replace(', sel=', ' ').replace(', out=', ' ').replace(')', '').strip().split())
    outs = [f'Not(in={sel}, out=n{sel});']
    kolvo = int(out[out.index('[')+1:-1] if )
    print(kolvo)
    al = a[-1]==']'
    bl = b[-1]==']'
    ol = out[-1]==']'
    a = a[:a.index('[')]
    b = b[:b.index('[')]
    out = out[:out.index('[')]
    for i in range(kolvo):
        outs.append(f'Nand(a={a}{al*'[' + (not al)*'X'}{i}{al*']'}, b=n{sel}, out={a}X{i}Xn{sel})')
        outs.append(f'Nand(a={b}{bl*'[' + (not bl)*'X'}{i}{bl*']'}, b={sel}, out={b}X{i}X{sel})')
        outs.append(f'Nand(a={a}X{i}Xn{sel}, b={b}X{i}X{sel}, out={out}{ol*'[' + (not ol)*'X'}{i}{ol*']'})')
    return outs

p = list(Mux('Mux(a=a, b=b, sel=sel, out=out)'))

for i in p:print('	', i, ';', sep='')
