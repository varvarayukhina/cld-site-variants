/* Заставка CLD: лаймовый экран с логотипом при первом заходе за сеанс (с ?splash в адресе — всегда).
   Держится, пока грузится страница: не меньше 600 мс, не больше 1 с. Подключать в <head>. */
(function () {
  var force = /[?&]splash\b/.test(location.search); // ?splash — показать всегда, для демонстрации
  if (!force) { try { if (sessionStorage.getItem("cldSplash")) return; sessionStorage.setItem("cldSplash", "1"); } catch (e) { return; } }
  var t0 = Date.now(), over = false;
  var st = document.createElement("style");
  st.textContent =
    "#cld-splash{position:fixed;inset:0;z-index:2147483647;display:grid;place-items:center;background:#AFC81E;transition:opacity .4s cubic-bezier(.23,1,.32,1),visibility 0s linear .4s}" +
    "#cld-splash img{width:min(64vw,520px);height:auto;animation:cldsp-in .5s cubic-bezier(.23,1,.32,1) both}" +
    "#cld-splash.out{opacity:0;visibility:hidden}" +
    "@keyframes cldsp-in{from{opacity:0;transform:scale(.96)}}" +
    "@media (prefers-reduced-motion: reduce){#cld-splash{transition:none}#cld-splash img{animation:none}}";
  document.head.appendChild(st);
  var el = document.createElement("div");
  el.id = "cld-splash"; el.setAttribute("aria-hidden", "true");
  el.innerHTML = '<img src="../assets/cld-logo-horizontal-navy.svg" alt="">';
  document.documentElement.appendChild(el); // до <body>: закрывает страницу с первого кадра
  function done() {
    if (over) return; over = true;
    setTimeout(function () {
      el.classList.add("out");
      setTimeout(function () { el.remove(); }, 450);
    }, Math.max(0, 600 - (Date.now() - t0)));
  }
  if (document.readyState === "complete") done(); else window.addEventListener("load", done);
  setTimeout(done, 1000);
})();
