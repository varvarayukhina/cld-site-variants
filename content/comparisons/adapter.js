  /* COMPARISON_DATA */
  var comparisonOrigin = null, comparisonNavigating = false;
  function comparisonTeaser(key) {
    var a = COMPARISONS[key];
    return '<button type="button" class="cmp-teaser" data-comparison="' + key + '"><span><small>Разобраться перед выбором</small><b>' + esc(a.shortTitle) + '</b></span><span aria-hidden="true">↗</span></button>';
  }
  function comparisonProducts(a) {
    return a.tests.filter(function(c){return A[c];}).map(function(c){
      var x=A[c];return '<div class="cmp-product"><div><b>'+esc(x.n)+'</b><small>'+esc(x.off || '')+'</small></div><div class="cmp-price">'+(x.na?'Нет в выбранном пункте':'<b>'+rub(online(x.p))+'</b><small>на сайте · в пункте '+rub(x.p)+'</small>')+'</div>'+(x.na?'':'<button class="btn btn-lime" type="button" data-add="'+c+'">Добавить</button>')+'</div>';
    }).join('');
  }
  function comparisonPara(x) {
    if (typeof x === 'string') return '<p>'+esc(x)+'</p>';
    if (x && x.list) return '<ul>'+x.list.map(function(t){return '<li>'+esc(t)+'</li>';}).join('')+'</ul>';
    return '';
  }
  function comparisonBody(key,full) {
    var a=COMPARISONS[key];
    var head='<p class="cmp-intro">'+esc(a.intro)+'</p>'+(full&&a.situation?'<p class="cmp-situation">'+esc(a.situation)+'</p>':'');
    var grid='<div class="cmp-grid">'+a.items.map(function(x,i){return '<section class="cmp-item"><span class="cmp-number">0'+(i+1)+'</span><h2>'+esc(x.title)+'</h2><h3>'+esc(x.question)+'</h3><p>'+esc(x.text)+'</p></section>';}).join('')+'</div><div class="cmp-outcome"><b>Как это помогает выбрать исследование</b><p>'+esc(a.use)+'</p></div>';
    var sections=full?(a.sections||[]).map(function(s){return '<section class="cmp-section"><h2>'+esc(s.h)+'</h2>'+s.p.map(comparisonPara).join('')+'</section>';}).join(''):'';
    var prep=full?'<section class="cmp-prep"><h2>Подготовка</h2><p>'+esc(a.preparation)+'</p></section>':'<details class="cmp-detail"><summary>Как подготовиться</summary><p>'+esc(a.preparation)+'</p></details>';
    var faq=a.details.map(function(d){return '<details class="cmp-detail"><summary>'+esc(d[0])+'</summary><p>'+esc(d[1])+'</p></details>';}).join('');
    if(full&&a.details.length)faq='<section class="cmp-faq"><h2>Частые вопросы</h2>'+faq+'</section>';
    var buy='<section class="cmp-buy"><h2>Исследования по теме</h2><p class="cmp-point">Цены и доступность: '+esc(ptName(POINTS[state.pt]))+'</p>'+comparisonProducts(a)+(a.availability?'<p>'+esc(a.availability)+'</p>':'')+'<p class="cmp-note">Состав исследований сверяют с назначением. Сдавать все анализы из сравнения требуется не каждому.</p></section>';
    var related=full?(a.related||[]).filter(function(k){return COMPARISONS[k]&&k!==key;}):[];
    var rel=related.length?'<section class="cmp-related"><h2>Читайте также</h2><div class="cmp-related-list">'+related.map(function(k){return '<a href="#compare-'+k+'" data-go="compare:'+k+'">'+esc(COMPARISONS[k].title)+'</a>';}).join('')+'</div></section>':'';
    return head+grid+sections+prep+faq+buy+rel;
  }
  function comparisonsForTest(code) {
    return Object.keys(COMPARISONS).filter(function(k){return COMPARISONS[k].tests.indexOf(code)>=0;});
  }
  function cardComparisons(code) {
    var keys=comparisonsForTest(code);if(!keys.length)return '';
    return '<section class="cmp-card-links"><h2>Чем отличается от похожих анализов</h2>'+keys.map(function(k){return '<a href="#compare-'+k+'" data-go="compare:'+k+'">'+esc(COMPARISONS[k].title)+' →</a>';}).join('')+'</section>';
  }
  function comparisonSync() {
    document.querySelectorAll('.cmp-root [data-add]').forEach(function(b){var c=b.dataset.add;b.textContent=cart[c]?'В корзине ✓':'Добавить +';b.setAttribute('aria-pressed',cart[c]?'true':'false');b.setAttribute('aria-label',(cart[c]?'Убрать из корзины: ':'Добавить: ')+A[c].n);});
    var cartLink=document.querySelector('#comparison-dialog [data-comparison-cart]');if(cartLink) cartLink.hidden=!cartCount();
  }
  function decorateComparisonSlots(root) {
    root.querySelectorAll('[data-comparison-slot]').forEach(function(el){el.innerHTML=comparisonTeaser(el.dataset.comparisonSlot);});
  }
  function decorateGuideComparisons() {
    var map={men:{glucose:'glucose'},senior:{glucose:'glucose',iron:'iron'},kids:{iron:'iron'}};
    var rules=map[state.guide]||{};
    GUIDES[state.guide].sections.forEach(function(s){var key=null; if(/сахар|глюкоз/i.test(s.h))key=rules.glucose;if(/желез|анеми/i.test(s.h))key=rules.iron;var el=document.getElementById(s.id);if(key&&el&&!el.querySelector('[data-comparison]'))el.insertAdjacentHTML('beforeend',comparisonTeaser(key));});
  }
  function closeComparison(navigation) {
    var d=document.getElementById('comparison-dialog');if(d.open){comparisonNavigating=!!navigation;d.close();}
  }
  function openComparison(key,trigger) {
    if(!COMPARISONS[key])return;
    comparisonOrigin={y:scrollY,trigger:trigger};comparisonNavigating=false;
    var d=document.getElementById('comparison-dialog');
    d.querySelector('.cmp-dialog-content').innerHTML='<h1 id="cmp-dialog-title">'+esc(COMPARISONS[key].title)+'</h1>'+comparisonBody(key,false)+(COMPARISONS[key].sections?'<p class="cmp-full-link"><a href="#compare-'+key+'" data-go="compare:'+key+'">Читать статью целиком →</a></p>':'');
    d.showModal();document.documentElement.classList.add('cmp-modal-open');d.scrollTop=0;comparisonSync();
  }
  function renderComparisonPage() {
    var key=state.comparison||'iron',a=COMPARISONS[key];
    document.getElementById('comparison-page').innerHTML='<a class="cmp-back" href="#comparisons" data-go="comparisons">← Справочник об анализах</a><h1>'+esc(a.title)+'</h1>'+comparisonBody(key,true)+'<a class="btn btn-navy" href="#cart" data-go="cart">Перейти в корзину</a>';
    var ld=$('#g-ld');if(!ld){ld=document.createElement('script');ld.type='application/ld+json';ld.id='g-ld';document.head.appendChild(ld);}ld.textContent=JSON.stringify({'@context':'https://schema.org','@type':'FAQPage',mainEntity:a.details.map(function(d){return {'@type':'Question',name:d[0],acceptedAnswer:{'@type':'Answer',text:d[1]}};})});
    comparisonSync();
  }
  var COMPARISON_GROUPS = [
    { id: 'krov', n: 'Кровь и воспаление', ic: 'blood', keys: ['iron', 'inflammation', 'b12'] },
    { id: 'serdce', n: 'Сердце, сосуды и сахар', ic: 'heart', keys: ['lipids', 'glucose'] },
    { id: 'pechen', n: 'Печень, почки и моча', ic: 'liver', keys: ['liver', 'kidneys', 'urine'] },
    { id: 'gormony', n: 'Гормоны и щитовидная железа', ic: 'thyroid', keys: ['hormones', 'thyroid'] },
    { id: 'muzhskoe', n: 'Мужское здоровье', ic: 'men', keys: ['testosterone', 'psa'] },
    { id: 'allergiya', n: 'Аллергия', ic: 'allergy', keys: ['allergy', 'food-intolerance'] }
  ];
  function comparisonGroups() {
    var used = {}, groups = COMPARISON_GROUPS.map(function (g) { var keys = g.keys.filter(function (k) { return COMPARISONS[k]; }); keys.forEach(function (k) { used[k] = 1; }); return { id: g.id, n: g.n, ic: g.ic, keys: keys }; }).filter(function (g) { return g.keys.length; });
    var rest = Object.keys(COMPARISONS).filter(function (k) { return !used[k]; }); if (rest.length) groups.push({ id: 'drugoe', n: 'Другие исследования', ic: 'checkups', keys: rest });
    return groups;
  }
  function renderComparisonHub() {
    var groups = comparisonGroups(), total = groups.reduce(function (s, g) { return s + g.keys.length; }, 0);
    document.getElementById('comparison-hub-hero').innerHTML = '<div class="crumbs"><button type="button" data-go="home">Главная</button><span>/</span><span>Справочник об анализах</span></div>' +
      '<div class="cmp-hero-grid"><div><h1>Справочник об анализах</h1><p class="lede">Чем отличаются похожие анализы, что показывает каждый из них и как сопоставить исследования с назначением. ' + plural(total, ['статья', 'статьи', 'статей']) + ' по системам органов.</p>' +
      '<nav class="cmp-hub-nav" aria-label="Системы органов">' + groups.map(function (g) { return '<button type="button" data-hub-group="' + g.id + '"><span class="cmp-chip-ic">' + picto(g.ic) + '</span>' + esc(g.n) + ' <span class="cmp-chip-n">' + g.keys.length + '</span></button>'; }).join('') + '</nav></div>' +
      '<div class="cmp-hero-mosaic" aria-hidden="true">' + ['blood', 'heart', 'liver', 'thyroid', 'allergy', 'urine', 'sugar', 'men', 'hormones'].map(function (id) { return '<span>' + picto(id) + '</span>'; }).join('') + '</div></div>';
    var card = function (k, ic) { var a = COMPARISONS[k]; return '<a class="cmp-hub-card" href="#compare-' + k + '" data-go="compare:' + k + '"><span class="cmp-card-ic">' + picto(ic) + '</span><h3>' + esc(a.shortTitle) + '</h3><p>' + esc(a.intro) + '</p><b>Читать →</b></a>'; };
    document.getElementById('comparison-hub').innerHTML = groups.map(function (g) { return '<section class="cmp-hub-group" id="cmp-group-' + g.id + '"><h2><span class="cmp-group-ic">' + picto(g.ic) + '</span>' + esc(g.n) + '</h2><div class="cmp-hub-grid">' + g.keys.map(function (k) { return card(k, g.ic); }).join('') + '</div></section>'; }).join('');
  }
  document.addEventListener('click', function (e) { var b = e.target.closest('[data-hub-group]'); if (!b) return; var s = document.getElementById('cmp-group-' + b.dataset.hubGroup); if (!s) return; var top = document.getElementById('top'); window.scrollTo({ top: s.getBoundingClientRect().top + scrollY - (top ? top.offsetHeight : 94) - 16, behavior: reduceMotion ? 'auto' : 'smooth' }); });
  PAGES.push('comparisons','compare');RENDER.compare=renderComparisonPage;RENDER.comparisons=renderComparisonHub;
  document.addEventListener('click',function(e){var b=e.target.closest('[data-comparison]');if(b){e.preventDefault();openComparison(b.dataset.comparison,b);}if(e.target.closest('[data-comparison-close]'))closeComparison(false);});
  document.getElementById('comparison-dialog').addEventListener('close',function(){
    document.documentElement.classList.remove('cmp-modal-open');var origin=comparisonOrigin;comparisonOrigin=null;
    if(!comparisonNavigating&&origin)requestAnimationFrame(function(){if(origin.trigger&&origin.trigger.isConnected)origin.trigger.focus({preventScroll:true});window.scrollTo(0,origin.y);});
  });
