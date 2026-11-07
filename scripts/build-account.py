"""Личный кабинет пациента (#lk-…) — демо-кабинет по описи кабинета lab.discript.ru (07.11.2026): записи и результаты,
бланк результата, деталь заказа, оплаты, сертификаты и баланс, уведомления, семья, профиль, смена пароля, привязка e-mail.
Данные — content/account/account.json. Вход: «Войти» → телефон и код из SMS (#results) → кабинет; прямая ссылка #lk-… открывает
кабинет сразу (демо). Состояния для проверки: #lk-empty (новый пациент), #lk-gate (подтверждение входа к результатам),
#lk-nocard (карты пациента в лаборатории нет), #lk-full (обратно). Идемпотентно. Запускать последним."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

MARKUP = '''  <!-- LK VIEW START -->
  <section id="v-lk" data-view="lk" hidden>
    <div class="wrap lk">
      <div class="crumbs" id="lk-crumbs"></div>
      <div class="lk-grid">
        <aside class="lk-side" id="lk-side" aria-label="Личный кабинет"></aside>
        <div class="lk-main" id="lk-main"></div>
      </div>
    </div>
    <dialog class="lk-dlg" id="lk-dlg" aria-labelledby="lk-dlg-h"></dialog>
  </section>
  <!-- LK VIEW END -->
'''

ICONS = '''  <symbol id="i-bell" viewBox="0 0 24 24"><path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4Z"/><path d="M10 20.5a2 2 0 0 0 4 0"/></symbol>
  <symbol id="i-logout" viewBox="0 0 24 24"><path d="M10 4H5v16h5"/><path d="m15 8 4 4-4 4M19 12H9"/></symbol>
  <symbol id="i-key" viewBox="0 0 24 24"><circle cx="8" cy="15" r="4"/><path d="m11 12 8-8M16 7l2 2M14 9l2 2"/></symbol>
  <symbol id="i-up" viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6"/></symbol>
  <symbol id="i-dn" viewBox="0 0 24 24"><path d="M12 5v14M6 13l6 6 6-6"/></symbol>
  <symbol id="i-repeat" viewBox="0 0 24 24"><path d="M4 12a8 8 0 0 1 14-5.3M20 12a8 8 0 0 1-14 5.3"/><path d="M18 3v4h-4M6 21v-4h4"/></symbol>
  <symbol id="i-card" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h4"/></symbol>
'''

JS = r'''  /* LK START */
  var LK = __DATA__;
  PAGES.push("lk"); NAVOF.lk = "results";
  var LK_MON = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];
  // статус: подпись фильтра, подпись метки, значок, класс
  var LK_ST = { upcoming: ["Предстоящие", "Запланирован", "i-cal", "up"], paid: ["Оплачен", "Оплачен", "i-check", "up"], wait: ["Ожидает оплаты", "Ожидает оплаты", "i-card", "wait"], work: ["В работе", "В работе", "i-clock", "work"], done: ["Завершён", "Визит состоялся", "i-check", "done"], cancel: ["Отменён", "Отменён", "i-x", "off"] };
  var LK_PREP_RANK = { "Н12": 5, "Н8": 4, "О": 4, "Г": 3, "Е3": 2, "К": 1 };
  var LK_NAV = [["orders", "Записи и результаты", "i-file"], ["invoices", "Оплаты", "i-card"], ["certs", "Сертификаты и баланс", "i-gift"], ["notifications", "Уведомления", "i-bell"], ["family", "Семья", "i-users"], ["profile", "Профиль", "i-user"]];
  var LK_PARENT = { results: "orders", order: "orders", result: "orders", password: "profile", email: "profile" };
  var LK_TITLE = { orders: "Записи и результаты", results: "Записи и результаты", order: "Заказ", result: "Результат анализа", invoices: "Оплаты", certs: "Сертификаты и баланс", notifications: "Уведомления", family: "Семья", profile: "Профиль", password: "Новый пароль", email: "Привязка e-mail" };
  var lk = { sub: "orders", id: "", mode: "full", filter: "all", who: "me", certf: "all", hist: false, gate: 0, resch: false, rd: null, rt: "", data: null, pending: null };

  function lkD() {
    if (lk.data) return lk.data;
    var d = JSON.parse(JSON.stringify(LK));
    if (lk.mode === "empty") { d.family = []; d.orders = []; d.results = []; d.invoices = []; d.certs = []; d.notes = []; d.wallet = { balance: 0, hist: [] }; d.patient.email = ""; }
    return (lk.data = d);
  }
  function lkDate(off) { var d = new Date(); d.setHours(12, 0, 0, 0); d.setDate(d.getDate() + off); return d; }
  function lkLong(off) { return lkDate(off).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" }).replace(/\s?г\.$/, ""); }
  function lkShort(off) { return lkDate(off).toLocaleDateString("ru-RU"); }
  function lkRel(off) { return off === 0 ? "сегодня" : off === -1 ? "вчера" : off === 1 ? "завтра" : lkLong(off); }
  function lkIso(ru) { var p = (ru || "").split("."); return p.length === 3 ? p[2] + "-" + p[1] + "-" + p[0] : ""; }
  function lkRu(iso) { var p = (iso || "").split("-"); return p.length === 3 ? p[2] + "." + p[1] + "." + p[0] : ""; }
  function lkWho(id) { return lkD().family.filter(function (f) { return f.id === id; })[0] || null; }
  function lkOrder(id) { return lkD().orders.filter(function (o) { return o.id === id; })[0]; }
  function lkResult(id) { return lkD().results.filter(function (r) { return r.id === id; })[0]; }
  function lkFull(p) { return p.last + " " + p.first + (p.mid ? " " + p.mid : ""); }
  function lkSum(o) { // цена выбранного пункта, скидка при оплате онлайн, взятие крови — без скидки
    var s = 0, blood = false;
    o.codes.forEach(function (c) { var it = item(c); s += it.p; if (it.blood) blood = true; });
    return { s: s, off: s - online(s), blood: blood, total: online(s) + (blood ? BLOOD_DRAW : 0) };
  }
  function lkPrep(codes) { // самое строгое общее правило + особые (ПСА, моча)
    var best = "", special = [];
    codes.forEach(function (c) { var k = DPREP[c]; if (!k) return; if (LK_PREP_RANK[k]) { if (!best || LK_PREP_RANK[k] > LK_PREP_RANK[best]) best = k; } else if (special.indexOf(k) < 0) special.push(k); });
    return (best ? [best] : []).concat(special);
  }
  function lkFlag(v, ref) { // сравнение с референсным интервалом лаборатории; категории риска («оптимальный: …») не размечаем
    function n(s) { return parseFloat(s.replace(",", ".")); }
    var x = n(String(v)), m;
    if (isNaN(x) || ref.indexOf(":") >= 0) return "";
    if ((m = ref.match(/^([\d,.]+)\s*-\s*([\d,.]+)$/))) return x < n(m[1]) ? "low" : x > n(m[2]) ? "high" : "";
    if ((m = ref.match(/^<\s*([\d,.]+)$/))) return x >= n(m[1]) ? "high" : "";
    if ((m = ref.match(/^>\s*([\d,.]+)$/))) return x <= n(m[1]) ? "low" : "";
    return "";
  }
  function lkTag(st) { var s = LK_ST[st]; return '<span class="lk-tag lk-' + s[3] + '">' + icon(s[2]) + s[1] + "</span>"; }
  function lkHead(h1, lede, acts) { return '<div class="lk-head"><div><h1>' + h1 + "</h1>" + (lede ? '<p class="lk-lede">' + typo(lede) + "</p>" : "") + "</div>" + (acts ? '<div class="lk-acts">' + acts + "</div>" : "") + "</div>"; }
  function lkEmpty(ic, h, p, btn) { return '<div class="lk-empty">' + icon(ic) + "<h2>" + h + "</h2>" + (p ? "<p>" + typo(p) + "</p>" : "") + (btn || "") + "</div>"; }
  function lkBack(go, label) { return '<button class="lk-back" type="button" data-go="' + go + '">' + icon("i-left") + label + "</button>"; }
  function lkHeader() { // «Войти» в шапке → имя пациента, ведёт в кабинет
    var a = $(".s-login"); if (!a) return;
    var on = res.step === "in";
    a.setAttribute("href", on ? "#lk-orders" : "#results"); a.dataset.go = on ? "lk:orders" : "results";
    a.querySelector("span").textContent = on ? lkD().patient.first : "Войти";
    a.setAttribute("aria-label", on ? "Личный кабинет" : "Войти в личный кабинет");
  }

  function lkRoute(p) {
    var m = { empty: 1, full: 1, gate: 1, nocard: 1 }[p[0]] ? p[0] : "";
    if (m) { lk.mode = m; lk.data = null; lk.gate = 0; lk.filter = "all"; lk.who = "me"; lk.certf = "all"; p = [m === "gate" || m === "nocard" ? "results" : "orders"]; }
    if (lk.sub !== p[0] || lk.id !== (p[1] || "")) { lk.resch = false; lk.rd = null; lk.rt = ""; }
    lk.sub = LK_TITLE[p[0]] ? p[0] : "orders"; lk.id = p[1] || "";
    if (res.step !== "in") { res.step = "in"; res.phone = res.phone || lkD().patient.phone; } // демо: кабинет открывается сразу
  }
  function lkHash() { return "lk-" + lk.sub + (lk.id ? "-" + lk.id : ""); }

  function lkSide() {
    var d = lkD(), p = d.patient, cur = LK_PARENT[lk.sub] || lk.sub, unread = d.notes.filter(function (n) { return !n.read; }).length;
    return '<div class="lk-me"><span class="lk-ava" aria-hidden="true">' + esc(p.first.charAt(0) + p.last.charAt(0)) + "</span><span><b>" + esc(p.first + " " + p.last) + '</b><small class="num">' + esc(p.phone) + "</small></span></div>" +
      '<nav class="lk-nav" aria-label="Разделы кабинета">' + LK_NAV.map(function (n) {
        var badge = n[0] === "notifications" && unread ? '<span class="lk-badge num">' + unread + '<span class="vh"> новых</span></span>' : "";
        return '<a href="#lk-' + n[0] + '" data-go="lk:' + n[0] + '"' + (cur === n[0] ? ' aria-current="page"' : "") + ">" + icon(n[2]) + "<span>" + n[1] + "</span>" + badge + "</a>";
      }).join("") + "</nav>" +
      '<button class="lk-out" type="button" data-lk="logout">' + icon("i-logout") + "Выйти</button>";
  }
  function lkCrumbs() {
    var parent = LK_PARENT[lk.sub], html = '<button type="button" data-go="home">Главная</button><span>/</span>';
    if (lk.sub === "orders" || lk.sub === "results") return html + "<span>Личный кабинет</span>";
    html += '<button type="button" data-go="lk:orders">Личный кабинет</button><span>/</span>';
    if (parent && parent !== "orders") html += '<button type="button" data-go="lk:' + parent + '">' + LK_TITLE[parent] + "</button><span>/</span>";
    if (lk.sub === "result") html += '<button type="button" data-go="lk:results">Результаты</button><span>/</span>';
    return html + "<span>" + (lk.sub === "order" && lkOrder(lk.id) ? "Заказ " + lkOrder(lk.id).no : LK_TITLE[lk.sub]) + "</span>";
  }

  // ---------- записи и результаты ----------
  function lkOrders() {
    var tabs = '<nav class="lk-tabs" aria-label="Записи или результаты">' + [["orders", "Записи", "i-cal"], ["results", "Результаты", "i-file"]].map(function (t) {
      return '<a href="#lk-' + t[0] + '" data-go="lk:' + t[0] + '"' + (lk.sub === t[0] ? ' aria-current="page"' : "") + ">" + icon(t[2]) + t[1] + "</a>";
    }).join("") + "</nav>";
    return lkHead("Записи и результаты", lk.sub === "orders" ? "Записи в пункты CLD и заказы с сайта." : "Готовые бланки результатов и анализы, которые ещё выполняются.") + tabs + (lk.sub === "results" ? lkResultsList() : lkOrdersList());
  }
  function lkOrdersList() {
    var os = lkD().orders;
    if (!os.length) return lkEmpty("i-file", "Заказов пока нет", "Оформите первый заказ — здесь появятся запись, оплата и результаты.", '<button class="btn btn-lime" type="button" data-go="catalog:blood">Перейти в каталог</button>');
    var next = os.filter(function (o) { return o.st === "upcoming" && o.day != null && o.day >= 0; }).sort(function (a, b) { return a.day - b.day; })[0];
    var counts = {}; os.forEach(function (o) { counts[o.st] = (counts[o.st] || 0) + 1; });
    if (lk.filter !== "all" && !counts[lk.filter]) lk.filter = "all";
    var chips = '<div class="lk-chips" role="group" aria-label="Показать записи">' + [["all", "Все", os.length]].concat(Object.keys(LK_ST).filter(function (k) { return counts[k]; }).map(function (k) { return [k, LK_ST[k][0], counts[k]]; })).map(function (c) {
      return '<button class="chip" type="button" data-lk="filter:' + c[0] + '" aria-pressed="' + (lk.filter === c[0]) + '">' + c[1] + ' <span class="n num">' + c[2] + "</span></button>";
    }).join("") + "</div>";
    var list = os.filter(function (o) { return lk.filter === "all" || o.st === lk.filter; });
    return (next && lk.filter === "all" ? lkNext(next) : "") + chips + '<div class="lk-list">' + list.map(lkOrderCard).join("") + "</div>";
  }
  function lkNext(o) {
    var pt = POINTS[o.pt], prep = lkPrep(o.codes), d = lkDate(o.day);
    return '<section class="lk-next" aria-labelledby="lk-next-h"><div class="lk-next-when"><b class="num">' + d.getDate() + "</b><span>" + LK_MON[d.getMonth()] + '</span><small class="num">' + o.time + "</small></div>" +
      '<div><h2 id="lk-next-h">Ближайший визит — ' + lkRel(o.day) + "</h2><p>" + esc(ptName(pt)) + " · " + ptHours(pt) + "</p>" +
      (prep.length ? '<p class="lk-next-prep">' + icon("i-info") + "<span>Подготовка: " + prep.map(function (k) { return esc(PREPL[k]).toLowerCase(); }).join("; ") + "</span></p>" : "") +
      '<div class="lk-next-acts"><button class="btn btn-lime" type="button" data-go="lk:order:' + o.id + '">Детали и подготовка</button>' +
      (pt.lat != null ? '<a class="btn lk-btn-on" href="https://yandex.ru/maps/?rtext=~' + pt.lat + "," + pt.lng + '" target="_blank" rel="noopener">' + icon("i-pin") + "Маршрут</a>" : "") + "</div></div></section>";
  }
  function lkOrderCard(o) {
    var who = lkWho(o.who), dd = o.day != null ? lkDate(o.day) : null, s = lkSum(o), names = o.codes.map(function (c) { return item(c).n; });
    var when = dd ? '<div class="lk-when"><b class="num">' + dd.getDate() + "</b><span>" + LK_MON[dd.getMonth()] + '</span><small class="num">' + o.time + "</small></div>" : '<div class="lk-when lk-when-no">' + icon("i-cal") + "<span>Без записи</span></div>";
    var acts = '<button class="btn btn-ghost" type="button" data-go="lk:order:' + o.id + '">Подробнее</button>';
    if (o.st === "wait") acts = '<button class="btn btn-lime" type="button" data-lk="pay:' + o.id + '">' + icon("i-card") + "Оплатить</button>" + acts;
    if (o.st === "done" && o.res) acts = '<button class="btn btn-navy" type="button" data-go="lk:result:' + o.res[0] + '">' + icon("i-file") + "Результат</button>" + acts;
    return '<article class="lk-card lk-ord' + (o.st === "cancel" ? " is-off" : "") + '">' + when +
      '<div class="lk-ord-body"><div class="lk-ord-h"><h3><a href="#lk-order-' + o.id + '" data-go="lk:order:' + o.id + '">Заказ <span class="num">' + o.no + "</span></a></h3>" + lkTag(o.st) + "</div>" +
      (who ? '<p class="lk-meta">' + icon("i-user") + "Для: " + esc(who.first + " " + who.last) + "</p>" : "") +
      '<ul class="lk-items">' + names.slice(0, 3).map(function (n) { return "<li>" + esc(n) + "</li>"; }).join("") + (names.length > 3 ? '<li class="lk-more">и ещё ' + nAn(names.length - 3) + "</li>" : "") + "</ul>" +
      '<p class="lk-meta">' + icon("i-pin") + esc(ptName(POINTS[o.pt])) + "</p></div>" +
      '<div class="lk-ord-side"><b class="num">' + rub(s.total) + '</b><div class="lk-ord-acts">' + acts + "</div></div></article>";
  }
  function lkResultsList() {
    var d = lkD();
    if (lk.mode === "nocard") return '<div class="lk-empty">' + icon("i-info") + "<h2>Карта пациента не найдена</h2><p>" + typo("В лаборатории пока нет медицинской карты с вашим номером телефона. Её заводят в пункте CLD при первом визите.") + "</p><p>" + typo("После первого визита результаты появятся здесь сами — при следующем входе в кабинет.") + "</p></div>";
    if (lk.mode === "gate" && lk.gate < 3) return lkGate();
    if (!d.results.length) return lkEmpty("i-file", "Результатов пока нет", "Когда лаборатория выполнит анализ, бланк появится здесь, а мы пришлём уведомление.");
    var people = [{ id: "me", n: d.patient.first + " (вы)", ok: true }].concat(d.family.map(function (f) { return { id: f.id, n: f.first, ok: f.res }; }));
    var who = people.length > 1 ? '<div class="lk-chips" role="group" aria-label="Чьи результаты показать">' + people.map(function (p) {
      return '<button class="chip" type="button" data-lk="who:' + p.id + '" aria-pressed="' + (lk.who === p.id) + '"' + (p.ok ? "" : " disabled") + ">" + esc(p.n) + (p.ok ? "" : " · нет доступа") + "</button>";
    }).join("") + "</div>" : "";
    var list = d.results.filter(function (r) { return r.who === lk.who; });
    return who + (list.length ? '<div class="lk-list">' + list.map(lkResultCard).join("") + "</div>" : '<p class="lk-none">Результатов пока нет.</p>') +
      (people.some(function (p) { return !p.ok; }) ? '<p class="lk-hint">' + typo("Чтобы видеть результаты родственника, подключите доступ в разделе «Семья».") + ' <button class="linkbtn" type="button" data-go="lk:family">Открыть «Семью»</button></p>' : "");
  }
  function lkResultCard(r) {
    var o = lkOrder(r.ord), ready = r.st === "ready";
    var meta = ready ? lkLong(r.day) + " · " + plural(r.rows.length, ["показатель", "показателя", "показателей"]) : "Будет готов " + lkRel(r.day + (r.ready || 1));
    return '<article class="lk-card lk-res"><div class="lk-res-ic' + (ready ? "" : " is-work") + '">' + icon(ready ? "i-file" : "i-clock") + "</div>" +
      '<div><div class="lk-ord-h"><h3>' + (ready ? '<a href="#lk-result-' + r.id + '" data-go="lk:result:' + r.id + '">' + esc(r.name) + "</a>" : esc(r.name)) + "</h3>" +
      (ready ? '<span class="lk-tag lk-done">' + icon("i-check") + "Готов</span>" : lkTag("work")) + '</div><p class="lk-meta">' + meta + ' · заказ <span class="num">' + o.no + "</span></p></div>" +
      (ready ? '<div class="lk-ord-acts"><button class="btn btn-navy" type="button" data-go="lk:result:' + r.id + '">Открыть бланк</button><button class="btn btn-ghost" type="button" data-lk="pdf:' + r.id + '">' + icon("i-down") + "PDF</button></div>" : "") + "</article>";
  }
  function lkGate() {
    var d = lkD();
    if (lk.gate < 2) return '<form class="lk-card lk-form lk-gate" data-form="lk-gate1" novalidate><h2>Подтвердите вход к результатам</h2><p>' +
      typo("Результаты хранятся в медицинской системе лаборатории. Мы отправили логин и пароль от неё на " + (d.patient.email || "ваш e-mail") + ". Введите их ниже.") + "</p>" +
      '<label class="fld"><span>Логин из письма</span><input name="login" autocomplete="username"></label><label class="fld"><span>Пароль из письма</span><input name="pw" type="password" autocomplete="current-password"></label>' +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">Продолжить</button></div></form>';
    return '<form class="lk-card lk-form lk-gate" data-form="lk-gate2" novalidate><h2>Код из SMS</h2><p>Отправили 4-значный код на номер <b class="num">' + esc(d.patient.phone) + "</b>.</p>" +
      '<label class="fld"><span>Код из SMS</span><input name="code" inputmode="numeric" autocomplete="one-time-code" maxlength="4" placeholder="0000"></label>' +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">Подтвердить</button><button class="btn btn-ghost" type="button" data-lk="gateback">Назад</button></div></form>';
  }

  // ---------- бланк результата ----------
  function lkResultPage() {
    var r = lkResult(lk.id);
    if (!r || r.st !== "ready") return lkBack("lk:results", "Все результаты") + lkEmpty("i-file", "Результат не найден", "Возможно, ссылка устарела. Все готовые бланки — в разделе «Результаты».");
    var o = lkOrder(r.ord), p = lkWho(r.who) || lkD().patient, nflag = 0;
    var rows = r.rows.map(function (x) {
      var fl = lkFlag(x[1], x[3]), ref = x[3].indexOf(":") >= 0 ? x[3].split(/;\s*/).map(function (s) { var i = s.indexOf(":"); return "<span>" + esc(s.slice(0, i + 1)) + ' <span class="nw">' + esc(s.slice(i + 1).trim()) + "</span></span>"; }).join("") : '<span class="nw">' + esc(x[3]) + "</span>";
      if (fl) nflag++;
      return "<tr" + (fl ? ' class="is-flag"' : "") + '><th scope="row">' + esc(x[0]) + '</th><td class="lk-v"><b class="num">' + esc(x[1]) + "</b>" +
        (fl ? '<span class="lk-flag">' + icon(fl === "high" ? "i-up" : "i-dn") + (fl === "high" ? "выше" : "ниже") + " интервала</span>" : "") +
        (x[4] ? '<small>ранее <span class="num">' + esc(x[4]) + "</span> · " + lkShort(x[5]) + "</small>" : "") +
        '</td><td class="lk-u">' + esc(x[2]) + '</td><td class="lk-ref"><span class="vh">Референсный интервал: </span>' + ref + "</td></tr>";
    }).join("");
    function facts(list, cls) { return '<dl class="lk-facts' + (cls || "") + '">' + list.map(function (x) { return "<div><dt>" + x[0] + "</dt><dd>" + esc(x[1]) + "</dd></div>"; }).join("") + "</dl>"; }
    return lkBack("lk:results", "Все результаты") +
      lkHead(esc(r.name), lkLong(r.day) + " · заказ " + o.no, '<button class="btn btn-navy" type="button" data-lk="pdf:' + r.id + '">' + icon("i-down") + "Скачать PDF</button>") +
      facts([["Пациент", lkFull(p)], ["Дата рождения", p.birth], ["Пол", p.sex], ["№ заявки", r.no], ["Образец поступил", lkShort(r.day)], ["Пункт", ptName(POINTS[o.pt])]]) +
      (nflag ? '<p class="lk-sum">' + icon("i-info") + "<span>" + typo(plural(nflag, ["показатель", "показателя", "показателей"]) + " вне референсного интервала лаборатории. Это не диагноз: результат оценивает врач вместе с жалобами и другими обследованиями.") + "</span></p>" : "") +
      '<div class="lk-blank"><table><caption class="vh">' + esc(r.name) + '</caption><thead><tr><th scope="col">Показатель</th><th scope="col">Результат</th><th scope="col">Ед. изм.</th><th scope="col">Референсный интервал</th></tr></thead><tbody>' + rows + "</tbody></table></div>" +
      facts([["Биоматериал", r.bio], ["Оборудование", r.device], ["Исследование выполнил", r.by], ["Дата выполнения", lkShort(r.day)]], " lk-facts-foot") +
      '<p class="lk-note">' + typo("Референсный интервал — диапазон, в который попадает результат у большинства здоровых людей. Он зависит от метода, пола и возраста, поэтому у разных лабораторий может отличаться. Для интерпретации результатов обратитесь к врачу.") + "</p>";
  }

  // ---------- заказ ----------
  function lkOrderPage() {
    var o = lkOrder(lk.id);
    if (!o) return lkBack("lk:orders", "Все записи") + lkEmpty("i-file", "Заказ не найден", "Возможно, ссылка устарела. Все заказы — в разделе «Записи и результаты».");
    var pt = POINTS[o.pt], s = lkSum(o), who = lkWho(o.who), live = o.st === "upcoming" || o.st === "wait" || o.st === "paid";
    var acts = (o.st === "wait" ? '<button class="btn btn-lime" type="button" data-lk="pay:' + o.id + '">' + icon("i-card") + "Оплатить " + rub(s.total) + "</button>" : "") +
      '<button class="btn btn-ghost" type="button" data-lk="repeat:' + o.id + '">' + icon("i-repeat") + "Повторить заказ</button>" +
      (live ? '<button class="btn btn-ghost" type="button" data-lk="cancel:' + o.id + '">' + icon("i-x") + "Отменить</button>" : "");
    var when = o.day != null ? "<b>" + lkLong(o.day) + ', <span class="num">' + o.time + "</span></b>" : "<b>Без записи на время</b><p>" + typo("Приходите в часы работы пункта.") + "</p>";
    var band = '<div class="lk-band"><div><h2>Визит</h2>' + when + (o.st === "upcoming" ? '<button class="linkbtn" type="button" data-lk="resch" aria-expanded="' + lk.resch + '">Перенести</button>' : "") + "</div>" +
      "<div><h2>Пункт</h2><b>" + esc(ptName(pt)) + "</b><p>" + ptHours(pt) + "</p>" + (pt.lat != null ? '<a class="linkbtn" href="https://yandex.ru/maps/?rtext=~' + pt.lat + "," + pt.lng + '" target="_blank" rel="noopener">Маршрут</a>' : "") + "</div>" +
      "<div><h2>Оплата</h2><b>" + (o.paid ? "Оплачено онлайн" : o.st === "cancel" ? "Не оплачен" : "Ожидает оплаты") + '</b><p class="num">' + rub(s.total) + "</p></div></div>";
    var html = lkBack("lk:orders", "Все записи") + lkHead('Заказ <span class="num">' + o.no + "</span> " + lkTag(o.st), "Оформлен " + lkLong(o.created) + (who ? " · для: " + who.first + " " + who.last : ""), acts) + band + (lk.resch ? lkResch() : "");
    if (o.res) html += '<section class="lk-sec"><h2>Результаты</h2><div class="lk-list">' + o.res.map(function (id) { return lkResultCard(lkResult(id)); }).join("") + "</div></section>";
    if (o.st === "upcoming" || o.st === "paid") {
      var prep = lkPrep(o.codes);
      if (prep.length) html += '<section class="lk-sec"><h2>Как подготовиться</h2><div class="lk-prep">' + prep.map(function (k) { return "<div><h3>" + esc(PREPL[k]) + "</h3>" + prepList(k) + "</div>"; }).join("") + PP_LINK + "</div></section>";
    }
    html += '<section class="lk-sec"><h2>Анализы в заказе</h2><ul class="lk-lines">' + o.codes.map(function (c) {
      return '<li><a href="#card-' + c + '" data-go="card:' + c + '">' + esc(item(c).n) + '</a><span class="num">' + c + '</span><b class="num">' + rub(item(c).p) + "</b></li>";
    }).join("") + (s.blood ? '<li><span>Взятие крови из вены</span><span></span><b class="num">' + rub(BLOOD_DRAW) + "</b></li>" : "") + "</ul>" +
      '<dl class="lk-total"><div><dt>Анализы</dt><dd class="num">' + rub(s.s) + '</dd></div><div><dt>Скидка при оплате онлайн</dt><dd class="num">−' + rub(s.off) + "</dd></div>" +
      (s.blood ? '<div><dt>Взятие крови</dt><dd class="num">' + rub(BLOOD_DRAW) + "</dd></div>" : "") + '<div class="t"><dt>Итого</dt><dd class="num">' + rub(s.total) + "</dd></div></dl></section>";
    html += '<section class="lk-sec"><h2>История заказа</h2><ol class="lk-hist">' + o.hist.map(function (h) { return '<li><time class="num">' + lkShort(h[0]) + ", " + h[1] + "</time><span>" + esc(h[2]) + "</span></li>"; }).join("") + "</ol></section>";
    return html;
  }
  function lkResch() {
    var days = [], times = ["07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00"];
    for (var i = 2; i <= 8; i++) days.push(i); // перенос — не раньше чем через сутки
    return '<div class="lk-resch"><h2>Новая дата и время</h2><div class="lk-chips" role="group" aria-label="День">' + days.map(function (i) {
      var d = lkDate(i); return '<button class="chip" type="button" data-lk="rd:' + i + '" aria-pressed="' + (lk.rd === i) + '">' + d.toLocaleDateString("ru-RU", { weekday: "short", day: "numeric", month: "short" }) + "</button>";
    }).join("") + '</div><div class="lk-chips" role="group" aria-label="Время">' + times.map(function (t) {
      return '<button class="chip num" type="button" data-lk="rt:' + t.replace(":", "") + '" aria-pressed="' + (lk.rt === t) + '"' + (lk.rd == null ? " disabled" : "") + ">" + t + "</button>";
    }).join("") + '</div><div class="lk-form-acts"><button class="btn btn-lime" type="button" data-lk="rsave"' + (lk.rd != null && lk.rt ? "" : " disabled") + '>Перенести визит</button><button class="btn btn-ghost" type="button" data-lk="resch">Отмена</button></div></div>';
  }

  // ---------- оплаты ----------
  function lkInvoices() {
    var d = lkD(), h = lkHead("Оплаты", "Счета за заказы и подарочные сертификаты.");
    if (!d.invoices.length) return h + lkEmpty("i-card", "Оплат пока нет", "Здесь появятся счета после первого заказа.", '<button class="btn btn-lime" type="button" data-go="catalog:blood">Перейти в каталог</button>');
    return h + '<div class="lk-tblw"><table class="lk-tbl"><thead><tr><th scope="col">Счёт</th><th scope="col">Дата</th><th scope="col">За что</th><th scope="col">Сумма</th><th scope="col">Статус</th></tr></thead><tbody>' + d.invoices.map(function (v) {
      var o = v.ord ? lkOrder(v.ord) : null, c = v.cert ? d.certs.filter(function (x) { return x.id === v.cert; })[0] : null;
      var paid = o ? o.paid : v.paid, sum = o ? lkSum(o).total : v.sum;
      var what = o ? 'Заказ <a class="num" href="#lk-order-' + o.id + '" data-go="lk:order:' + o.id + '">' + o.no + "</a>" : "Подарочный сертификат" + (c ? "<small>для: " + esc(c.owner) + "</small>" : "");
      var st = paid ? '<span class="lk-tag lk-done">' + icon("i-check") + "Оплачен</span>" : o && o.st === "cancel" ? lkTag("cancel") : '<button class="btn btn-lime" type="button" data-lk="pay:' + o.id + '">Оплатить</button>';
      return '<tr><td class="num">№ ' + v.no + '</td><td class="num">' + lkShort(v.day) + "</td><td>" + what + '</td><td class="num">' + rub(sum) + "</td><td>" + st + "</td></tr>";
    }).join("") + "</tbody></table></div>";
  }

  // ---------- сертификаты и баланс ----------
  function lkCerts() {
    var d = lkD(), w = d.wallet;
    var hist = '<ul class="lk-bal-hist" id="lk-bal-hist">' + (w.hist.length ? w.hist.map(function (x) {
      return "<li><span><b>" + x.t + "</b><small>" + esc(x.s) + " · " + lkShort(x.day) + '</small></span><b class="num' + (x.n > 0 ? " plus" : "") + '">' + (x.n > 0 ? "+" : "−") + rub(Math.abs(x.n)) + "</b></li>";
    }).join("") : "<li><span>Операций за последние 12 месяцев нет.</span></li>") + "</ul>";
    var bal = '<section class="lk-bal" aria-label="Баланс"><div class="lk-bal-sum">' + icon("i-wallet") + '<span>Баланс</span><b class="num">' + rub(w.balance) + "</b><p>" + typo("Сертификаты пополняют баланс. Им можно оплатить анализы, чек-апы и выезд на дом.") + "</p></div>" +
      '<div class="lk-bal-acts"><button class="btn lk-btn-on" type="button" data-lk="hist" aria-expanded="' + lk.hist + '" aria-controls="lk-bal-hist">История</button><button class="btn btn-lime" type="button" data-go="gifts">' + icon("i-gift") + "Купить сертификат</button></div>" + (lk.hist ? hist : "") + "</section>";
    var h = lkHead("Сертификаты и баланс", "Подарочные сертификаты, которые вы получили или подарили.");
    if (!d.certs.length) return h + bal + lkEmpty("i-gift", "Сертификатов пока нет", "Подаренный вам сертификат сразу пополнит баланс, а купленные вами — появятся здесь.");
    var mine = d.certs.filter(function (c) { return c.role === "owner"; }).length, gift = d.certs.length - mine;
    var chips = '<div class="lk-chips" role="group" aria-label="Какие сертификаты показать">' + [["all", "Все", d.certs.length], ["owner", "Мои", mine], ["buyer", "Подаренные", gift]].map(function (c) {
      return '<button class="chip" type="button" data-lk="certf:' + c[0] + '" aria-pressed="' + (lk.certf === c[0]) + '">' + c[1] + ' <span class="n num">' + c[2] + "</span></button>";
    }).join("") + "</div>";
    var list = d.certs.filter(function (c) { return lk.certf === "all" || c.role === lk.certf; });
    return h + bal + chips + '<div class="lk-list">' + (list.length ? list.map(function (c) {
      return '<article class="lk-card lk-cert"><div class="lk-cert-face"><img src="../assets/cld-logo-horizontal-navy.svg" alt="" width="1778" height="276"><b class="num">' + rub(c.nominal) + "</b></div>" +
        '<div><div class="lk-ord-h"><h3>' + esc(c.owner) + '</h3><span class="lk-tag ' + (c.role === "owner" ? "lk-done" : "lk-work") + '">' + (c.role === "owner" ? "Вы получатель" : "Вы подарили") + "</span></div>" +
        '<p class="lk-meta num">' + esc(c.code) + " · " + (c.role === "owner" ? "получен " : "куплен ") + lkShort(c.day) + "</p>" +
        (c.role === "owner" ? '<p class="lk-meta">От: ' + esc(c.buyer) + "</p>" : c.contact ? '<p class="lk-meta">Получатель: <span class="num">' + esc(c.contact) + "</span></p>" : "") +
        (c.msg ? '<p class="lk-msg">«' + esc(c.msg) + "»</p>" : "") + "</div>" +
        '<div class="lk-ord-acts"><button class="btn btn-ghost" type="button" data-lk="certpdf:' + c.id + '">' + icon("i-down") + "PDF</button></div></article>";
    }).join("") : '<p class="lk-none">Таких сертификатов нет.</p>') + "</div>";
  }

  // ---------- уведомления ----------
  function lkNotes() {
    var d = lkD(), unread = d.notes.filter(function (n) { return !n.read; }).length;
    var h = lkHead("Уведомления", unread ? plural(unread, ["новое", "новых", "новых"]) + " из " + d.notes.length : "", unread ? '<button class="btn btn-ghost" type="button" data-lk="readall">' + icon("i-check") + "Прочитать все</button>" : "");
    if (!d.notes.length) return h + lkEmpty("i-bell", "Уведомлений пока нет", "Сюда придут сообщения о записи, оплате и готовых результатах.");
    return h + '<div class="lk-list">' + d.notes.map(function (n) {
      return '<article class="lk-card lk-ntf' + (n.read ? "" : " is-new") + '"><span class="lk-dot" aria-hidden="true"></span><div><p class="lk-meta num">' + (n.read ? "" : '<span class="lk-tag lk-up">Новое</span>') + lkRel(n.day).replace(/^./, function (c) { return c.toUpperCase(); }) + ", " + n.time + "</p><h3>" + esc(n.t) + "</h3><p>" + typo(esc(n.x)) + "</p></div>" +
        '<div class="lk-ord-acts">' + (n.go ? '<button class="btn btn-navy" type="button" data-lk="open:' + n.id + '">Открыть</button>' : "") + (n.read ? "" : '<button class="btn btn-ghost" type="button" data-lk="read:' + n.id + '">Прочитано</button>') + "</div></article>";
    }).join("") + "</div>";
  }

  // ---------- семья ----------
  function lkFamily() {
    var d = lkD(), h = lkHead("Семья", "Родственников можно записывать на анализы и видеть их результаты.", '<button class="btn btn-lime" type="button" data-lk="fadd">' + icon("i-plus") + "Добавить родственника</button>");
    if (!d.family.length) return h + lkEmpty("i-users", "Родственников пока нет", "Добавьте ребёнка, родителей или супруга — и оформляйте анализы на них из своего кабинета.");
    return h + '<div class="lk-fam">' + d.family.map(function (f) {
      return '<article class="lk-card lk-person"><div class="lk-me"><span class="lk-ava" aria-hidden="true">' + esc(f.first.charAt(0) + f.last.charAt(0)) + "</span><span><b>" + esc(lkFull(f)) + '</b><small class="num">' + esc(f.birth) + "</small></span></div>" +
        (f.res ? '<p class="lk-meta">' + icon("i-check") + "Результаты подключены</p>" : '<p class="lk-meta">' + icon("i-info") + 'Результаты не подключены</p><button class="btn btn-navy" type="button" data-lk="facc:' + f.id + '">Подключить результаты</button>') +
        '<div class="lk-person-acts"><button class="linkbtn" type="button" data-lk="fedit:' + f.id + '">Изменить</button><button class="linkbtn" type="button" data-lk="fdel:' + f.id + '">Удалить</button></div></article>';
    }).join("") + "</div>";
  }
  function lkDlgHead(h, p) { return '<button class="lk-dlg-x" type="button" data-lk="close" aria-label="Закрыть">' + icon("i-x") + '</button><h2 id="lk-dlg-h">' + h + "</h2>" + (p ? "<p>" + typo(p) + "</p>" : ""); }
  function lkFamForm(id) {
    var f = id ? lkWho(id) : { last: "", first: "", mid: "", birth: "", sex: "" }, today = new Date().toISOString().slice(0, 10);
    function sel(v) { return ["Не указан", "Мужской", "Женский"].map(function (x) { return "<option" + (x === v ? " selected" : "") + ">" + x + "</option>"; }).join(""); }
    return lkDlgHead(id ? "Изменить данные" : "Добавить родственника", id ? "" : "Данные — как в документе: по ним лаборатория найдёт карту пациента.") +
      '<form class="lk-form" data-form="lk-fam" data-id="' + (id || "") + '" novalidate>' +
      '<label class="fld"><span>Фамилия</span><input name="last" autocomplete="off" value="' + esc(f.last) + '" required></label>' +
      '<label class="fld"><span>Имя</span><input name="first" autocomplete="off" value="' + esc(f.first) + '" required></label>' +
      '<label class="fld"><span>Отчество, если есть</span><input name="mid" autocomplete="off" value="' + esc(f.mid) + '"></label>' +
      '<div class="lk-2"><label class="fld"><span>Дата рождения</span><input name="birth" type="date" max="' + today + '" value="' + lkIso(f.birth) + '" required></label><label class="fld"><span>Пол</span><select name="sex">' + sel(f.sex) + "</select></label></div>" +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">' + (id ? "Сохранить" : "Добавить") + '</button><button class="btn btn-ghost" type="button" data-lk="close">Отмена</button></div></form>';
  }
  function lkFamAccess(f, step) {
    if (step === 2) return lkDlgHead("Код из SMS", "Отправили 4-значный код на " + lkD().patient.phone + ".") +
      '<form class="lk-form" data-form="lk-fcode" novalidate><label class="fld"><span>Код из SMS</span><input name="code" inputmode="numeric" autocomplete="one-time-code" maxlength="4" placeholder="0000"></label>' +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">Подтвердить</button></div></form>';
    return lkDlgHead("Доступ к результатам: " + esc(f.first), "Отправили логин и пароль от медицинской системы лаборатории на телефон и e-mail вашего аккаунта. Введите их — и результаты " + f.first + " появятся в кабинете.") +
      '<form class="lk-form" data-form="lk-facc" novalidate><label class="fld"><span>Логин</span><input name="login" autocomplete="off"></label><label class="fld"><span>Пароль</span><input name="pw" type="password" autocomplete="off"></label>' +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">Подключить</button><button class="btn btn-ghost" type="button" data-lk="flater">Подключить позже</button></div></form>';
  }

  // ---------- профиль, пароль, e-mail ----------
  function lkProfile() {
    var p = lkD().patient;
    return lkHead("Профиль", "Изменить личные данные можно в пункте CLD или по телефону 8 800 201 78 30.") +
      '<dl class="lk-prof">' + [["Фамилия", p.last], ["Имя", p.first], ["Отчество", p.mid], ["Дата рождения", p.birth || "не указана"], ["Пол", p.sex || "не указан"], ["Телефон", p.phone]].map(function (x) { return "<div><dt>" + x[0] + "</dt><dd>" + esc(x[1]) + "</dd></div>"; }).join("") +
      "<div><dt>E-mail</dt><dd>" + (p.email ? esc(p.email) : 'не указан <button class="linkbtn" type="button" data-go="lk:email">Привязать e-mail</button>') + "</dd></div></dl>" +
      '<div class="lk-form-acts lk-prof-acts"><button class="btn btn-ghost" type="button" data-go="lk:password">' + icon("i-key") + 'Сменить пароль</button><button class="btn btn-ghost" type="button" data-lk="logout">' + icon("i-logout") + "Выйти из кабинета</button></div>";
  }
  function lkPassword() {
    return lkBack("lk:profile", "Профиль") + lkHead("Новый пароль", "После сохранения можно входить с этим паролем или по-прежнему по коду из SMS.") +
      '<form class="lk-form" data-form="lk-pw" novalidate>' +
      '<label class="fld"><span>Текущий пароль</span><input name="cur" type="password" autocomplete="current-password" aria-describedby="lk-cur-h"><small class="hint" id="lk-cur-h">Оставьте пустым, если входили по коду из SMS.</small></label>' +
      '<label class="fld"><span>Новый пароль</span><span class="lk-pw"><input name="pw" type="password" autocomplete="new-password" aria-describedby="lk-pw-h"><button class="btn btn-ghost" type="button" data-lk="pwshow" aria-pressed="false">Показать</button></span><small class="hint" id="lk-pw-h">Не меньше 8 символов.</small></label>' +
      '<button class="linkbtn" type="button" data-lk="pwgen">Придумать надёжный пароль</button>' +
      '<label class="fld"><span>Повторите новый пароль</span><input name="pw2" type="password" autocomplete="new-password"></label>' +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">Сохранить пароль</button></div></form>';
  }
  function lkEmail() {
    var p = lkD().patient;
    return lkBack("lk:profile", "Профиль") + lkHead("Привязка e-mail", "На e-mail придут результаты анализов, чеки и ссылка для восстановления пароля.") +
      (lk.emailSent ? '<p class="lk-ok">' + typo("Отправили ссылку на " + esc(p.email) + ". Откройте письмо и нажмите кнопку подтверждения.") + "</p>" :
      '<form class="lk-form" data-form="lk-email" novalidate><label class="fld"><span>E-mail</span><input name="email" type="email" autocomplete="email" inputmode="email" value="' + esc(p.email) + '"></label>' +
      '<p class="err" hidden></p><div class="lk-form-acts"><button class="btn btn-lime" type="submit">Отправить ссылку</button></div>' +
      '<p class="hint">' + typo("Нет e-mail? Его можно бесплатно завести в Яндексе, Mail.ru или Gmail за пару минут. Если не получается — позвоните 8 800 201 78 30, поможем.") + "</p></form>");
  }

  function renderLk() {
    var view = { orders: lkOrders, results: lkOrders, order: lkOrderPage, result: lkResultPage, invoices: lkInvoices, certs: lkCerts, notifications: lkNotes, family: lkFamily, profile: lkProfile, password: lkPassword, email: lkEmail }[lk.sub];
    lkHeader();
    $("#lk-side").innerHTML = lkSide();
    $("#lk-main").innerHTML = view();
    $("#lk-crumbs").innerHTML = lkCrumbs();
    PAGE_META.lk = [(lk.sub === "order" && lkOrder(lk.id) ? "Заказ " + lkOrder(lk.id).no : LK_TITLE[lk.sub]) + " — личный кабинет CLD", "Личный кабинет пациента CLD: записи, результаты анализов, оплаты, сертификаты и семья."];
  }
  RENDER.lk = renderLk;
  function lkRe(focus) { renderLk(); var el = focus && document.querySelector('#v-lk [data-lk="' + focus + '"]'); if (el) el.focus(); }
  function lkDlg(html) { var dl = $("#lk-dlg"); dl.innerHTML = html; if (!dl.open) dl.showModal(); var f = dl.querySelector("input, select, textarea, .btn"); if (f) f.focus(); }
  function lkDlgClose() { var dl = $("#lk-dlg"); if (dl.open) dl.close(); }
  function lkPrint() { setTimeout(function () { window.print(); }, 250); }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-lk]"); if (!b) return;
    var a = b.dataset.lk.split(":"), cmd = a[0], arg = a[1], d = lkD(), o = arg ? lkOrder(arg) : null;
    if (cmd === "filter") { lk.filter = arg; lkRe(b.dataset.lk); }
    else if (cmd === "who") { lk.who = arg; lkRe(b.dataset.lk); }
    else if (cmd === "certf") { lk.certf = arg; lkRe(b.dataset.lk); }
    else if (cmd === "hist") { lk.hist = !lk.hist; lkRe("hist"); }
    else if (cmd === "resch") { lk.resch = !lk.resch; lk.rd = null; lk.rt = ""; renderLk(); var r = $("#v-lk .lk-resch .chip") || $('#v-lk [data-lk="resch"]'); if (r) r.focus(); }
    else if (cmd === "rd") { lk.rd = +arg; lk.rt = ""; lkRe(b.dataset.lk); }
    else if (cmd === "rt") { lk.rt = arg.slice(0, 2) + ":" + arg.slice(2); lkRe(b.dataset.lk); }
    else if (cmd === "rsave") { o = lkOrder(lk.id); o.day = lk.rd; o.time = lk.rt; o.hist.push([0, new Date().toTimeString().slice(0, 5), "Визит перенесён на " + lkLong(lk.rd) + ", " + lk.rt]); lk.resch = false; toast("Визит перенесён"); renderLk(); }
    else if (cmd === "pay") { o.paid = true; o.st = o.day != null ? "upcoming" : "paid"; o.hist.push([0, new Date().toTimeString().slice(0, 5), "Оплачен онлайн"]); d.invoices.forEach(function (v) { if (v.ord === o.id) v.paid = true; }); toast("Оплата прошла"); renderLk(); }
    else if (cmd === "repeat") { var n = 0; o.codes.forEach(function (c) { if (!item(c).na && !cart[c]) { cart[c] = 1; n++; } }); syncCart(); toast(n ? "В корзину: " + nAn(n) : "Эти анализы уже в корзине"); go("cart"); }
    else if (cmd === "cancel") {
      if (o.day != null && o.day < 1) { lkDlg(lkDlgHead("Отменить через кабинет нельзя", "До визита меньше суток. Чтобы отменить или перенести запись, позвоните 8 800 201 78 30.") + '<div class="lk-form-acts"><a class="btn btn-lime" href="tel:88002017830">Позвонить</a><button class="btn btn-ghost" type="button" data-lk="close">Закрыть</button></div>'); return; }
      lkDlg(lkDlgHead("Отменить запись?", "Заказ " + o.no + ". Запись в пункте освободится. Если заказ оплачен, деньги вернутся на карту за 3–7 рабочих дней.") +
        '<form class="lk-form" data-form="lk-cancel" data-id="' + o.id + '" novalidate><label class="fld"><span>Причина, если хотите указать</span><select name="reason"><option value="">Не указывать</option><option>Изменились планы</option><option>Плохо себя чувствую</option><option>Сдам в другом пункте</option><option>Другое</option></select></label>' +
        '<label class="fld"><span>Комментарий</span><textarea name="note" maxlength="500" placeholder="Например: заболел, перенесу на следующую неделю"></textarea></label>' +
        '<div class="lk-form-acts"><button class="btn btn-navy" type="submit">Отменить запись</button><button class="btn btn-ghost" type="button" data-lk="close">Не отменять</button></div></form>');
    }
    else if (cmd === "pdf") { if (lk.sub === "result" && lk.id === arg) lkPrint(); else { go("lk:result:" + arg); lkPrint(); } }
    else if (cmd === "certpdf") toast("Сертификат скачивается в PDF");
    else if (cmd === "open") { var nt = d.notes.filter(function (x) { return x.id === arg; })[0]; nt.read = true; go(nt.go); }
    else if (cmd === "read") { d.notes.forEach(function (x) { if (x.id === arg) x.read = true; }); toast("Отмечено как прочитанное"); renderLk(); }
    else if (cmd === "readall") { d.notes.forEach(function (x) { x.read = true; }); toast("Все уведомления прочитаны"); renderLk(); }
    else if (cmd === "fadd") lkDlg(lkFamForm());
    else if (cmd === "fedit") lkDlg(lkFamForm(arg));
    else if (cmd === "facc") { lk.pending = lkWho(arg); lkDlg(lkFamAccess(lk.pending)); }
    else if (cmd === "flater") { if (lk.pending && !lkWho(lk.pending.id)) d.family.push(lk.pending); lk.pending = null; lkDlgClose(); toast("Родственник добавлен"); renderLk(); }
    else if (cmd === "fdel") { var f = lkWho(arg); lkDlg(lkDlgHead("Удалить родственника?", f.first + " " + f.last + " пропадёт из списка. Заказы и результаты останутся в истории.") + '<div class="lk-form-acts"><button class="btn btn-navy" type="button" data-lk="fdelok:' + arg + '">Удалить</button><button class="btn btn-ghost" type="button" data-lk="close">Отмена</button></div>'); }
    else if (cmd === "fdelok") { d.family = d.family.filter(function (x) { return x.id !== arg; }); if (lk.who === arg) lk.who = "me"; lkDlgClose(); toast("Удалено"); renderLk(); }
    else if (cmd === "close") lkDlgClose();
    else if (cmd === "gateback") { lk.gate = 0; renderLk(); }
    else if (cmd === "pwshow") { var inp = b.parentNode.querySelector("input"), on = inp.type === "password"; inp.type = on ? "text" : "password"; b.textContent = on ? "Скрыть" : "Показать"; b.setAttribute("aria-pressed", String(on)); }
    else if (cmd === "pwgen") {
      var abc = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789", pw = "", rnd = new Uint32Array(14); crypto.getRandomValues(rnd);
      for (var i = 0; i < 14; i++) pw += abc[rnd[i] % abc.length];
      var fm = b.closest("form"); fm.pw.value = pw; fm.pw2.value = pw; fm.pw.type = "text"; var sh = fm.querySelector('[data-lk="pwshow"]'); sh.textContent = "Скрыть"; sh.setAttribute("aria-pressed", "true");
      toast("Пароль придуман — сохраните его");
    }
    else if (cmd === "logout") { res.step = "phone"; res.phone = ""; lk.data = null; lk.mode = "full"; lkHeader(); go("results"); toast("Вы вышли из кабинета"); }
  });
  document.addEventListener("submit", function (e) {
    var fm = e.target, f = fm.dataset.form; if (!f || f.indexOf("lk-") !== 0) return;
    e.preventDefault();
    var d = lkD(), err = fm.querySelector(".err"), now = new Date().toTimeString().slice(0, 5);
    function fail(t, name) { err.textContent = t; err.hidden = false; if (name) fm[name].focus(); }
    function val(name) { return (fm[name] && fm[name].value || "").trim(); }
    if (f === "lk-cancel") {
      var o = lkOrder(fm.dataset.id), why = val("reason");
      o.st = "cancel"; o.paid = false; o.hist.push([0, now, "Запись отменена" + (why ? ": " + why.toLowerCase() : "")]);
      lkDlgClose(); toast("Запись отменена"); renderLk();
    } else if (f === "lk-fam") {
      if (!val("last")) return fail("Укажите фамилию.", "last");
      if (!val("first")) return fail("Укажите имя.", "first");
      if (!val("birth")) return fail("Укажите дату рождения.", "birth");
      var data = { last: val("last"), first: val("first"), mid: val("mid"), birth: lkRu(val("birth")), sex: val("sex") };
      var cur = fm.dataset.id && lkWho(fm.dataset.id);
      if (cur) { Object.keys(data).forEach(function (k) { cur[k] = data[k]; }); lkDlgClose(); toast("Сохранено"); renderLk(); return; }
      data.id = "f" + Date.now(); data.res = false; lk.pending = data; lkDlg(lkFamAccess(data));
    } else if (f === "lk-facc") {
      if (!val("login")) return fail("Введите логин из сообщения.", "login");
      if (!val("pw")) return fail("Введите пароль из сообщения.", "pw");
      lkDlg(lkFamAccess(lk.pending, 2));
    } else if (f === "lk-fcode" || f === "lk-gate2") {
      if (!/^\d{4}$/.test(val("code"))) return fail("Введите 4 цифры кода.", "code");
      if (f === "lk-gate2") { lk.gate = 3; toast("Доступ к результатам подтверждён"); renderLk(); return; }
      var p = lk.pending, known = lkWho(p.id); p.res = true; if (!known) d.family.push(p); else known.res = true;
      lk.pending = null; lkDlgClose(); toast(known ? "Результаты подключены" : "Родственник добавлен"); renderLk();
    } else if (f === "lk-gate1") {
      if (!val("login")) return fail("Введите логин из письма.", "login");
      if (!val("pw")) return fail("Введите пароль из письма.", "pw");
      lk.gate = 2; renderLk(); var c = $("#v-lk [name=code]"); if (c) c.focus();
    } else if (f === "lk-pw") {
      if (val("pw").length < 8) return fail("Пароль короче 8 символов.", "pw");
      if (val("pw") !== val("pw2")) return fail("Пароли не совпадают.", "pw2");
      toast("Пароль обновлён"); go("lk:profile");
    } else if (f === "lk-email") {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val("email"))) return fail("Проверьте e-mail: в нём должны быть @ и домен, например name@mail.ru.", "email");
      d.patient.email = val("email"); lk.emailSent = true; renderLk();
    }
  });
  /* LK END */
'''

CSS = '''/* LK CSS */
.lk { padding-bottom: 80px; }
.lk-grid { display: grid; grid-template-columns: 284px minmax(0, 1fr); gap: 40px; align-items: start; margin-top: 18px; }
.lk-side { position: sticky; top: 196px; display: grid; gap: 12px; padding: 18px; border-radius: 20px; background: var(--surface-2); }
.lk-me { display: flex; align-items: center; gap: 12px; min-width: 0; }
.lk-side > .lk-me { padding: 2px 4px 14px; border-bottom: 1.5px solid var(--line); }
.lk-me > span:last-child { min-width: 0; }
.lk-ava { display: grid; place-items: center; width: 48px; height: 48px; flex: none; border-radius: 50%; background: var(--lime); color: var(--navy); font: 800 17px/1 var(--text); }
.lk-me b { display: block; font-size: 17px; line-height: 1.3; }
.lk-me small { display: block; font-size: 16px; color: var(--muted); }
.lk-nav { display: grid; gap: 2px; }
.lk-nav a { position: relative; display: flex; align-items: center; gap: 12px; padding: 11px 12px; border-radius: 12px; font-weight: 600; font-size: 16px; line-height: 1.3; text-decoration: none; color: var(--ink); transition: background-color .2s var(--ease); }
.lk-nav a:hover { background: #FFF; }
.lk-nav a[aria-current="page"] { background: var(--navy); color: #FFF; }
.lk-nav .ico { width: 22px; height: 22px; }
.lk-badge { margin-left: auto; min-width: 28px; padding: 3px 9px; border-radius: 999px; background: var(--lime); color: var(--navy); font: 800 16px/1.25 var(--text); text-align: center; }
.lk-out { display: flex; align-items: center; gap: 12px; padding: 12px 12px 4px; border: 0; border-top: 1.5px solid var(--line); background: none; font: 600 16px var(--text); color: var(--ink); cursor: pointer; text-align: left; }
.lk-out:hover { text-decoration: underline; text-underline-offset: 3px; }
.lk-out .ico { width: 22px; height: 22px; }
.lk-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 16px 24px; margin-bottom: 22px; }
.lk-head h1 { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; font-size: clamp(30px, 3.2vw, 40px); }
.lk-lede { margin-top: 8px; max-width: 62ch; font-size: 17px; color: var(--muted); }
.lk-acts, .lk-form-acts, .lk-ord-acts { display: flex; flex-wrap: wrap; gap: 10px; }
.lk-acts .btn, .lk-ord-acts .btn { padding: 11px 16px; }
.lk-back { display: inline-flex; align-items: center; gap: 6px; margin-bottom: 8px; padding: 6px 0; border: 0; background: none; font: 700 16px var(--text); color: var(--navy); cursor: pointer; }
.lk-back:hover { text-decoration: underline; text-underline-offset: 3px; }
.lk-tabs { display: inline-flex; gap: 4px; margin-bottom: 20px; padding: 4px; border-radius: 14px; background: var(--surface); }
.lk-tabs a { display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 10px; font-weight: 700; font-size: 16px; text-decoration: none; color: var(--ink); }
.lk-tabs a[aria-current="page"] { background: #FFF; box-shadow: 0 2px 8px rgba(20,55,75,.14); }
.lk-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
.lk .chip { font-size: 16px; }
.lk .chip .n { margin-left: 2px; font-size: 16px; }
.lk .chip:disabled { cursor: not-allowed; color: var(--muted); background: var(--surface-2); }
.lk-list { display: grid; gap: 14px; }
.lk-card { padding: 20px 22px; border-radius: 18px; background: #FFF; box-shadow: inset 0 0 0 1.5px var(--line); }
.lk-ord { display: grid; grid-template-columns: 84px minmax(0, 1fr) auto; gap: 20px; align-items: start; }
.lk-ord.is-off { background: var(--surface-2); box-shadow: none; }
.lk-when { display: grid; justify-items: center; align-content: start; padding: 10px 6px 12px; border-radius: 14px; background: var(--navy-soft); text-align: center; }
.lk-when b { font: 800 30px/1.05 var(--text); }
.lk-when span { font-weight: 700; font-size: 16px; }
.lk-when small { margin-top: 2px; font-size: 16px; color: var(--muted); }
.lk-when-no { gap: 6px; padding-inline: 4px; }
.lk-when-no span { font-size: 16px; line-height: 1.2; }
.lk-ord-h { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.lk-ord-h h3 { font: 700 19px/1.3 var(--text); }
.lk-ord-h h3 a { text-decoration: none; }
.lk-ord-h h3 a:hover { text-decoration: underline; text-underline-offset: 3px; }
.lk-tag { display: inline-flex; align-items: center; gap: 6px; padding: 3px 11px; border-radius: 999px; background: var(--surface); color: var(--ink); font: 700 16px/1.4 var(--text); white-space: nowrap; }
.lk-tag .ico { width: 17px; height: 17px; }
.lk-tag.lk-up { background: var(--lime); color: var(--navy); }
.lk-tag.lk-wait { background: var(--navy); color: #FFF; }
.lk-tag.lk-work { background: var(--navy-soft); }
.lk-tag.lk-done { background: var(--lime-soft); }
.lk-tag.lk-off { color: var(--muted); }
.lk-meta { margin-top: 8px; font-size: 16px; color: var(--muted); }
.lk-meta .ico { display: inline-block; width: 18px; height: 18px; margin-right: 6px; vertical-align: -3px; }
.lk-meta .lk-tag { margin-right: 4px; }
.lk-items { display: grid; gap: 4px; margin: 10px 0 0; padding: 0; list-style: none; font-size: 16px; }
.lk-items li { display: flex; gap: 10px; align-items: baseline; }
.lk-items li::before { content: ""; width: 7px; height: 7px; flex: none; border-radius: 50%; background: var(--navy); transform: translateY(-2px); }
.lk-items .lk-more { color: var(--muted); }
.lk-items .lk-more::before { background: var(--line); }
.lk-ord-side { display: grid; justify-items: end; gap: 12px; }
.lk-ord-side > b { font: 800 20px/1.2 var(--text); }
.lk-ord-acts { justify-content: flex-end; }
.lk-next { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 24px; align-items: center; margin-bottom: 22px; padding: 22px 24px; border-radius: 20px; background: var(--navy); color: #FFF; }
.lk-next-when { display: grid; justify-items: center; min-width: 100px; padding: 12px 10px; border-radius: 16px; background: var(--lime); color: var(--navy); }
.lk-next-when b { font: 800 42px/1 var(--text); }
.lk-next-when span { font-weight: 700; font-size: 17px; }
.lk-next-when small { margin-top: 4px; font: 800 18px var(--text); color: var(--navy); }
.lk-next h2 { font-size: clamp(22px, 2.4vw, 28px); color: #FFF; }
.lk-next p { margin-top: 6px; font-size: 17px; color: var(--on-navy); }
.lk-next-prep { display: flex; gap: 10px; align-items: flex-start; }
.lk-next-prep .ico { width: 22px; height: 22px; margin-top: 2px; color: var(--lime); }
.lk-next-acts { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.lk-btn-on { background: transparent; color: #FFF; box-shadow: inset 0 0 0 1.5px rgba(255,255,255,.7); }
.lk-btn-on:hover { box-shadow: inset 0 0 0 1.5px #FFF; background: rgba(255,255,255,.08); }
.lk-res { display: grid; grid-template-columns: 52px minmax(0, 1fr) auto; gap: 18px; align-items: center; }
.lk-res-ic { display: grid; place-items: center; width: 52px; height: 52px; border-radius: 14px; background: var(--lime-soft); color: var(--navy); }
.lk-res-ic.is-work { background: var(--navy-soft); }
.lk-res-ic .ico { width: 26px; height: 26px; }
.lk-res .lk-meta { margin-top: 6px; }
.lk-empty { display: grid; justify-items: center; gap: 10px; padding: 48px 24px; border-radius: 20px; background: var(--surface-2); text-align: center; }
.lk-empty > .ico { width: 48px; height: 48px; color: var(--navy); }
.lk-empty h2 { font-size: 24px; }
.lk-empty p { max-width: 48ch; font-size: 17px; color: var(--muted); }
.lk-empty .btn { margin-top: 8px; }
.lk-none, .lk-hint { font-size: 16px; color: var(--muted); }
.lk-hint { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 10px; margin-top: 16px; }
.lk .linkbtn { font-size: 16px; }
.lk-gate { max-width: 560px; }
.lk-gate h2 { font-size: 24px; }
.lk-gate p { font-size: 17px; }
.lk-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px 24px; margin: 0 0 20px; padding: 18px 20px; border-radius: 16px; background: var(--surface-2); }
.lk-facts dt { font-size: 16px; color: var(--muted); }
.lk-facts dd { margin: 2px 0 0; font-weight: 700; font-size: 17px; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.lk-facts-foot { margin: 20px 0 0; }
.lk-sum { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 18px; padding: 16px 18px; border-radius: 16px; background: var(--lime-soft); font-size: 17px; }
.lk-sum .ico { width: 22px; height: 22px; margin-top: 2px; }
.lk-blank { position: relative; border-radius: 16px; box-shadow: inset 0 0 0 1.5px var(--line); overflow: hidden; }
.lk-blank table { width: 100%; border-collapse: collapse; font-size: 16px; }
.lk-blank th, .lk-blank td { padding: 13px 16px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }
.lk-blank thead th { background: var(--navy); color: #FFF; font-weight: 700; }
.lk-blank tbody th { font-weight: 600; }
.lk-blank tbody tr:last-child > * { border-bottom: 0; }
.lk-blank tr.is-flag { background: var(--lime-soft); }
.lk-v b { font: 800 18px/1.3 var(--text); }
.lk-v small { display: block; margin-top: 4px; font-size: 16px; color: var(--muted); }
.lk-flag { display: inline-flex; align-items: center; gap: 4px; margin-left: 10px; padding: 1px 10px 1px 7px; border-radius: 999px; background: var(--navy); color: #FFF; font: 700 16px/1.45 var(--text); white-space: nowrap; vertical-align: 1px; }
.lk-flag .ico { width: 16px; height: 16px; stroke-width: 2.4; }
.lk-u { color: var(--muted); white-space: nowrap; }
.lk-ref { font-variant-numeric: tabular-nums; }
.lk-ref > span:not(.vh) { display: block; }
.lk-ref .nw { white-space: nowrap; }
.lk-blank thead th:nth-child(1) { width: 33%; }
.lk-blank thead th:nth-child(2) { width: 25%; }
.lk-blank thead th:nth-child(3) { width: 11%; }
.lk-note { max-width: 75ch; margin-top: 18px; font-size: 16px; color: var(--muted); }
.lk-band { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 8px; border-radius: 18px; box-shadow: inset 0 0 0 1.5px var(--line); }
.lk-band > div { display: grid; align-content: start; justify-items: start; gap: 4px; padding: 18px 20px; }
.lk-band > div + div { border-left: 1.5px solid var(--line); }
.lk-band h2 { font: 600 16px var(--text); color: var(--muted); }
.lk-band b { font-size: 18px; line-height: 1.35; }
.lk-band p { font-size: 16px; color: var(--muted); }
.lk-band .linkbtn { margin-top: 6px; }
.lk-sec { margin-top: 32px; }
.lk-sec > h2 { margin-bottom: 14px; font-size: 24px; }
.lk-resch { display: grid; gap: 14px; margin-top: 14px; padding: 20px; border-radius: 18px; background: var(--surface-2); }
.lk-resch h2 { font-size: 20px; }
.lk-resch .lk-chips { margin: 0; }
.lk-prep { display: grid; gap: 16px; padding: 20px 22px; border-radius: 18px; background: var(--lime-soft); }
.lk-prep h3 { font: 700 18px/1.3 var(--text); }
.lk-prep ul { display: grid; gap: 4px; margin: 8px 0 0; padding-left: 22px; font-size: 16px; }
.lk-prep .pp-more { justify-self: start; margin-top: 0; background: #FFF; }
.lk-lines { margin: 0; padding: 0; list-style: none; border-radius: 16px; box-shadow: inset 0 0 0 1.5px var(--line); }
.lk-lines li { display: grid; grid-template-columns: minmax(0, 1fr) auto 110px; gap: 16px; align-items: baseline; padding: 13px 18px; border-bottom: 1px solid var(--line); font-size: 16px; }
.lk-lines li:last-child { border-bottom: 0; }
.lk-lines a { font-weight: 600; text-decoration: none; }
.lk-lines a:hover { text-decoration: underline; text-underline-offset: 3px; }
.lk-lines span.num { color: var(--muted); }
.lk-lines b { justify-self: end; }
.lk-total { display: grid; gap: 6px; max-width: 420px; margin: 14px 0 0 auto; font-size: 16px; }
.lk-total div { display: flex; justify-content: space-between; gap: 16px; }
.lk-total dd { margin: 0; font-weight: 700; }
.lk-total .t { margin-top: 4px; padding-top: 10px; border-top: 1.5px solid var(--line); font-size: 19px; }
.lk-total .t dd { font-weight: 800; }
.lk-hist { margin: 0; padding: 0; list-style: none; }
.lk-hist li { position: relative; display: grid; grid-template-columns: 180px minmax(0, 1fr); gap: 12px; padding: 9px 0 9px 26px; font-size: 16px; }
.lk-hist li::before { content: ""; position: absolute; left: 3px; top: 16px; width: 10px; height: 10px; border-radius: 50%; background: var(--lime); box-shadow: 0 0 0 2px var(--navy); }
.lk-hist li + li::after { content: ""; position: absolute; left: 7px; top: -8px; width: 2px; height: 22px; background: var(--line); }
.lk-hist time { color: var(--muted); }
.lk-tblw { border-radius: 16px; box-shadow: inset 0 0 0 1.5px var(--line); overflow: hidden; }
.lk-tbl { width: 100%; border-collapse: collapse; font-size: 16px; }
.lk-tbl th, .lk-tbl td { padding: 14px 18px; text-align: left; vertical-align: middle; border-bottom: 1px solid var(--line); }
.lk-tbl thead th { background: var(--surface-2); color: var(--muted); font-weight: 700; }
.lk-tbl tbody tr:last-child td { border-bottom: 0; }
.lk-tbl td:nth-child(4) { font-weight: 800; }
.lk-tbl small { display: block; color: var(--muted); font-size: 16px; }
.lk-tbl a { font-weight: 700; }
.lk-tbl .btn { padding: 9px 14px; }
.lk-bal { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px 24px; align-items: center; margin-bottom: 22px; padding: 22px 24px; border-radius: 20px; background: var(--navy); color: #FFF; }
.lk-bal-sum { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 0 14px; align-items: center; }
.lk-bal-sum .ico { grid-row: span 2; width: 40px; height: 40px; color: var(--lime); }
.lk-bal-sum span { font-weight: 600; color: var(--on-navy-muted); }
.lk-bal-sum b { font: 800 34px/1.15 var(--text); }
.lk-bal-sum p { grid-column: 1 / -1; margin-top: 10px; max-width: 52ch; font-size: 16px; }
.lk-bal-acts { display: flex; flex-wrap: wrap; gap: 10px; }
.lk-bal-hist { grid-column: 1 / -1; margin: 0; padding: 4px 0 0; list-style: none; border-top: 1px solid rgba(255,255,255,.25); }
.lk-bal-hist li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 12px; align-items: baseline; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,.15); font-size: 16px; }
.lk-bal-hist li:last-child { border-bottom: 0; }
.lk-bal-hist small { display: block; font-size: 16px; color: var(--on-navy-muted); }
.lk-bal-hist b.plus { color: var(--lime); }
.lk-cert { display: grid; grid-template-columns: 210px minmax(0, 1fr) auto; gap: 20px; align-items: center; }
.lk-cert-face { display: grid; align-content: space-between; aspect-ratio: 1.6; padding: 14px 16px; border-radius: 14px; background: var(--lime); color: var(--navy); box-shadow: 0 6px 16px rgba(20,55,75,.14); }
.lk-cert-face img { width: 96px; }
.lk-cert-face b { font: 800 26px/1 var(--text); }
.lk-msg { margin-top: 8px; font-size: 16px; font-style: italic; }
.lk-ntf { display: grid; grid-template-columns: 14px minmax(0, 1fr) auto; gap: 14px; align-items: start; }
.lk-dot { width: 12px; height: 12px; margin-top: 12px; border-radius: 50%; background: var(--line); }
.lk-ntf.is-new .lk-dot { background: var(--lime); box-shadow: 0 0 0 2px var(--navy); }
.lk-ntf .lk-meta { margin-top: 0; }
.lk-ntf h3 { margin-top: 4px; font: 700 18px/1.3 var(--text); }
.lk-ntf p:not(.lk-meta) { margin-top: 4px; font-size: 16px; }
.lk-fam { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 14px; }
.lk-person { display: grid; gap: 12px; align-content: start; justify-items: start; }
.lk-person .lk-meta { margin-top: 0; }
.lk-person-acts { display: flex; gap: 18px; }
.lk-prof { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); margin: 0; border-radius: 18px; box-shadow: inset 0 0 0 1.5px var(--line); overflow: hidden; }
.lk-prof > div { padding: 16px 20px; border-bottom: 1px solid var(--line); }
.lk-prof > div:nth-child(odd) { border-right: 1px solid var(--line); }
.lk-prof > div:last-child { border-bottom: 0; }
.lk-prof dt { font-size: 16px; color: var(--muted); }
.lk-prof dd { margin: 4px 0 0; font-weight: 700; font-size: 18px; overflow-wrap: anywhere; }
.lk-prof dd .linkbtn { margin-left: 8px; }
.lk-prof-acts { margin-top: 20px; }
.lk-form { display: grid; gap: 14px; max-width: 520px; }
.lk-form .fld > span:first-child { font-size: 16px; font-weight: 600; color: var(--ink); }
.lk-form input, .lk-form select, .lk-form textarea { width: 100%; min-width: 0; padding: 12px 14px; border: 1.5px solid var(--line); border-radius: var(--r-ctrl); background: #FFF; font: 500 17px var(--text); color: var(--ink); }
.lk-form textarea { min-height: 96px; resize: vertical; }
.lk-form input:focus, .lk-form select:focus, .lk-form textarea:focus { outline: none; border-color: var(--navy); box-shadow: 0 0 0 3px var(--navy-soft); }
.lk-form .hint { font-size: 16px; color: var(--muted); }
.lk-form .err { font-size: 16px; }
.lk-2 { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 12px; }
.lk-pw { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; }
.lk-pw .btn { padding: 11px 14px; }
.lk-ok { max-width: 62ch; padding: 16px 18px; border-radius: 14px; background: var(--lime-soft); font-weight: 600; }
.lk-dlg { width: min(560px, calc(100vw - 32px)); max-height: calc(100dvh - 32px); padding: 26px; border: 0; border-radius: 20px; box-shadow: 0 24px 60px rgba(20,55,75,.30); color: var(--ink); }
.lk-dlg::backdrop { background: rgba(15,43,59,.55); }
.lk-dlg h2 { margin-bottom: 8px; padding-right: 48px; font-size: 26px; }
.lk-dlg > p { margin-bottom: 16px; font-size: 16px; }
.lk-dlg-x { position: absolute; top: 14px; right: 14px; display: grid; place-items: center; width: 44px; height: 44px; border: 0; border-radius: 50%; background: var(--surface); color: var(--navy); cursor: pointer; }
.lk-dlg-x:hover { background: var(--navy-soft); }
.lk-dlg .lk-form { max-width: none; }
@media (max-width: 1100px) { .lk-grid { grid-template-columns: 250px minmax(0, 1fr); gap: 28px; } .lk-ord { grid-template-columns: 76px minmax(0, 1fr); } .lk-ord-side { grid-column: 2; grid-template-columns: auto minmax(0, 1fr); justify-items: start; align-items: center; } }
@media (max-width: 960px) {
  .lk-grid { grid-template-columns: minmax(0, 1fr); gap: 16px; margin-top: 12px; }
  .lk-side { position: static; padding: 0; gap: 12px; background: none; }
  .lk-side > .lk-me { padding: 0; border: 0; }
  .lk-nav { display: flex; gap: 8px; margin-inline: -20px; padding: 0 20px 4px; overflow-x: auto; scrollbar-width: none; }
  .lk-nav::-webkit-scrollbar { display: none; }
  .lk-nav a { flex: none; padding: 9px 14px; border-radius: 999px; background: #FFF; box-shadow: inset 0 0 0 1.5px var(--line); }
  .lk-nav a[aria-current="page"] { box-shadow: none; }
  .lk-nav .ico { width: 20px; height: 20px; }
  .lk-out { display: none; }
}
@media (max-width: 700px) {
  .lk-card { padding: 16px; }
  .lk-head h1 { font-size: 28px; }
  .lk-acts { width: 100%; }
  .lk-ord { grid-template-columns: 64px minmax(0, 1fr); gap: 14px; }
  .lk-ord-side { grid-column: 1 / -1; grid-template-columns: minmax(0, 1fr); justify-items: stretch; }
  .lk-ord-acts { justify-content: flex-start; }
  .lk-ord-acts .btn, .lk-acts .btn { flex: 1 1 auto; }
  .lk-when b { font-size: 26px; }
  .lk-next { grid-template-columns: minmax(0, 1fr); gap: 14px; padding: 18px; }
  .lk-next-when { justify-self: start; grid-auto-flow: column; align-items: baseline; gap: 8px; min-width: 0; padding: 8px 14px; }
  .lk-next-when b { font-size: 30px; }
  .lk-next-when small { margin: 0; }
  .lk-next-acts .btn { flex: 1 1 auto; }
  .lk-res { grid-template-columns: 44px minmax(0, 1fr); gap: 14px; }
  .lk-res-ic { width: 44px; height: 44px; }
  .lk-res .lk-ord-acts { grid-column: 1 / -1; }
  .lk-tabs { display: flex; }
  .lk-tabs a { flex: 1; justify-content: center; }
  .lk-blank thead { display: none; }
  .lk-blank tr { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 12px; padding: 14px 16px; border-bottom: 1px solid var(--line); }
  .lk-blank tbody tr:last-child { border-bottom: 0; }
  .lk-blank th, .lk-blank td { padding: 0; border: 0; }
  .lk-blank tbody th { grid-column: 1 / -1; }
  .lk-u { grid-column: 2; grid-row: 2; }
  .lk-ref { grid-column: 1 / -1; color: var(--muted); }
  .lk-ref .vh { position: static; width: auto; height: auto; clip: auto; white-space: normal; }
  .lk-flag { margin: 4px 0 0; display: flex; width: max-content; }
  .lk-band { grid-template-columns: minmax(0, 1fr); }
  .lk-band > div + div { border-left: 0; border-top: 1.5px solid var(--line); }
  .lk-lines li { grid-template-columns: minmax(0, 1fr) auto; gap: 2px 12px; }
  .lk-lines li > span { grid-row: 2; }
  .lk-lines li > b { grid-row: 1 / span 2; grid-column: 2; align-self: center; }
  .lk-hist li { grid-template-columns: minmax(0, 1fr); gap: 2px; }
  .lk-tbl thead { display: none; }
  .lk-tbl tr { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 12px; padding: 14px 16px; border-bottom: 1px solid var(--line); }
  .lk-tbl tbody tr:last-child { border-bottom: 0; }
  .lk-tbl td { padding: 0; border: 0; }
  .lk-tbl td:nth-child(2) { grid-column: 2; grid-row: 1; color: var(--muted); }
  .lk-tbl td:nth-child(3) { grid-column: 1 / -1; }
  .lk-tbl td:nth-child(4) { grid-column: 1; }
  .lk-tbl td:nth-child(5) { grid-column: 2; justify-self: end; }
  .lk-bal { grid-template-columns: minmax(0, 1fr); padding: 18px; }
  .lk-bal-acts .btn { flex: 1 1 auto; }
  .lk-cert { grid-template-columns: minmax(0, 1fr); }
  .lk-cert-face { max-width: 260px; }
  .lk-cert .lk-ord-acts { justify-content: flex-start; }
  .lk-ntf { grid-template-columns: 12px minmax(0, 1fr); }
  .lk-ntf .lk-ord-acts { grid-column: 2; justify-content: flex-start; }
  .lk-prof { grid-template-columns: minmax(0, 1fr); }
  .lk-prof > div:nth-child(odd) { border-right: 0; }
  .lk-2 { grid-template-columns: minmax(0, 1fr); }
  .lk-dlg { padding: 22px 18px; }
  .lk-dlg h2 { font-size: 23px; }
}
@media print {
  body[data-screen="lk"] > :not(#app), body[data-screen="lk"] #app > :not(#v-lk), #v-lk .crumbs, #v-lk .lk-side, #v-lk .lk-back, #v-lk .lk-acts { display: none !important; }
  #v-lk .lk-grid { display: block; }
  .lk-blank thead th { background: #FFF !important; color: var(--ink) !important; border-bottom: 2px solid var(--ink); }
}
/* LK CSS END */
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
    data = json.loads((ROOT / "content/account/account.json").read_text())
    data.pop("_about")
    html = block(html, "  <!-- LK VIEW START -->", "<!-- LK VIEW END -->", MARKUP, '  <section id="v-card" data-view="card" hidden>')
    html = block(html, "  /* LK START */", "/* LK END */", JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)), "  /* SHARED NAVIGATION START */")
    html = block(html, "/* LK CSS */", "/* LK CSS END */", CSS, "</style>")
    a = '  <symbol id="i-file" viewBox="0 0 24 24">'
    html = once(html, '<symbol id="i-bell"', a, ICONS + a)
    # маршрут #lk-<раздел>[-<id>]
    a = "    else if (PAGES.indexOf(v) >= 0) state.view = v;\n"
    html = once(html, 'else if (v === "lk")', a, '    else if (v === "lk") { lkRoute(p.slice(1)); state.view = "lk"; }\n' + a)
    a = '    var hash = state.view === "situation" ?'
    html = once(html, 'state.view === "lk" ? lkHash()', a, '    var hash = state.view === "lk" ? lkHash() : state.view === "situation" ?')
    a = "    else if (PAGES.indexOf(h) >= 0) go(h, false);\n"
    html = once(html, 'h.indexOf("lk-") === 0', a, '    else if (h === "lk" || h.indexOf("lk-") === 0) go("lk:" + h.slice(3).replace(/-/g, ":"), false);\n' + a)
    # вход по коду из SMS ведёт в кабинет; «Результаты анализов» у вошедшего — вкладка результатов
    a = 'res.step = "in"; renderResults(); window.scrollTo(0, 0);'
    html = once(html, 'res.step = "in"; go("lk:orders");', a, 'res.step = "in"; go("lk:orders");')
    a = "  function renderResults() {"
    html = once(html, 'if (res.step === "in") { go("lk:results"); return; }', a, a + ' if (res.step === "in") { go("lk:results"); return; }')
    return html


if __name__ == "__main__":
    p = ROOT / "v4/index.html"
    p.write_text(integrate(p.read_text()))
    print("Built patient account.")
