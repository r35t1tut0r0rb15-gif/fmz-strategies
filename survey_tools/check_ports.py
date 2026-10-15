"""Static contract check of every ports/*/module.py. Parses the AST only: nothing is imported,
executed or backtested.

Checks: the exact public names the contract requires (FAMILY included); no occurrence of the
banned known-answer-test name anywhere in a module; GRID keys are a subset of
DEFAULT_PARAMS; USES_STOPS <-> stops(); no shift(-k), bfill, centred windows, whole-series
statistics, cost constants or forbidden portfolio kwargs; the four companion files exist.

Added 2026-10-07 (SURVEY_README.md, "Rules added 2026-10-07"):
- every module docstring carries one `Marks:` line (`none` or a comma list from MARKS);
- FREQ = "bar_size_pending" is accepted only together with the mark bar_size_pending, and the
  mark only with that FREQ;
- a stop Series built from bar data must be shifted inside stops() itself (`.shift(k)`, k >= 1):
  stops() that reads its bars argument without such a shift is flagged as built from the current
  bar (the engine passes stop Series unlagged and vbt reads them on the fill bar);
- stops() returns only sl_stop / tp_stop / max_hold_time;
- stops on bars longer than 1 h need the mark coarse_bar_stop;
- every resample() is label="left", closed="left".
- a port whose id is in near_duplicate_groups.csv names its group id in PORT_NOTES.md (rule 7).

Added 2026-10-15 (FMZ-C; SURVEY_README.md, "Rules added 2026-10-15"):
- stops() may also return "trail" (the house trailing stop, skill 30-strategy-authoring section 7):
  type percent / volatility / lock_in, a declared anchor close / high_low; such a port carries the
  mark trailing_stop, and the mark only with a trail;
- ports with fmz_id >= 427064 (FMZ-C) also need: a stop module whose portfolio_kwargs returns {}
  exactly (the mining driver refuses anything else, D4); docstring lines "FMZ source id: <id>",
  "Admission criteria", "Volume:", "Session open:"; NAME starting fmz_<id>_; with
  FREQ = "bar_size_pending", a precompute that builds its bars from params["bar_size"] and no
  bar_size in GRID / DEFAULT_PARAMS.
"""
import ast
import csv
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
MARKS = {'bar_size_pending', 'trailing_stop_pending', 'coarse_bar_stop', 'stop_is_entry_condition',
         'trailing_stop'}
PENDING_FREQ = 'bar_size_pending'
STOP_KEYS = {'sl_stop', 'tp_stop', 'max_hold_time', 'trail'}
TRAIL_KEYS = {'type', 'anchor', 'pct', 'atr_n', 'k', 'gain', 'activate_after'}
TRAIL_TYPES = {'percent', 'volatility', 'lock_in'}
TRAIL_ANCHORS = {'close', 'high_low'}
FMZ_C_FROM = 427064


def _groups():
    path = ROOT / 'near_duplicate_groups.csv'
    out = {}
    if path.exists():
        with path.open(encoding='utf-8') as f:
            for r in csv.DictReader(f):
                out.setdefault(r['fmz_id'], set()).add(r['group_id'])
    return out


GROUPS = _groups()


def freq_minutes(freq):
    """Minutes in a pandas-style bar size ("15min", "1h", "4h", "1D" ...); None if unknown."""
    m = re.fullmatch(r'(\d*)\s*(min|T|h|H|D|d|W|w)', freq.strip())
    if not m:
        return None
    n = int(m.group(1) or 1)
    return n * {'min': 1, 'T': 1, 'h': 60, 'H': 60, 'D': 1440, 'd': 1440, 'W': 10080, 'w': 10080}[m.group(2)]


def marks_of(tree):
    """The module docstring's `Marks:` line as a set; None if the line is missing."""
    doc = ast.get_docstring(tree) or ''
    m = re.search(r'^\s*Marks:\s*(.+)$', doc, re.M)
    if not m:
        return None
    vals = {v.strip() for v in m.group(1).split(',') if v.strip()}
    return set() if vals == {'none'} else vals


def stop_problems(src, fn):
    """Static checks on stops(): data-derived Series must be shifted in stops() itself."""
    errs = []
    if not fn.args.args:
        return ['stops() takes no bars argument']
    bars_arg = fn.args.args[0].arg
    reads_bars = any(isinstance(n, ast.Name) and n.id == bars_arg for stmt in fn.body for n in ast.walk(stmt))
    shifted = False
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'shift'
                and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, int)
                and n.args[0].value >= 1):
            shifted = True
    if reads_bars and not shifted:
        errs.append('stop Series built from the current bar: stops() reads bar data but never '
                    '.shift(k>=1) inside stops()')
    for n in ast.walk(fn):
        if isinstance(n, ast.Dict):
            keys = {k.value: v for k, v in zip(n.keys, n.values)
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if keys.keys() & {'type', 'anchor'}:   # a trail declaration (2026-10-15)
                for k in sorted(set(keys) - TRAIL_KEYS):
                    errs.append(f'trail key {k!r} not in {sorted(TRAIL_KEYS)}')
                for k, allowed in (('type', TRAIL_TYPES), ('anchor', TRAIL_ANCHORS)):
                    v = keys.get(k)
                    if v is None:
                        errs.append(f'trail without a declared {k!r}')
                    elif isinstance(v, ast.Constant) and v.value not in allowed:
                        errs.append(f'trail {k} {v.value!r} not in {sorted(allowed)}')
                continue
            for k in sorted(set(keys) - STOP_KEYS):
                errs.append(f'stops() key {k!r} not in {sorted(STOP_KEYS)}')
    return errs


def uses_trail(fn):
    """True when stops() names the key "trail" (a dict key or a subscript)."""
    for n in ast.walk(fn):
        if isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == 'trail' for k in n.keys):
            return True
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value == 'trail':
            return True
    return False


