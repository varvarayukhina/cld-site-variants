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
    document.getElementById('comparison-page').innerHTML='<a class="cmp-back" href="#comparisons" data-go="comparisons">← Об анализах</a><h1>'+esc(a.title)+'</h1>'+comparisonBody(key,true)+'<a class="btn btn-navy" href="#cart" data-go="cart">Перейти в корзину</a>';
    var ld=$('#g-ld');if(!ld){ld=document.createElement('script');ld.type='application/ld+json';ld.id='g-ld';document.head.appendChild(ld);}ld.textContent=JSON.stringify({'@context':'https://schema.org','@type':'FAQPage',mainEntity:a.details.map(function(d){return {'@type':'Question',name:d[0],acceptedAnswer:{'@type':'Answer',text:d[1]}};})});
    comparisonSync();
  }
  function renderComparisonHub() {
    document.getElementById('comparison-hub').innerHTML='<h1>Об анализах: чем отличаются похожие исследования</h1><p class="cmp-intro">Разбираемся, что показывает каждый анализ и как сопоставить исследования с назначением.</p><div class="cmp-hub-grid">'+Object.keys(COMPARISONS).map(function(k){var a=COMPARISONS[k];return '<a class="cmp-hub-card" href="#compare-'+k+'" data-go="compare:'+k+'"><h2>'+esc(a.shortTitle)+'</h2><p>'+esc(a.intro)+'</p><b>Разобраться →</b></a>';}).join('')+'</div>';
  }
  PAGES.push('comparisons','compare');RENDER.compare=renderComparisonPage;RENDER.comparisons=renderComparisonHub;
  document.addEventListener('click',function(e){var b=e.target.closest('[data-comparison]');if(b){e.preventDefault();openComparison(b.dataset.comparison,b);}if(e.target.closest('[data-comparison-close]'))closeComparison(false);});
  document.getElementById('comparison-dialog').addEventListener('close',function(){
    document.documentElement.classList.remove('cmp-modal-open');var origin=comparisonOrigin;comparisonOrigin=null;
    if(!comparisonNavigating&&origin)requestAnimationFrame(function(){if(origin.trigger&&origin.trigger.isConnected)origin.trigger.focus({preventScroll:true});window.scrollTo(0,origin.y);});
  });
