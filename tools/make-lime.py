"""v4 = v0 с лаймовой шапкой. Запускать после каждой правки v0: python3 tools/make-lime.py"""
from pathlib import Path

R = Path(__file__).resolve().parent.parent
s = (R / "v0/index.html").read_text()
s = s.replace('<html lang="ru">', '<html lang="ru" data-theme="lime">', 1)
s = s.replace("<title>CLD — прототип сайта</title>", "<title>CLD — вариант 4, лайм</title>", 1)
assert 'data-theme="lime"' in s
(R / "v4").mkdir(exist_ok=True)
(R / "v4/index.html").write_text(s)
print("v4 written")
