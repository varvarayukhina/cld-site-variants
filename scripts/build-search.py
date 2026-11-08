"""Site search v4: everyday words and referral abbreviations (content/search/search.json),
search over guides, situations, reference articles and service pages, Enter -> results page #poisk-<query>."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

JS = r'''
  var SRCH = __DATA__;
  var S_STOP = {}; SRCH.stop.forEach(function (w) { S_STOP[w] = 1; });
  function sToks(s) { return norm(String(s || "")).replace(/[^a-zа-я0-9]+/g, " ").trim().split(" ").filter(function (w) { return w && !S_STOP[w]; }); }
  function sRaw(s) { return norm(String(s || "")).replace(/[^a-zа-я0-9]+/g, " ").trim().split(" ").filter(Boolean); } // «где сдать» — only stop words
  function sStem(w) { if (w.length < 5) return w; var s = w.replace(/(иями|ями|ами|ого|его|ому|ему|ыми|ими|ость|ов|ев|ей|ий|ый|ой|ая|яя|ое|ее|ые|ие|ым|им|ом|ем|ам|ям|ах|ях|ую|юю|у|ю|а|я|ы|и|е|о|ь)$/, ""); return s.length >= 3 ? s : w; }
  function sWordHit(w, x) { return x.indexOf(w) === 0 || x.indexOf(sStem(w)) === 0; } // word of the query = beginning of the word (with a simple ending cut)
  var S_TERMS = null, S_PAGES = null;
  function sInit() {
    if (S_TERMS) return;
    S_TERMS = [];
    function term(t, codes, page) { var toks = sToks(t); if (!toks.length) toks = sRaw(t); if (toks.length) S_TERMS.push({ k: toks.join(" "), toks: toks, codes: codes, page: page }); }
    SRCH.syn.forEach(function (e) { e.w.forEach(function (t) { term(t, e.c.filter(function (c) { return A[c] || CXX[c]; }), ""); }); });
    Object.keys(SRCH.pages).forEach(function (go) { SRCH.pages[go].forEach(function (t) { term(t, null, go); }); });
    POINTS.forEach(function (p) { term(p.city, null, "points"); });
    S_PAGES = [];
    function page(go, t, kind, more) { if (t) S_PAGES.push({ go: go, t: t, kind: kind, toks: sToks(t + " " + (more || "")) }); }
    Object.keys(GUIDES).forEach(function (k) { page("guide:" + k, GUIDES[k].h1, "Гид: какие анализы и когда сдают", GUIDES[k].crumb); });
    Object.keys(SITUATIONS).forEach(function (k) { page("situation:" + k, SITUATIONS[k].h1, "Анализы по поводу"); });
    Object.keys(COMPARISONS).forEach(function (k) { page("compare:" + k, COMPARISONS[k].title, "Справочник об анализах", COMPARISONS[k].shortTitle); });
    CATS.forEach(function (c) { if (!c.aud) page("catalog:" + c.id, c.n, "Раздел каталога", c.s); });
    SRCH["static"].forEach(function (s) { page(s[0], s[1], s[2]); });
  }
  function sPage(go) { for (var i = 0; i < S_PAGES.length; i++) if (S_PAGES[i].go === go) return S_PAGES[i]; return null; }
  // dictionary term vs query: exact > same word stems > phrase inside the query > query is the start of the term (still typing)
  function sTermScore(t, qt, qk) {
    if (t.k === qk) return 300;
    if (qt.length === t.toks.length && qt.every(function (w, i) { return sStem(w) === sStem(t.toks[i]); })) return 280;
    if (t.toks.length < qt.length && (" " + qk + " ").indexOf(" " + t.k + " ") >= 0) return 240 + t.toks.length;
    if (qk.length >= 3 && qt.length <= t.toks.length && qt.every(function (w, i) { return i < qt.length - 1 ? sStem(w) === sStem(t.toks[i]) : sWordHit(w, t.toks[i]); })) return 200;
    if (qk.length >= 5 && lev(qk, t.k) <= (qk.length > 7 ? 2 : 1)) return 150; // typo: «витамн д», «щитовидк»
    return 0;
  }
  // name/title vs query: phrase at a word start > all words found > typo
  function sTextScore(qt, qk, toks) {
    var hk = " " + toks.join(" "), pos = hk.indexOf(" " + qk);
    // a short word that is only the start of a longer one («кал» → «калий», «дом» → «домашней») ranks low
    var weak = qt.length === 1 && qt[0].length <= 3 && !toks.some(function (x) { return x.indexOf(qt[0]) === 0 && x.length <= qt[0].length + 1; });
    if (pos >= 0) return weak ? 95 : 180 - Math.min(pos, 60) / 2;
    if (qt.every(function (w) { return toks.some(function (x) { return sWordHit(w, x); }); })) return 120;
    return 0;
  }
  function search(q) {
    sInit();
    var out = { p: [], a: [], fuzzy: false }, raw = norm(q);
    if (raw.length < 2) return out;
    var digits = /^[\d\s.\-]+$/.test(raw) ? raw.replace(/\D/g, "") : "";
    if (digits.length >= 2) { // a code from the referral
      Object.keys(A).concat(Object.keys(CXX)).forEach(function (code) { if (code.replace(/\D/g, "").indexOf(digits) === 0) out.a.push({ code: code, cx: !A[code], score: 200 - code.length }); });
      out.a.sort(function (x, y) { return y.score - x.score; });
      return out;
    }
    var qt = sToks(q); if (!qt.length) qt = sRaw(q);
    var qk = qt.join(" "), R = {};
    function add(key, rec) { var o = R[key]; if (o && o.dict) rec.dict = true; if (!o || o.score < rec.score) R[key] = rec; else if (rec.dict) o.dict = true; }
    var hits = [];
    S_TERMS.forEach(function (t) { var s = sTermScore(t, qt, qk); if (s) hits.push({ t: t, s: s }); });
    // «кровь в кале» also contains «кровь»: a shorter term inside a longer matched one is dropped
    var strong = hits.some(function (h) { return h.s >= 280; });
    if (hits.some(function (h) { return h.s >= 200; })) hits = hits.filter(function (h) { return h.s !== 150; }); // typo guess only when nothing matched as typed
    hits = hits.filter(function (h) { return !hits.some(function (o) { return o !== h && o.s >= 240 && o.t.k.length > h.t.k.length && (" " + o.t.k + " ").indexOf(" " + h.t.k + " ") >= 0; }); });
    hits.forEach(function (h) {
      var fz = h.s === 150;
      if (h.t.page) { if (sPage(h.t.page)) add("p:" + h.t.page, { page: sPage(h.t.page), score: h.s, fuzzy: fz, dict: true }); return; }
      h.t.codes.forEach(function (c, i) { add("a:" + c, { code: c, cx: !A[c], score: h.s - i * 0.5, fuzzy: fz, dict: true }); });
    });
    S_PAGES.forEach(function (p) { var s = sTextScore(qt, qk, p.toks); if (s) add("p:" + p.go, { page: p, score: s - 20 }); });
    Object.keys(CXX).forEach(function (code) { var s = sTextScore(qt, qk, sToks(CXX[code].n + " " + cxMis(code) + " чек ап")); if (s) add("a:" + code, { code: code, cx: true, score: s - 5 }); });
    Object.keys(A).forEach(function (code) {
      var a = A[code], words = sToks(a.n + " " + a.off), s = sTextScore(qt, qk, words), fuzzy = false;
      if (!s) { // typo in the name: «ферретин», «витамн д»
        var all = qt.every(function (w) { return words.some(function (x) { return sWordHit(w, x); }) || (w.length >= 3 && words.some(function (x) { return lev(w, x.slice(0, w.length + 1)) <= (w.length > 5 ? 2 : 1) || lev(w, x) <= (w.length > 5 ? 2 : 1); })); });
        if (all) { s = 90; fuzzy = true; }
      }
      if (!s && qt.every(function (w) { return w.length >= 4; })) { // description and material: «гемоглобин», «мазок»
        var more = sToks(a.d + " " + (a.bio === "Кровь из вены" ? "" : a.bio));
        if (qt.every(function (w) { return more.some(function (x) { return sWordHit(w, x); }); })) s = 70;
      }
      if (s) { add("a:" + code, { code: code, score: s - (a.pop || 30) / 100, fuzzy: fuzzy }); }
    });
    Object.keys(R).forEach(function (k) { var r = R[k]; if (r.page) out.p.push(r); else out.a.push(r); });
    function by(x, y) { return y.score - x.score; }
    out.p.sort(by); out.a.sort(by);
    // when there are good matches, guesses (typos, descriptions, short prefixes) are noise
    var best = Math.max(out.p.length ? out.p[0].score : 0, out.a.length ? out.a[0].score : 0);
    if (strong) { out.a = out.a.filter(function (x) { return x.dict || x.score >= 150; }); out.p = out.p.filter(function (x) { return x.dict || x.score >= 150; }); } // «сердце» ≠ «сердцевинный антиген»
    if (best >= 120) { out.a = out.a.filter(function (x) { return x.score >= 100; }); out.p = out.p.filter(function (x) { return x.score >= 100; }); }
    out.fuzzy = out.a.concat(out.p).some(function (x) { return x.fuzzy; });
    out.pagesFirst = out.p.length && (!out.a.length || out.p[0].score >= out.a[0].score);
    return out;
  }
  function sItemHTML(r, on) {
    if (r.page) return '<button type="button" data-go="' + esc(r.page.go) + '" class="s-page' + (on ? " on" : "") + '"><span class="s-name">' + esc(r.page.t) + '</span><span class="s-hint">' + esc(r.page.kind) + '</span><span class="s-price s-go-ic" aria-hidden="true">' + icon("i-right") + '</span></button>';
    if (r.cx) { var x = CX[r.code]; return '<button type="button" data-go="cx:' + r.code + '" class="' + (on ? "on" : "") + '"><span class="s-name">' + esc(CXX[r.code].n) + '</span><span class="s-hint">Чек-ап · ' + nAn(CXX[r.code].parts.length) + '</span><span class="s-price">' + rub(x.p) + "</span></button>"; }
    var a = A[r.code]; return '<button type="button" data-go="card:' + r.code + '" class="' + (on ? "on" : "") + '"><span class="s-name">' + esc(a.n) + '</span><span class="s-hint">' + esc(a.d || "Код " + r.code) + '</span><span class="s-price">' + rub(a.p) + "</span></button>";
  }
  function sGo(q) { return "poisk:" + encodeURIComponent(q.trim()); }
  function bindSearch(input, box) {
    var idx = -1, items = [];
    function render() {
      var q = input.value;
      if (!q.trim()) { box.hidden = true; items = []; return; }
      var r = search(q), pg = r.p.slice(0, 3), an = r.a.slice(0, r.p.length ? 5 : 6), groups = r.pagesFirst ? [["Страницы сайта", pg], ["Анализы", an]] : [["Анализы", an], ["Страницы сайта", pg]];
      items = []; var h = "";
      groups.forEach(function (g) { if (!g[1].length) return; if (pg.length && an.length) h += '<p class="s-grp">' + g[0] + "</p>"; g[1].forEach(function (x) { h += sItemHTML(x, items.length === idx); items.push(x); }); });
      var total = r.p.length + r.a.length;
      if (total) h += '<button type="button" class="s-all' + (idx === items.length ? " on" : "") + '" data-go="' + esc(sGo(q)) + '"><span class="s-name">Все результаты: ' + total + "</span><span class=\"s-price s-go-ic\" aria-hidden=\"true\">" + icon("i-right") + "</span></button>";
      if (total) items.push({ all: true });
      if (r.fuzzy) h += '<p class="fixnote">Показали похожие: исправили опечатку в запросе «' + esc(q) + "».</p>";
      if (!total) h = '<p class="s-empty">Ничего не нашли по запросу «' + esc(q) + '». Нажмите Enter: покажем, где ещё поискать.</p>' + (PAGES.indexOf("vybor-analiza") >= 0 ? '<button type="button" class="s-all" data-go="vybor-analiza"><span class="s-name">Не знаете, какой анализ нужен? Помощь в выборе</span><span class="s-price s-go-ic" aria-hidden="true">' + icon("i-right") + "</span></button>" : "");
      box.innerHTML = h; box.hidden = false;
    }
    input.addEventListener("input", function () { idx = -1; render(); });
    input.addEventListener("focus", function () {
      render();
      if (innerWidth > 960 || input.closest("#top")) return;
      var sw = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--sw-h"), 10) || 0;
      var y = input.getBoundingClientRect().top + scrollY - $("#top").offsetHeight - sw - 12;
      if (Math.abs(scrollY - y) > 4) window.scrollTo(0, Math.max(0, y));
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { // Enter = the list of all results; an item chosen with the arrows opens itself
        e.preventDefault();
        var it = idx >= 0 && items[idx];
        if (it && !it.all) go(it.page ? it.page.go : (it.cx ? "cx:" : "card:") + it.code);
        else if (input.value.trim()) { go(sGo(input.value)); input.blur(); }
        return;
      }
      if (box.hidden) return;
      if (e.key === "ArrowDown") { idx = Math.min(idx + 1, items.length - 1); render(); e.preventDefault(); }
      else if (e.key === "ArrowUp") { idx = Math.max(idx - 1, 0); render(); e.preventDefault(); }
      else if (e.key === "Escape") { box.hidden = true; }
    });
    document.addEventListener("click", function (e) { if (!e.target.closest(".search")) box.hidden = true; });
  }
  function renderSearchPage() {
    var q = state.q || "", r = search(q);
    PAGE_META.poisk = [q ? "Поиск: " + q : "Поиск по сайту", "Поиск анализов и страниц на сайте лаборатории CLD."];
    $("#q-top").value = q;
    $("#srp-crumb").textContent = q ? "Поиск: «" + q + "»" : "Поиск";
    $("#srp-h").textContent = q ? "Поиск: «" + q + "»" : "Поиск по сайту";
    var pg = r.p.slice(0, 12), cx = r.a.filter(function (x) { return x.cx; }).slice(0, 8), an = r.a.filter(function (x) { return !x.cx; }).slice(0, 40);
    var n = pg.length + cx.length + an.length;
    $("#srp-sub").textContent = n ? "Нашли: " + [pg.length ? plural(pg.length, ["страница", "страницы", "страниц"]) : "", cx.length ? plural(cx.length, ["чек-ап", "чек-апа", "чек-апов"]) : "", an.length ? nAn(an.length) : ""].filter(Boolean).join(", ") + "." : "";
    var secP = pg.length ? '<section class="srp-sec"><h2>Страницы сайта</h2><div class="rm-list">' + pg.map(function (x) { return '<button class="rm-link" type="button" data-go="' + esc(x.page.go) + '">' + icon("i-file") + "<span><b>" + esc(x.page.t) + "</b><small>" + esc(x.page.kind) + "</small></span></button>"; }).join("") + "</div></section>" : "";
    var secC = cx.length ? '<section class="srp-sec"><h2>Чек-апы</h2><div class="rm-list">' + cx.map(function (x) { var c = CXX[x.code]; return '<button class="rm-link rm-cx" type="button" data-go="cx:' + x.code + '">' + icon("i-lab") + "<span><b>" + esc(c.n) + "</b><small>" + nAn(c.parts.length) + '</small><span class="rm-pr"><b>' + rub(CX[x.code].p) + "</b></span></span></button>"; }).join("") + "</div></section>" : "";
    var codes = an.map(function (x) { return x.code; }), cm = codes.length ? commonOf(codes) : null;
    var secA = an.length ? '<section class="srp-sec"><h2>Анализы</h2><div class="rows">' + codes.map(function (c) { return row(c, cm); }).join("") + "</div></section>" : "";
    var empty = n ? "" : '<div class="srp-empty"><p>' + (q ? "По запросу «" + esc(q) + "» ничего не нашли. " : "") + "Попробуйте написать по-другому, например «анализ крови», «сахар», «глисты». Или выберите анализ по разделам:</p>" +
      '<div class="srp-alt"><button class="btn btn-lime" type="button" data-go="organs">По органам</button><button class="btn btn-ghost" type="button" data-go="povody">По поводу: справки, операция, бассейн</button><button class="btn btn-ghost" type="button" data-go="checkups">Чек-апы</button></div>' +
      (PAGES.indexOf("vybor-analiza") >= 0 ? '<p><button class="btn btn-navy" type="button" data-go="vybor-analiza">Помощь в выборе анализа</button></p>' : "") +
      '<p>Помощь в выборе анализа — по телефону <a class="num" href="tel:88002017830">8&nbsp;800&nbsp;201&nbsp;78&nbsp;30</a>, звонок бесплатный.</p></div>';
    $("#srp-body").innerHTML = empty + (r.pagesFirst ? secP + secC + secA : secC + secA + secP);
  }
'''

CSS = '''/* SEARCH CSS */
.sugg .s-hint, .sugg .s-empty, .fixnote { font-size: 16px; }
.sugg .s-grp { padding: 10px 12px 4px; font-size: 16px; font-weight: 700; color: var(--navy); }
.sugg .s-go-ic { color: var(--navy); display: flex; }
.sugg .s-go-ic .ico { width: 22px; height: 22px; }
.sugg .s-all { margin-top: 4px; border-top: 1px solid var(--line); border-radius: 0 0 8px 8px; }
.sugg .s-all .s-name { color: var(--navy); font-weight: 700; text-decoration: underline; text-underline-offset: 3px; }
.srp { padding-bottom: 72px; }
.srp h1 { margin: 18px 0 8px; font-size: clamp(32px, 4vw, 48px); overflow-wrap: anywhere; }
.srp-sub { font-size: 18px; color: var(--muted); }
.srp-sec { margin-top: 36px; }
.srp-sec h2 { margin-bottom: 14px; font-size: clamp(24px, 2.4vw, 30px); }
.srp-empty { margin-top: 24px; max-width: 760px; display: grid; gap: 18px; font-size: 18px; line-height: 1.5; }
.srp-alt { display: flex; flex-wrap: wrap; gap: 10px; }
.srp-empty a { font-weight: 700; color: var(--navy); }
/* SEARCH CSS END */
'''

VIEW = '''  <!-- SEARCH VIEW START -->
  <section id="v-poisk" data-view="poisk" hidden>
    <div class="wrap srp">
      <div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><span id="srp-crumb">Поиск</span></div>
      <h1 id="srp-h">Поиск по сайту</h1>
      <p class="srp-sub" id="srp-sub"></p>
      <div id="srp-body"></div>
    </div>
  </section>
  <!-- SEARCH VIEW END -->
'''


def swap(html: str, start: str, end: str, block: str, anchor: str | None = None, before: bool = True) -> str:
    """Replace the marked block, or insert it at the anchor on the first run."""
    if start in html:
        return re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end) + r'\n?', lambda m: block, html, count=1)
    assert anchor and html.count(anchor) == 1, f'anchor not unique: {anchor[:60]}'
    return html.replace(anchor, block + anchor if before else anchor + block, 1)


def patch(html: str, old: str, new: str, done_mark: str) -> str:
    if done_mark in html:
        return html
    assert html.count(old) == 1, f'not found once: {old[:70]}'
    return html.replace(old, new, 1)


def integrate(html: str) -> str:
    data = json.loads((ROOT / 'content/search/search.json').read_text())
    data.pop('_note', None)
    js = JS.replace('__DATA__', json.dumps(data, ensure_ascii=False))
    # 1. the old search(q) + bindSearch -> new ones (between the search helpers and the views)
    start, end = '  /* SEARCH START */', '  /* SEARCH END */'
    if start not in html:
        m = re.search(r'  function search\(q\) \{[\s\S]*?(?=  // ---------- views ----------)', html)
        assert m, 'old search block not found'
        html = html[:m.start()] + start + '\n' + end + '\n\n' + html[m.end():]
    html = swap(html, start, end, start + js + end + '\n')
    # 2. results view and styles
    html = swap(html, '  <!-- SEARCH VIEW START -->', '  <!-- SEARCH VIEW END -->', VIEW, '  <!-- SITUATIONS VIEWS START -->')
    html = swap(html, '/* SEARCH CSS */', '/* SEARCH CSS END */', CSS, '/* SITUATIONS CSS */')
    # 3. router: #poisk-<query>
    html = patch(html, '    else if (PAGES.indexOf(v) >= 0) state.view = v;',
                 '    else if (v === "poisk") { state.view = "poisk"; try { state.q = decodeURIComponent(p[1] || ""); } catch (err) { if (!(err instanceof URIError)) throw err; state.q = p[1] || ""; } } // search results\n'
                 '    else if (PAGES.indexOf(v) >= 0) state.view = v;', 'state.view = "poisk"')
    html = patch(html, '    var hash = state.view === "lk" ? lkHash()',
                 '    var hash = state.view === "poisk" ? "poisk-" + encodeURIComponent(state.q || "") : state.view === "lk" ? lkHash()', '"poisk-" + encodeURIComponent')
    html = patch(html, '    else if (h.indexOf("povod-") === 0)',
                 '    else if (h.indexOf("poisk-") === 0) go("poisk:" + h.slice(6), false);\n    else if (h.indexOf("povod-") === 0)', 'go("poisk:" + h.slice(6)')
    html = patch(html, '  window.CLD_PROTO = {', '  RENDER.poisk = renderSearchPage; NAVOF.poisk = "catalog"; // search results view\n  window.CLD_PROTO = {', 'RENDER.poisk = renderSearchPage')
    # 4. the «Найти» button opens the results list, not the first card
    html = patch(html, 'var best = si.value.trim() && search(si.value)[0]; if (best) go("card:" + best.code); else si.focus(); return;',
                 'if (si.value.trim()) go(sGo(si.value)); else si.focus(); return;', 'go(sGo(si.value))')
    return html


if __name__ == '__main__':
    path = ROOT / 'v4/index.html'
    path.write_text(integrate(path.read_text()))
    print('Search: dictionary, pages and results view integrated.')
