"""Static screen of the FMZ corpus against admission criteria 1, 2, 3 and 6.

Reads source text only. No strategy is executed, backtested or ranked, and
FMZ's own performance claims (description text) are never read by the rules:
every rule below looks at the source code only (criterion 7).

Outcomes are PRELIMINARY where marked REVIEW: those are settled by reading the
file when it is ported, and PORT_NOTES.md records the final outcome.

Usage:  python3 survey_tools/screen.py      (writes screening.csv, duplicates.csv)
"""
import csv
import glob
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fmzparse import parse  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- helpers

STR_RE = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'')
LINE_COMMENT_RE = re.compile(r'//[^\n]*')
PY_COMMENT_RE = re.compile(r'#[^\n]*')
BLOCK_COMMENT_RE = re.compile(r'/\*.*?\*/', re.S)


def strip_code(code, lang):
    """Remove comments; keep string literals (some rules need tickers)."""
    out = []
    for line in code.split('\n'):
        # drop comments that start outside a string
        masked = STR_RE.sub(lambda m: '\x00' * len(m.group(0)), line)
        cut = masked.find('#') if lang == 'python' else masked.find('//')
        out.append(line if cut < 0 else line[:cut])
    s = '\n'.join(out)
    if lang in ('javascript', 'cpp'):
        s = BLOCK_COMMENT_RE.sub('', s)
    if lang == 'python':
        s = re.sub(r'""".*?"""|\'\'\'.*?\'\'\'', '', s, flags=re.S)
    return s


