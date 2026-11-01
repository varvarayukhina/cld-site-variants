"""Build the approved pregnancy view inside v4's existing router and catalogue.
Run from any directory: python3 scripts/build-pregnancy-guide.py
Other v4 build scripts may call integrate(html) before writing their output.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content/pregnancy-guide'

def scope_css(css):
    """Scope ordinary rules, recursively preserving media blocks and declarations."""
    out=[];pos=0
    while pos<len(css):
        brace=css.find('{',pos)
        if brace<0: break
        head=css[pos:brace].strip();depth=1;end=brace+1;quote=None
        while end<len(css) and depth:
            char=css[end]
            if quote:
                if char==quote and css[end-1]!='\\': quote=None
            elif char in ['"',"'"]:quote=char
            elif char=='{':depth+=1
            elif char=='}':depth-=1
            end+=1
        body=css[brace+1:end-1]
        head=re.sub(r'/\*.*?\*/','',head,flags=re.S).strip()
        if not head:pos=end;continue
        if head.startswith('@media') or head.startswith('@supports'):
            out.append(head+'{'+scope_css(body)+'}')
        elif head.startswith('@'):
            raise ValueError('Unexpected global CSS at-rule: '+head[:50])
        else:
            selectors=[]
            for sel in head.split(','):
                sel=re.sub(r'\.([A-Za-z_][\w-]*)',lambda m:'.pg-'+m[1],sel.strip())
                if sel in [':root','body','html']:sel='.pregnancy-guide'
                elif sel.startswith('body'):sel=sel.replace('body','.pregnancy-guide',1)
                elif sel.startswith('html'):sel=sel.replace('html','.pregnancy-guide',1)
                else:sel='.pregnancy-guide '+sel
                selectors.append(sel)
            out.append(','.join(selectors)+'{'+body+'}')
        pos=end
    return '\n'.join(out)

def prepare_markup(source):
    # Shared header/footer, global overlays and demo cart deliberately stay outside.
    markup=re.search(r'<main id="main">([\s\S]*?)</main>',source)[1]
    defs=re.search(r'(<svg aria-hidden="true" style="position:absolute;[\s\S]*?</svg>)',source)[1]
    markup=defs+'\n'+markup
    markup=markup.replace('ASSET_HERO','../assets/img/pregnancy/hero.webp').replace('ASSET_SUGAR','../assets/img/pregnancy/sugar.webp').replace('ASSET_COUPLE','../assets/img/pregnancy/couple.webp').replace('ASSET_BOOTS','../assets/img/guide/pregnant.webp')
    # Namespace every local id, including SVG symbols and tab panels.
    ids=re.findall(r'\bid="([^"]+)"',markup)
    for ident in sorted(ids,key=len,reverse=True):
        markup=markup.replace('id="'+ident+'"','id="pg-'+ident+'"')
        markup=markup.replace('href="#'+ident+'"','href="#pg-'+ident+'"')
        for attr in ['aria-controls','aria-labelledby','for']:
            markup=markup.replace(attr+'="'+ident+'"',attr+'="pg-'+ident+'"')
    def local_link(m):
        ident=m[1]
        if ident.startswith('i-'):return m[0]
        return 'href="#for-pregnant:'+ident+'" data-preg-target="'+ident+'"'
    markup=re.sub(r'href="#pg-([^"]+)"',local_link,markup)
    # SVG references above must refer to local symbols, never to a route.
    markup=re.sub(r'(<use )href="#for-pregnant:(i-[^"]+)" data-preg-target="[^"]+"',r'\1href="#pg-\2"',markup)
    base='https://varvarayukhina.github.io/cld-site-variants/v4/'
    markup=markup.replace('href="'+base+'"','href="#home" data-go="home"')
    markup=re.sub(r'href="'+re.escape(base)+r'#([^"]+)"',lambda m:'href="#'+m[1]+'" data-go="'+m[1]+'"',markup)
    markup=markup.replace(' target="_blank"','').replace(' rel="noopener"','')
    markup=markup.replace(' data-stage=',' data-preg-stage=')
    markup=markup.replace('data-open-cart','data-go="cart"')
    # Legacy section URLs still open the relevant disclosure.
    needles=[('Щитовидная железа: что показывают ТТГ и антитела к ТПО','shchitovidka'),('Моча: общий анализ и проверка на бактерии','mocha'),('Подтверждение беременности и обследование в конце I триместра','hgch'),('Стрептококк группы B перед родами','streptokokk')]
    for title,slug in needles:
        markup=markup.replace('<details class="more"><summary>'+title,'<details class="more" id="pg-'+slug+'"><summary>'+title)
        markup=markup.replace('<details class="more" open><summary>'+title,'<details class="more" id="pg-'+slug+'" open><summary>'+title)
    markup=markup.replace('<div class="route-note">','<div class="route-note" id="pg-po-pokazaniyam">')
    markup=markup.replace('<div class="catalog-heading">','<p class="preg-point" data-preg-point></p><div class="catalog-heading">')
    markup=re.sub(r'class="([^"]+)"',lambda m:'class="'+' '.join('pg-'+c for c in m[1].split())+'"',markup)
    return markup

def integrate(html):
    source=(CONTENT/'page.html').read_text()
    css=re.search(r'<style>([\s\S]*?)</style>',source)[1]
    css=scope_css(css)
    css+='\n.pregnancy-guide{display:block}.pregnancy-guide[hidden]{display:none!important}.pregnancy-guide .pg-add-btn:disabled{background:var(--grey);cursor:default;border-color:var(--line)}.pregnancy-guide .pg-preg-na{display:block;margin-top:8px}.pregnancy-guide .pg-preg-point{padding-top:20px;font-size:16px}.pregnancy-guide .pg-add-btn.pg-added{background:var(--soft);border-color:var(--navy)}\n'
    (ROOT/'assets/pregnancy-guide.css').write_text(css)
    data=(CONTENT/'calendar.js').read_text()
    markup=prepare_markup(source)
    faq_section=source[source.index('id="questions"'):source.index('id="all-tests"')]
    faqs=[]
    for q,a in re.findall(r'<summary>(.*?)</summary><div class="detail-body"><p>(.*?)</p></div>',faq_section,re.S):
        faqs.append({'@type':'Question','name':re.sub('<[^>]+>','',q),'acceptedAnswer':{'@type':'Answer','text':re.sub('<[^>]+>','',a)}})
    module=(CONTENT/'adapter.js').read_text().replace('/* PREG_TEMPLATE */','var PREG_TEMPLATE='+json.dumps(markup,ensure_ascii=False)+';').replace('/* PREG_CALENDAR */',data).replace('/* PREG_FAQ */','var PREG_FAQ='+json.dumps({'@context':'https://schema.org','@type':'FAQPage','mainEntity':faqs},ensure_ascii=False)+';')
    module=re.sub(r'class="([^"]+)"',lambda m:'class="'+' '.join(c if c.startswith('pg-') else 'pg-'+c for c in m[1].split())+'"',module)
    block='  /* PREGNANCY GUIDE START */\n'+module+'\n  /* PREGNANCY GUIDE END */\n'
    if '/* PREGNANCY GUIDE START */' in html:
        html=re.sub(r'  /\* PREGNANCY GUIDE START \*/[\s\S]*?/\* PREGNANCY GUIDE END \*/\n',lambda m:block,html,count=1)
    else:
        assert html.count('  function renderGuide() {')==1
        html=html.replace('  function renderGuide() {',block+'  function renderGuide() {',1)
    hook='''\n    var isPregnant = state.guide === "pregnant";
    $$("#v-guide > .cxhero, #v-guide > .gd").forEach(function (el) { el.hidden = isPregnant; });
    $("#pregnancy-guide").hidden = !isPregnant;
    if (pregSpy) { pregSpy.disconnect(); pregSpy = null; }
    if (isPregnant) { renderPregnancyGuide(); return; }
'''
    if 'var isPregnant = state.guide' not in html:
        html=html.replace('  function renderGuide() {','  function renderGuide() {'+hook,1)
    container='\n    <div class="pregnancy-guide" id="pregnancy-guide" hidden></div>'
    if 'id="pregnancy-guide"' not in html:
        html=html.replace('<section id="v-guide" data-view="guide" hidden>','<section id="v-guide" data-view="guide" hidden>'+container,1)
    if 'href="../assets/pregnancy-guide.css' not in html:
        html=html.replace('</head>','<link rel="stylesheet" href="../assets/pregnancy-guide.css?v=20261102">\n</head>',1)
    if 'pregSyncControls(); // shared cart' not in html:
        html=html.replace('    if (state.view === "cart") renderCart();','    if (state.view === "cart") renderCart();\n    pregSyncControls(); // shared cart',1)
    return html

if __name__=='__main__':
    path=ROOT/'v4/index.html'
    path.write_text(integrate(path.read_text()))
    print('Built pregnancy guide into v4; shared catalogue, point selection and cart retained.')
