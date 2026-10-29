/* Переключатель вариантов дизайна. Фиксированная полоса сверху высотой var(--sw-h).
   Варианты ставят липкие шапки на top: var(--sw-h, 0px). Экран (#hash) при переключении сохраняется. */
(function () {
  var V = [
    { id: "v0", n: "До встречи", d: "Прототип, который показывали 28.10" },
    { id: "v4", n: "После встречи 28.10", d: "Поиск в шапке, цены выбранного пункта, экспресс и ЦИТО" }
  ];
  var EXTRA = '<a href="../v4/headers.html" data-x="headers"' + (/headers\.html/.test(location.pathname) ? ' aria-current="page"' : "") + ">5 шапок</a>"; // страница с вариантами шапки
  var m = location.pathname.match(/\/(v\d)\//), cur = m ? m[1] : "v0", H = 40;
  document.documentElement.style.setProperty("--sw-h", H + "px");
  var css = document.createElement("style");
  css.textContent =
    ".cldsw{position:fixed;top:0;left:0;right:0;height:" + H + "px;z-index:9999;display:flex;align-items:center;gap:14px;padding:0 max(12px,env(safe-area-inset-left,0px));" +
    "background:#0B2230;color:#DCE6EB;font:500 16px/1.3 Montserrat,Arial,sans-serif;box-shadow:0 1px 0 rgba(255,255,255,.08)}" +
    ".cldsw b{font-weight:700;color:#FFF;white-space:nowrap}.cldsw .d{opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}" +
    ".cldsw nav{display:flex;gap:4px;background:rgba(255,255,255,.08);padding:3px;border-radius:999px;flex:none}" +
    ".cldsw a{color:#DCE6EB;text-decoration:none;padding:7px 12px;border-radius:999px;font-weight:600;white-space:nowrap}" +
    ".cldsw a[aria-current=page]{background:#AFC81E;color:#14374B}.cldsw a:focus-visible{outline:2px solid #AFC81E;outline-offset:2px}" +
    
    ".cldsw a,.cldsw b,.cldsw .d{font-size:16px}.cldsw-gap{height:" + H + "px}@media (max-width:700px){.cldsw .d,.cldsw .t{display:none}.cldsw{justify-content:center}}@media (max-width:520px){.cldsw{justify-content:flex-start}.cldsw nav{overflow-x:auto;scrollbar-width:none;max-width:100%}.cldsw nav::-webkit-scrollbar{display:none}.cldsw>b,.cldsw .rep{display:none}.cldsw a{padding:7px 10px;font-size:16px}.cldsw nav{gap:2px}}";
  document.head.appendChild(css);
  var bar = document.createElement("div");
  bar.className = "cldsw"; bar.setAttribute("role", "navigation"); bar.setAttribute("aria-label", "Варианты дизайна");
  bar.innerHTML = '<b class="t">Прототип CLD</b><b>Вариант:</b><nav>' + V.map(function (v, i) {
    return '<a href="../' + v.id + '/" data-v="' + v.id + '"' + (v.id === cur && !/headers\.html/.test(location.pathname) ? ' aria-current="page"' : "") + ">" + v.n + "</a>";
  }).join("") + EXTRA + '</nav><span class="d">' + (/headers\.html/.test(location.pathname) ? "Пять вариантов шапки — выбрать один" : V.filter(function (v) { return v.id === cur; })[0].d) + "</span>";
  function sync() { bar.querySelectorAll("a[data-v]").forEach(function (a) { a.href = "../" + a.dataset.v + "/" + location.hash; }); /* only variant links, not «Отчёт»/«PDF» */ }
  function mount() { var gap = document.createElement("div"); gap.className = "cldsw-gap"; document.body.prepend(gap); document.body.prepend(bar); sync(); }
  window.addEventListener("hashchange", sync);
  if (document.body) mount(); else document.addEventListener("DOMContentLoaded", mount);
})();
