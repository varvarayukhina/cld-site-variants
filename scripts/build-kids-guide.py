"""Build task-first children's guide with native catalogue and cart."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
def integrate(html):
    markup=(ROOT/'content/kids-guide/view.html').read_text()
    ids=re.findall(r'\bid="([^"]+)"',markup)
    for ident in sorted(ids,key=len,reverse=True):
        markup=markup.replace('id="'+ident+'"','id="kg-'+ident+'"').replace('href="#'+ident+'"','href="#kg-'+ident+'"')
        for attr in ['for','aria-controls','aria-labelledby']:markup=markup.replace(attr+'="'+ident+'"',attr+'="kg-'+ident+'"')
    # Symbols use the existing editorial set; no duplicated illustration assets.
    markup=markup.replace('href="#i-','href="#pg-i-')
    markup=re.sub(r'href="#kg-([^"]+)"',lambda m:'href="#for-kids:'+m[1]+'" data-kids-target="'+m[1]+'"',markup)
    markup=re.sub(r'class="([^"]+)"',lambda m:'class="'+' '.join('pg-'+c for c in m[1].split())+'"',markup)
    module=(ROOT/'content/kids-guide/adapter.js').read_text().replace('/* KIDS_TEMPLATE */','var KIDS_TEMPLATE='+json.dumps(markup,ensure_ascii=False)+';')
    # Product helper icon references use pregnancy symbols.
    module=module.replace('#kg-i-','#pg-i-')
    block='  /* KIDS GUIDE START */\n'+module+'\n  /* KIDS GUIDE END */\n'
    if '/* KIDS GUIDE START */' in html:html=re.sub(r'  /\* KIDS GUIDE START \*/[\s\S]*?/\* KIDS GUIDE END \*/\n',lambda m:block,html,count=1)
    else:html=html.replace('  function renderGuide() {',block+'  function renderGuide() {',1)
    hook='''
    /* EDITORIAL VIEW SWITCH START */
    var isPregnant = state.guide === "pregnant", isWomen = state.guide === "women", isKids = state.guide === "kids";
    $("#kids-guide").hidden = !isKids;
    $("#women-guide").hidden = !isWomen;
    $("#pregnancy-guide").hidden = !isPregnant;
    $$("#v-guide > .cxhero, #v-guide > .gd").forEach(function(el){el.hidden = isPregnant || isWomen || isKids;});
    if (pregSpy) { pregSpy.disconnect(); pregSpy = null; }
    if (womenSpy) { womenSpy.disconnect(); womenSpy = null; }
    if (kidsSpy) { kidsSpy.disconnect(); kidsSpy = null; }
    if (isPregnant) { renderPregnancyGuide(); return; }
    if (isWomen) { renderWomenGuide(); return; }
    if (isKids) { renderKidsGuide(); return; }
    /* EDITORIAL VIEW SWITCH END */
'''
    html,n=re.subn(r'\n    /\* EDITORIAL VIEW SWITCH START \*/[\s\S]*?/\* EDITORIAL VIEW SWITCH END \*/\n',lambda m:hook,html,count=1);assert n==1
    if 'id="kids-guide"' not in html:html=html.replace('<div class="pregnancy-guide women-guide" id="women-guide" hidden></div>','<div class="pregnancy-guide women-guide" id="women-guide" hidden></div>\n    <div class="pregnancy-guide kids-guide" id="kids-guide" hidden></div>',1)
    if 'kidsSyncControls(); // shared kids cart' not in html:html=html.replace('womenSyncControls(); // shared women cart','womenSyncControls(); // shared women cart\n    kidsSyncControls(); // shared kids cart',1)
    return html
if __name__=='__main__':
 p=ROOT/'v4/index.html';p.write_text(integrate(p.read_text()));print('Built kids guide.')
