from itertools import product
from collections import defaultdict

class Not:
    def __init__(self, token):
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
        return int(not self.value)

    def hdl(self, out_name: str = None):
        out = out_name or f'outX{self.name}'
        return f'    Nand(a = {self.name}, b = {self.name}, out = {out});'

    def __repr__(self):
        return str(self.evaluate())


class And:
    def __init__(self, token_a, token_b):
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
        return int(self.a_val and self.b_val)

    def hdl(self, out_name: str = None):
        tmp = f'tmpX{self.a_name}X{self.b_name}'
        out = out_name or f'outX{self.a_name}X{self.b_name}'
        return (f'    Nand(a = {self.a_name}, b = {self.b_name}, out = {tmp});\n'
                f'    Nand(a = {tmp}, b = {tmp}, out = {out});')

    def __repr__(self):
        return str(self.evaluate())


class Or:
    def __init__(self, token_a, token_b):
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
        return int(self.a_val or self.b_val)

    def hdl(self, out_name: str = None):
        tmp1 = f'tmpX{self.a_name}X{self.a_name}'
        tmp2 = f'tmpX{self.b_name}X{self.b_name}'
        out = out_name or f'outX{self.a_name}X{self.b_name}'
        return (f'    Nand(a = {self.a_name}, b = {self.a_name}, out = {tmp1});\n'
                f'    Nand(a = {self.b_name}, b = {self.b_name}, out = {tmp2});\n'
                f'    Nand(a = {tmp1}, b = {tmp2}, out = {out});')

    def __repr__(self):
        return str(self.evaluate())


class Xor:
    def __init__(self, token_a, token_b):
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
        return int(self.a_val != self.b_val)

    def hdl(self, out_name: str = None):
        tmp1 = f'tmpX{self.a_name}X{self.b_name}'
        tmp2 = f'tmpX{self.a_name}X{tmp1}'
        tmp3 = f'tmpX{self.b_name}X{tmp1}'
        out = out_name or f'outX{tmp2}X{tmp3}'
        return (f'    Nand(a = {self.a_name}, b = {self.b_name}, out = {tmp1});\n'
                f'    Nand(a = {self.a_name}, b = {tmp1}, out = {tmp2});\n'
                f'    Nand(a = {self.b_name}, b = {tmp1}, out = {tmp3});\n'
                f'    Nand(a = {tmp2}, b = {tmp3}, out = {out});')

    def __repr__(self):
        return str(self.evaluate())


class Mux:
    def __init__(self, token_a, token_b, token_sel):
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
        self.sel_name, self.sel_val = parse(token_sel)

    def evaluate(self):
        return int(self.b_val if self.sel_val else self.a_val)

    def hdl(self, out_name: str = None):
        q = f'q{self.a_name}{self.b_name}{self.sel_name}'
        w = f'w{self.a_name}{self.b_name}{self.sel_name}'
        e = f'e{self.a_name}{self.b_name}{self.sel_name}'
        out = out_name or f'outMux{self.a_name}{self.b_name}{self.sel_name}'
        return (f'    Nand(a = {self.a_name}, b = {self.sel_name}, out = {q});\n'
                f'    Nand(a = {q}, b = {self.a_name}, out = {w});\n'
                f'    Nand(a = {self.b_name}, b = {self.sel_name}, out = {e});\n'
                f'    Nand(a = {w}, b = {e}, out = {out});')

    def __repr__(self):
        return str(self.evaluate())


