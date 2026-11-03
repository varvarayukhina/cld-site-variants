"""Build continuous guides for older parents and men with the shared native cart."""
from pathlib import Path
import re,json,runpy,hashlib
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content/audience-guides'
def integrate(html):
 helpers=runpy.run_path(str(ROOT/'scripts/build-pregnancy-guide.py'))
 css=helpers['scope_css']((CONTENT/'style.css').read_text());(ROOT/'assets/audience-guides.css').write_text(css+'\n')
 render=runpy.run_path(str(CONTENT/'templates.py'))['template'];templates={}
 for key in ['senior','men']:
  markup=render(key);ids=re.findall(r'\bid="([^"]+)"',markup)
  for ident in sorted(ids,key=len,reverse=True):
   markup=markup.replace('id="'+ident+'"','id="ag-'+ident+'"').replace('href="#'+ident+'"','href="#ag-'+ident+'"')
   for attr in ['for','aria-controls','aria-labelledby']:markup=markup.replace(attr+'="'+ident+'"',attr+'="ag-'+ident+'"')
  markup=re.sub(r'href="#ag-([^"]+)"',lambda m:'href="#for-'+key+':'+m[1]+'" data-audience-target="'+m[1]+'"',markup)
  markup=re.sub(r'class="([^"]+)"',lambda m:'class="'+' '.join('pg-'+c for c in m[1].split())+'"',markup)
  templates[key]=markup
 module=(CONTENT/'adapter.js').read_text().replace('/* AUDIENCE_TEMPLATES */','var AUDIENCE_TEMPLATES='+json.dumps(templates,ensure_ascii=False)+';\nvar AUDIENCE_COPY='+json.dumps({key:json.loads((CONTENT/(key+'.json')).read_text()) for key in templates},ensure_ascii=False)+';\nObject.keys(AUDIENCE_COPY).forEach(function(key){GUIDES[key]=AUDIENCE_COPY[key];});')
 block='  /* AUDIENCE GUIDES START */\n'+module+'\n  /* AUDIENCE GUIDES END */\n'
 if '/* AUDIENCE GUIDES START */' in html:html=re.sub(r'  /\* AUDIENCE GUIDES START \*/[\s\S]*?/\* AUDIENCE GUIDES END \*/\n',lambda m:block,html,count=1)
 else:html=html.replace('  function renderGuide() {',block+'  function renderGuide() {',1)
 hook='''
    /* EDITORIAL VIEW SWITCH START */
    var isPregnant = state.guide === "pregnant", isWomen = state.guide === "women", isKids = state.guide === "kids", isAudience = !!AUDIENCE_TEMPLATES[state.guide];
    $("#audience-guide").hidden = !isAudience;
    $("#kids-guide").hidden = !isKids;
    $("#women-guide").hidden = !isWomen;
    $("#pregnancy-guide").hidden = !isPregnant;
    $$("#v-guide > .cxhero, #v-guide > .gd").forEach(function(el){el.hidden = isPregnant || isWomen || isKids || isAudience;});
    if (pregSpy) { pregSpy.disconnect(); pregSpy = null; }
    if (womenSpy) { womenSpy.disconnect(); womenSpy = null; }
    if (kidsSpy) { kidsSpy.disconnect(); kidsSpy = null; }
    if (isPregnant) { renderPregnancyGuide(); return; }
    if (isWomen) { renderWomenGuide(); return; }
    if (isKids) { renderKidsGuide(); return; }
    if (isAudience) { renderAudienceGuide(); return; }
    /* EDITORIAL VIEW SWITCH END */
'''
 html,n=re.subn(r'\n    /\* EDITORIAL VIEW SWITCH START \*/[\s\S]*?/\* EDITORIAL VIEW SWITCH END \*/\n',lambda m:hook,html,count=1);assert n==1
 if 'id="audience-guide"' not in html:html=html.replace('<div class="pregnancy-guide kids-guide" id="kids-guide" hidden></div>','<div class="pregnancy-guide kids-guide" id="kids-guide" hidden></div>\n    <div class="pregnancy-guide" id="audience-guide" hidden></div>',1)
 if 'audienceSyncControls(); // shared audience cart' not in html:html=html.replace('kidsSyncControls(); // shared kids cart','kidsSyncControls(); // shared kids cart\n    audienceSyncControls(); // shared audience cart',1)
 version=hashlib.sha256(css.encode()).hexdigest()[:12];link='<link rel="stylesheet" href="../assets/audience-guides.css?v='+version+'">'
 if 'href="../assets/audience-guides.css' in html:html=re.sub(r'<link rel="stylesheet" href="../assets/audience-guides.css[^\"]*">',link,html,count=1)
 else:html=html.replace('</head>',link+'\n</head>',1)
 return html
if __name__=='__main__':
 p=ROOT/'v4/index.html';p.write_text(integrate(p.read_text()));print('Built continuous parent and men guides with shared catalogue and cart.')
