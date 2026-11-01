  /* Approved content; all commercial state comes from the existing v4 application. */
  /* PREG_TEMPLATE */
  /* PREG_CALENDAR */
  /* PREG_FAQ */
  var pregStage = 1, pregSearch = "", pregOpen = {}, pregSpy = null;
  var pregAliases = { grafik: "calendar", zhelezo: "iron", sahar: "sugar", infekcii: "infections", rezus: "rhesus", podgotovka: "prepare", voprosy: "questions", "vse-analizy": "all-tests" };
  var pregCanonical = { calendar: "grafik", iron: "zhelezo", sugar: "sahar", infections: "infekcii", rhesus: "rezus", prepare: "podgotovka", questions: "voprosy", "all-tests": "vse-analizy" };
  function pregIcon(name) { return '<svg aria-hidden="true"><use href="#pg-i-' + name + '"/></svg>'; }
  function pregName(code) { return code === "18.103" ? "Тест на сахар с нагрузкой при беременности" : A[code].n; }
  function pregTest(code) {
    var a = A[code]; if (!a) return "";
    var note = code === "40-111" ? "При подозрении на дефицит железа" : code === "80-049" ? "По показаниям" : code === "18.103" ? "ПГТТ с 75 г глюкозы" : "";
    return '<div class="test-row" data-preg-code="' + esc(code) + '"><div class="test-info"><button class="test-name test-details" type="button" data-go="card:' + esc(code) + '">' + esc(pregName(code)) + '</button><small>' + esc(a.bio) + " · " + dLabel(a.days) + '</small>' + (a.na ? '<span class="preg-na">Нет в выбранном пункте — доступность в других пунктах можно уточнить по телефону</span>' : "") + (note ? '<span class="tag-note">' + note + '</span>' : "") + '</div><div class="test-price">' + (a.na ? "" : '<b class="num">' + rub(online(a.p)) + '</b><span>на сайте</span>') + '</div><button type="button" class="add-btn btn-lime" data-add="' + esc(code) + '"' + (a.na ? ' disabled aria-label="Недоступно в выбранном пункте"' : ' aria-label="Добавить: ' + esc(pregName(code)) + '"') + '>' + (a.na ? "Недоступно" : "Добавить +") + '</button></div>';
  }
  function pregSyncControls() {
    var root = $("#pregnancy-guide"); if (!root || root.hidden || !root.firstChild) return;
    root.querySelectorAll("[data-add]").forEach(function (button) {
      var code = button.dataset.add, a = A[code]; if (!a) return;
      button.disabled = !!a.na;
      if (a.na) { button.textContent = "Недоступно"; button.setAttribute("aria-label", "Недоступно в выбранном пункте"); return; }
      var on = !!cart[code]; button.classList.toggle("pg-added", on);
      button.innerHTML = on ? pregIcon("check") + " В корзине" : "Добавить +";
      button.setAttribute("aria-label", (on ? "Убрать из корзины: " : "Добавить: ") + pregName(code));
    });
  }
  function pregCalendar(index) {
    pregStage = index; var stage = PREG_STAGES[index], root = $("#pregnancy-guide"), panel = $("#pg-calendar-panel");
    root.querySelectorAll("[data-preg-stage]").forEach(function (button) {
      var on = +button.dataset.pregStage === index; button.setAttribute("aria-selected", String(on)); button.tabIndex = on ? 0 : -1;
    });
    panel.setAttribute("aria-labelledby", "pg-tab-" + index);
    panel.innerHTML = '<div class="calendar-head"><div><h3>' + esc(stage.title) + '</h3><p>' + esc(stage.desc) + '</p></div><span class="calendar-counter" aria-hidden="true">' + stage.label + '</span></div>' + stage.rows.map(function (row, j) {
      var id = "pg-cal-why-" + index + "-" + j, open = !!pregOpen[id];
      return '<div class="cal-row"><div class="cal-when">' + esc(row[0]) + '</div><div><h4>' + esc(row[1]) + '</h4><p>' + esc(row[2]) + '</p></div><button type="button" class="cal-go" data-preg-why="' + id + '" aria-controls="' + id + '" aria-expanded="' + open + '">' + (open ? "Свернуть −" : "Зачем +") + '</button></div><div class="cal-explanation" id="' + id + '"' + (open ? "" : " hidden") + ' role="region" aria-label="Зачем: ' + esc(row[1]) + '"><p>' + esc(PREG_WHY[index][j]) + '</p></div>';
    }).join("") + '<div class="cal-note">' + pregIcon("info") + '<span>' + esc(stage.note) + '</span></div>';
  }
  function pregFilter() {
    var count = 0, q = pregSearch.trim().toLowerCase();
    $$("#pg-catalog-list [data-preg-code]").forEach(function (row) {
      var code = row.dataset.pregCode, a = A[code], match = !q || (code + " " + a.n + " " + a.off + " " + pregName(code)).toLowerCase().indexOf(q) >= 0;
      row.hidden = !match; if (match) count++;
    });
    $("#pg-no-results").hidden = !!count;
  }
  function pregJump(slug, update) {
    var key = pregAliases[slug] || slug, target = document.getElementById("pg-" + key);
    if (!target) return;
    if (target.tagName === "DETAILS") target.open = true;
    for (var parent = target.parentElement; parent && parent.id !== "pregnancy-guide"; parent = parent.parentElement) if (parent.tagName === "DETAILS") parent.open = true;
    var top = $("#top"), sw = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--sw-h"), 10) || 0;
    window.scrollTo({ top: Math.max(0, target.getBoundingClientRect().top + window.scrollY - (top ? top.offsetHeight : 94) - sw - 22), behavior: reduceMotion || !update ? "auto" : "smooth" });
    if (update) {
      state.gsec = pregCanonical[key] || slug; curHash = "for-pregnant:" + state.gsec;
      try { history.replaceState(null, "", "#" + curHash); } catch (error) { /* sandboxed preview */ }
    }
    var mobile = $("#pregnancy-guide .pg-mobile-toc"); if (mobile) mobile.open = false;
  }
  function renderPregnancyGuide() {
    if (gSpy) gSpy.disconnect();
    var root = $("#pregnancy-guide"); root.innerHTML = PREG_TEMPLATE;
    root.querySelectorAll("[data-tests]").forEach(function (el) { el.innerHTML = el.dataset.tests.split(",").map(pregTest).join(""); });
    var cat = CATS.filter(function (item) { return item.id === "pregnant"; })[0], codes = cat.items.filter(function (code, i, arr) { return A[code] && arr.indexOf(code) === i; });
    $("#pg-catalog-list").innerHTML = codes.map(pregTest).join("");
    $("#pg-catalog-q").value = pregSearch; pregFilter();
    root.querySelector(".pg-catalog-heading > span").textContent = nAn(codes.length);
    root.querySelector("[data-preg-point]").textContent = "Цены и доступность: " + ptName(POINTS[state.pt]);
    pregCalendar(pregStage);
    var topics = Array.prototype.slice.call(root.querySelectorAll("[data-topic]"));
    var toc = topics.map(function (section) { var id = section.id.slice(3), slug = pregCanonical[id] || id; return '<a href="#for-pregnant:' + slug + '" data-preg-target="' + id + '">' + esc(section.dataset.topic) + '</a>'; }).join("");
    root.querySelectorAll("[data-toc-links]").forEach(function (el) { el.innerHTML = toc; });
    pregSpy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { if (!entry.isIntersecting) return; root.querySelectorAll("[data-toc-links] a").forEach(function (a) { a.setAttribute("aria-current", a.dataset.pregTarget === entry.target.id.slice(3) ? "true" : "false"); }); });
    }, { rootMargin: "-20% 0px -65% 0px" });
    topics.forEach(function (section) { pregSpy.observe(section); });
    document.title = "Анализы при беременности: календарь исследований | CLD";
    var meta = document.querySelector('meta[name="description"]'); if (!meta) { meta = document.createElement("meta"); meta.name = "description"; document.head.appendChild(meta); }
    meta.content = "Календарь анализов при беременности: зачем назначают исследования на разных сроках, что показывают результаты, подготовка и цены в выбранном пункте CLD.";
    var ld = $("#g-ld"); if (!ld) { ld = document.createElement("script"); ld.type = "application/ld+json"; ld.id = "g-ld"; document.head.appendChild(ld); } ld.textContent = JSON.stringify(PREG_FAQ);
    if (typeof decorateComparisonSlots === "function") decorateComparisonSlots(root);
    syncCart();
    if (state.gsec) { var slug = state.gsec; setTimeout(function () { if (state.view === "guide" && state.guide === "pregnant") pregJump(slug, false); }, 80); }
  }
  $("#pregnancy-guide").addEventListener("click", function (event) {
    var stage = event.target.closest("[data-preg-stage]"); if (stage) { event.preventDefault(); pregCalendar(+stage.dataset.pregStage); return; }
    var why = event.target.closest("[data-preg-why]"); if (why) {
      var id = why.dataset.pregWhy, on = why.getAttribute("aria-expanded") !== "true"; pregOpen[id] = on; why.setAttribute("aria-expanded", String(on)); why.textContent = on ? "Свернуть −" : "Зачем +"; document.getElementById(id).hidden = !on; return;
    }
    var anchor = event.target.closest("[data-preg-target]"); if (anchor) { event.preventDefault(); event.stopPropagation(); pregJump(anchor.dataset.pregTarget, true); }
  });
  $("#pregnancy-guide").addEventListener("input", function (event) { if (event.target.id === "pg-catalog-q") { pregSearch = event.target.value; pregFilter(); } });
  $("#pregnancy-guide").addEventListener("keydown", function (event) {
    var button = event.target.closest("[data-preg-stage]"); if (!button) return;
    var index = +button.dataset.pregStage;
    if (event.key === "ArrowRight") index = (index + 1) % 4; else if (event.key === "ArrowLeft") index = (index + 3) % 4; else if (event.key === "Home") index = 0; else if (event.key === "End") index = 3; else return;
    event.preventDefault(); pregCalendar(index); $("#pregnancy-guide [data-preg-stage='" + index + "']").focus();
  });
