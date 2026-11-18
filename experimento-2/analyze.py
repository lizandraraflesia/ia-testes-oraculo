"""Roda cada suíte gerada pela IA contra o código (pedido.py) e contra a
intenção do PO (pedido_intencao_po.py) e grava results.json.

Para cada execução, separa:
- falhas: testes cuja asserção não bate com a implementação;
- xpass_estrito: testes marcados como xfail(strict=True) que PASSARAM.
  O pytest conta esses como falha, mas eles concordam com a implementação
  (a IA marcou o comportamento como "provável bug" e escreveu o teste
  esperando o comportamento correto).

Uso (dentro desta pasta):  python3 analyze.py .
"""
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

E = sys.argv[1] if len(sys.argv) > 1 else '.'
IMPLS = {
    'codigo': open(f'{E}/pedido.py', encoding='utf8').read(),
    'intencao_po': open(f'{E}/pedido_intencao_po.py', encoding='utf8').read(),
}


def run(test_file, impl):
    d = f'{E}/sandbox'
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    open(f'{d}/pedido.py', 'w', encoding='utf8').write(impl)
    shutil.copy(test_file, f'{d}/test_pedido.py')
    subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
         '--junitxml=r.xml', 'test_pedido.py'],
        cwd=d, capture_output=True, text=True, timeout=120)
    res = {'passed': 0, 'xfailed': 0, 'falhas': [], 'xpass_estrito': []}
    for tc in ET.parse(f'{d}/r.xml').getroot().iter('testcase'):
        name = tc.get('name')
        cls = tc.get('classname', '').split('.')[-1]
        full = name if cls in ('', 'test_pedido') else f'{cls}::{name}'
        fail = tc.find('failure')
        skip = tc.find('skipped')
        if fail is not None:
            if 'XPASS(strict)' in (fail.get('message') or ''):
                res['xpass_estrito'].append(full)
            else:
                res['falhas'].append(full)
        elif skip is not None and (skip.get('type') == 'pytest.xfail' or 'xfail' in (skip.get('message') or '').lower()):
            res['xfailed'] += 1
        elif tc.find('error') is None:
            res['passed'] += 1
    shutil.rmtree(d, ignore_errors=True)
    res['falhas'].sort()
    res['xpass_estrito'].sort()
    return res


results = {}
for f in sorted(os.listdir(f'{E}/runs')):
    if not f.endswith('_test.py'):
        continue
    name = f[:-len('_test.py')]
    results[name] = {k: run(f'{E}/runs/{f}', v) for k, v in IMPLS.items()}
    c, po = results[name]['codigo'], results[name]['intencao_po']
    print(f"{name}: contra o código -> {len(c['falhas'])} falhas, {c['xfailed']} xfail | "
          f"contra a intenção do PO -> {len(po['falhas'])} testes contradizem"
          + (f" (+{len(po['xpass_estrito'])} xfail estrito que concorda com o PO)" if po['xpass_estrito'] else ''))

json.dump(results, open(f'{E}/results.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
