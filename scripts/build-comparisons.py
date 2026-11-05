"""Integrate comparison pages and contextual purchase-preserving dialogs."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def integrate(html):
    data=json.loads((ROOT/'content/comparisons/articles.json').read_text())
    module=(ROOT/'content/comparisons/adapter.js').read_text().replace('/* COMPARISON_DATA */','var COMPARISONS='+json.dumps(data,ensure_ascii=False)+';')
    block='  /* COMPARISONS START */\n'+module+'\n  /* COMPARISONS END */\n'
    if '/* COMPARISONS START */' in html:
        html=re.sub(r'  /\* COMPARISONS START \*/[\s\S]*?/\* COMPARISONS END \*/\n',lambda m:block,html,count=1)
    else:html=html.replace('  function go(target, push) {',block+'  function go(target, push) {',1)
    hub_section='<section id="v-comparisons" data-view="comparisons" hidden><div class="cxhero cmp-hub-hero"><div class="wrap" id="comparison-hub-hero"></div></div><div class="cmp-root cmp-page" id="comparison-hub"></div></section>'
    html=re.sub(r'<section id="v-comparisons" data-view="comparisons" hidden>.*?</section>',lambda m:hub_section,html,count=1,flags=re.S)
    if 'id="v-compare"' not in html:
        html=html.replace('  <footer class="foot">','''  <section id="v-compare" data-view="compare" hidden><article class="cmp-root cmp-page" id="comparison-page"></article></section>
  <section id="v-comparisons" data-view="comparisons" hidden><div class="cmp-root cmp-page" id="comparison-hub"></div></section>
  <dialog id="comparison-dialog" class="cmp-root" aria-labelledby="cmp-dialog-title"><div class="cmp-dialog-top"><button type="button" data-comparison-close aria-label="Закрыть сравнение">×</button></div><div class="cmp-dialog-content"></div><div class="cmp-dialog-footer"><button type="button" class="btn" data-comparison-close>Вернуться к выбору</button><a class="btn btn-navy" href="#cart" data-go="cart" data-comparison-cart hidden>Перейти в корзину</a></div></dialog>
  <footer class="foot">''',1)
    footer_link='<a href="#comparisons" data-go="comparisons">Справочник об анализах</a>'
    html=html.replace('<a href="#comparisons" data-go="comparisons">Статьи об анализах</a>',footer_link)
    if footer_link not in html:
        anchor='          <a href="#points" data-go="points">Где сдать анализы</a>\n          <a href="#results" data-go="results">Результаты анализов</a>\n'
        assert html.count(anchor)==1,'footer anchor'
        html=html.replace(anchor,anchor+'          '+footer_link+'\n',1)
    if 'closeComparison(true); // comparison navigation' not in html:
        html=html.replace('  function go(target, push) {','  function go(target, push) {\n    closeComparison(true); // comparison navigation',1)
    if 'state.comparison = p[1]' not in html:
        html=html.replace('    else if (v === "card")','    else if (v === "compare" && COMPARISONS[p[1]]) { state.view = "compare"; state.comparison = p[1]; }\n    else if (v === "card")',1)
    if 'state.view === "compare" ? "compare-"' not in html:
        html=html.replace('var hash = state.view === "home"','var hash = state.view === "compare" ? "compare-" + state.comparison : state.view === "home"',1)
    if 'h.indexOf("compare-")' not in html:
        html=html.replace('    else if (h.indexOf("card-")','    else if (h.indexOf("compare-") === 0) go("compare:" + h.slice(8), false);\n    else if (h.indexOf("card-")',1)
    if '// comparison metadata' not in html:
        html=html.replace('    document.title = /', '''    // comparison metadata
    if (state.view === "compare" && COMPARISONS[state.comparison]) { title = COMPARISONS[state.comparison].title; description = COMPARISONS[state.comparison].description || COMPARISONS[state.comparison].intro; }
    if (state.view === "comparisons") { title = "Справочник об анализах: чем отличаются похожие исследования"; description = "Чем отличаются похожие анализы: железо, сахар, щитовидная железа, печень, почки, холестерин, гормоны и другие. Понятные объяснения и выбор исследований CLD."; }
    document.title = /''',1)
    if 'cardComparisons(code); // comparison links' not in html:
        html=html.replace('    if (togHtml) html += togHtml;','    html += cardComparisons(code); // comparison links\n    if (togHtml) html += togHtml;',1)
    if 'comparisonSync(); // shared comparison cart' not in html:
        html=html.replace('womenSyncControls(); // shared women cart','womenSyncControls(); // shared women cart\n    comparisonSync(); // shared comparison cart',1)
    if 'decorateGuideComparisons(); // contextual comparisons' not in html:
        html=html.replace('    $("#g-toc").innerHTML =','    decorateGuideComparisons(); // contextual comparisons\n    $("#g-toc").innerHTML =',1)
    if 'href="../assets/comparisons.css' not in html:html=html.replace('</head>','<link rel="stylesheet" href="../assets/comparisons.css?v=20261102">\n</head>',1)
    import hashlib
    html=re.sub(r'href="../assets/comparisons.css[^"]*"','href="../assets/comparisons.css?v='+hashlib.sha256((ROOT/'assets/comparisons.css').read_bytes()).hexdigest()[:12]+'"',html,count=1)
    return html
if __name__=='__main__':
    path=ROOT/'v4/index.html';path.write_text(integrate(path.read_text()));print('Built comparisons, shared cart, card links and contextual dialogs.')
