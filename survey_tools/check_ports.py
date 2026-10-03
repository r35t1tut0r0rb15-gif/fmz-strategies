"""Static contract check of every ports/*/module.py. Parses the AST only: nothing is imported,
executed or backtested.

Checks: the exact public names the contract requires (FAMILY included); no occurrence of the
banned known-answer-test name anywhere in a module; GRID keys are a subset of
DEFAULT_PARAMS; USES_STOPS <-> stops(); no shift(-k), bfill, centred windows, whole-series
statistics, cost constants or forbidden portfolio kwargs; the four companion files exist.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {'NAME', 'FAMILY', 'GRID', 'DEFAULT_PARAMS', 'FREQ', 'PERIODS_PER_YEAR_OVERRIDE',
            'precompute', 'simulate', 'portfolio_kwargs'}
FORBIDDEN = [
    (r'\.shift\(\s*-', 'negative shift'),
    (r'\bbfill\b|backfill|fillna\(\s*method\s*=\s*["\']b', 'backward fill'),
    (r'center\s*=\s*True', 'centred window'),
    (r'\bffill\b|fillna\(\s*method\s*=\s*["\']f|\bpad\(', 'forward fill'),
    (r'\b(fees|slippage|fixed_fees|swap)\s*=', 'cost argument'),
    (r'resample\(\s*["\']1D["\']', 'midnight daily resample (use broker_day)'),
    (r'\[["\'](open|high|low|close)["\']\]\.(mean|std|max|min|quantile|median|sum)\(', 'whole-column statistic'),
]
COMPANIONS = ['original_source.md', 'original_sizing.txt', 'PORT_NOTES.md']


def check(path):
    errs = []
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src)
    names = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            names[node.name] = node
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names[t.id] = node
    missing = REQUIRED - names.keys()
    if missing:
        errs.append(f'missing {sorted(missing)}')
    try:
        grid = ast.literal_eval(names['GRID'].value)
        defaults = ast.literal_eval(names['DEFAULT_PARAMS'].value)
        if not set(grid) <= set(defaults):
            errs.append(f'GRID keys not in DEFAULT_PARAMS: {set(grid) - set(defaults)}')
        if not all(isinstance(v, list) and v for v in grid.values()):
            errs.append('GRID values must be non-empty lists')
    except (KeyError, ValueError) as e:
        errs.append(f'GRID/DEFAULT_PARAMS not literal: {e}')
    if 'FAMILY' in names:
        try:
            fam = ast.literal_eval(names['FAMILY'].value)
            if not (isinstance(fam, str) and fam.strip()):
                errs.append('FAMILY must be a non-empty string')
        except ValueError:
            errs.append('FAMILY must be a string literal')
    if 'KNOWN_ANSWER_TEST' in src:   # banned anywhere in a module, comments included
        errs.append('name KNOWN_ANSWER_TEST appears in the module')
    uses_stops = 'USES_STOPS' in names
    if uses_stops != ('stops' in names):
        errs.append('USES_STOPS and stops() must appear together')
    if 'precompute' in names and [a.arg for a in names['precompute'].args.args][:2] != ['raw_1m_df', 'symbol_key']:
        errs.append('precompute signature')
    if 'simulate' in names and [a.arg for a in names['simulate'].args.args][:1] != ['bars_df']:
        errs.append('simulate signature')
    code = re.sub(r'""".*?"""', '', src, flags=re.S)
    code = '\n'.join(line.split('#')[0] for line in code.split('\n'))
    for pat, why in FORBIDDEN:
        for m in re.finditer(pat, code, re.M):
            errs.append(f'{why}: {m.group(0)!r}')
    if not re.search(r'REVERSAL INTENDED|upon_opposite_entry|[Ll]ong only|Opposite entries cannot occur', src):
        errs.append('opposite-entry behaviour not declared')
    if 'portfolio_kwargs' in names:
        body = ast.get_source_segment(src, names['portfolio_kwargs']) or ''
        if re.search(r'["\'](price|open)["\']|\bprice\s*=|\bopen\s*=', body):
            errs.append('portfolio_kwargs sets price/open')
    for c in COMPANIONS:
        if not (path.parent / c).exists():
            errs.append(f'missing {c}')
    return errs


def main():
    bad = 0
    ports = sorted((ROOT / 'ports').glob('*/module.py'))
    for p in ports:
        errs = check(p)
        if errs:
            bad += 1
            print(p.parent.name, *errs, sep='\n   ')
    print(f'{len(ports)} ports checked, {bad} with problems')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
