import os

# ---------------------------------------------------------
# Автоматическая генерация HDL файлов RAM64 / RAM512 / RAM4K / RAM16K
# Построено на иерархии из RAM8 → RAM64 → RAM512 → RAM4K → RAM16K
# ---------------------------------------------------------

def generate_ram_chip(name, in_bits, lower_chip, address_bits, block_count, dmux, mux, lower_addr_bits):
    """
    Генерирует HDL код для RAM-чипа на основе меньшего блока.
    """
    parts = []
    parts.append(f"CHIP {name} {{")
    parts.append(f"    IN in[{in_bits}], load, address[{address_bits}];")
    parts.append(f"    OUT out[{in_bits}];\n")

    parts.append("    PARTS:")
    # Разброс load на блоки
    load_names = [f"load{i}" for i in range(block_count)]
    load_lines = ", ".join([f"{chr(97+i)} = {load_names[i]}" for i in range(block_count)])
    parts.append(f"    {dmux}(in = load, sel = address[{address_bits - (address_bits - lower_addr_bits)}..{address_bits-1}], {load_lines});\n")

    # Подблоки RAM
    for i in range(block_count):
        parts.append(f"    {lower_chip}(in = in, load = {load_names[i]}, address = address[0..{lower_addr_bits-1}], out = out{i});")

    # Сборка через MUX
    mux_inputs = ", ".join([f"{chr(97+i)} = out{i}" for i in range(block_count)])
    parts.append(f"\n    {mux}({mux_inputs}, sel = address[{address_bits - (address_bits - lower_addr_bits)}..{address_bits-1}], out = out);")
    parts.append("}\n")
    return "\n".join(parts)


def main():
    # Папка текущего файла
    base_dir = os.path.dirname(os.path.abspath(__file__))

    chips = [
        {
            "name": "RAM64",
            "lower_chip": "RAM8",
            "address_bits": 6,
            "block_count": 8,
            "dmux": "DMux8Way",
            "mux": "Mux8Way16",
            "lower_addr_bits": 3
        },
        {
            "name": "RAM512",
            "lower_chip": "RAM64",
            "address_bits": 9,
            "block_count": 8,
            "dmux": "DMux8Way",
            "mux": "Mux8Way16",
            "lower_addr_bits": 6
        },
        {
            "name": "RAM4K",
            "lower_chip": "RAM512",
            "address_bits": 12,
            "block_count": 8,
            "dmux": "DMux8Way",
            "mux": "Mux8Way16",
            "lower_addr_bits": 9
        },
        {
            "name": "RAM16K",
            "lower_chip": "RAM4K",
            "address_bits": 14,
            "block_count": 4,
            "dmux": "DMux4Way",
            "mux": "Mux4Way16",
            "lower_addr_bits": 12
        }
    ]

    for chip in chips:
        code = generate_ram_chip(
            chip["name"],
            16,
            chip["lower_chip"],
            chip["address_bits"],
            chip["block_count"],
            chip["dmux"],
            chip["mux"],
            chip["lower_addr_bits"]
        )

        file_path = os.path.join(base_dir, f"{chip['name']}.hdl")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ Сгенерировано: {file_path}")


if __name__ == "__main__":
    main()
