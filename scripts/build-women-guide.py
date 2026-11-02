"""Build the women's guide with isolated shared editorial components."""
from pathlib import Path
import re,json,runpy,hashlib
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content/women-guide'

def integrate(html):
    helpers=runpy.run_path(str(ROOT/'scripts/build-pregnancy-guide.py'))
    css=helpers['scope_css']((CONTENT/'style.css').read_text())
    (ROOT/'assets/women-guide.css').write_text(css+'\n')
    source=(ROOT/'content/pregnancy-guide/page.html').read_text()
    defs=re.search(r'(<svg aria-hidden="true" style="position:absolute;[\s\S]*?</svg>)',source)[1]
    markup=defs+'\n'+(CONTENT/'view.html').read_text()
    ids=re.findall(r'\bid="([^"]+)"',markup)
    for ident in sorted(ids,key=len,reverse=True):
        markup=markup.replace('id="'+ident+'"','id="wg-'+ident+'"').replace('href="#'+ident+'"','href="#wg-'+ident+'"')
        for attr in ['for','aria-controls','aria-labelledby']:
            markup=markup.replace(attr+'="'+ident+'"',attr+'="wg-'+ident+'"')
    markup=re.sub(r'href="#wg-([^"]+)"',lambda m:m[0] if m[1].startswith('i-') else 'href="#for-women:'+m[1]+'" data-women-target="'+m[1]+'"',markup)
    markup=re.sub(r'class="([^"]+)"',lambda m:'class="'+' '.join('pg-'+c for c in m[1].split())+'"',markup)
    markup=markup.replace('ASSET_WOMEN_HERO','../assets/img/women/hero.webp').replace('ASSET_WOMEN_CYCLE','../assets/img/women/cycle.webp')
    module=(CONTENT/'adapter.js').read_text().replace('/* WOMEN_TEMPLATE */','var WOMEN_TEMPLATE='+json.dumps(markup,ensure_ascii=False)+';')
    block='  /* WOMEN GUIDE START */\n'+module+'\n  /* WOMEN GUIDE END */\n'
    if '/* WOMEN GUIDE START */' in html:
        html=re.sub(r'  /\* WOMEN GUIDE START \*/[\s\S]*?/\* WOMEN GUIDE END \*/\n',lambda m:block,html,count=1)
    else:html=html.replace('  function renderGuide() {',block+'  function renderGuide() {',1)
    hook='''
    /* EDITORIAL VIEW SWITCH START */
    var isPregnant = state.guide === "pregnant", isWomen = state.guide === "women";
    $$("#v-guide > .cxhero, #v-guide > .gd").forEach(function (el) { el.hidden = isPregnant || isWomen; });
    $("#pregnancy-guide").hidden = !isPregnant;
    $("#women-guide").hidden = !isWomen;
    if (pregSpy) { pregSpy.disconnect(); pregSpy = null; }
    if (womenSpy) { womenSpy.disconnect(); womenSpy = null; }
    if (isPregnant) { renderPregnancyGuide(); return; }
    if (isWomen) { renderWomenGuide(); return; }
    /* EDITORIAL VIEW SWITCH END */
'''
    if '/* EDITORIAL VIEW SWITCH START */' in html:
        html=re.sub(r'\n    /\* EDITORIAL VIEW SWITCH START \*/[\s\S]*?/\* EDITORIAL VIEW SWITCH END \*/\n',lambda m:hook,html,count=1)
    else:
        html,count=re.subn(r'\n    var isPregnant = state.guide === "pregnant";[\s\S]*?if \(isPregnant\) \{ renderPregnancyGuide\(\); return; \}\n',lambda m:hook,html,count=1)
        assert count==1,'Pregnancy guide must be integrated first'
    if 'id="women-guide"' not in html:
        html=html.replace('<div class="pregnancy-guide" id="pregnancy-guide" hidden></div>','<div class="pregnancy-guide" id="pregnancy-guide" hidden></div>\n    <div class="pregnancy-guide women-guide" id="women-guide" hidden></div>',1)
    if 'womenSyncControls(); // shared women cart' not in html:
        html=html.replace('pregSyncControls(); // shared cart','pregSyncControls(); // shared cart\n    womenSyncControls(); // shared women cart',1)
    if 'href="../assets/women-guide.css' not in html:
        html=html.replace('</head>','<link rel="stylesheet" href="../assets/women-guide.css?v=20261102">\n</head>',1)
    version=hashlib.sha256(css.encode()).hexdigest()[:12]
    html=re.sub(r'href="../assets/women-guide.css[^\"]*"', 'href="../assets/women-guide.css?v='+version+'"', html, count=1)
    return html

if __name__=='__main__':
    path=ROOT/'v4/index.html';path.write_text(integrate(path.read_text()))
    print('Built women guide with shared prices, availability and cart.')
