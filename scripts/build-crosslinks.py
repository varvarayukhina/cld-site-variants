"""Перелинковка на странице анализа: «Читайте также» — гиды «Для кого», где есть этот анализ, и чек-апы, в которые он входит.
Идемпотентно: блок функции заменяется при каждом запуске. Запускать последним в порядке сборки."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FN = r'''  /* CROSSLINKS START */
  function cardReadMore(code) {
    var gs = CATS.filter(function (c) { return c.aud && typeof GUIDES !== "undefined" && GUIDES[c.id] && c.items.indexOf(code) >= 0; });
    var cx = typeof CXP === "undefined" ? [] : Object.keys(CXP).filter(function (k) { return CXP[k].indexOf(code) >= 0 && CX[k] && !CX[k].na && CXX[k]; }).slice(0, 4);
    if (!gs.length && !cx.length) return "";
    var h = '<section class="readmore-sec"><h2>Читайте также</h2>';
    if (gs.length) h += '<div class="rm-list">' + gs.map(function (c) { var g = GUIDES[c.id]; return '<button class="rm-link" type="button" data-go="guide:' + c.id + '">' + icon("i-file") + "<span><b>" + esc(g.h1 || ("Анализы: " + c.n.toLowerCase())) + "</b><small>Гид: какие анализы и когда сдают</small></span></button>"; }).join("") + "</div>";
    if (cx.length) h += '<h3>Входит в чек-апы</h3><div class="rm-list">' + cx.map(function (k) { return '<button class="rm-link" type="button" data-go="cx:' + k + '">' + icon("i-check") + "<span><b>" + esc(CXX[k].n) + "</b><small>" + nAn(CXX[k].parts.length) + " · " + rub(CX[k].p) + "</small></span></button>"; }).join("") + "</div>";
    return h + "</section>";
  }
  /* CROSSLINKS END */
'''
CSS = '''/* CROSSLINKS CSS */
.readmore-sec { margin-top: 44px; padding-top: 30px; border-top: 2px solid var(--navy-soft); }
.readmore-sec h2 { margin-bottom: 14px; font-size: clamp(26px, 2.6vw, 32px) !important; }
.readmore-sec h3 { margin: 22px 0 10px; font: 700 18px var(--text); color: var(--muted); }
.rm-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.rm-link { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border: 0; border-radius: 14px; background: #FFF; box-shadow: inset 0 0 0 1px var(--line); text-align: left; color: var(--ink); cursor: pointer; }
.rm-link:hover { box-shadow: inset 0 0 0 1.5px var(--navy); }
.rm-link .ico { width: 36px; height: 36px; flex: none; padding: 8px; border-radius: 50%; background: var(--lime-soft); color: var(--navy); }
.rm-link b { display: block; font: 600 16px/1.35 var(--text); }
.rm-link small { display: block; font-size: 16px; color: var(--muted); }
@media (max-width: 700px) { .rm-list { grid-template-columns: minmax(0, 1fr); } }
/* CROSSLINKS CSS END */
'''


def integrate(html: str) -> str:
    if "/* CROSSLINKS START */" in html:
        html = re.sub(r"  /\* CROSSLINKS START \*/[\s\S]*?/\* CROSSLINKS END \*/\n", lambda m: FN, html, count=1)
    else:
        assert html.count("  function renderGuide() {") >= 1
        html = html.replace("  function renderGuide() {", FN + "  function renderGuide() {", 1)
    if "html += cardReadMore(code);" not in html:
        assert html.count("if (togHtml) html += togHtml;") == 1
        html = html.replace("if (togHtml) html += togHtml;", "if (togHtml) html += togHtml;\n    html += cardReadMore(code); // гиды и чек-апы с этим анализом", 1)
    if "/* CROSSLINKS CSS */" in html:
        html = re.sub(r"/\* CROSSLINKS CSS \*/[\s\S]*?/\* CROSSLINKS CSS END \*/\n", lambda m: CSS, html, count=1)
    else:
        html = html.replace("</style>", CSS + "</style>", 1)
    return html


if __name__ == "__main__":
    p = ROOT / "v4/index.html"
    p.write_text(integrate(p.read_text()))
    print("Built card crosslinks.")