def calls(code, name):
    """Yield the argument text of every call `name(...)` (balanced parens)."""
    for m in re.finditer(r'\b' + re.escape(name) + r'\s*\(', code):
        i, depth = m.end(), 1
        while i < len(code) and depth:
            c = code[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            i += 1
        yield code[m.end():i - 1]


def has_kwarg(args, key):
    """True if a call's arguments set `key=` to something other than na."""
    m = re.search(r'\b' + key + r'\s*=\s*([^,=][^,]*)', args)
    return bool(m) and m.group(1).strip() not in ('na', 'None')


# ---------------------------------------------------------------- rules

PRICE = r'\b(?:close|open|high|low|hl2|hlc3|ohlc4)\b(?:\s*\[\d+\])?'
NUM = r'(?<![\w.])\d{2,}(?:\.\d+)?(?![\w.])'
PRICE_LEVEL_RE = re.compile(PRICE + r'\s*[<>]=?\s*' + NUM + '|' + NUM + r'\s*[<>]=?\s*' + PRICE)

def screen_pine(code):
    c1, c2, c3, notes = [], [], [], []
    fail1 = review1 = fail2 = adapt2 = review2 = False

    entries = list(calls(code, 'strategy.entry')) + list(calls(code, 'strategy.order'))
    if not entries:
        c1.append('no strategy.entry/strategy.order calls (indicator only, no signals)')
        fail1 = True
    if re.search(r'process_orders_on_close\s*=\s*true', code):
        c1.append('process_orders_on_close=true: original fills at the signal bar close')
        fail1 = True
    if re.search(r'calc_on_every_tick\s*=\s*true', code):
        c1.append('calc_on_every_tick=true: original recalculates intrabar')
        fail1 = True
    if re.search(r'calc_on_order_fills\s*=\s*true', code):
        c1.append('calc_on_order_fills=true: original recalculates intrabar after fills')
        fail1 = True
    if any(has_kwarg(a, 'limit') or has_kwarg(a, 'stop') for a in entries):
        c1.append('entries are resting limit/stop orders filled intrabar at set prices')
        fail1 = True
    if re.search(r'lookahead\s*=\s*(barmerge\.)?lookahead_on', code):
        c1.append('REVIEW lookahead_on in security(): check for the [1]-offset idiom')
        review1 = True
    exits = list(calls(code, 'strategy.exit'))
    if any(has_kwarg(a, k) for a in exits for k in ('trail_points', 'trail_price', 'trail_offset')):
        c1.append('REVIEW trailing stop: not expressible in stops(); becomes a signal exit or stored money-management')
        review1 = True
    if any(has_kwarg(a, 'stop') or has_kwarg(a, 'limit') for a in exits):
        c1.append('REVIEW strategy.exit price-level stop/limit: must reduce to a fraction of entry fill')
        review1 = True

    # criterion 2: generic across instruments
    for a in list(calls(code, 'security')) + list(calls(code, 'request.security')):
        first = a.split(',')[0].strip()
        if STR_RE.fullmatch(first) or re.match(r'["\']', first):
            c2.append(f'security() on a named instrument {first[:40]}')
            fail2 = True
            break
    nostr = STR_RE.sub('S', code)
    level = distance = False
    for m in PRICE_LEVEL_RE.finditer(nostr):
        before = nostr[max(0, m.start() - 3):m.start()].strip()
        after = nostr[m.end():m.end() + 3].strip()
        if before[-1:] in ('-', '+', '*', '/') or after[:1] in ('-', '+', '*', '/'):
            distance = True            # e.g. `entryPrice - close > 300`: a price-unit distance
        else:
            level = True
    if level:
        c2.append('price compared with a hard-coded numeric level')
        fail2 = True
    if distance:
        c2.append('ADAPT hard-coded price-unit distance: re-expressed as an ATR multiple in the port')
        adapt2 = True
    if re.search(r'syminfo\.(ticker|tickerid|root)\s*==', code):
        c2.append('logic branches on a specific ticker')
        fail2 = True
    if re.search(r'syminfo\.mintick|\b(profit|loss|trail_points|trail_offset)\s*=', code):
        c2.append('ADAPT tick/point distances: re-expressed as ATR multiples in the port')
        adapt2 = True
    if re.search(r'input[.\w]*\s*\([^)]*(?:[Pp]rice|价格|[Ll]evel)', code):
        c2.append('REVIEW input named price/level: check it is not an absolute price')
        review2 = True
    if re.search(r'\btime\s*\([^)]*"\d{4}-\d{4}|\bhour\s*(==|>=|<=|<|>)|\bdayofweek\s*==|\bsession\.', code):
        c2.append('REVIEW session/time-of-day logic: market-specific hours')
        review2 = True
    if re.search(r'\bvolume\b|\bta\.(obv|mfi|vwap|pvt|accdist|nvi|pvi|wad)\b|\b(obv|mfi|vwap)\b', nostr):
        notes.append('USES_VOLUME')

    # criterion 3: crypto-exchange-only features
    # Pine cannot see funding or the order book itself; only via a funding/premium symbol
    for a in list(calls(code, 'security')) + list(calls(code, 'request.security')):
        if re.search(r'FUNDING|PREMIUM|OPEN_?INTEREST|_OI\b', a, re.I):
            c3.append('funding/premium/open-interest series requested via security()')
            break

    s1 = 'FAIL' if fail1 else ('REVIEW' if review1 else 'PASS')
    s2 = 'FAIL' if fail2 else ('REVIEW' if review2 else ('ADAPT' if adapt2 else 'PASS'))
    s3 = 'FLAG' if c3 else 'PASS'
    return s1, c1, s2, c2, s3, c3, notes


C3_STRONG = [
    (r'GetDepth|\.Bids\b|\.Asks\b|orderbook|order_book|盘口|深度', 'order book (depth) used'),
    (r'[Ff]unding|资金费率', 'funding rate'),
    (r'exchanges\s*\[\s*[1-9]|exchanges\.length|len\(exchanges\)', 'multiple exchanges (cross-exchange arbitrage/hedge)'),
    (r'套利|对冲|arbitrage|[Hh]edg', 'arbitrage/hedging between contracts or venues'),
    (r'做市|market.?mak', 'market making'),
    (r'高频|HFT|high.?frequency', 'high-frequency/tick execution'),
    (r'Transfer|划转|Withdraw|提币', 'account transfer/withdrawal tooling'),
]
C3_VENUE = [
    (r'SetContractType\s*\(\s*["\'](swap|quarter|next_quarter|this_week|next_week)', 'perpetual/dated crypto contract'),
    (r'永续|perpetual|USDT-SWAP|_USDT\.swap', 'perpetual swap'),
    (r'SetMarginLevel|leverage|杠杆', 'exchange leverage/margin setting'),
    (r'GetTicker\s*\(\s*\)\s*\.\s*(Buy|Sell)|ticker\.(Buy|Sell)|\[["\']Buy["\']\]|\[["\']Sell["\']\]', 'best bid/ask from ticker'),
]


def screen_bot(code, name):
    """JavaScript / Python / C++ / MyLanguage: FMZ live-loop bots."""
    c1, c2, c3, notes = [], [], [], []
    strong = [why for pat, why in C3_STRONG if re.search(pat, code)]
    venue = [why for pat, why in C3_VENUE if re.search(pat, code)]
    trades = re.search(r'\.(Buy|Sell|CreateOrder)\s*\(|\bBK\b|\bSK\b|\bBPK\b|\bSPK\b|\bBP\b|\bSP\b|\$\.(Buy|Sell|OpenLong|OpenShort|Cover)|CoverAll|\bq\.pushTask|\$\.Trade|OpenOrder', code)
    bars = re.search(r'GetRecords|\bTA\.|talib\.|\bMA\(|\bEMA\(|\bCROSS\(|\bREF\(|\bHHV\(|\bLLV\(', code)
    library = (re.search(r'模板|类库|[Tt]emplate|[Ll]ibrary|插件|[Pp]lugin', name)
               or (re.search(r'工具|监控|[Mm]onitor|测试|[Tt]est|[Dd]emo|范例|教程', name) and not bars))
    grid = re.search(r'网格|[Gg]rid|马丁|[Mm]artingale|冰山|[Ii]ceberg', name + code[:4000])

    s3 = 'PASS'
    if strong:
        c3 += strong + venue
        s3 = 'FLAG'
    elif venue and not bars:
        c3 += venue
        s3 = 'FLAG'
    elif venue:
        c3.append('REVIEW venue set-up only (' + '; '.join(venue) + '): check the signals do not need it')
        s3 = 'REVIEW'

    if not trades or library:
        c1.append('not a signal strategy (tool, library, template, monitor or demo)')
        s1 = 'FAIL'
    elif grid:
        c1.append('order-level logic (grid/martingale/iceberg ladder), no bar signals')
        s1 = 'FAIL'
    elif bars:
        c1.append('REVIEW bar-based bot: signals must be read out of the live loop')
        s1 = 'REVIEW'
    else:
        c1.append('tick/order-level loop with no bar data (no GetRecords/indicators)')
        s1 = 'FAIL'

    s2 = 'REVIEW'
    c2.append('REVIEW bot parameters are read at port time')
    if re.search(r'\bV\b|\bVOL\b|\bVOLUME\b|\.Volume\b|\[["\']Volume|\bvolume\b', STR_RE.sub('S', code)):
        notes.append('USES_VOLUME')
    return s1, c1, s2, c2, s3, c3, notes


# ---------------------------------------------------------------- criterion 6

TOKEN_RE = re.compile(r'[A-Za-z_][\w.]*|\d+(?:\.\d+)?|==|!=|<=|>=|:=|=>|\S')
KW_ARG_NAMES = re.compile(r'\b(title|tooltip|group|inline|color|linewidth|style|transp|text|textcolor|size|location|offset|minval|maxval|step|options|comment|alert_message|id)\s*=\s*[^,)]*')
COSMETIC = re.compile(r'^\s*(plot\w*|bgcolor|fill|hline|label\.\w+|line\.\w+|box\.\w+|table\.\w+|alertcondition|alert)\s*\(.*$', re.M)


def shingles(code, k=5):
    s = STR_RE.sub('S', code)
    s = COSMETIC.sub('', s)
    s = KW_ARG_NAMES.sub('', s)
    toks = ['0' if t[0].isdigit() else t for t in TOKEN_RE.findall(s)]
    return {tuple(toks[i:i + k]) for i in range(max(1, len(toks) - k + 1))}


def near_duplicates(rows, threshold, report_from=None):
    """Union-find over pairs with exact Jaccard >= threshold (same language).

    Pairs with report_from <= Jaccard < threshold are returned in `scores` too,
    but are not merged."""
    floor = threshold if report_from is None else report_from
    sh = [shingles(r['_code'], 5) for r in rows]
    index = defaultdict(list)
    for i, s in enumerate(sh):
        for g in s:
            index[g].append(i)
    parent = list(range(len(rows)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    scores = {}
    for i, s in enumerate(sh):
        if len(s) < 10:
            continue
        shared = defaultdict(int)
        for g in s:
            post = index[g]
            if len(post) > 300:        # skip boiler-plate shingles for candidate generation only
                continue
            for j in post:
                if j > i and rows[j]['lang'] == rows[i]['lang']:
                    shared[j] += 1
        for j, n in shared.items():
            # cheap upper bound before the exact Jaccard
            if n < floor * min(len(s), len(sh[j])) * 0.5:
                continue
            jac = len(s & sh[j]) / len(s | sh[j])
            if jac >= floor:
                scores[(i, j)] = jac
            if jac >= threshold:
                parent[find(j)] = find(i)
    groups = defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)
    return [g for g in groups.values() if len(g) > 1], scores


# ---------------------------------------------------------------- main

NOT_CORPUS = {'README.md', 'SURVEY_README.md', 'SURVEY_SUMMARY.md', 'PROGRESS.md'}
DUP_THRESHOLD = 0.80        # merged automatically
POSSIBLE_DUP_FLOOR = 0.65   # listed in possible_duplicates.csv, checked by hand at port time
STATUS_ORDER = {'PASS': 0, 'ADAPT': 1, 'REVIEW': 2, 'FLAG': 3, 'FAIL': 4}


def slug(name):
    s = re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-').lower()
    return (s[:60].rstrip('-') or 'strategy')


def main():
    rows = []
    for f in sorted(glob.glob(str(ROOT / '*.md'))):
        if Path(f).name in NOT_CORPUS:
            continue
        r = parse(f)
        lang = r['lang'].lower()
        r['_code'] = strip_code(r['code'], 'python' if lang == 'python' else ('pine' if lang == 'pinescript' else lang))
        if lang == 'pinescript':
            res = screen_pine(r['_code'])
        else:
            res = screen_bot(r['_code'], r['name'])
        r['c1'], r['c1_why'], r['c2'], r['c2_why'], r['c3'], r['c3_why'], r['notes'] = res
        r['slug'] = f"{r['fmz_id']}_{slug(r['name'])}"
        rows.append(r)

    groups, scores = near_duplicates(rows, DUP_THRESHOLD, POSSIBLE_DUP_FLOOR)
    for r in rows:
        r['dup_group'] = ''
        r['representative'] = r['fmz_id']

    def rank_key(i):
        r = rows[i]
        # neutral choice: best screening status, then lowest FMZ id (earliest published)
        return (STATUS_ORDER[r['c3']] if r['c3'] == 'FLAG' else 0,
                max(STATUS_ORDER[r['c1']], STATUS_ORDER[r['c2']]), r['fmz_id'])

    dup_rows = []
    for g in groups:
        rep = min(g, key=rank_key)
        gid = rows[rep]['fmz_id']
        for i in g:
            rows[i]['dup_group'] = gid
            rows[i]['representative'] = gid
        others = sorted(rows[i]['fmz_id'] for i in g if i != rep)
        best = {rows[i]['fmz_id']: max(scores.get((min(i, j), max(i, j)), 0) for j in g if j != i) for i in g}
        dup_rows.append({
            'representative_id': gid,
            'representative_file': rows[rep]['file'],
            'lang': rows[rep]['lang'],
            'n_members': len(g),
            'collapsed_ids': ';'.join(map(str, others)),
            'collapsed_files': ' | '.join(rows[i]['file'] for i in sorted(g, key=lambda i: rows[i]['fmz_id']) if i != rep),
            'max_jaccard_per_collapsed': ';'.join(f"{k}:{best[k]:.2f}" for k in others),
        })

    for r in rows:
        blocked_vol = 'USES_VOLUME' in r['notes']
        if r['c3'] == 'FLAG':
            overall = 'FLAGGED_CRYPTO_ONLY'
        elif r['c1'] == 'FAIL' or r['c2'] == 'FAIL':
            overall = 'REJECTED'
        elif r['representative'] != r['fmz_id']:
            overall = 'DUPLICATE'
        elif blocked_vol:
            overall = 'HELD_NEEDS_VOLUME'
        else:
            overall = 'PORT_CANDIDATE'
        r['overall'] = overall

    fields = ['fmz_id', 'file', 'name', 'author', 'lang', 'last_modified', 'detail_url',
              'c1', 'c1_why', 'c2', 'c2_why', 'c3', 'c3_why', 'notes',
              'dup_group', 'representative', 'overall', 'slug']
    with open(ROOT / 'screening.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in sorted(rows, key=lambda r: r['fmz_id']):
            out = dict(r)
            for k in ('c1_why', 'c2_why', 'c3_why', 'notes'):
                out[k] = ' | '.join(r[k])
            w.writerow(out)
    with open(ROOT / 'duplicates.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(dup_rows[0].keys()))
        w.writeheader()
        for d in sorted(dup_rows, key=lambda d: d['representative_id']):
            w.writerow(d)
    with open(ROOT / 'possible_duplicates.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['fmz_id_a', 'fmz_id_b', 'jaccard', 'file_a', 'file_b'])
        band = sorted(((rows[i]['fmz_id'], rows[j]['fmz_id'], v, rows[i]['file'], rows[j]['file'])
                       for (i, j), v in scores.items() if v < DUP_THRESHOLD))
        for a, b, v, fa, fb in band:
            w.writerow([a, b, f'{v:.2f}', fa, fb])
    print(len(rows), 'screened;', len(groups), 'duplicate groups')


if __name__ == '__main__':
    main()
