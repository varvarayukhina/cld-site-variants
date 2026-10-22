/* Переключатель вариантов дизайна. Фиксированная полоса сверху высотой var(--sw-h).
   Варианты ставят липкие шапки на top: var(--sw-h, 0px). Экран (#hash) при переключении сохраняется. */
(function () {
  var V = [
    { id: "v0", n: "Первый", d: "Первый прототип: подробная навигация и пояснения" },
    { id: "v1", n: "Поиск", d: "Главное — строка поиска и короткий список частых анализов" },
    { id: "v2", n: "Кнопки", d: "Крупные кнопки: человек выбирает, что ему нужно" },
    { id: "v3", n: "Помощник", d: "Сайт задаёт простые вопросы и подсказывает анализы" }
  ];
  var m = location.pathname.match(/\/(v[0-3])\//), cur = m ? m[1] : "v1", H = 40;
  document.documentElement.style.setProperty("--sw-h", H + "px");
  var css = document.createElement("style");
  css.textContent =
    ".cldsw{position:fixed;top:0;left:0;right:0;height:" + H + "px;z-index:9999;display:flex;align-items:center;gap:14px;padding:0 max(12px,env(safe-area-inset-left,0px));" +
    "background:#0B2230;color:#DCE6EB;font:500 13px/1 Montserrat,Arial,sans-serif;box-shadow:0 1px 0 rgba(255,255,255,.08)}" +
    ".cldsw b{font-weight:700;color:#FFF;white-space:nowrap}.cldsw .d{opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}" +
    ".cldsw nav{display:flex;gap:4px;background:rgba(255,255,255,.08);padding:3px;border-radius:999px;flex:none}" +
    ".cldsw a{color:#DCE6EB;text-decoration:none;padding:7px 12px;border-radius:999px;font-weight:600;white-space:nowrap}" +
    ".cldsw a[aria-current=page]{background:#AFC81E;color:#14374B}.cldsw a:focus-visible{outline:2px solid #AFC81E;outline-offset:2px}" +
    ".cldsw-gap{height:" + H + "px}@media (max-width:700px){.cldsw .d,.cldsw .t{display:none}.cldsw{justify-content:center}}@media (max-width:520px){.cldsw>b{display:none}.cldsw a{padding:7px 8px;font-size:12px}.cldsw nav{gap:2px}}";
  document.head.appendChild(css);
  var bar = document.createElement("div");
  bar.className = "cldsw"; bar.setAttribute("role", "navigation"); bar.setAttribute("aria-label", "Варианты дизайна");
  bar.innerHTML = '<b class="t">Прототип CLD</b><b>Вариант:</b><nav>' + V.map(function (v, i) {
    return '<a href="../' + v.id + '/" data-v="' + v.id + '"' + (v.id === cur ? ' aria-current="page"' : "") + ">" + v.id.slice(1) + " · " + v.n + "</a>";
  }).join("") + '</nav><span class="d">' + V.filter(function (v) { return v.id === cur; })[0].d + "</span>";
  function sync() { bar.querySelectorAll("a").forEach(function (a) { a.href = "../" + a.dataset.v + "/" + location.hash; }); }
  function mount() { var gap = document.createElement("div"); gap.className = "cldsw-gap"; document.body.prepend(gap); document.body.prepend(bar); sync(); }
  window.addEventListener("hashchange", sync);
  if (document.body) mount(); else document.addEventListener("DOMContentLoaded", mount);
})();
