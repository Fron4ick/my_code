class Not:
    """NOT-gate wrapper. Конструктор принимает 'name-value' (пример: 'a-0')."""
    def __init__(self, token):
        # Поддерживаем строку 'a-0' или кортеж ('a', 0)
        if isinstance(token, str) and '-' in token:
            name, val = token.split('-', 1)
            self.name = name
            self.value = bool(int(val))
        elif isinstance(token, (tuple, list)) and len(token) == 2:
            self.name = str(token[0])
            self.value = bool(int(token[1]))
        else:
            raise ValueError("Ожидается 'name-value' или ('name', value)")

    def evaluate(self):
        """Возвращает 0 или 1 — логическое отрицание входа."""
        return int(not self.value)

    def hdl(self, out_name: str = None):
        """
        Возвращает строку с эквивалентом на NAND.
        NAND(a,a) = NOT a — поэтому достаточно одной строки.
        """
        out = out_name or f'not_{self.name}'
        return f'    Nand(a = {self.name}, b = {self.name}, out = {out})'

    def __repr__(self):
        # При печати экземпляра покажем результат evaluate() в виде 0/1
        return str(self.evaluate())


class And:
    """AND-gate реализован через NAND: out = NAND(NAND(a,b), NAND(a,b))"""
    def __init__(self, token_a, token_b):
        # Парсим оба входа (поддерживаем 'a-0' или ('a',0))
        def parse(t):
            if isinstance(t, str) and '-' in t:
                name, val = t.split('-', 1)
                return name, bool(int(val))
            elif isinstance(t, (tuple, list)) and len(t) == 2:
                return str(t[0]), bool(int(t[1]))
            else:
                raise ValueError("Ожидается 'name-value' или ('name', value)")

        self.a_name, self.a_val = parse(token_a)
        self.b_name, self.b_val = parse(token_b)

    def evaluate(self):
        """Возвращает 0 или 1 — логическое AND двух входов."""
        return int(self.a_val and self.b_val)

    def hdl(self, out_name: str = None):
        """
        Возвращает эквивалент на NAND:
        tmp = Nand(a, b)
        out = Nand(tmp, tmp)
        """
        tmp = f'tmp_{self.a_name}_{self.b_name}'
        out = out_name or f'out_{self.a_name}_{self.b_name}'
        return (f'    Nand(a = {self.a_name}, b = {self.b_name}, out = {tmp})\n'
                f'    Nand(a = {tmp}, b = {tmp}, out = {out})')

    def __repr__(self):
        return str(self.evaluate())


# --- Тесты, которые печатают то, что ты хотел ---
print("NOT-tests (ожидается: (0,1) (0,1) (1,0) (1,0) на отдельных строках):")
for a in (0, 1):
    for b in (0, 1):
        n1 = Not(f'a-{a}')
        print(a, n1)

print("\nAND-tests (ожидается: (0,0,0) (0,1,0) (1,0,0) (1,1,1) на отдельных строках):")
for a in (0, 1):
    for b in (0, 1):
        n2 = And(f'a-{a}', f'b-{b}')
        print(a, b, n2)

# Примеры генерации HDL:
print("\nПример HDL для Not(a):")
print(Not('a-0').hdl())

print("\nПример HDL для And(a,b):")
print(And('a-1', 'b-1').hdl())


print("\nTEST: функция a and b and c")

for a in (0, 1):
    for b in (0, 1):
        for c in (0, 1):
            # Сначала считаем a AND b
            ab = And(f'a-{a}', f'b-{b}')
            # Теперь (a AND b) AND c
            abc = And(('ab', ab.evaluate()), f'c-{c}')
            print(f"a={a}, b={b}, c={c} => {abc.evaluate()}")
