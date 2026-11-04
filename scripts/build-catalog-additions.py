"""Add new analyses (catalogue entry, per-point prices, category, card text) from content/catalog-additions/*.json.
Idempotent: the injected block is replaced on every run."""
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[1]
def integrate(html):
    rows = []
    for f in sorted((ROOT / 'content/catalog-additions').glob('*.json')):
        rows += json.loads(f.read_text())
    data = json.dumps(rows, ensure_ascii=False)
    block = ('  /* CATALOG ADDITIONS START */\n  (function () { var ADD = ' + data + ';\n'
             '    ADD.forEach(function (x) { if (A[x.code]) return; A[x.code] = x.a; PRICES[x.code] = x.prices; CARDS[x.code] = x.card;\n'
             '      var c = CATS.filter(function (k) { return k.id === x.cat; })[0]; if (c && c.items.indexOf(x.code) < 0) c.items.push(x.code); }); })();\n'
             '  /* CATALOG ADDITIONS END */\n')
    if '/* CATALOG ADDITIONS START */' in html:
        html = re.sub(r'  /\* CATALOG ADDITIONS START \*/[\s\S]*?/\* CATALOG ADDITIONS END \*/\n', lambda m: block, html, count=1)
    else:
        html = html.replace('  function renderGuide() {', block + '  function renderGuide() {', 1)
    return html
if __name__ == '__main__':
    p = ROOT / 'v4/index.html'; p.write_text(integrate(p.read_text())); print('Built catalogue additions.')
