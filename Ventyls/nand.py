# Исправь код. Убери все синтаксические, логические и другие ошибки. Возможно предложи что-то, чтобы это выглядело и работало правильнее. + соблюдай правилам ООП

class Not:
    def __init__(self, var):
        self.var = var.split('-')
        self.var[1] = bool(var[1])

    def get_function(self,a,b): #логический вентиль написанный на языке hdl из нандов
        return(f'    Nand(a = {var[0]}, b = {var[0]}, out = {not var[1]})')
    
    def __main__(self): # то что должен выводить клас по умолчанию, без обращения к конкретному методу
        return not var[1]

class And:
    def __init__(self, var):
        self.var = var.split('-')
        self.var[1] = bool(var[1])

    def get_function(self,a,b): #логический вентиль написанный на языке hdl из нандов
        return(f'    Nand(a = {var[0]}, b = {var[2]}, out = cV{not (var[0] and var[2])})\n    Nand(a = cV, b = cV, out = {var[0] and var[2]})')
    
    def __main__(self): # то что должен выводить клас по умолчанию, без обращения к конкретному методу
        return var[1] and var[3]


for a in 0,1:
    for b in 0,1:
        n1 = Not(f'a-{a}')
        print(a, n1) #Должен вывести 0 1, 0 1, 1 0, 1 0; (только с новых строчек)

for a in 0,1:
    for b in 0,1:
        n2 = And(f'a-{a}')
        print(a, b, n2) #Должен вывести 0 0 0, 0 1 0, 1 0 0, 1 1 1; (только с новых строчек)
