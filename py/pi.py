import re
from pathlib import Path

in_path = Path("p.hdl")
out_path = Path("p_converted.hdl")
text = in_path.read_text(encoding="utf-8")

pattern = re.compile(
    r'(?P<indent>^[ \t]*)'
    r'Mux\s*\(\s*'
    r'a\s*=\s*(?P<a>[^,]+),\s*'
    r'b\s*=\s*(?P<b>[^,]+),\s*'
    r'sel\s*=\s*(?P<sel>[^,]+),\s*'
    r'out\s*=\s*(?P<out>[^)]+)\s*'
    r'\)\s*;',
    re.MULTILINE
)

def make_nin_name(sel_text):
    sel = sel_text.strip()
    m = re.match(r'in\[(\d+)\]', sel)
    if m:
        return f"nin{m.group(1)}"
    san = re.sub(r'[^\w]', '_', sel)
    return f"nin_{san}"

def repl(m):
    indent = m.group("indent") or ""
    a = m.group("a").strip()
    b = m.group("b").strip()
    sel = m.group("sel").strip()
    out = m.group("out").strip()
    nin_sel = make_nin_name(sel)
    nan1 = f"nan1{out}"
    nan2 = f"nan2{out}"
    lines = [
        f'{indent}Nand (a = {b}, b = {sel}, out = {nan1});',
        f'{indent}Nand (a = {a}, b = {nin_sel}, out = {nan2});',
        f'{indent}Nand (a = {nan1}, b = {nan2}, out = {out});\n'
    ]
    return "\n".join(lines)

new_text, count = pattern.subn(repl, text)
out_path.write_text(new_text, encoding="utf-8")
print(f"Replaced {count} occurrences.")
