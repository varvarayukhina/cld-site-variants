"""Preview page v4-new/: v4 + new navigation for people who rarely use sites and do not know test names.
Search (build-search.py), «Помощь в выборе анализа» page #vybor-analiza with four entries,
home tiles 3 × 3, grouped mobile menu, «Ваш город» as a strip under the header.
Main v4/index.html is not changed: run after the v4 build, output goes to v4-new/index.html."""
from pathlib import Path
from runpy import run_path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def once(html: str, old: str, new: str) -> str:
    assert html.count(old) == 1, f'not found once: {old[:70]}'
    return html.replace(old, new, 1)


PZ_VIEW = '''  <!-- VYBOR VIEW START -->
  <section id="v-vybor-analiza" data-view="vybor-analiza" hidden>
    <div class="cxhero">
      <div class="wrap pz-hero">
        <div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><button type="button" data-go="catalog:blood">Анализы и цены</button><span>/</span><span id="pz-crumb"></span></div>
        <h1 id="pz-h"></h1>
        <p class="lede" id="pz-lede"></p>
      </div>
    </div>
    <div class="wrap pz" id="pz-list"></div>
  </section>
  <!-- VYBOR VIEW END -->
'''

PZ_JS = r'''
  /* VYBOR START */
  var PZ = __DATA__;
  function pzLink(l, i) {
    var cls = "btn " + (i ? "btn-ghost" : "btn-lime");
    if (l[0] === "tel") return '<a class="' + cls + '" href="tel:88002017830">' + icon("i-phone") + esc(l[1]) + "</a>";
    if (l[0] === "search") return '<button class="' + cls + '" type="button" data-focus-search>' + icon("i-search") + esc(l[1]) + "</button>";
    return '<button class="' + cls + '" type="button" data-go="' + esc(l[0]) + '">' + esc(l[1]) + "</button>";
  }
  function renderVybor() {
    PAGE_META["vybor-analiza"] = [PZ.seo_title, PZ.description];
    $("#pz-crumb").textContent = PZ.crumb; $("#pz-h").textContent = PZ.title; $("#pz-lede").textContent = typo(PZ.lede);
    $("#pz-list").innerHTML = PZ.items.map(function (it) {
      var ill = it.img.indexOf("icon:") === 0 ? '<span class="pz-ic">' + icon(it.img.slice(5)) + "</span>" : '<img src="../assets/img/aud/' + it.img + '" alt="" width="88" height="88">';
      return '<article class="pz-it" id="pz-' + it.id + '"><div class="pz-ill">' + ill + '</div><div class="pz-tx"><h2>' + esc(typo(it.h)) + "</h2><p>" + esc(typo(it.p)) + '</p><div class="pz-links">' + it.links.map(pzLink).join("") + "</div></div></article>";
    }).join("");
  }
  PAGES.push("vybor-analiza"); NAVOF["vybor-analiza"] = "catalog"; RENDER["vybor-analiza"] = renderVybor;
  /* VYBOR END */
'''

MMENU = '''<div class="mmenu" id="mmenu" hidden>
  <div class="wrap">
    <button type="button" class="mm-help" data-go="vybor-analiza"><svg class="ico"><use href="#i-chat"/></svg><span>Не знаю, какой анализ нужен</span><svg class="ico"><use href="#i-right"/></svg></button>
    <p class="mm-h">Найти анализ</p>
    <div class="mm-g">
      <button type="button" data-go="catalog:blood">Все анализы</button>
      <button type="button" data-go="organs">По органам</button>
      <button type="button" data-go="povody">По поводу</button>
      <button type="button" data-go="checkups">Чек-апы</button>
      <button type="button" data-go="guide:women">Женщинам</button>
      <button type="button" data-go="guide:men">Мужчинам</button>
      <button type="button" data-go="guide:kids">Детям</button>
      <button type="button" data-go="guide:pregnant">Беременным</button>
      <button type="button" data-go="guide:senior">Родителям</button>
      <button type="button" data-go="express">Экспресс</button>
    </div>
    <p class="mm-h">Перед сдачей</p>
    <div class="mm-g">
      <button type="button" data-go="podgotovka">Как подготовиться</button>
      <button type="button" data-go="points">Где сдать</button>
      <button type="button" data-go="home-visit">Выезд на дом</button>
    </div>
    <p class="mm-h">После</p>
    <div class="mm-g">
      <button type="button" data-go="results">Результаты анализов</button>
      <button type="button" data-go="kak-chitat-blank">Как читать бланк</button>
      <button type="button" data-go="comparisons">Справочник</button>
    </div>
    <p class="mm-h">Ещё</p>
    <div class="mm-g">
      <button type="button" data-go="promos">Акции</button>
      <button type="button" data-go="gifts">Сертификаты</button>
      <button type="button" data-go="about">О компании</button>
      <button type="button" data-go="doctors">Врачам</button>
    </div>
    <div class="mm-call">
      <a class="btn btn-lime" href="tel:88002017830"><svg class="ico"><use href="#i-phone"/></svg>Позвонить 8&nbsp;800&nbsp;201&nbsp;78&nbsp;30</a>
      <a class="btn btn-ghost" href="#" data-stub="Номер WhatsApp появится после согласования"><svg class="ico"><use href="#i-wa"/></svg>Написать в WhatsApp</a>
    </div>
  </div>
</div>
'''

