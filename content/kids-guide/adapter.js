  /* KIDS_TEMPLATE */
  var kidsSpy = null, kidsSearch = "";
  var KIDS_FAQ = [["Какие анализы входят в профосмотр ребёнка?", "Общий анализ крови и мочи — в 3 и 12 месяцев, в 3, 6, 10, 15, 16 и 17 лет. В 6 и 10 лет детям из группы риска определяют холестерин."], ["Нужен ли ребёнку анализ на витамин D?", "Профилактику витамином D клинические рекомендации советуют всем детям. Анализ нужен при подозрении на рахит или дефицит, при факторах риска и при лечении лечебными дозами."], ["Покажет ли общий IgE, на что аллергия?", "Нет. Конкретный аллерген ищут по специфическим IgE, общий IgE для этого неинформативен."], ["Зачем ферритин, если гемоглобин в норме?", "Ферритин отражает запасы железа, а дефицит железа бывает и без анемии."], ["Проверяют ли сахар на профосмотре?", "Глюкоза не входит в перечень исследований профосмотра детей. Её назначает врач по показаниям."]];
  function kidsIcon(name) { return '<svg aria-hidden="true"><use href="#kg-i-' + name + '"/></svg>'; }
  function kidsTest(code) {
    var html = pregTest(code), flag = { "40-297": "По назначению врача", "60-011": "Не определяет конкретный аллерген" }[code];
    return flag ? html.replace('</small>', '</small><span class="pg-tag-note">' + flag + '</span>') : html;
  }
  function kidsComplex(code) {
    var x = CXX[code], price = CX[code]; if (!x || !price) return "";
    return '<article class="pg-w-complex"><h3><a href="#card-' + esc(code) + '" data-go="card:' + esc(code) + '">' + esc(x.n) + '</a></h3><p>' + esc(x.parts.join(", ")) + '.</p>' + (price.na ? '<p class="pg-w-complex-na">Нет в выбранном пункте</p>' : '<div class="pg-w-complex-price"><span><b class="num">' + rub(online(price.p)) + '</b><small>на сайте · в пункте ' + rub(price.p) + '</small></span><button type="button" class="pg-add-btn" data-add="' + esc(code) + '">Добавить +</button></div>') + '</article>';
  }
  function kidsSyncControls() {
    var root = $("#kids-guide"); if (!root || root.hidden || !root.firstChild) return;
    root.querySelectorAll("[data-add]").forEach(function (button) {
      var code = button.dataset.add, entry = A[code] || CX[code]; if (!entry) return;
      button.disabled = !!entry.na;
      if (entry.na) { button.textContent = "Недоступно"; button.setAttribute("aria-label", "Недоступно в выбранном пункте"); return; }
      var on = !!cart[code], title = A[code] ? A[code].n : CXX[code].n;
      button.classList.toggle("pg-added", on); button.innerHTML = on ? kidsIcon("check") + " В корзине" : "Добавить +";
      button.setAttribute("aria-label", (on ? "Убрать из корзины: " : "Добавить: ") + title);
    });
  }
  function kidsFilter() {
    var count = 0, q = kidsSearch.trim().toLowerCase();
    $$("#kg-catalog-list [data-preg-code]").forEach(function (row) { var c = row.dataset.pregCode, a = A[c], match = !q || (c + " " + a.n + " " + a.off).toLowerCase().indexOf(q) >= 0; row.hidden = !match; if (match) count++; });
    $("#kg-no-results").hidden = !!count;
  }
  function kidsJump(slug, update) {
    var target = document.getElementById("kg-" + slug); if (!target) return;

    if (target.tagName === "DETAILS") target.open = true;
    for (var parent = target.parentElement; parent && parent.id !== "kids-guide"; parent = parent.parentElement) if (parent.tagName === "DETAILS") parent.open = true;
    var top = $("#top"), sw = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--sw-h"), 10) || 0;
    window.scrollTo({ top: Math.max(0, target.getBoundingClientRect().top + scrollY - (top ? top.offsetHeight : 94) - sw - 22), behavior: reduceMotion || !update ? "auto" : "smooth" });
    if (update) { state.gsec = slug; curHash = "for-kids:" + slug; try { history.replaceState(null, "", "#" + curHash); } catch (error) { /* sandboxed preview */ } }
    var mobile = $("#kids-guide .pg-mobile-toc"); if (mobile) mobile.open = false;
  }
  function renderKidsGuide() {
    if (gSpy) gSpy.disconnect(); var root = $("#kids-guide"); root.innerHTML = KIDS_TEMPLATE;
    root.querySelectorAll("[data-kids-tests]").forEach(function (el) { el.innerHTML = el.dataset.kidsTests.split(",").map(kidsTest).join(""); });
    root.querySelector("[data-kids-complexes]").innerHTML = (GUIDES.kids.cx || []).map(kidsComplex).join("");
    var cat = CATS.filter(function (item) { return item.id === "kids"; })[0], codes = cat.items.filter(function (code, i, arr) { return A[code] && arr.indexOf(code) === i; });
    $("#kg-catalog-list").innerHTML = codes.map(kidsTest).join(""); $("#kg-catalog-q").value = kidsSearch; kidsFilter();
    root.querySelector("[data-kids-count]").textContent = nAn(codes.length);
    root.querySelector("[data-kids-point]").textContent = "Цены и доступность: " + ptName(POINTS[state.pt]);
    var topics = Array.prototype.slice.call(root.querySelectorAll("[data-topic]"));
    var toc = topics.map(function (section) { var id = section.id.slice(3); return '<a href="#for-kids:' + id + '" data-kids-target="' + id + '">' + esc(section.dataset.topic) + '</a>'; }).join("");
    root.querySelectorAll("[data-kids-toc]").forEach(function (el) { el.innerHTML = toc; });
    root.querySelector("[data-kids-faq]").innerHTML = KIDS_FAQ.map(function (f) { return '<details class="pg-more"><summary>' + esc(f[0]) + '</summary><div class="pg-detail-body"><p>' + esc(f[1]) + '</p></div></details>'; }).join("");
    kidsSpy = new IntersectionObserver(function (entries) { entries.forEach(function (entry) { if (!entry.isIntersecting) return; root.querySelectorAll("[data-kids-toc] a").forEach(function (a) { a.setAttribute("aria-current", a.dataset.kidsTarget === entry.target.id.slice(3) ? "true" : "false"); }); }); }, { rootMargin: "-20% 0px -65% 0px" });
    topics.forEach(function (section) { kidsSpy.observe(section); });
    var ld = $("#g-ld"); if (!ld) { ld = document.createElement("script"); ld.type = "application/ld+json"; ld.id = "g-ld"; document.head.appendChild(ld); }
    ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: KIDS_FAQ.map(function (f) { return { "@type": "Question", name: f[0], acceptedAnswer: { "@type": "Answer", text: f[1] } }; }) });
    if (typeof decorateComparisonSlots === "function") decorateComparisonSlots(root);
    syncCart();
    if (state.gsec) { var slug = state.gsec; setTimeout(function () { if (state.view === "guide" && state.guide === "kids") kidsJump(slug, false); }, 80); }
  }
  $("#kids-guide").addEventListener("click", function (event) { var anchor = event.target.closest("[data-kids-target]"); if (anchor) { event.preventDefault(); event.stopPropagation(); kidsJump(anchor.dataset.kidsTarget, true); } });
  $("#kids-guide").addEventListener("input", function (event) { if (event.target.id === "kg-catalog-q") { kidsSearch = event.target.value; kidsFilter(); } });
