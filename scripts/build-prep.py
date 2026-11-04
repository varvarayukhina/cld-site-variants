"""Памятка «Как подготовиться к анализам» (#podgotovka) — комикс из content/prep-guide/prep.json, картинки assets/img/prep/.
Ссылка на неё — в блоке «Как подготовиться» каждой карточки, в памятке после заказа и в подвале. Факты: ~/cld-work/prep-guide-ledger.md
(регламент CLD + первоисточники), тексты прошли независимую проверку. Идемпотентно. Запускать после situations, перед card-fixes."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

MARKUP = '''  <!-- PREP VIEW START -->
  <section id="v-podgotovka" data-view="podgotovka" hidden>
    <div class="st-hero pp-hero" style="--st-bg: url(../assets/img/prep/p04-voda.webp)">
      <div class="wrap st-hero-in">
        <div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><span>Подготовка к анализам</span></div>
        <h1 id="pp-h1"></h1>
        <p class="lede" id="pp-lede"></p>
      </div>
    </div>
    <div class="wrap pp-art" id="pp-art"></div>
  </section>
  <!-- PREP VIEW END -->
'''

JS = r'''  /* PREP START */
  var PREP = __DATA__;
  PAGES.push("podgotovka"); NAVOF.podgotovka = "catalog";
  function ppPanel(p, n) {
    return '<figure class="pp-panel"><div class="pp-head"><span class="pp-n num">' + n + "</span>" + (p.bubble ? '<span class="pp-bub">' + typo(esc(p.bubble)) + "</span>" : "") + "</div>" +
      '<img src="../assets/img/prep/' + p.id + '.webp" alt="" width="1200" height="800" loading="lazy"><figcaption><h3>' + typo(esc(p.title)) + "</h3><p>" + typo(esc(p.text)) + "</p></figcaption></figure>";
  }
  function renderPrep() {
    PAGE_META.podgotovka = [PREP.title + " — памятка в картинках | CLD", PREP.description];
    $("#pp-h1").textContent = PREP.title; $("#pp-lede").innerHTML = typo(esc(PREP.lede));
    var html = '<section class="pp-sec" id="skolko-ne-est"><h2><span class="st-hi">' + icon("i-clock") + "</span>Сколько не есть перед анализом</h2>" +
      '<p class="pp-p">' + typo("Точное правило для вашего анализа — в его карточке, в разделе «Как подготовиться».") + '</p><div class="pp-fast">' +
      PREP.fasting.map(function (f) { return '<div class="pp-f"><b class="num">' + typo(esc(f.label)) + "</b><span>" + typo(esc(f.text)) + "</span></div>"; }).join("") + "</div></section>";
    var n = 0, groups = [];
    PREP.panels.forEach(function (p) { var g = groups[groups.length - 1]; if (!g || g.when !== p.when) groups.push(g = { when: p.when, items: [] }); g.items.push(p); });
    html += '<section class="pp-sec" id="po-shagam"><h2><span class="st-hi">' + icon("i-check") + "</span>Подготовка по шагам</h2>" +
      groups.map(function (g) { return '<h3 class="pp-when">' + esc(g.when) + '</h3><div class="pp-strip" style="--n:' + Math.min(3, g.items.length) + '">' + g.items.map(function (p) { return ppPanel(p, ++n); }).join("") + "</div>"; }).join("") + "</section>";
    html += '<section class="pp-sec" id="osobye"><h2><span class="st-hi">' + icon("i-info") + "</span>Если сдаёте не кровь</h2>" +
      PREP.special.map(function (s) {
        return '<div class="pp-spec' + (s.img ? "" : " no-img") + '" id="' + s.id + '">' + (s.img ? '<img src="../assets/img/prep/' + s.img + '.webp" alt="" width="1200" height="800" loading="lazy">' : "") +
          "<div><h3>" + typo(esc(s.title)) + '</h3><ol class="pp-ol">' + s.steps.map(function (x) { return "<li>" + typo(esc(x)) + "</li>"; }).join("") + "</ol>" + (s.note ? '<p class="pp-note">' + typo(esc(s.note)) + "</p>" : "") + "</div></div>";
      }).join("") + "</section>";
    html += '<section class="pp-sec pp-call" id="ne-poluchilos"><h2><span class="st-hi">' + icon("i-chat") + "</span>Если не получилось подготовиться</h2><p>" + typo(esc(PREP.if_not_ready)) + "</p></section>";
    html += '<section class="pp-sec st-faq" id="voprosy"><h2>Частые вопросы</h2>' + PREP.faq.map(function (f) { return "<details><summary>" + esc(f.q) + "</summary><p>" + typo(esc(f.a)) + "</p></details>"; }).join("") + "</section>";
    html += '<div class="pp-end"><button class="btn btn-lime" type="button" data-go="catalog:blood">Найти свой анализ</button><span>' + typo("Помогут с подготовкой по телефону 8 800 201 78 30") + "</span></div>";
    $("#pp-art").innerHTML = html;
    var ld = $("#s-ld"); if (!ld) { ld = document.createElement("script"); ld.type = "application/ld+json"; ld.id = "s-ld"; document.head.appendChild(ld); }
    ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@graph": [
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Главная" }, { "@type": "ListItem", position: 2, name: "Подготовка к анализам" }] },
      { "@type": "MedicalWebPage", name: PREP.title, description: PREP.description, inLanguage: "ru" },
      { "@type": "FAQPage", mainEntity: PREP.faq.map(function (f) { return { "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } }; }) }] });
  }
  RENDER.podgotovka = renderPrep;
  var PP_LINK = '<a class="pp-more" href="#podgotovka" data-go="podgotovka">' + icon("i-file") + "<span>Памятка в картинках: как подготовиться к анализам</span></a>";
  /* PREP END */
'''

CSS = '''/* PREP CSS */
.pp-art { padding-block: 40px 72px; }
.pp-sec { scroll-margin-top: 140px; }
.pp-sec + .pp-sec { margin-top: 56px; }
.pp-sec > h2 { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; font-size: clamp(26px, 2.6vw, 32px); line-height: 1.2; }
.pp-p, .pp-call p { max-width: 70ch; font-size: 18px; line-height: 1.6; color: var(--ink); }
.pp-fast { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
.pp-f { display: grid; align-content: start; gap: 8px; padding: 20px; border-radius: 18px; background: var(--surface-2); }
.pp-f b { font: 800 30px/1.1 var(--text); color: var(--navy); }
.pp-f span { font-size: 17px; line-height: 1.5; color: var(--ink); }
.pp-when { display: inline-block; margin: 28px 0 14px; padding: 8px 16px; border-radius: 999px; background: var(--navy); color: #FFF; font: 700 17px/1.3 var(--text); }
.pp-strip { display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: 18px; }
.pp-panel { margin: 0; display: grid; grid-row: span 3; grid-template-rows: subgrid; gap: 0; border: 2.5px solid var(--navy); border-radius: 20px; overflow: hidden; background: #FFF; }
.pp-head { display: flex; align-items: flex-end; gap: 12px; padding: 14px 14px 4px; }
.pp-n { display: grid; place-items: center; width: 44px; height: 44px; flex: none; border-radius: 50%; background: var(--lime); color: var(--navy); font: 800 18px var(--text); border: 2.5px solid var(--navy); }
.pp-bub { position: relative; flex: 1; padding: 10px 14px; border: 2.5px solid var(--navy); border-radius: 18px; background: #FFF; color: var(--ink); font: 700 16px/1.35 var(--text); }
.pp-bub::after { content: ""; position: absolute; left: 34%; bottom: -10px; width: 16px; height: 16px; background: #FFF; border-right: 2.5px solid var(--navy); border-bottom: 2.5px solid var(--navy); transform: rotate(45deg); }
.pp-panel > img { display: block; width: 100%; height: auto; max-height: 400px; aspect-ratio: 3 / 2; object-fit: contain; border-bottom: 2.5px solid var(--navy); background: #FFF; }
.pp-panel figcaption { padding: 16px 18px 20px; }
.pp-panel h3 { margin-bottom: 6px; font: 700 20px/1.3 var(--display); color: var(--ink); }
.pp-panel p { font-size: 17px; line-height: 1.55; color: var(--ink); }
.pp-spec { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 28px; align-items: center; padding: 22px; border: 2.5px solid var(--navy); border-radius: 20px; }
.pp-spec + .pp-spec { margin-top: 18px; }
.pp-spec img { display: block; width: 100%; height: auto; border-radius: 14px; }
.pp-spec.no-img { grid-template-columns: minmax(0, 1fr); }
.pp-spec.no-img > div { max-width: 72ch; }
.pp-sec.st-faq details p { max-width: 64ch; }
.pp-spec h3 { margin-bottom: 10px; font: 700 22px/1.3 var(--display); color: var(--ink); }
.pp-ol { margin: 0; padding-left: 24px; display: grid; gap: 8px; font-size: 17px; line-height: 1.55; color: var(--ink); }
.pp-ol li::marker { font-weight: 800; color: var(--navy); }
.pp-note { margin-top: 12px; font-size: 17px; line-height: 1.55; color: var(--ink); }
.pp-call { padding: 24px; border-radius: 20px; background: var(--lime-soft); }
.pp-end { display: flex; flex-wrap: wrap; align-items: center; gap: 18px; margin-top: 44px; font-size: 17px; color: var(--ink); }
.pp-more { display: inline-flex; align-items: center; gap: 10px; margin-top: 12px; padding: 10px 16px; border-radius: 12px; background: var(--lime-soft); color: var(--navy); font: 700 16px/1.35 var(--text); text-decoration: none; }
.pp-more:hover { background: var(--lime); }
.pp-more .ico { width: 20px; height: 20px; flex: none; }
@media (max-width: 1100px) { .pp-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } .pp-strip > .pp-panel:last-child:nth-child(odd) { grid-column: span 2; } .pp-fast { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 700px) {
  .pp-art { padding-block: 24px 48px; }
  .pp-strip, .pp-fast, .pp-spec { grid-template-columns: minmax(0, 1fr); }
  .pp-strip > .pp-panel:last-child:nth-child(odd) { grid-column: auto; }
  .pp-spec { padding: 16px; gap: 16px; }
  .pp-p, .pp-call p { font-size: 17px; }
  .pp-f b { font-size: 26px; }
}
/* PREP CSS END */
'''


def block(html: str, start: str, end: str, new: str, anchor: str) -> str:
    if start in html:
        return re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end) + r"\n", lambda m: new, html, count=1)
    assert html.count(anchor) == 1, anchor[:60]
    return html.replace(anchor, new + anchor, 1)


def once(html: str, mark: str, anchor: str, new: str) -> str:
    if mark in html:
        return html
    assert html.count(anchor) == 1, anchor[:60]
    return html.replace(anchor, new, 1)


def integrate(html: str) -> str:
    data = json.loads((ROOT / "content/prep-guide/prep.json").read_text())
    data = {k: data[k] for k in ("title", "lede", "description", "panels", "fasting", "special", "if_not_ready", "faq")}
    html = block(html, "  <!-- PREP VIEW START -->", "<!-- PREP VIEW END -->", MARKUP, '  <section id="v-card" data-view="card" hidden>')
    html = block(html, "  /* PREP START */", "/* PREP END */", JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)), "  /* SHARED NAVIGATION START */")
    html = block(html, "/* PREP CSS */", "/* PREP CSS END */", CSS, "</style>")
    # карточка анализа: ссылка на памятку в конце блока «Как подготовиться»
    a = '    $("#k-blocks").innerHTML = html;\n'
    html = once(html, "// памятка в карточке", a, a + '    $$("#k-blocks > section").forEach(function (s) { var h = s.querySelector("h2"); if (h && /подготов/i.test(h.textContent)) s.insertAdjacentHTML("beforeend", PP_LINK); }); // памятка в карточке\n')
    # памятка после заказа
    a = '''</ol><p class="prep-last">Приём лекарств перед анализом согласуйте с лечащим врачом.</p>';'''
    html = once(html, "</p>' + PP_LINK;", a, a[:-2] + "' + PP_LINK;")
    # подвал, колонка «Пациентам»
    a = '          <a href="#comparisons" data-go="comparisons">Справочник об анализах</a>\n'
    html = once(html, 'data-go="podgotovka">Подготовка к анализам</a>', a, a + '          <a href="#podgotovka" data-go="podgotovka">Подготовка к анализам</a>\n')
    # убрать JSON-LD памятки на других страницах
    a = 'var sld = $("#s-ld"); if (sld && state.view !== "situation") sld.remove();'
    html = once(html, 'state.view !== "podgotovka") sld.remove();', a, a.replace('state.view !== "situation")', 'state.view !== "situation" && state.view !== "podgotovka")'))
    return html


if __name__ == "__main__":
    p = ROOT / "v4/index.html"
    p.write_text(integrate(p.read_text()))
    print("Built preparation guide.")
