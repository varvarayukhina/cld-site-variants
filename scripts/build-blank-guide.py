"""Статья «Как читать бланк результата анализа» (#kak-chitat-blank): образец бланка CLD с номерами зон и крупные фрагменты
с маркером (assets/img/blank/, нарезка — ~/cld-work/blank-guide/crops.py из макета «05 Печать/Бланк результатов», вариант 1).
Тексты — content/blank-guide/blank.json (автор + независимая проверка по первоисточникам, реестр ~/cld-work/blank-guide/).
Ссылки: подвал «Пациентам», бланк в личном кабинете, страница «Результаты анализов». Идемпотентно. Запускать после build-account."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

# Номер зоны на миниатюре: x, y — центр метки в % от ширины и высоты бланка (по разметке макета 793 × 1122 px)
PINS = {"pat": (3, 17), "head": (97, 24), "ok": (3, 29.8), "out": (97, 57.8), "one": (97, 33.7), "risk": (3, 50.4), "calc": (3, 59.7), "foot": (97, 66)}

MARKUP = '''  <!-- BLANK VIEW START -->
  <section id="v-kak-chitat-blank" data-view="kak-chitat-blank" hidden>
    <div class="bg-hero">
      <div class="wrap">
        <div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><button type="button" data-go="results">Результаты анализов</button><span>/</span><span>Как читать бланк</span></div>
        <h1 id="bg-h1"></h1>
        <p class="lede" id="bg-lede"></p>
      </div>
    </div>
    <div class="wrap bg-grid">
      <aside class="bg-map" aria-label="Образец бланка: номера разделов"><div class="bg-sheet" id="bg-sheet"></div><p class="bg-cap">Образец бланка CLD. Нажмите на номер — откроется объяснение.</p></aside>
      <div class="bg-art" id="bg-art"></div>
    </div>
  </section>
  <!-- BLANK VIEW END -->
'''

JS = r'''  /* BLANK START */
  var BLANK = __DATA__, BLANK_PINS = __PINS__, bgSpy = null;
  PAGES.push("kak-chitat-blank"); NAVOF["kak-chitat-blank"] = "results";
  function bgP(list) { return list.map(function (x) { return "<p>" + typo(esc(x)) + "</p>"; }).join(""); }
  function bgList(list) { return list && list.length ? '<ul class="bg-ul">' + list.map(function (x) { return "<li>" + typo(esc(x)) + "</li>"; }).join("") + "</ul>" : ""; }
  function renderBlankGuide() {
    PAGE_META["kak-chitat-blank"] = [BLANK.seo_title, BLANK.description];
    $("#bg-h1").textContent = BLANK.title; $("#bg-lede").innerHTML = typo(esc(BLANK.lede));
    $("#bg-sheet").innerHTML = '<img src="../assets/img/blank/blank-full.webp" alt="Образец бланка результата CLD: биохимические исследования крови" width="900" height="1273">' +
      BLANK.zones.map(function (z, i) { var p = BLANK_PINS[z.id]; return '<a class="bg-pin" href="#bg-' + z.id + '" data-bg="' + z.id + '" style="left:' + p[0] + "%;top:" + p[1] + '%" aria-label="' + (i + 1) + ". " + esc(z.h) + '"><span class="num">' + (i + 1) + "</span></a>"; }).join("");
    var html = BLANK.zones.map(function (z, i) {
      return '<section class="bg-zone" id="bg-' + z.id + '" data-zone="' + z.id + '"><h2><span class="bg-n num" aria-hidden="true">' + (i + 1) + "</span><span>" + typo(esc(z.h)) + "</span></h2>" +
        '<figure class="bg-zoom"><img src="../assets/img/blank/z-' + z.id + '.webp" alt="Фрагмент бланка: ' + esc(z.h.toLowerCase()) + '" loading="lazy" width="1400"><figcaption class="bg-swipe">Листайте вбок, чтобы увидеть фрагмент целиком</figcaption></figure>' + bgP(z.p) +
        (z.tip ? '<p class="bg-tip">' + icon("i-info") + "<span>" + typo(esc(z.tip)) + "</span></p>" : "") + "</section>";
    }).join("");
    [["why_out", "i-info"], ["labs_differ", "i-lab"], ["next", "i-check"]].forEach(function (k) {
      var s = BLANK[k[0]]; if (!s) return;
      html += '<section class="bg-sec" id="bg-' + k[0].replace("_", "-") + '"><h2><span class="st-hi">' + icon(k[1]) + "</span>" + typo(esc(s.h)) + "</h2>" + bgP(s.p || []) + bgList(s.list) + "</section>";
    });
    html += '<section class="bg-sec st-faq" id="bg-voprosy"><h2>Частые вопросы</h2>' + BLANK.faq.map(function (f) { return "<details><summary>" + esc(f.q) + "</summary><p>" + typo(esc(f.a)) + "</p></details>"; }).join("") + "</section>";
    html += '<div class="bg-end"><button class="btn btn-navy" type="button" data-go="lk:results">' + icon("i-file") + 'Мои результаты</button><button class="btn btn-ghost" type="button" data-go="podgotovka">Как подготовиться к анализам</button><button class="btn btn-ghost" type="button" data-go="comparisons">Справочник об анализах</button></div>';
    $("#bg-art").innerHTML = html;
    var ld = $("#s-ld"); if (!ld) { ld = document.createElement("script"); ld.type = "application/ld+json"; ld.id = "s-ld"; document.head.appendChild(ld); }
    ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@graph": [
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Главная" }, { "@type": "ListItem", position: 2, name: "Результаты анализов" }, { "@type": "ListItem", position: 3, name: "Как читать бланк" }] },
      { "@type": "MedicalWebPage", name: BLANK.title, description: BLANK.description, inLanguage: "ru" },
      { "@type": "FAQPage", mainEntity: BLANK.faq.map(function (f) { return { "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } }; }) }] });
    // номер раздела, который сейчас читают, подсвечен на миниатюре бланка
    if (bgSpy) bgSpy.disconnect();
    if ("IntersectionObserver" in window) {
      bgSpy = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) $$("#bg-sheet .bg-pin").forEach(function (a) { if (a.dataset.bg === e.target.dataset.zone) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); }); }); }, { rootMargin: "-45% 0px -50% 0px" });
      $$("#bg-art .bg-zone").forEach(function (s) { bgSpy.observe(s); });
    }
  }
  RENDER["kak-chitat-blank"] = renderBlankGuide;
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-bg]"); if (!a) return;
    e.preventDefault(); var s = $("#bg-" + a.dataset.bg); if (!s) return;
    var top = s.getBoundingClientRect().top + scrollY - ($("#top") ? $("#top").offsetHeight : 0) - 16;
    window.scrollTo({ top: top, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    var h = s.querySelector("h2"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  });
  /* BLANK END */
'''

CSS = '''/* BLANK CSS */
.bg-hero { background: var(--navy); color: #FFF; }
.bg-hero .wrap { display: block; padding-bottom: 44px; }
.bg-hero .crumbs { color: var(--on-navy-muted); }
.bg-hero .crumbs button { color: var(--on-navy); }
.bg-hero h1 { margin-top: 18px; max-width: 18ch; font-size: clamp(34px, 4.4vw, 54px); color: #FFF; }
.bg-hero .lede { max-width: 56ch; color: var(--on-navy); }
.bg-grid { display: grid; grid-template-columns: 360px minmax(0, 1fr); gap: 56px; align-items: start; padding-block: 40px 80px; }
.bg-map { position: sticky; top: 176px; }
.bg-sheet { position: relative; border-radius: 6px; background: #FFF; box-shadow: 0 1px 2px rgba(20,55,75,.12), 0 16px 36px rgba(20,55,75,.16); }
.bg-sheet img { width: 100%; height: auto; border-radius: 6px; }
.bg-pin { position: absolute; display: grid; place-items: center; width: 30px; height: 30px; margin: -15px 0 0 -15px; border-radius: 50%; background: var(--lime); color: var(--navy); box-shadow: 0 0 0 2px var(--navy), 0 2px 6px rgba(20,55,75,.3); font: 800 16px/1 var(--text); text-decoration: none; transition: transform .25s var(--ease), background-color .25s var(--ease), color .25s var(--ease); }
.bg-pin:hover { transform: scale(1.12); }
.bg-pin[aria-current="true"] { background: var(--navy); color: #FFF; box-shadow: 0 0 0 3px var(--lime), 0 4px 12px rgba(20,55,75,.35); transform: scale(1.18); }
.bg-cap { margin-top: 12px; font-size: 16px; color: var(--muted); }
.bg-art { max-width: 820px; }
.bg-zone, .bg-sec { scroll-margin-top: 170px; }
.bg-zone + .bg-zone { margin-top: 52px; }
.bg-zone h2, .bg-sec > h2 { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; font-size: clamp(24px, 2.4vw, 30px); line-height: 1.2; }
.bg-zone h2:focus { outline: none; }
.bg-n { display: grid; place-items: center; width: 44px; height: 44px; flex: none; border-radius: 50%; background: var(--lime); color: var(--navy); box-shadow: 0 0 0 2.5px var(--navy); font: 800 19px/1 var(--text); }
.bg-zoom { margin: 0 0 18px; padding: 14px; border-radius: 14px; background: var(--surface-2); }
.bg-zoom img { display: block; width: 100%; height: auto; border-radius: 4px; background: #FFF; box-shadow: 0 1px 2px rgba(20,55,75,.14), 0 8px 20px rgba(20,55,75,.10); }
.bg-swipe { display: none; }
.bg-art p { max-width: 60ch; font-size: 18px; line-height: 1.6; }
.bg-art p + p { margin-top: 12px; }
.bg-tip { display: flex; gap: 12px; align-items: flex-start; margin-top: 16px; padding: 14px 18px; border-radius: 14px; background: var(--lime-soft); font-weight: 600; }
.bg-tip .ico { width: 22px; height: 22px; margin-top: 3px; }
.bg-sec { margin-top: 60px; }
.bg-ul { display: grid; gap: 8px; margin: 14px 0 0; padding-left: 24px; max-width: 60ch; font-size: 18px; line-height: 1.55; }
.bg-ul li::marker { color: var(--navy); }
.bg-sec.st-faq details p { max-width: 64ch; }
.bg-end { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 48px; }
@media (max-width: 1100px) { .bg-grid { grid-template-columns: 280px minmax(0, 1fr); gap: 36px; } }
@media (max-width: 860px) {
  .bg-grid { grid-template-columns: minmax(0, 1fr); gap: 28px; padding-top: 24px; }
  .bg-map { position: static; max-width: 420px; justify-self: center; width: 100%; }
  .bg-art p, .bg-ul { font-size: 17px; }
  .bg-zoom { margin-inline: -8px; padding: 8px; overflow-x: auto; overscroll-behavior-x: contain; }
  .bg-zoom img { width: 700px; max-width: none; }  /* текст фрагмента ≈ 14 px — читается без увеличения */
  .bg-swipe { display: block; position: sticky; left: 0; width: calc(100vw - 40px); margin-top: 8px; font-size: 16px; color: var(--muted); }
  .bg-n { width: 38px; height: 38px; font-size: 17px; }
  .bg-end .btn { flex: 1 1 auto; }
}
/* BLANK CSS END */
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
    data = json.loads((ROOT / "content/blank-guide/blank.json").read_text())
    data = {k: data[k] for k in ("title", "seo_title", "description", "lede", "zones", "why_out", "labs_differ", "next", "faq")}
    assert [z["id"] for z in data["zones"]] == list(PINS), "зоны статьи не совпадают с номерами на бланке"
    html = block(html, "  <!-- BLANK VIEW START -->", "<!-- BLANK VIEW END -->", MARKUP, '  <section id="v-card" data-view="card" hidden>')
    data_js = json.dumps(data, ensure_ascii=False).replace("№ ", "№\u00a0")  # «№ заявки» не разрывается
    js = JS.replace("__DATA__", data_js).replace("__PINS__", json.dumps(PINS))
    html = block(html, "  /* BLANK START */", "/* BLANK END */", js, "  /* SHARED NAVIGATION START */")
    html = block(html, "/* BLANK CSS */", "/* BLANK CSS END */", CSS, "</style>")
    # подвал, «Пациентам» — после памятки о подготовке
    a = '          <a href="#podgotovka" data-go="podgotovka">Подготовка к анализам</a>\n'
    html = once(html, 'data-go="kak-chitat-blank">Как читать бланк', a, a + '          <a href="#kak-chitat-blank" data-go="kak-chitat-blank">Как читать бланк результата</a>\n')
    # JSON-LD статьи не остаётся на других страницах
    a = 'state.view !== "situation" && state.view !== "podgotovka")'
    html = once(html, 'state.view !== "kak-chitat-blank")', a, a[:-1] + ' && state.view !== "kak-chitat-blank")')
    # страница «Результаты анализов» ведёт на статью (из бланка в кабинете ссылка — в build-account.py)
    i = html.index('data-note="res1"'); j = html.index("</div>", i)
    if "kak-chitat-blank" not in html[i:j]:
        html = html[:j] + '<p class="lede"><a href="#kak-chitat-blank" data-go="kak-chitat-blank">Как читать бланк результата</a></p>' + html[j:]
    return html


if __name__ == "__main__":
    p = ROOT / "v4/index.html"
    p.write_text(integrate(p.read_text()))
    print("Built result form guide.")
