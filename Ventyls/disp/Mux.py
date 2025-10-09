def Mux(s):
    a, b, sel, out = map(str, s.replace('	Mux(a=', '').replace(', b=', ' ').replace(', sel=', ' ').replace(', out=', ' ').replace(');', '').strip().split())
    print(f'	Not(in={sel}, out=n{sel});')
    print(int(out[out.index('[')+1:-2]))
    #if out[-1]==']':
        #for i in range(out[out.index('[')])

	#Not(in=sel, out=nsel);
	#Nand(a=a, b=nsel, out=aXnsel);
	#Nand(a=b, b=sel, out=bXsel);
	#Nand(a=aXnsel, b=bXsel, out=aXnselXbXsel);
#Mux('	Mux(a=a, b=b, sel=sel, out=out[16])')


print( ('['=='[') * '[',  ('['==']') * '[' )
print( ('['=='[') *  5 ,  ('['==']') *  5  )