class DMux:
    def __init__(self, token_in, token_sel):
        def parse(t):
            if isinstance(t, str) and '-' in t:
                name, val = t.split('-', 1)
                return name, bool(int(val))
            elif isinstance(t, (tuple, list)) and len(t) == 2:
                return str(t[0]), bool(int(t[1]))
            else:
                raise ValueError("Ожидается 'name-value' или ('name', value)")

        self.in_name, self.in_val = parse(token_in)
        self.sel_name, self.sel_val = parse(token_sel)

    def evaluate(self):
        if self.sel_val:
            return (0, int(self.in_val))
        else:
            return (int(self.in_val), 0)

    def hdl(self, out_a_name: str = None, out_b_name: str = None):
        out1 = f'out1_{self.in_name}{self.sel_name}'
        out2 = f'out2_{self.in_name}{self.sel_name}'
        out_a = out_a_name or f'a{self.in_name}{self.sel_name}'
        out_b = out_b_name or f'b{self.in_name}{self.sel_name}'
        return (f'    Nand(a = {self.in_name}, b = {self.sel_name}, out = {out1});\n'
                f'    Nand(a = {self.in_name}, b = {out1}, out = {out2});\n'
                f'    Nand(a = {out2}, b = {out2}, out = {out_a});\n'
                f'    Nand(a = {out1}, b = {out1}, out = {out_b});')

    def __repr__(self):
        a, b = self.evaluate()
        return f'(a={a}, b={b})'


# Многобитные чипы генерируются циклично
def generate_multibit_class(gate_class, bit_width, class_name):
    """Генерирует класс для многобитных вентилей"""
    
    class MultibitGate:
        def __init__(self, *args):
            # Парсим входы - могут быть списками или отдельными значениями
            self.gates = []
            self.bit_width = bit_width
            self.class_name = class_name
            
            # Для каждого бита создаем отдельный вентиль
            for i in range(bit_width):
                bit_args = []
                for arg in args:
                    if isinstance(arg, list):
                        bit_args.append((f"{arg[0]}[{i}]", arg[1][i] if i < len(arg[1]) else 0))
                    else:
                        bit_args.append(arg)
                self.gates.append(gate_class(*bit_args))
        
        def evaluate(self):
            return [gate.evaluate() for gate in self.gates]
        
        def hdl(self, out_name: str = None):
            lines = []
            for i, gate in enumerate(self.gates):
                out = f"{out_name}[{i}]" if out_name else f"out[{i}]"
                lines.append(gate.hdl(out))
            return '\n'.join(lines)
        
        def __repr__(self):
            return str(self.evaluate())
    
    MultibitGate.__name__ = class_name
    return MultibitGate


# Создаем 16-битные версии
Not16 = generate_multibit_class(Not, 16, "Not16")
And16 = generate_multibit_class(And, 16, "And16")
Or16 = generate_multibit_class(Or, 16, "Or16")

