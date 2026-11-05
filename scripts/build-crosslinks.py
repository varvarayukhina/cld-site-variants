"""Перелинковка на странице анализа: «Входит в чек-апы» (первым, яркими карточками с ценой набора) и ниже «Читайте также» — гиды «Для кого», где есть этот анализ.
Идемпотентно: блок функции заменяется при каждом запуске. Запускать последним в порядке сборки."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FN = r'''  /* CROSSLINKS START */
  function cardReadMore(code) {
    var gs = CATS.filter(function (c) { return c.aud && typeof GUIDES !== "undefined" && GUIDES[c.id] && c.items.indexOf(code) >= 0; });
    var cx = typeof CXP === "undefined" ? [] : Object.keys(CXP).filter(function (k) { return CXP[k].indexOf(code) >= 0 && CX[k] && !CX[k].na && CXX[k]; }).slice(0, 4);
    if (!gs.length && !cx.length) return "";
    var h = "";
    if (cx.length) h += '<section class="readmore-sec"><h2>Входит в чек-апы</h2><div class="rm-list">' + cx.map(function (k) { var sv = cxSave(k); return '<button class="rm-link rm-cx" type="button" data-go="cx:' + k + '">' + icon("i-check") + "<span><b>" + esc(CXX[k].n) + "</b><small>" + nAn(CXX[k].parts.length) + '</small><span class="rm-pr"><b class="num">' + rub(CX[k].p) + "</b>" + (sv ? '<s class="num"><span class="vh">По отдельности </span>' + rub(CXX[k].sum) + '</s><span class="rm-save num">−' + sv + "%</span>" : "") + "</span></span></button>"; }).join("") + "</div></section>";
    if (gs.length) h += '<section class="readmore-sec"><h2>Читайте также</h2><div class="rm-list">' + gs.map(function (c) { var g = GUIDES[c.id]; return '<button class="rm-link" type="button" data-go="guide:' + c.id + '">' + icon("i-file") + "<span><b>" + esc(g.h1 || ("Анализы: " + c.n.toLowerCase())) + "</b><small>Гид: какие анализы и когда сдают</small></span></button>"; }).join("") + "</div></section>";
    return h;
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
.rm-cx { align-items: flex-start; padding: 18px 20px; border-radius: 16px; background: var(--lime-soft); box-shadow: inset 0 0 0 1.5px var(--lime); }
.rm-cx:hover { box-shadow: inset 0 0 0 2px var(--navy); }
.rm-cx .ico { width: 40px; height: 40px; padding: 9px; background: var(--lime); }
.rm-cx b { font-size: 18px; font-weight: 700; }
.rm-pr { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 10px; margin-top: 8px; }
.rm-cx .rm-pr b { font-size: 22px; font-weight: 800; }
.rm-pr s { color: var(--muted); font-size: 16px; }
.rm-save { font-size: 16px; font-weight: 700; padding: 2px 10px; border-radius: 999px; background: var(--lime); color: var(--navy); }
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
