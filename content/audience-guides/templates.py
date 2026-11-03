"""Editorial audience templates: source explanations before native purchase controls."""
from pathlib import Path
from html import escape as esc
import json,re
BASE=Path(__file__).resolve().parent

def para(x):
 if isinstance(x,str):return '' if x.startswith('[[t:') else '<p>'+esc(x)+'</p>'
 if 'list' in x:return '<ul>'+''.join('<li>'+esc(t)+'</li>' for t in x['list'])+'</ul>'
 if 'h3' in x:return '<h3>'+esc(x['h3'])+'</h3>'
 if 'table' in x:
  t=x['table'];return '<div class="ag-table-wrap"><table class="ag-table"><thead><tr>'+''.join('<th scope="col">'+esc(h)+'</th>' for h in t['head'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td data-label="'+esc(t['head'][i])+'">'+esc(v)+'</td>' for i,v in enumerate(row))+'</tr>' for row in t['rows'])+'</tbody></table></div>'
 return ''
def small_cards(items):return '<div class="ag-compare">'+''.join('<article><h3>'+esc(a)+'</h3><p>'+esc(b)+'</p></article>' for a,b in items)+'</div>'
def template(key):
 g=json.loads((BASE/(key+'.json')).read_text());titles={
 'senior':{'serdce':'Холестерин и NT-proBNP: разные задачи','sahar':'Глюкоза и гликированный гемоглобин: в чём разница?','pochki':'Что показывают креатинин и СКФ?','mno':'Зачем контролируют МНО при приёме варфарина?','shchitovidka':'Как ТТГ используют для контроля лечения?','vitaminy':'Анемия, B12 и витамин D: разные причины обследования','psa':'Когда назначают ПСА мужчинам старшего возраста?'},
 'men':{'testosteron':'Зачем вместе с тестостероном назначают ГСПГ?','psa':'Повышенный ПСА — это обязательно рак?','holesterin':'Что можно узнать по липидному профилю?','sahar':'Что показывает гликированный гемоглобин?','mochevaya-kislota':'Высокая мочевая кислота — это подагра?','pechen':'Зачем проверяют АЛТ на фоне лечения?'}}[key]
 title='Анализы для родителей<br><span>старшего возраста</span>' if key=='senior' else 'Анализы для мужчин'
 intro='Что показывают исследования сердца, сахара и работы почек. Как подготовиться и выбрать анализы из назначения.' if key=='senior' else g['lede']
 nav=''.join('<a href="#'+x[0]+'">'+esc(x[1])+'</a>' for x in g['topics'])
 out='<div class="ag-guide"><section class="ag-hero"><div class="wrap"><div class="crumb"><a href="#home" data-go="home">Главная</a><span>/</span><span>'+esc(g['crumb'])+'</span></div><div class="ag-hero-grid"><div><h1>'+title+'</h1><p>'+esc(intro)+'</p><div class="ag-actions"><a class="btn lime" href="#'+g['sections'][0]['id']+'">Разобраться в назначении ↓</a><a class="ag-hero-link" href="#vse-analizy">Найти анализ из назначения →</a></div></div><aside class="ag-visit"><span class="ag-label">Перед визитом</span><h2>Что проверить заранее</h2><ol><li>Названия исследований в назначении</li><li>Подготовку к каждому анализу</li><li>Пункт сдачи и стоимость</li></ol><a href="#podgotovka">О подготовке к сдаче →</a></aside></div></div></section><nav class="ag-nav wrap" id="temy" aria-label="Разделы гида"><b>В этом гиде</b>'+nav+'</nav><div class="wrap ag-content">'
 for sec in g['sections']:
  ident=sec['id'];body=('<p class="ag-situation">'+esc(sec['situation'])+'</p>') if sec.get('situation') else '';tests=list(sec.get('tests',[]));ps=[]
  for x in sec.get('p',[]):
   if isinstance(x,str) and x.startswith('[[t:'):tests.append(x[4:-2])
   else:ps.append(x)
  if sec.get('short'):body+='<p class="ag-answer">'+esc(sec['short'])+'</p>'
  if sec.get('compare'):body+=small_cards(sec['compare']['rows'])
  # Main explanatory copy, with a practical lead first for kidneys.
  if key=='senior' and ident=='pochki' and len(ps)>1:ps=[ps[1],ps[0]]+ps[2:]
  if ident=='sahar':
   cmp=json.loads((BASE.parent/'comparisons/articles.json').read_text())['glucose'];body+=small_cards([(x['title'],x['text']) for x in cmp['items']])
  if ident=='vitaminy':
   labels=['Общий анализ крови','Витамин B12','Витамин D'];body+='<div class="ag-explain-list">'+''.join('<article><span class="ag-label">'+labels[i]+'</span>'+para(x)+'</article>' for i,x in enumerate(ps))+'</div>';ps=[]
  for i,x in enumerate(ps):
   html=para(x)
   if i==0 and isinstance(x,str):html=html.replace('<p>','<p class="ag-answer">',1)
   body+=html
  if sec.get('life'):body+='<div class="ag-use"><b>Как используют результат</b><p>'+esc(sec['life'])+'</p></div>'
  if sec.get('more'):body+='<details class="more"><summary>'+esc(sec.get('more_h','Дополнительные условия и ограничения'))+'</summary><div class="detail-body">'+''.join(para(x) for x in sec['more'])+'</div></details>'
  if ident=='sahar':body+='<button class="ag-compare-link" type="button" data-comparison="glucose">Подробнее: глюкоза и гликированный гемоглобин</button>'
  if tests:body+='<div class="ag-related"><div class="ag-label">Исследования по теме — сверить с назначением</div><div data-audience-tests="'+','.join(dict.fromkeys(tests))+'"></div></div>'
  out+='<section class="ag-section" id="'+ident+'" data-topic="'+esc(sec['h'])+'"><h2>'+esc(titles.get(ident,sec['h']))+'</h2>'+body+'</section>'
 out+='<section class="ag-section" id="zachem"><h2>'+esc(g['life']['h'])+'</h2><ul class="ag-benefits">'+''.join('<li>'+esc(x)+'</li>' for x in g['life']['items'])+'</ul></section><section class="ag-section" id="voprosy"><h2>Частые вопросы</h2><div data-audience-faq></div></section><section class="ag-section" id="chek-apy"><h2>Наборы анализов</h2><p>Состав набора следует сверить с назначением. Не все исследования требуются каждому человеку.</p><div data-audience-complexes></div></section><section class="ag-section" id="vse-analizy"><h2>Все анализы раздела</h2><p>Полный список для выбора по назначению. Добавленные выше исследования уже отмечены в корзине.</p><div class="catalog-details catalog-visible"><p class="preg-point" data-audience-point></p><div class="catalog-heading"><h3>'+esc(g['crumb'])+'</h3><span data-audience-count></span></div><label class="sr" for="catalog-q">Название или код анализа</label><input class="catalog-search" id="catalog-q" type="search" placeholder="Название или код анализа"><div id="catalog-list"></div><p id="no-results" hidden>По этому запросу анализы не найдены.</p></div><div class="final-cta"><h3>Проверить выбранные исследования</h3><p>Состав заказа и итоговая стоимость доступны в общей корзине.</p><button type="button" class="btn dark" data-go="cart">Посмотреть корзину →</button></div></section><p class="medical-note">Результат оценивает лечащий врач. Помощь в выборе анализа — по телефону <a href="tel:88002017830">8 800 201 78 30</a>.</p></div></div>'
 out+='<div class="wrap ag-content"><details class="more"><summary>Источники медицинской информации</summary><div class="detail-body"><ul>'+''.join('<li><a href="'+esc(x['url'])+'" target="_blank" rel="noopener noreferrer">'+esc(x['title'])+'</a></li>' for x in g.get('source_links',[]))+'</ul></div></details></div>'
 return out