class HDLOptimizer:
    """Оптимизатор HDL кода - удаляет дублирующиеся NAND вентили"""
    
    def __init__(self, hdl_code):
        self.hdl_code = hdl_code
        self.nand_gates = []  # Список всех NAND вентилей
        self.truth_tables = {}  # Таблицы истинности для каждого NAND
        self.input_vars = set()  # Все входные переменные
        
    def parse_nands(self):
        """Извлекает все NAND вентили из HDL кода"""
        lines = self.hdl_code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Nand'):
                # Парсим: Nand(a = var1, b = var2, out = var3);
                parts = line.replace('Nand(', '').replace(');', '').replace(' ', '').split(',')
                nand_info = {}
                for part in parts:
                    key, val = part.split('=')
                    nand_info[key] = val
                
                self.nand_gates.append(nand_info)
                # Собираем входные переменные
                a_var = nand_info['a']
                b_var = nand_info['b']
                # Если переменная не содержит '[' и не начинается с tmp/out - это входная
                if '[' not in a_var and not a_var.startswith(('tmp', 'out', 'q', 'w', 'e')):
                    self.input_vars.add(a_var)
                if '[' not in b_var and not b_var.startswith(('tmp', 'out', 'q', 'w', 'e')):
                    self.input_vars.add(b_var)
    
    def build_truth_table(self, nand_idx):
        """Строит таблицу истинности для конкретного NAND вентиля"""
        # Получаем все комбинации входных значений
        input_list = sorted(list(self.input_vars))
        truth_table = []
        
        for combo in product([0, 1], repeat=len(input_list)):
            values = dict(zip(input_list, combo))
            # Симулируем схему
            result = self.simulate_circuit(values, nand_idx)
            truth_table.append((combo, result))
        
        return tuple(truth_table)
    
    def simulate_circuit(self, input_values, target_nand_idx):
        """Симулирует схему до целевого NAND вентиля"""
        computed = dict(input_values)
        
        for idx in range(target_nand_idx + 1):
            nand = self.nand_gates[idx]
            a_val = computed.get(nand['a'], 0)
            b_val = computed.get(nand['b'], 0)
            # NAND: NOT(a AND b)
            result = int(not (a_val and b_val))
            computed[nand['out']] = result
        
        return computed[self.nand_gates[target_nand_idx]['out']]
    
    def find_duplicates(self):
        """Находит NAND вентили с одинаковыми таблицами истинности"""
        self.parse_nands()
        
        if not self.input_vars:
            return {}, {}
        
        # Строим таблицы истинности
        for idx in range(len(self.nand_gates)):
            tt = self.build_truth_table(idx)
            self.truth_tables[idx] = tt
        
        # Группируем по таблицам истинности
        tt_groups = defaultdict(list)
        for idx, tt in self.truth_tables.items():
            tt_groups[tt].append(idx)
        
        # Находим дубликаты
        duplicates = {}
        replacements = {}
        
        for tt, indices in tt_groups.items():
            if len(indices) > 1:
                # Первый (младший) остается, остальные удаляются
                keeper = indices[0]
                for dup_idx in indices[1:]:
                    duplicates[dup_idx] = keeper
                    # Замена: выход дубликата -> выход keeper
                    replacements[self.nand_gates[dup_idx]['out']] = self.nand_gates[keeper]['out']
        
        return duplicates, replacements
    
    def optimize(self):
        """Оптимизирует HDL код"""
        duplicates, replacements = self.find_duplicates()
        
        if not duplicates:
            return self.hdl_code, "Оптимизация не требуется - дубликаты не найдены"
        
        # Удаляем дублирующиеся NAND и заменяем ссылки
        lines = self.hdl_code.split('\n')
        new_lines = []
        removed_count = 0
        
        for idx, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith('Nand'):
                # Определяем индекс этого NAND
                current_nand_idx = sum(1 for l in lines[:idx] if l.strip().startswith('Nand'))
                
                if current_nand_idx in duplicates:
                    removed_count += 1
                    continue  # Пропускаем дубликат
            
            # Заменяем ссылки на удаленные выходы
            modified_line = line
            for old_var, new_var in replacements.items():
                modified_line = modified_line.replace(f'= {old_var}', f'= {new_var}')
                modified_line = modified_line.replace(f'={old_var}', f'={new_var}')
            
            new_lines.append(modified_line)
        
        optimized_code = '\n'.join(new_lines)
        stats = f"Удалено {removed_count} дублирующихся NAND вентилей"
        
        return optimized_code, stats







# Пример использования
if __name__ == "__main__":
    print("=== Пример работы оптимизатора ===\n")
    
    # Создаем простую схему Mux
    mux = Mux('a-1', 'b-0', 'sel-1')
    hdl_code = mux.hdl('out')
    
    print("Исходный HDL код:")
    print(hdl_code)
    print(f"\nРезультат: {mux.evaluate()}\n")
    
    # Оптимизируем
    optimizer = HDLOptimizer(hdl_code)
    optimized, stats = optimizer.optimize()
    
    print("=" * 50)
    print("Оптимизированный HDL код:")
    print(optimized)
    print(f"\n{stats}\n")
    
    # Тестируем многобитные вентили
    print("=" * 50)
    print("=== Тест многобитных вентилей ===\n")
    
    not16 = Not16(['a', [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]])
    print("Not16 результат:", not16.evaluate())







print(input())
