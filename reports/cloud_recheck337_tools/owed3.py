"""5G-A owed 3: among coarse-bar strategies with a working stop exit, count (static, approximate)
   reversal (opposite strategy.entry while a position is open), time-based exit, same-bar entry+exit."""
import csv, re, sys, collections
sys.path.insert(0, '.')
import classify337 as c

conf = [r for r in csv.DictReader(open('../cloud_coarse_bar_stops_2026-10-01.csv')) if r['detection'] == 'confirmed']
prob = {r['strategy_id'] + r['file']: r for r in csv.DictReader(open('../cloud_recheck337_2026-10-01.csv'))}
pop = [(r, 'intrabar_order') for r in conf]
pop += [(r, r['recheck_class']) for r in prob.values()
        if r['recheck_class'] in ('intrabar_order', 'live_price_stop', 'close_based_stop', 'stop_and_reverse')]

LONG = re.compile(r'strategy\.entry\s*\([^)]*?(strategy\.long|long\s*=\s*true|,\s*true\b)')
SHORT = re.compile(r'strategy\.entry\s*\([^)]*?(strategy\.short|long\s*=\s*false|,\s*false\b)')
ONE_SIDE = re.compile(r'allow_entry_in\s*\(\s*strategy\.direction\.(long|short)\s*\)')
# likely: names/APIs that only exist to measure time in the trade; possible: barssince() on an entry-like
# signal, which is often signal timing rather than an exit. max_bars_back is a Pine memory setting: excluded.
TIME_LIKELY = re.compile(
    r'bar_index\s*-\s*\w*(entry|open|start|buy|sell|trade|pos)\w*(\[\d+\])?\s*[><]=?'
    r'|entry_bar_index|opentrades\.entry_time|barssince\s*\(\s*strategy\.position_size'
    r'|\b(?!max_?bars_?back\b)\w*(bars_?held|hold_?bars|holding_?period|bars_?in_?trade|max_?bars|max_?hold'
    r'|exit_?after|bars_?since_?entry|time_?stop)\w*\b', re.I)
TIME_POSSIBLE = re.compile(r'barssince\s*\([^)]*(entry|buy|sell|long|short|open)', re.I)
rows = []
for r, cls in pop:
    if r['language'] != 'PineScript':
        rows.append((r, cls, 'n/a', 'n/a')); continue
    _, code = c.source(c.REPO + r['file'])
    nc = '\n'.join(l.split('//')[0] for l in code.split('\n'))
    rev = bool(LONG.search(nc) and SHORT.search(nc) and not ONE_SIDE.search(nc))
    nc2 = re.sub(r'(?i)max_?bars_?back\s*=\s*\d+', '', nc)
    tex = 'likely' if TIME_LIKELY.search(nc2) else ('possible' if TIME_POSSIBLE.search(nc2) else '')
    rows.append((r, cls, rev, tex))

def n(f): return sum(1 for x in rows if f(x))
print('population (coarse-bar, working stop exit):', len(rows))
print('  of which intrabar (stop/limit order or live price):', n(lambda x: x[1] in ('intrabar_order', 'live_price_stop')))
print('  of which next-bar-open (close-based or stop-and-reverse):', n(lambda x: x[1] in ('close_based_stop', 'stop_and_reverse')))
print('Pine files:', n(lambda x: x[2] != 'n/a'))
print('  can reverse (long and short strategy.entry, no one-side restriction):', n(lambda x: x[2] is True))
print('  time-based exit, likely:', n(lambda x: x[3] == 'likely'), ' possible (barssince on a signal):', n(lambda x: x[3] == 'possible'))
print('  can reverse or likely time exit:', n(lambda x: x[2] is True or x[3] == 'likely'))
print('  same-bar entry+exit possible (an inside-the-bar exit order):', n(lambda x: x[1] == 'intrabar_order' and x[2] != 'n/a'))
with open('../cloud_owed3_counts_2026-10-01.csv', 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['strategy_id', 'bar_size', 'language', 'tier', 'stop_class', 'can_reverse', 'time_exit', 'same_bar_possible', 'file'])
    for r, cls, rev, tex in rows:
        w.writerow([r['strategy_id'], r['bar_size'], r['language'], r.get('detection') or 'probable', cls, rev, tex,
                    'yes' if cls == 'intrabar_order' else ('n/a' if r['language'] != 'PineScript' else 'no'), r['file']])
