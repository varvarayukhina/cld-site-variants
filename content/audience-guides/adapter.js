  /* AUDIENCE_TEMPLATES */
  var audienceSearch = {}, audienceSpy = null;
  function audienceFilter() {
    var q=(audienceSearch[state.guide]||"").trim().toLowerCase(),count=0;
    $$("#ag-catalog-list [data-preg-code]").forEach(function(row){var c=row.dataset.pregCode,a=A[c],match=!q||(c+" "+a.n+" "+a.off).toLowerCase().indexOf(q)>=0;row.hidden=!match;if(match)count++;});
    $("#ag-no-results").hidden=!!count;
  }
  function audienceSyncControls() {
    var root=$("#audience-guide");if(!root||root.hidden||!root.firstChild)return;
    root.querySelectorAll('[data-add]').forEach(function(b){var c=b.dataset.add,a=A[c]||CX[c];if(!a)return;b.disabled=!!a.na;var on=!!cart[c];b.classList.toggle('pg-added',on);b.textContent=a.na?'Недоступно':on?'В корзине ✓':'Добавить +';b.setAttribute('aria-label',a.na?'Недоступно в выбранном пункте':(on?'Убрать из корзины: ':'Добавить: ')+(A[c]?A[c].n:CXX[c].n));});
  }
  function audienceJump(slug,update) {
    var target=document.getElementById('ag-'+slug);if(!target)return;
    if(target.tagName==='DETAILS')target.open=true;
    for(var x=target.parentElement;x&&x.id!=='audience-guide';x=x.parentElement)if(x.tagName==='DETAILS')x.open=true;
    var top=$('#top'),sw=parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sw-h'),10)||0;
    window.scrollTo({top:Math.max(0,target.getBoundingClientRect().top+scrollY-(top?top.offsetHeight:94)-sw-22),behavior:reduceMotion||!update?'auto':'smooth'});
    if(update){state.gsec=slug;curHash='for-'+state.guide+':'+slug;try{history.replaceState(null,'','#'+curHash);}catch(e){}}
    if(slug==='vse-analizy')setTimeout(function(){var input=$('#ag-catalog-q');if(input)input.focus({preventScroll:true});},reduceMotion?0:350);
  }
  function renderAudienceGuide() {
    if(gSpy)gSpy.disconnect();var root=$('#audience-guide'),g=GUIDES[state.guide];root.innerHTML=AUDIENCE_TEMPLATES[state.guide];
    root.querySelectorAll('[data-audience-tests]').forEach(function(el){el.innerHTML=el.dataset.audienceTests.split(',').map(pregTest).join('');});
    root.querySelectorAll('[data-sg-chips]').forEach(function(el){el.innerHTML=el.dataset.sgChips.split(',').filter(function(c){return A[c];}).map(function(c){return '<a class="pg-sg-chip" href="#card-'+esc(c)+'" data-go="card:'+esc(c)+'">'+esc(pregName(c))+'</a>';}).join('');}); // названия анализов в схеме и подготовке
    var cxBox=root.querySelector('[data-audience-complexes]');if(cxBox)cxBox.innerHTML=(g.cx||[]).map(womenComplex).join('');
    var cat=CATS.filter(function(c){return c.id===state.guide;})[0],codes=cat.items.filter(function(c,i,a){return A[c]&&a.indexOf(c)===i;});
    $('#ag-catalog-list').innerHTML=codes.map(pregTest).join('');$('#ag-catalog-q').value=audienceSearch[state.guide]||"";audienceFilter();
    root.querySelector('[data-audience-count]').textContent=nAn(codes.length);root.querySelector('[data-audience-point]').textContent='Цены и доступность: '+ptName(POINTS[state.pt]);
    root.querySelector('[data-audience-faq]').innerHTML=(g.faq||[]).map(function(f){return '<details class="pg-more"><summary>'+esc(f.q)+'</summary><div class="pg-detail-body"><p>'+esc(f.a)+'</p></div></details>';}).join('');
    var ld=$('#g-ld');if(!ld){ld=document.createElement('script');ld.type='application/ld+json';ld.id='g-ld';document.head.appendChild(ld);}ld.textContent=JSON.stringify({'@context':'https://schema.org','@type':'FAQPage',mainEntity:(g.faq||[]).map(function(f){return {'@type':'Question',name:f.q,acceptedAnswer:{'@type':'Answer',text:f.a}};})});
    var topics=Array.prototype.slice.call(root.querySelectorAll('section[data-topic]'));
    root.querySelectorAll('[data-audience-toc]').forEach(function(el){el.innerHTML=topics.map(function(s){var id=s.id.slice(3);return '<a href="#for-'+state.guide+':'+id+'" data-audience-target="'+id+'">'+esc(s.dataset.topic)+'</a>';}).join('');});
    if(audienceSpy)audienceSpy.disconnect();
    audienceSpy=new IntersectionObserver(function(entries){entries.forEach(function(entry){if(!entry.isIntersecting)return;root.querySelectorAll('[data-audience-toc] a').forEach(function(a){a.setAttribute('aria-current',a.dataset.audienceTarget===entry.target.id.slice(3)?'true':'false');});});},{rootMargin:'-20% 0px -65% 0px'});
    topics.forEach(function(s){audienceSpy.observe(s);});
    syncCart();if(state.gsec){var slug=state.gsec,key=state.guide;setTimeout(function(){if(state.view==='guide'&&state.guide===key)audienceJump(slug,false);},80);}
  }
  $('#audience-guide').addEventListener('click',function(e){var a=e.target.closest('[data-audience-target]');if(a){e.preventDefault();e.stopPropagation();audienceJump(a.dataset.audienceTarget,true);}});
  $('#audience-guide').addEventListener('input',function(e){if(e.target.id==='ag-catalog-q'){audienceSearch[state.guide]=e.target.value;audienceFilter();}});
