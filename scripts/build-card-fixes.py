"""Правки текстов карточек анализов поверх всех источников (v0, catalog-additions) из content/card-fixes/rules.json.
global: [было, стало, не трогать строки, где есть этот текст]; codes: {код: [[было, стало], …]}. Идемпотентно; запускать последним."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def integrate(html: str) -> str:
    rules = json.loads((ROOT / "content/card-fixes/rules.json").read_text())
    data = json.dumps({"global": rules["global"], "codes": rules["codes"]}, ensure_ascii=False)
    block = ('  /* CARD FIXES START */\n  (function () { var R = ' + data + ';\n'
             '    function fix(s, code) { if (typeof s !== "string") return s;\n'
             '      function rx(t) { return new RegExp(t.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&").replace(/ /g, "[ \\u00a0]"), "g"); } // неразрывные пробелы в текстах\n'
             '      R.global.forEach(function (g) { if (!g[2] || s.indexOf(g[2]) < 0) s = s.replace(rx(g[0]), g[1]); });\n'
             '      (R.codes[code] || []).forEach(function (g) { s = s.replace(rx(g[0]), g[1]); });\n'
             '      return s.replace(/\\s{2,}/g, " ").trim(); }\n'
             '    Object.keys(CARDS).forEach(function (code) { var c = CARDS[code]; if (!c) return;\n'
             '      c.lede = fix(c.lede, code);\n'
             '      (c.blocks || []).forEach(function (b) { ["p", "list"].forEach(function (k) { if (b[k]) b[k] = b[k].map(function (x) { return fix(x, code); }).filter(function (x) { return x; }); }); if (b.note) b.note = fix(b.note, code); });\n'
             '      (c.faq || []).forEach(function (q) { q.q = fix(q.q, code); q.a = fix(q.a, code); }); });\n'
             '    Object.keys(A).forEach(function (code) { if (A[code] && A[code].d) A[code].d = fix(A[code].d, code); });\n'
             '    if (typeof SPOT !== "undefined") SPOT.forEach(function (x) { if (x.c && x.ds) x.ds = fix(x.ds, x.c); if (x.c && x.d) x.d = fix(x.d, x.c); }); // тексты слайдера\n'
             '    if (typeof SEASON !== "undefined") SEASON.forEach(function (x) { if (x.c && x.p) x.p = fix(x.p, x.c); });\n'
             '    if (typeof renderSpot === "function" && document.getElementById("spot-track")) renderSpot(); })(); // главная отрисована раньше — перерисовать слайдер\n'
             '  /* CARD FIXES END */\n')
    if "/* CARD FIXES START */" in html:
        return re.sub(r"  /\* CARD FIXES START \*/[\s\S]*?/\* CARD FIXES END \*/\n", lambda m: block, html, count=1)
    i = html.rfind("\n  route();\n")
    assert i > 0, "route() call not found"
    return html[: i + 1] + block + html[i + 1:]


if __name__ == "__main__":
    p = ROOT / "v4/index.html"
    p.write_text(integrate(p.read_text()))
    print("Built card fixes.")