CITY = '''<div class="cityq cityq-strip" id="cityq" role="region" aria-labelledby="cityq-t" hidden><div class="wrap"><p id="cityq-t">Ваш город — <b id="cityq-n">Черкесск</b>?</p><div><button class="btn btn-lime" type="button" data-city="yes">Да, верно</button><button class="btn btn-ghost" type="button" data-city="change">Изменить</button></div></div></div>
'''

CSS = '''/* PREVIEW NAV CSS */
/* «Помощь в выборе анализа» */
.pz-hero { padding-bottom: 34px; }
.pz-hero h1 { margin-top: 14px; }
.pz-hero .lede { margin-top: 14px; }
.pz { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; padding-block: 32px 72px; }
.pz-it { display: grid; grid-template-columns: 88px minmax(0, 1fr); gap: 20px; align-items: start; padding: 24px; border: 1.5px solid var(--line); border-radius: 18px; background: #FFF; }
.pz-ill img { width: 88px; height: 88px; object-fit: contain; }
.pz-ic { display: grid; place-items: center; width: 80px; height: 80px; border-radius: 50%; background: var(--lime-soft); color: var(--navy); }
.pz-ic .ico { width: 38px; height: 38px; }
.pz-tx h2 { font-size: 26px; }
.pz-tx p { margin-top: 10px; font-size: 18px; line-height: 1.55; color: var(--ink); }
.pz-links { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.pz-links .btn { min-height: 48px; font-size: 16px; }
.pz-links .btn .ico { width: 20px; height: 20px; }
@media (max-width: 860px) { .pz { grid-template-columns: minmax(0, 1fr); padding-top: 20px; } }
@media (max-width: 520px) { .pz-it { grid-template-columns: minmax(0, 1fr); gap: 12px; padding: 20px 18px; } .pz-ill img { width: 72px; height: 72px; } .pz-ic { width: 64px; height: 64px; } .pz-tx h2 { font-size: 23px; } .pz-tx p { font-size: 17px; } .pz-links .btn { flex: 1 1 auto; justify-content: center; } }
/* line under the hero search */
.hero-help { display: inline-flex; align-items: center; gap: 10px; margin-top: 14px; padding: 0; border: 0; background: none; color: #FFF; font: 600 17px/1.35 var(--text); text-align: left; cursor: pointer; }
.hero-help b { color: var(--lime); text-decoration: underline; text-underline-offset: 4px; }
.hero-help .ico { flex: none; width: 22px; height: 22px; color: var(--lime); }
.hero-help:hover b { color: #FFF; }
/* desktop mega menu: first line */
.mg-help { display: flex; align-items: center; gap: 12px; width: 100%; margin-bottom: 18px; padding: 14px 18px; border: 0; border-radius: 14px; background: var(--lime-soft); color: var(--navy); font: 700 17px var(--text); text-align: left; cursor: pointer; }
.mg-help .ico { width: 22px; height: 22px; }
.mg-help:hover { box-shadow: inset 0 0 0 1.5px var(--lime-dark); }
/* tiles: 9 in a row, 3 × 3 on smaller screens */
.aud { grid-template-columns: repeat(9, minmax(0, 1fr)); }
@media (max-width: 1300px) {
  .aud { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .audt { flex-direction: row; justify-content: flex-start; gap: 14px; padding: 12px 16px; text-align: left; }
  .audt-l { min-height: 0; }
}
@media (max-width: 960px) {
  .aud { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 0; padding: 20px 0 0; overflow: visible; }
  .audt { flex-direction: column; justify-content: flex-end; gap: 8px; padding: 12px 4px 10px; text-align: center; }
  .audt-l { min-height: 2.6em; font-size: 16px; line-height: 1.25; }
}
/* mobile menu in groups */
.mmenu { bottom: 0; overflow-y: auto; overscroll-behavior: contain; }
.mmenu .wrap { padding-block: 12px 110px; }
.mmenu .mm-help { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; padding: 14px 16px; border: 0; border-radius: 14px; background: var(--lime); color: var(--navy); font: 700 18px var(--text); }
.mmenu .mm-help span { flex: 1; }
.mmenu .mm-help .ico { width: 22px; height: 22px; }
.mmenu .mm-h { margin: 18px 0 6px; font: 700 16px var(--text); color: var(--muted); }
.mmenu .mm-g { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.mmenu .mm-g button:last-child:nth-child(odd) { grid-column: 1 / -1; }
.mmenu .mm-g button { padding: 13px 14px; border: 0; border-radius: 12px; background: var(--navy-soft); font: 600 17px/1.25 var(--text); color: var(--ink); }
.mmenu .mm-call { display: grid; gap: 10px; margin-top: 22px; }
.mmenu .mm-call .btn { justify-content: center; min-height: 54px; padding: 14px; border-radius: 14px; font: 700 18px var(--text); border-bottom: 0; }
.mmenu .mm-call .btn-lime { background: var(--lime); color: var(--navy); }
.mmenu .mm-call .btn-ghost { background: #FFF; box-shadow: inset 0 0 0 1.5px var(--line); }
.mmenu .mm-call .ico { width: 22px; height: 22px; }
/* «Ваш город — …?» as a strip under the header */
.cityq.cityq-strip { position: static; width: auto; padding: 10px 0; border-radius: 0; box-shadow: none; background: var(--lime-soft); color: var(--ink); display: block; font-size: 17px; }
.cityq.cityq-strip[hidden] { display: none; }
.cityq.cityq-strip::before { display: none; }
.cityq-strip .wrap { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; }
.cityq-strip .wrap > div { display: flex; gap: 8px; }
.cityq-strip .btn { padding: 10px 16px; border-radius: 10px; font-weight: 700; }
.cityq-strip .btn-ghost { background: #FFF; }
/* PREVIEW NAV CSS END */
'''


