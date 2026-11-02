  /* WOMEN_TEMPLATE */
  var womenSpy = null, womenSearch = "";
  var WOMEN_FAQ = [
    ["Гемоглобин в норме — зачем назначают ферритин?", "Ферритин помогает оценить запасы железа. Они могут снижаться раньше гемоглобина. При воспалении результат требует дополнительной оценки."],
    ["Все гормоны можно сдать в один день?", "Дата зависит от исследования и цели обследования. Например, для подтверждения овуляции прогестерон назначают в другие сроки, чем ФСГ и ЛГ при нарушениях цикла."],
    ["АМГ показывает вероятность естественной беременности?", "По одному АМГ её надёжно не предсказывают. Результат используют вместе с другими данными, в частности при планировании стимуляции яичников."],
    ["Всем ли нужен анализ на витамин D?", "Он не относится к одинаковому набору исследований для каждого здорового человека. Необходимость анализа определяется по показаниям."],
    ["CA 125 подходит для обычной проверки на рак?", "Для профилактического обследования женщин без симптомов и без известного наследственного синдрома высокого риска его не используют. Анализ назначают при определённых показаниях."],
    ["Нужен ли анализ на фолиевую кислоту перед её приёмом?", "При планировании беременности предварительный анализ не является условием начала приёма фолиевой кислоты. Дозу назначает врач."]
  ];
  function womenIcon(name) { return '<svg aria-hidden="true"><use href="#wg-i-' + name + '"/></svg>'; }
  function womenTest(code) {
    var html = pregTest(code), flag = { "30-021": "По назначению врача", "40-297": "По показаниям", "41-006": "Не для профилактической проверки на рак", "52.370": "По назначению врача" }[code];
    return flag ? html.replace('</small>', '</small><span class="pg-tag-note">' + flag + '</span>') : html;
  }
  function womenComplex(code) {
    var x = CXX[code], price = CX[code]; if (!x || !price) return "";
    return '<article class="pg-w-complex"><h3><a href="#card-' + esc(code) + '" data-go="card:' + esc(code) + '">' + esc(x.n) + '</a></h3><p>' + esc(x.parts.join(", ")) + '.</p>' + (price.na ? '<p class="pg-w-complex-na">Нет в выбранном пункте</p>' : '<div class="pg-w-complex-price"><span><b class="num">' + rub(online(price.p)) + '</b><small>на сайте · в пункте ' + rub(price.p) + '</small></span><button type="button" class="pg-add-btn" data-add="' + esc(code) + '">Добавить +</button></div>') + '</article>';
  }
  function womenSyncControls() {
    var root = $("#women-guide"); if (!root || root.hidden || !root.firstChild) return;
    root.querySelectorAll("[data-add]").forEach(function (button) {
      var code = button.dataset.add, entry = A[code] || CX[code]; if (!entry) return;
      button.disabled = !!entry.na;
      if (entry.na) { button.textContent = "Недоступно"; button.setAttribute("aria-label", "Недоступно в выбранном пункте"); return; }
      var on = !!cart[code], title = A[code] ? A[code].n : CXX[code].n;
      button.classList.toggle("pg-added", on); button.innerHTML = on ? womenIcon("check") + " В корзине" : "Добавить +";
      button.setAttribute("aria-label", (on ? "Убрать из корзины: " : "Добавить: ") + title);
    });
  }
  function womenFilter() {
    var count = 0, q = womenSearch.trim().toLowerCase();
    $$("#wg-catalog-list [data-preg-code]").forEach(function (row) { var c = row.dataset.pregCode, a = A[c], match = !q || (c + " " + a.n + " " + a.off).toLowerCase().indexOf(q) >= 0; row.hidden = !match; if (match) count++; });
    $("#wg-no-results").hidden = !!count;
  }
  function womenJump(slug, update) {
    var target = document.getElementById("wg-" + slug); if (!target) return;
    var panel = target.closest("[data-women-panel]");
    if (panel || slug === "temy" || slug === "vse-analizy") {
      document.querySelectorAll("#women-guide [data-women-panel]").forEach(function(el){el.hidden = el !== panel;});
      document.querySelectorAll("#women-guide .pg-w-task-grid a").forEach(function(a){a.setAttribute("aria-current",panel && a.dataset.womenTarget === panel.id.slice(3) ? "true" : "false");});
    }
    if (target.tagName === "DETAILS") target.open = true;
    for (var parent = target.parentElement; parent && parent.id !== "women-guide"; parent = parent.parentElement) if (parent.tagName === "DETAILS") parent.open = true;
    var top = $("#top"), sw = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--sw-h"), 10) || 0;
    window.scrollTo({ top: Math.max(0, target.getBoundingClientRect().top + scrollY - (top ? top.offsetHeight : 94) - sw - 22), behavior: reduceMotion || !update ? "auto" : "smooth" });
    if (update) { state.gsec = slug; curHash = "for-women:" + slug; try { history.replaceState(null, "", "#" + curHash); } catch (error) { /* sandboxed preview */ } }
    var mobile = $("#women-guide .pg-mobile-toc"); if (mobile) mobile.open = false;
  }
  function renderWomenGuide() {
    if (gSpy) gSpy.disconnect(); var root = $("#women-guide"); root.innerHTML = WOMEN_TEMPLATE;
    root.querySelectorAll("[data-women-tests]").forEach(function (el) { el.innerHTML = el.dataset.womenTests.split(",").map(womenTest).join(""); });
    root.querySelector("[data-women-complexes]").innerHTML = (GUIDES.women.cx || []).map(womenComplex).join("");
    var cat = CATS.filter(function (item) { return item.id === "women"; })[0], codes = cat.items.filter(function (code, i, arr) { return A[code] && arr.indexOf(code) === i; });
    $("#wg-catalog-list").innerHTML = codes.map(womenTest).join(""); $("#wg-catalog-q").value = womenSearch; womenFilter();
    root.querySelector("[data-women-count]").textContent = nAn(codes.length);
    root.querySelector("[data-women-point]").textContent = "Цены и доступность: " + ptName(POINTS[state.pt]);
    var topics = Array.prototype.slice.call(root.querySelectorAll("[data-topic]"));
    var toc = topics.map(function (section) { var id = section.id.slice(3); return '<a href="#for-women:' + id + '" data-women-target="' + id + '">' + esc(section.dataset.topic) + '</a>'; }).join("");
    root.querySelectorAll("[data-women-toc]").forEach(function (el) { el.innerHTML = toc; });
    root.querySelector("[data-women-faq]").innerHTML = WOMEN_FAQ.map(function (f) { return '<details class="pg-more"><summary>' + esc(f[0]) + '</summary><div class="pg-detail-body"><p>' + esc(f[1]) + '</p></div></details>'; }).join("");
    womenSpy = new IntersectionObserver(function (entries) { entries.forEach(function (entry) { if (!entry.isIntersecting) return; root.querySelectorAll("[data-women-toc] a").forEach(function (a) { a.setAttribute("aria-current", a.dataset.womenTarget === entry.target.id.slice(3) ? "true" : "false"); }); }); }, { rootMargin: "-20% 0px -65% 0px" });
    topics.forEach(function (section) { womenSpy.observe(section); });
    var ld = $("#g-ld"); if (!ld) { ld = document.createElement("script"); ld.type = "application/ld+json"; ld.id = "g-ld"; document.head.appendChild(ld); }
    ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: WOMEN_FAQ.map(function (f) { return { "@type": "Question", name: f[0], acceptedAnswer: { "@type": "Answer", text: f[1] } }; }) });
    if (typeof decorateComparisonSlots === "function") decorateComparisonSlots(root);
    root.querySelectorAll("[data-women-panel]").forEach(function(panel){
      panel.hidden = true;
      panel.insertAdjacentHTML("afterbegin", '<a class="pg-w-panel-back" href="#for-women:temy" data-women-target="temy">← Выбрать другую тему</a>');
    });
    syncCart();
    if (state.gsec) { var slug = state.gsec; setTimeout(function () { if (state.view === "guide" && state.guide === "women") womenJump(slug, false); }, 80); }
  }
  $("#women-guide").addEventListener("click", function (event) { var anchor = event.target.closest("[data-women-target]"); if (anchor) { event.preventDefault(); event.stopPropagation(); womenJump(anchor.dataset.womenTarget, true); } });
  $("#women-guide").addEventListener("input", function (event) { if (event.target.id === "wg-catalog-q") { womenSearch = event.target.value; womenFilter(); } });
