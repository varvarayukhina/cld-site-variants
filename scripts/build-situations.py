"""Страницы «Анализы по поводу» (#povod-<id>) и их оглавление (#povody) из content/situations/situations.json.
Факты: ~/cld-work/situations-facts.md (первоисточники); тексты прошли независимую проверку. Идемпотентно. Запускать после crosslinks."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITPAGE = {"Усталость и слабость": "ustalost", "Перед операцией": "pered-operaciey", "Ребёнку в сад и школу": "sad-shkola"}

MARKUP = '''  <!-- SITUATIONS VIEWS START -->
  <section id="v-situation" data-view="situation" hidden>
    <div class="st-hero" id="st-hero">
      <div class="wrap st-hero-in">
        <div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><button type="button" data-go="povody">Анализы по поводу</button><span>/</span><span id="st-crumb"></span></div>
        <h1 id="st-h1"></h1>
        <p class="lede st-lede" id="st-lede"></p>
      </div>
    </div>
    <div class="wrap st-g">
      <article class="st-art" id="st-art"></article>
      <aside class="st-toc" aria-label="Содержание"><p class="st-toc-h">На этой странице</p><nav id="st-toc"></nav></aside>
    </div>
  </section>
  <section id="v-povody" data-view="povody" hidden>
    <div class="cxhero">
      <div class="wrap">
        <div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><span>Анализы по поводу</span></div>
        <h1>Анализы по поводу</h1>
        <p class="lede st-lede">Какие анализы нужны перед операцией, для санатория, бассейна, детского сада и в других ситуациях: что требуется официально, что советуют клинические рекомендации и что не нужно.</p>
      </div>
    </div>
    <div class="wrap"><div class="st-hub" id="st-hub"></div></div>
  </section>
  <!-- SITUATIONS VIEWS END -->
'''

JS = r'''  /* SITUATIONS START */
  var SITUATIONS = __DATA__;
  var SITPAGE = __SITPAGE__;
  PAGES.push("povody"); NAVOF.situation = "catalog"; NAVOF.povody = "catalog";
  // значок раздела по смыслу заголовка: обязательное — галочка, «не нужно» — крестик, подготовка — часы и т. д.
  var ST_IC = [[/не нужн|не входит|не требу|не рекоменд|не обязат|нет смысла/i, "i-x"], [/обязател|требован|документ|правил/i, "i-check"], [/подготов|натощак|как сдать/i, "i-clock"], [/рекоменд/i, "i-file"], [/ребён|дет|школ|сад/i, "i-baby"], [/беремен|партн|пар[ауы]/i, "i-users"], [/врач|приём|хирург|анестез/i, "i-user"], [/вопрос|уточн|узна/i, "i-chat"], [/кров|анализ|набор|гепатит/i, "i-drop"]];
  function stIcon(h) { for (var i = 0; i < ST_IC.length; i++) if (ST_IC[i][0].test(h)) return ST_IC[i][1]; return "i-info"; }
  var stNo = false;
  function stPara(t) {
    if (t && typeof t === "object") {
      if (t.list) return '<ul class="st-ul' + (stNo ? " is-no" : "") + '">' + t.list.map(function (x) { return "<li>" + icon(stNo ? "i-x" : "i-check") + "<span>" + typo(esc(x)) + "</span></li>"; }).join("") + "</ul>";
      if (t.table) return '<div class="st-tw"><table class="st-tab"><thead><tr>' + t.table.head.map(function (x) { return "<th>" + esc(x) + "</th>"; }).join("") + "</tr></thead><tbody>" + t.table.rows.map(function (r) { return "<tr>" + r.map(function (x) { return "<td>" + typo(esc(x)) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>";
      return "";
    }
    var m = /^\[\[t:([^\]]+)\]\]$/.exec(t);
    if (m) return A[m[1]] ? '<div class="rows st-rows">' + row(m[1]) + "</div>" : "";
    return "<p>" + typo(esc(t)) + "</p>";
  }
  function renderSituation() {
    var s = SITUATIONS[state.sit]; if (!s) return;
    PAGE_META.situation = [s.title, s.desc];
    $("#st-hero").style.setProperty("--st-bg", "url(../assets/img/situations/" + s.id + ".webp)");
    $("#st-h1").textContent = s.h1; $("#st-crumb").textContent = s.h1; $("#st-lede").innerHTML = typo(esc(s.lede));
    var secs = s.sections.map(function (x) {
      var ic = stIcon(x.h); stNo = ic === "i-x";
      var body = x.p.map(stPara); var fi = x.p.findIndex(function (y) { return typeof y === "string" && y.indexOf("[[") !== 0; });
      if (fi >= 0) body[fi] = body[fi].replace("<p>", '<p class="st-lead">');
      stNo = false;
      return '<section class="st-sec" id="' + x.id + '"><h2><span class="st-hi' + (ic === "i-x" ? " is-no" : "") + '">' + icon(ic) + "</span>" + esc(x.h) + "</h2>" + body.join("") + "</section>";
    });
    var set = (s.set || []).filter(function (c) { return A[c] && !A[c].na; });
    if (set.length) {
      var sum = set.reduce(function (a, c) { return a + A[c].p; }, 0);
      secs.splice(1, 0, '<section class="st-sec st-set" id="nabor"><h2>Анализы одним заказом</h2>' + (s.set_note ? "<p>" + typo(esc(s.set_note)) + "</p>" : "") + '<div class="rows">' + set.map(function (c) { return row(c); }).join("") + '</div><div class="st-buy"><span class="st-sum"><span class="p-on">при оплате онлайн</span><b class="num">' + rub(online(sum)) + "</b><small>в пункте " + rub(sum) + '</small></span><button class="btn btn-lime" type="button" data-sit-add="' + set.join(",") + '">Добавить все в корзину</button></div></section>');
    }
    if (s.faq && s.faq.length) secs.push('<section class="st-sec st-faq" id="voprosy"><h2>Частые вопросы</h2>' + s.faq.map(function (f) { return "<details><summary>" + esc(f.q) + "</summary><p>" + typo(esc(f.a)) + "</p></details>"; }).join("") + "</section>");
    var others = Object.keys(SITUATIONS).filter(function (k) { return k !== state.sit; });
    secs.push('<section class="st-sec st-aux" id="drugie-povody"><h2>Другие поводы</h2><div class="rm-list">' + others.map(function (k) { return '<button class="rm-link" type="button" data-go="situation:' + k + '">' + icon("i-file") + "<span><b>" + esc(SITUATIONS[k].h1) + "</b></span></button>"; }).join("") + "</div></section>");
    $("#st-art").innerHTML = secs.join("") + '<p class="st-note">' + typo("Результат оценивает лечащий врач. Помощь в выборе анализов — по телефону 8 800 201 78 30.") + "</p>";
    $("#st-toc").innerHTML = $$("#st-art .st-sec:not(.st-aux)").map(function (x) { return '<a href="#' + x.id + '" data-st-toc="' + x.id + '">' + esc(x.querySelector("h2").textContent) + "</a>"; }).join("");
    var ld = $("#s-ld"); if (!ld) { ld = document.createElement("script"); ld.type = "application/ld+json"; ld.id = "s-ld"; document.head.appendChild(ld); }
    var graph = [{ "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Главная" }, { "@type": "ListItem", position: 2, name: "Анализы по поводу" }, { "@type": "ListItem", position: 3, name: s.h1 }] }, { "@type": "MedicalWebPage", name: s.h1, description: s.desc, inLanguage: "ru" }];
    if (s.faq && s.faq.length) graph.push({ "@type": "FAQPage", mainEntity: s.faq.map(function (f) { return { "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } }; }) });
    ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@graph": graph });
    syncCart();
  }
  function renderPovody() {
    PAGE_META.povody = ["Анализы по поводу: перед операцией, для санатория, бассейна, детского сада | CLD", "Какие анализы нужны перед операцией, для санаторно-курортной карты, бассейна, детского сада и в других ситуациях: требования, рекомендации и что не нужно."];
    $("#st-hub").innerHTML = Object.keys(SITUATIONS).map(function (k) { var s = SITUATIONS[k]; return '<button class="st-card" type="button" data-go="situation:' + k + '"><img src="../assets/img/situations/' + k + '.webp" alt="" width="800" height="800" loading="lazy"><b>' + esc(s.h1) + "</b><span>" + typo(esc(s.lede)) + "</span></button>"; }).join("");
  }
  RENDER.situation = renderSituation; RENDER.povody = renderPovody;
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-sit-add]");
    if (b) { var codes = b.dataset.sitAdd.split(","); codes.forEach(function (c) { if (!cart[c] && A[c] && !A[c].na) cart[c] = 1; }); syncCart(); toast("Добавили в корзину: " + nAn(codes.length)); return; }
    var t = e.target.closest("[data-st-toc]");
    if (t) { e.preventDefault(); var sec = document.getElementById(t.dataset.stToc); if (sec) window.scrollTo({ top: sec.getBoundingClientRect().top + window.scrollY - 140, behavior: reduceMotion ? "auto" : "smooth" }); }
  });
  /* SITUATIONS END */
'''

CSS = '''/* SITUATIONS CSS */
.st-lede { max-width: 68ch; }
#v-povody .cxhero .wrap { padding-bottom: 36px; }
.st-hero { position: relative; overflow: hidden; background: #FFF; border-bottom: 1px solid var(--line); }
.st-hero::before { content: ""; position: absolute; right: max(-60px, calc((100vw - 1440px) / 2)); bottom: -90px; width: 720px; height: 720px; background: var(--st-bg) center / contain no-repeat; opacity: .32; }
.st-hero-in { position: relative; z-index: 1; min-height: 440px; padding-block: 28px 48px; display: flex; flex-direction: column; }
.st-hero h1 { margin-top: auto; max-width: 20ch; font-size: clamp(36px, 4.4vw, 52px); line-height: 1.08; color: var(--ink); }
.st-hero .lede { margin-top: 16px; max-width: 46ch; font-size: 19px; line-height: 1.6; color: var(--ink); }
.st-hero .crumbs { color: var(--muted); }
.st-card img { width: 100%; height: 180px; object-fit: contain; border-radius: 14px; background: var(--surface-2); }
.st-g { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 56px; padding-block: 40px 72px; align-items: start; }
.st-art { min-width: 0; }
.st-sec { scroll-margin-top: 140px; }
.st-sec + .st-sec { margin-top: 44px; }
.st-sec h2 { margin-bottom: 14px; font-size: clamp(26px, 2.6vw, 32px); line-height: 1.2; }
.st-sec > p { margin-bottom: 14px; font-size: 18px; line-height: 1.65; color: var(--ink); max-width: 82ch; }
.st-sec h2 { display: flex; align-items: center; gap: 14px; }
.st-hi { display: inline-grid; place-items: center; width: 44px; height: 44px; flex: none; border-radius: 50%; background: var(--lime); color: var(--navy); }
.st-hi .ico { width: 22px; height: 22px; stroke-width: 2.4; }
.st-hi.is-no { background: var(--navy-soft); }
.st-sec > p.st-lead { font-size: 20px; line-height: 1.6; font-weight: 500; }
.st-ul { list-style: none; margin: 0 0 16px; padding: 0; display: grid; gap: 10px; font-size: 18px; line-height: 1.55; max-width: 80ch; }
.st-ul li { display: flex; gap: 12px; align-items: flex-start; }
.st-ul li .ico { width: 24px; height: 24px; flex: none; margin-top: 2px; padding: 4px; border-radius: 50%; background: var(--lime-soft); color: var(--navy); stroke-width: 2.6; }
.st-ul.is-no li .ico { background: var(--navy-soft); color: var(--muted); }
.st-tw { margin: 16px 0 20px; overflow-x: auto; }
.st-tab { width: 100%; border-collapse: collapse; font-size: 16px; line-height: 1.5; }
.st-tab th { text-align: left; padding: 12px 14px; background: var(--navy); color: #FFF; font-weight: 700; }
.st-tab td { padding: 12px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
.st-rows { margin: 10px 0 18px; }
.st-set { padding: 22px; border-radius: 20px; background: var(--surface-2); }
.st-buy { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; margin-top: 16px; }
.st-sum { display: grid; }
.st-sum b { font: 700 24px var(--text); color: var(--ink); }
.st-sum small { font-size: 16px; color: var(--muted); }
.st-faq details { border-bottom: 1px solid var(--line); }
.st-faq summary { padding: 18px 0; font: 700 18px/1.4 var(--text); color: var(--ink); cursor: pointer; }
.st-faq details p { padding: 0 0 18px; font-size: 18px; line-height: 1.6; max-width: 70ch; }
.st-note { margin-top: 36px; font-size: 16px; color: var(--muted); }
.st-toc { position: sticky; top: calc(var(--sw-h, 0px) + 108px); padding: 20px; border-radius: 18px; background: var(--surface-2); }
.st-toc-h { margin-bottom: 6px; font: 700 16px var(--text); color: var(--muted); }
.st-toc nav { display: grid; gap: 2px; }
.st-toc a { display: block; padding: 8px 12px; border-radius: 10px; font: 600 16px/1.35 var(--text); color: var(--ink); text-decoration: none; }
.st-toc a:hover { background: var(--navy-soft); }
.st-hub { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; padding-block: 36px 72px; }
.st-card { display: grid; gap: 8px; padding: 22px; border: 0; border-radius: 18px; background: #FFF; box-shadow: inset 0 0 0 1px var(--line); text-align: left; color: var(--ink); cursor: pointer; }
.st-card:hover { box-shadow: inset 0 0 0 1.5px var(--navy); }
.st-card b { font: 700 20px/1.3 var(--display); }
.st-card span { font-size: 16px; line-height: 1.5; color: var(--muted); }
@media (max-width: 960px) {
  .st-g { grid-template-columns: minmax(0, 1fr); gap: 24px; padding-block: 24px 48px; }
  .st-toc { position: static; order: -1; }
  .st-hub { grid-template-columns: minmax(0, 1fr); }
  .st-hero::before { right: -90px; bottom: -40px; width: 380px; height: 380px; opacity: .22; }
  .st-hero-in { min-height: 0; padding-top: 16px; }
  .st-hero h1 { margin-top: 28px; font-size: 32px; }
  .st-hero .lede { font-size: 17px; }
  .st-sec > p, .st-ul, .st-faq details p { font-size: 17px; }
  .st-sec > p.st-lead { font-size: 18px; }
  .st-hi { width: 36px; height: 36px; }
  .st-hi .ico { width: 18px; height: 18px; }
}
/* SITUATIONS CSS END */
'''


def block(html: str, start: str, end: str, new: str, anchor: str, before: bool = True) -> str:
    if start in html:
        return re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end) + r"\n", lambda m: new, html, count=1)
    assert html.count(anchor) == 1, anchor[:60]
    return html.replace(anchor, new + anchor if before else anchor + new, 1)


def integrate(html: str) -> str:
    data = json.loads((ROOT / "content/situations/situations.json").read_text())
    js = JS.replace("__DATA__", json.dumps({s["id"]: s for s in data}, ensure_ascii=False)).replace("__SITPAGE__", json.dumps(SITPAGE, ensure_ascii=False))
    html = block(html, "  <!-- SITUATIONS VIEWS START -->", "<!-- SITUATIONS VIEWS END -->", MARKUP, '  <section id="v-card" data-view="card" hidden>')
    html = block(html, "  /* SITUATIONS START */", "/* SITUATIONS END */", js, "  /* SHARED NAVIGATION START */")
    html = block(html, "/* SITUATIONS CSS */", "/* SITUATIONS CSS END */", CSS, "</style>")
    one = [
        ('    else if (v === "guide" && GUIDES[p[1]])', '    else if (v === "situation" && SITUATIONS[p[1]]) { state.view = "situation"; state.sit = p[1]; } // страница повода\n'),
        ('var hash = state.view === "compare" ? ', None),
        ('    else if (h.indexOf("for-") === 0) go("guide:" + h.slice(4), false);', None),
        ("applyPageMeta(); // reset metadata for every view", None),
    ]
    if "// страница повода" not in html:
        a = one[0][0]; assert html.count(a) == 1; html = html.replace(a, one[0][1] + a, 1)
    if '"povod-" + state.sit' not in html:
        a = one[1][0]; assert html.count(a) == 1; html = html.replace(a, 'var hash = state.view === "situation" ? "povod-" + state.sit : state.view === "compare" ? ', 1)
    if 'h.indexOf("povod-") === 0' not in html:
        a = one[2][0]; assert html.count(a) == 1; html = html.replace(a, a + '\n    else if (h.indexOf("povod-") === 0) go("situation:" + h.slice(6), false);', 1)
    if 'var sld = $("#s-ld")' not in html:
        a = one[3][0]; assert html.count(a) == 1; html = html.replace(a, a + '\n    var sld = $("#s-ld"); if (sld && state.view !== "situation") sld.remove();', 1)
    # меню «По поводу»: заголовок ведёт на оглавление поводов, у кого есть страница — на неё
    old = 'mgCol("По поводу", SITS.map(function (x) { return mgLink("catalog:" + x.go, x.n, "", mgPic(x.pic || "checkups")); }), "", false, "i-cal")'
    new = 'mgCol("По поводу", SITS.map(function (x) { return mgLink(SITPAGE[x.n] ? "situation:" + SITPAGE[x.n] : "catalog:" + x.go, x.n, "", mgPic(x.pic || "checkups")); }).concat([mgLink("povody", "Все поводы: санаторий, бассейн, COVID и другие")]), "povody", false, "i-cal")'
    if old in html:
        html = html.replace(old, new, 1)
    return html


if __name__ == "__main__":
    p = ROOT / "v4/index.html"
    p.write_text(integrate(p.read_text()))
    print("Built situation pages.")
