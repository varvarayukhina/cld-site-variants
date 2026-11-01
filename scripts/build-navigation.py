"""Apply shared view metadata and prominent audience-guide links to v4."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def integrate(html):
    module=(ROOT/'content/navigation/navigation.js').read_text()
    block='  /* SHARED NAVIGATION START */\n'+module+'\n  /* SHARED NAVIGATION END */\n'
    if '/* SHARED NAVIGATION START */' in html:
        html=re.sub(r'  /\* SHARED NAVIGATION START \*/[\s\S]*?/\* SHARED NAVIGATION END \*/\n',lambda m:block,html,count=1)
    else:
        assert html.count('  function go(target, push) {')==1
        html=html.replace('  function go(target, push) {',block+'  function go(target, push) {',1)
    needle='    if (RENDER[state.view]) RENDER[state.view]();'
    if 'applyPageMeta(); // reset metadata for every view' not in html:
        assert html.count(needle)==1
        html=html.replace(needle,needle+'\n    applyPageMeta(); // reset metadata for every view',1)
    # The exact JS is short; match the old generated inline button without touching descriptions.
    if 'renderCatalogGuide(cat); // visible guide entry' not in html:
        html,count=re.subn(r'if \(GUIDES\[cat\.id\]\) \$\("#c-desc"\)\.insertAdjacentHTML\("beforeend", [^\n]+?\);', 'renderCatalogGuide(cat); // visible guide entry',html,count=1)
        assert count==1,'Could not find the inline audience-guide link'
    if 'href="../assets/navigation.css' not in html:
        html=html.replace('</head>','<link rel="stylesheet" href="../assets/navigation.css?v=20261102">\n</head>',1)
    return html

if __name__=='__main__':
    path=ROOT/'v4/index.html';path.write_text(integrate(path.read_text()))
    print('Updated all view metadata and audience guide callouts.')