def integrate(html: str) -> str:
    html = run_path(str(ROOT / 'scripts/build-search.py'))['integrate'](html)
    data = json.loads((ROOT / 'content/vybor-analiza/vybor-analiza.json').read_text())
    # «Помощь в выборе анализа» page
    html = once(html, '  <!-- SEARCH VIEW START -->', PZ_VIEW + '  <!-- SEARCH VIEW START -->')
    html = once(html, '  window.CLD_PROTO = {', PZ_JS.replace('__DATA__', json.dumps(data, ensure_ascii=False)) + '  window.CLD_PROTO = {')
    html = once(html, '/* SEARCH CSS */', CSS + '/* SEARCH CSS */')
    # entries: line under the hero search, 9th tile, desktop mega menu (mobile menu below)
    html = once(html, '          <div class="quick" id="quick"></div>',
                '          <button class="hero-help" type="button" data-go="vybor-analiza"><svg class="ico"><use href="#i-chat"/></svg><span>Не знаете, какой анализ нужен? <b>Помощь в выборе</b></span></button>\n          <div class="quick" id="quick"></div>')
    html = once(html, 'var FTABS = ["women", "men", "kids", "senior", "gifts", "checkups", "organs", "reasons"];',
                'var FTABS = ["women", "men", "kids", "senior", "gifts", "checkups", "organs", "reasons", "vybor-analiza"];')
    html = once(html, 'var FTN = { gifts: "Подарочные сертификаты",', 'var FTN = { "vybor-analiza": "Помощь в выборе", gifts: "Подарочные сертификаты",')
    html = once(html, 'gifts: "Подарочные сертификаты", checkups: "Чек-апы"', 'gifts: "Сертификаты", checkups: "Чек-апы"')
    html = once(html, 'var AUDIMG = { women: "women.webp",', 'var AUDIMG = { "vybor-analiza": "vybor-analiza.svg", women: "women.webp",')
    m = re.search(r'  function megaHtml\(k\) \{[\s\S]*?\n  \}\n', html)
    assert m and m.group(0).count("    return '<div class=\"mg-cols\">' +") == 1, 'mega catalog panel not found'
    body = m.group(0).replace("    return '<div class=\"mg-cols\">' +",
                              "    return '<button class=\"mg-help\" type=\"button\" data-go=\"vybor-analiza\">' + icon(\"i-chat\") + 'Не знаете, какой анализ нужен? Помощь в выборе' + icon(\"i-arrow\") + '</button>' + '<div class=\"mg-cols\">' +")
    html = html[:m.start()] + body + html[m.end():]
    # mobile menu in groups
    m = re.search(r'<div class="mmenu" id="mmenu" hidden>[\s\S]*?\n</div>\n', html)
    assert m, 'mobile menu not found'
    html = html[:m.start()] + MMENU + html[m.end():]
    # «Ваш город» — strip under the header instead of a popover over the menu button
    m = re.search(r'      <div class="cityq" id="cityq"[^\n]*</div></div>\n', html)
    assert m, 'city prompt not found'
    html = html[:m.start()] + html[m.end():]
    html = once(html, '<div class="mmenu" id="mmenu" hidden>', CITY + '<div class="mmenu" id="mmenu" hidden>')
    # preview is not for search engines
    html = once(html, '</head>', '<meta name="robots" content="noindex">\n</head>')
    return html


if __name__ == '__main__':
    out = ROOT / 'v4-new/index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(integrate((ROOT / 'v4/index.html').read_text()))
    print('Preview written:', out.relative_to(ROOT))