def fmz_c_problems(src, tree, names, fid, freq, uses_stops):
    """Extra rules for FMZ-C ports (fmz_id >= 427064), SURVEY_README "Rules added 2026-10-15"."""
    errs = []
    doc = ast.get_docstring(tree) or ''
    if not re.search(rf'^\s*FMZ source id:\s*{fid}\b', doc, re.M):
        errs.append(f'docstring has no "FMZ source id: {fid}" line (lineage)')
    for label in ('Admission criteria', 'Volume:', 'Session open:'):
        if not re.search(rf'^\s*{re.escape(label)}', doc, re.M):
            errs.append(f'docstring has no "{label}" line')
    try:
        name = ast.literal_eval(names['NAME'].value)
        if not (isinstance(name, str) and name.startswith(f'fmz_{fid}_')):
            errs.append(f'NAME must start with fmz_{fid}_')
    except (KeyError, ValueError):
        errs.append('NAME must be a string literal')
    if uses_stops and 'portfolio_kwargs' in names:
        rets = [n for n in ast.walk(names['portfolio_kwargs']) if isinstance(n, ast.Return)]
        if not rets or not all(isinstance(r.value, ast.Dict) and not r.value.keys for r in rets):
            errs.append('a stop module\'s portfolio_kwargs must return {} (mining driver D4)')
    if freq == PENDING_FREQ:
        body = ast.get_source_segment(src, names['precompute']) if 'precompute' in names else ''
        if not re.search(r'params\[\s*["\']bar_size["\']\s*\]', body or ''):
            errs.append('bar_size_pending: precompute must build its bars from params["bar_size"]')
        for key in ('GRID', 'DEFAULT_PARAMS'):
            try:
                if 'bar_size' in ast.literal_eval(names[key].value):
                    errs.append(f'bar_size must not be in {key} (reserved driver parameter)')
            except (KeyError, ValueError):
                pass
    return errs


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
    marks = marks_of(tree)
    if marks is None:
        errs.append('docstring has no "Marks:" line (use "Marks: none")')
        marks = set()
    elif marks - MARKS:
        errs.append(f'unknown marks {sorted(marks - MARKS)}')
    freq = None
    if 'FREQ' in names:
        try:
            freq = ast.literal_eval(names['FREQ'].value)
        except ValueError:
            errs.append('FREQ must be a string literal')
    if isinstance(freq, str):
        if (freq == PENDING_FREQ) != ('bar_size_pending' in marks):
            errs.append(f'FREQ = "{PENDING_FREQ}" and the mark bar_size_pending must appear together')
        if freq != PENDING_FREQ and freq_minutes(freq) is None:
            errs.append(f'FREQ {freq!r} is not a recognised bar size')
        mins = freq_minutes(freq)
        if uses_stops and mins and mins > 60 and 'coarse_bar_stop' not in marks:
            errs.append('stops on bars longer than 1 h need the mark coarse_bar_stop')
    if 'stops' in names and isinstance(names['stops'], ast.FunctionDef):
        errs += stop_problems(src, names['stops'])
        if uses_trail(names['stops']) != ('trailing_stop' in marks):
            errs.append('stops() "trail" and the mark trailing_stop must appear together')
    elif 'trailing_stop' in marks:
        errs.append('mark trailing_stop without a stops() "trail"')
    fid = path.parent.name.split('_')[0]
    if fid.isdigit() and int(fid) >= FMZ_C_FROM:
        errs += fmz_c_problems(src, tree, names, fid, freq, uses_stops)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'resample':
            kw = {k.arg: getattr(k.value, 'value', None) for k in n.keywords}
            if kw.get('label') != 'left' or kw.get('closed') != 'left':
                errs.append('resample() without label="left", closed="left"')
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
    notes = path.parent / 'PORT_NOTES.md'
    if notes.exists():
        text = notes.read_text(encoding='utf-8')
        for g in sorted(GROUPS.get(path.parent.name.split('_')[0], ())):
            if g not in text:
                errs.append(f'PORT_NOTES.md does not name near-duplicate group {g} (rule 7)')
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
