/* Заставка CLD: лаймовый экран с логотипом при первом заходе за сеанс.
   Держится, пока грузится страница: не меньше 450 мс, не больше 900 мс. Подключать в <head>. */
(function () {
  try { if (sessionStorage.getItem("cldSplash")) return; sessionStorage.setItem("cldSplash", "1"); } catch (e) { return; }
  var d = document.documentElement, t0 = Date.now(), over = false;
  var logo = "../assets/cld-logo-horizontal-navy.svg";
  var pre = document.createElement("link"); pre.rel = "preload"; pre.as = "image"; pre.href = logo; document.head.appendChild(pre);
  var st = document.createElement("style");
  st.textContent = "html.splash::after{content:'';position:fixed;inset:0;z-index:100000;background:#AFC81E url('" + logo + "') center/min(64vw,520px) auto no-repeat;transition:opacity .35s cubic-bezier(.23,1,.32,1),visibility 0s linear .35s}" +
    "html.splash-out::after{opacity:0;visibility:hidden}" +
    "@media (prefers-reduced-motion: reduce){html.splash::after{transition:none}}";
  document.head.appendChild(st);
  d.classList.add("splash");
  function done() {
    if (over) return; over = true;
    setTimeout(function () {
      d.classList.add("splash-out");
      setTimeout(function () { d.classList.remove("splash", "splash-out"); }, 400);
    }, Math.max(0, 450 - (Date.now() - t0)));
  }
  if (document.readyState === "complete") done(); else window.addEventListener("load", done);
  setTimeout(done, 900);
})();
