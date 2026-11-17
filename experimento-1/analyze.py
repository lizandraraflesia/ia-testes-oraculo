import subprocess, sys, os, shutil, json, re
E = sys.argv[1]
BUGGY = open(f'{E}/desconto.py').read()
CORRECT = BUGGY.replace('if total > 100', 'if total >= 100')
MUTANTS = {
    '> vira >=': BUGGY.replace('total > 100', 'total >= 100'),
    '> vira <': BUGGY.replace('total > 100', 'total < 100'),
    '100 vira 101': BUGGY.replace('> 100', '> 101'),
    '0.9 vira 1.9': BUGGY.replace('0.9', '1.9'),
    'arredonda 3 casas': BUGGY.replace(', 2)', ', 3)'),
    'return total vira None': BUGGY.replace('    return total\n', '    return None\n'),
}
for k, v in MUTANTS.items(): assert v != BUGGY, k

def run(test, impl, cov=False):
    d = f'{E}/sandbox'
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    open(f'{d}/desconto.py', 'w').write(impl)
    shutil.copy(test, f'{d}/test_desconto.py')
    args = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'test_desconto.py']
    if cov: args += ['--cov=desconto', '--cov-branch', '--cov-report=json:cov.json']
    r = subprocess.run(args, cwd=d, capture_output=True, text=True, timeout=120)
    out = r.stdout
    m = re.search(r'(\d+) passed', out); passed = int(m.group(1)) if m else 0
    m = re.search(r'(\d+) failed', out); failed = int(m.group(1)) if m else 0
    c = None
    if cov and os.path.exists(f'{d}/cov.json'):
        j = json.load(open(f'{d}/cov.json'))['totals']
        c = (j['percent_covered'], j['covered_lines'], j['num_statements'], j['covered_branches'], j['num_branches'])
    return passed, failed, c

res = {}
for f in sorted(os.listdir(f'{E}/runs')):
    if not f.endswith('.py'): continue
    t = f'{E}/runs/{f}'; name = f[:-3]
    pb, fb, cov = run(t, BUGGY, cov=True)
    pc, fc, _ = run(t, CORRECT)
    killed = []
    for mk, mv in MUTANTS.items():
        _, fm, _ = run(t, mv)
        if fm > 0: killed.append(mk)
    asserts100 = re.findall(r'.*calcular_desconto\(100(?:\.0+)?\)[^\n]*|.*\(100(?:\.0+)?, [^)]*\)', open(t).read())
    res[name] = dict(buggy=(pb, fb), correct=(pc, fc), cov=cov, killed=killed, n_mut=len(MUTANTS),
                     lines100=[a.strip() for a in asserts100][:4])
    print(name, res[name])
json.dump(res, open(f'{E}/results.json', 'w'), ensure_ascii=False, indent=1)
