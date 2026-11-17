"""Roda cada suíte gerada pela IA contra o código (pedido.py) e contra a
intenção do PO (pedido_intencao_po.py) e grava results.json.

Uso (dentro desta pasta):  python3 analyze.py .
"""
import json
import os
import re
import shutil
import subprocess
import sys

E = sys.argv[1] if len(sys.argv) > 1 else '.'
IMPLS = {
    'codigo': open(f'{E}/pedido.py', encoding='utf8').read(),
    'intencao_po': open(f'{E}/pedido_intencao_po.py', encoding='utf8').read(),
}


def count(pattern, text):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else 0


def run(test_file, impl):
    d = f'{E}/sandbox'
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    open(f'{d}/pedido.py', 'w', encoding='utf8').write(impl)
    shutil.copy(test_file, f'{d}/test_pedido.py')
    out = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '-rf', '-p', 'no:cacheprovider', 'test_pedido.py'],
        cwd=d, capture_output=True, text=True, timeout=120).stdout
    shutil.rmtree(d, ignore_errors=True)
    return {
        'passed': count(r'(\d+) passed', out),
        'failed': count(r'(\d+) failed', out),
        'xfailed': count(r'(\d+) xfailed', out),
        'falhas': sorted(re.findall(r'FAILED test_pedido.py::(\S+)', out)),
    }


results = {}
for f in sorted(os.listdir(f'{E}/runs')):
    if not f.endswith('_test.py'):
        continue
    name = f[:-len('_test.py')]
    results[name] = {k: run(f'{E}/runs/{f}', v) for k, v in IMPLS.items()}
    r = results[name]
    print(f"{name}: código -> {r['codigo']['failed']} falhas | intenção do PO -> {r['intencao_po']['failed']} falhas")

json.dump(results, open(f'{E}/results.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
