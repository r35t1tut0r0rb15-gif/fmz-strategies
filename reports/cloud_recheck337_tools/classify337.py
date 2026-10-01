"""Cloud session, 2026-10-01. Stricter re-check of the 337 'probable' coarse-bar stop rows from cloud batch 5f.

Static analysis only; nothing is executed. For each Pine file it asks: does a
stop / target / trailing level actually reach an order call?

Method
  1. Extract the source block, drop the /*backtest*/ block, comments and string literals
     (input titles are kept separately so `a = input(2, title="Stop Loss %")` still seeds `a`).
  2. Join physical lines into statements (open brackets, trailing operators, deeper-indented
     continuation lines).
  3. Seed identifiers: names that look like stops/targets (stop, sl, tp, trail, target,
     profit, loss, 止损, 止盈 ...) plus any variable assigned from an input() whose title does.
     Also seed uses of strategy.position_avg_price / strategy.openprofit (entry-relative levels).
  4. Propagate: a variable is tainted if its assignment mentions a tainted name (fixed point).
  5. For every strategy.* order call, collect its argument text plus the conditions of every
     enclosing `if` (by indentation) and test them for taint.
Classes (first match wins)
  intrabar_order    strategy.exit/order/entry exit-side call with stop=/limit=/loss=/profit=/trail_*
                    (or positional price args) fed by a stop level -> fills inside the bar
  close_based_stop  strategy.close / close_all / exit(no price) / order driven by a stop level
                    evaluated on the bar's values -> fills at the next bar's open
  stop_and_reverse     the stop-named level only drives strategy.entry (signal flip, e.g. SuperTrend)
  display_or_unused stop names exist but reach no order call
  no_orders         the script places no orders at all (study/indicator)
"""
import csv, os, re, sys, collections

# the repository root (this file lives in reports/cloud_recheck337_tools/)
REPO = os.environ.get('FMZ_REPO') or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) + os.sep

# A name is stop-like if one of its words (split on _ and camelCase) is a stop word, or a word
# contains one of the stop stems. Whole-word matching keeps 'slow', 'slope', 'output' out.
STOP_WORDS = {'sltp', 'sl', 'tp', 'tsl', 'sls', 'tps', 'tp1', 'tp2', 'tp3', 'sl1', 'sl2'}
STOP_STEMS = re.compile(r'(stop|trail|target|tgt|profit|loss|止损|止盈)', re.I)
STOPPY = re.compile(r'(stop|trail|target|tgt|profit|loss|止损|止盈|\bsl\b|\btp\b)', re.I)  # for input titles


def words(name):
    parts = re.split(r'_+', name)
    out = []
    for p in parts:
        out += re.findall(r'[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|[A-Z]+|\d+|[\u4e00-\u9fff]+', p)
    return [w.lower() for w in out]


NOT_STOPPY = re.compile(r'^(strategy|true|false|na|close|open|high|low|volume|time|bar_index)$')
PNL_SEED = re.compile(r'strategy\.(position_avg_price|openprofit|opentrades\.entry_price)'
                      r'|(?<![\w.])\w*(entry_?price|EntryPrice|entryPrice|buy_?price|sell_?price|buyPrice|sellPrice)\w*', re.I)
IDENT = re.compile(r'(?<![\w.])([A-Za-z_一-鿿][\w一-鿿]*)(?![\w])')  # bare names and user-function calls
ORDER = re.compile(r'strategy\.(exit|close_all|close|order|entry|cancel_all|cancel)\s*\(')
PRICE_KW = re.compile(r'\b(stop|limit|loss|profit|trail_points|trail_offset|trail_price)\s*=')


def source(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'> Source \(([^)]*)\)\s*\n+```[^\n]*\n(.*?)\n```', t, re.S)
    if not m:
        return None, ''
    c = re.sub(r'/\*backtest.*?\*/', '', m.group(2), flags=re.S)
    return m.group(1), c


_q = [None]  # open quote carried across lines (Pine allows a string to continue on the next line)


def strip_line(line):
    """Remove // comments and string literals; return (code, strings)."""
    out, strs, i, q = [], [], 0, _q[0]
    buf = ''
    while i < len(line):
        ch = line[i]
        if q:
            if ch == '\\':
                buf += line[i:i + 2]; i += 2; continue
            if ch == q:
                strs.append(buf); buf = ''; q = None; out.append('""')
            else:
                buf += ch
        else:
            if ch in '"\'':
                q = ch
            elif line.startswith('//', i):
                break
            else:
                out.append(ch)
        i += 1
    _q[0] = q
    if q:
        strs.append(buf)
    return ''.join(out), strs


def statements(code):
    """Yield (lineno, indent, text, strings) joined over continuation lines."""
    lines = code.split('\n')
    _q[0] = None
    stmts, cur = [], None
    depth = 0
    for n, raw in enumerate(lines, 1):
        txt, strs = strip_line(raw)
        if not txt.strip():
            continue
        indent = len(raw.expandtabs(4)) - len(raw.expandtabs(4).lstrip())
        cont = cur is not None and (
            depth > 0
            or re.search(r'(\b(and|or|not)|[-+*/?:,=<>(\[]|:=)\s*$', cur[2])
            or (indent > cur[1] and not re.match(r'\s*(if|else|for|while|switch)\b', txt)
                and not re.search(r'(=>|\bif\b.*)$', cur[2].strip()) and indent % 4 != 0)
        )
        if cont:
            cur[2] += ' ' + txt.strip(); cur[3] += strs
        else:
            if cur: stmts.append(cur)
            cur = [n, indent, txt.rstrip(), strs]
            depth = 0
        depth += txt.count('(') + txt.count('[') - txt.count(')') - txt.count(']')
        depth = max(depth, 0)
    if cur: stmts.append(cur)
    return stmts


ASSIGN = re.compile(r'^\s*(?:var\s+|varip\s+)?(?:(?:float|int|bool|string|color|series|simple|const|line|label)\s+)*'
                    r'(\[[^\]]+\]|[A-Za-z_一-鿿][\w一-鿿]*)\s*(:=|=)(?!=)\s*(.*)$')


def names(expr):
    return {m for m in IDENT.findall(expr) if not NOT_STOPPY.match(m)}


# words that make a stop-like name something other than a price level: backtest date windows
# (testStopYear, testPeriodStop), display settings, loss-streak counters
NOT_LEVEL_WORDS = {'year', 'month', 'day', 'hour', 'minute', 'date', 'time', 'color', 'colour', 'col',
                   'transp', 'tooltip', 'label', 'print', 'string', 'info', 'count', 'filter', 'alert'}


def stoppy(name):
    if NOT_STOPPY.match(name):
        return False
    ws = words(name)
    if NOT_LEVEL_WORDS & set(ws) or ('test' in ws and 'period' in ws):
        return False
    # glue digits back on (tp1, sl2)
    ws += [a + b for a, b in zip(ws, ws[1:]) if b.isdigit()]
    return any(w in STOP_WORDS for w in ws) or bool(STOP_STEMS.search(name))


def classify_pine(code):
    st = statements(code)
    assigns = []  # (lhs names, rhs, strings, lineno)
    # user-defined functions: name(params) => body (same line, or the deeper-indented lines below)
    order_funcs = {}  # user functions whose body places orders -> order kinds
    FUNC = re.compile(r'^\s*([A-Za-z_]\w*)\s*\(([^)]*)\)\s*=>\s*(.*)$')
    for k, (n, ind, txt, strs) in enumerate(st):
        mf = FUNC.match(txt)
        if not mf:
            continue
        body = [mf.group(3)]
        for n2, ind2, txt2, strs2 in st[k + 1:]:
            if ind2 <= ind:
                break
            body.append(txt2)
        assigns.append(([mf.group(1)], ' '.join(body), strs, n))
        kinds = ORDER.findall(' '.join(body))
        if kinds:
            order_funcs[mf.group(1)] = kinds
    # control dependence: a value set inside `if cond` also depends on cond
    cstack = []
    for n, ind, txt, strs in st:
        while cstack and cstack[-1][0] >= ind:
            cstack.pop()
        m = ASSIGN.match(txt)
        if m and '=>' not in m.group(3)[:2]:
            lhs = m.group(1)
            lhs_names = re.findall(r'[\w\u4e00-\u9fff]+', lhs) if lhs.startswith('[') else [lhs]
            assigns.append((lhs_names, m.group(3) + ' ' + ' '.join(c for _, c in cstack), strs, n))
        mi = re.match(r'\s*(?:else\s+)?if\b(.*)$', txt)
        if mi:
            cstack.append((ind, mi.group(1)))
        elif re.match(r'\s*else\b', txt) or re.match(r'\s*(for|while)\b', txt) or txt.rstrip().endswith('=>'):
            cstack.append((ind, ''))
    tainted, why = set(), {}
    for lhs, rhs, strs, n in assigns:
        is_switch = bool(re.search(r'\binput\.bool\b|\binput\s*\(\s*(defval\s*=\s*)?(true|false)\b|defval\s*=\s*(true|false)\b'
                                   r'|options\s*=\s*\[\s*""\s*,\s*""\s*\]', rhs))
        for v in lhs:
            if is_switch:
                continue  # a use/enable switch gates a stop but is not one; the level itself must reach the order
            if stoppy(v):
                tainted.add(v); why.setdefault(v, f'L{n} name')
            if re.search(r'\binput', rhs) and any(title_stoppy(s) for s in strs[:2]):  # title, not tooltip
                tainted.add(v); why.setdefault(v, f'L{n} input title')
            if PNL_SEED.search(rhs):
                tainted.add(v); why.setdefault(v, f'L{n} entry-price/openprofit')
    changed = True
    while changed:
        changed = False
        for lhs, rhs, strs, n in assigns:
            if names(rhs) & tainted:
                for v in lhs:
                    if v not in tainted:
                        tainted.add(v); why[v] = f'L{n} from {sorted(names(rhs) & tainted)[0]}'; changed = True

    # enclosing-if stack by indentation
    stack, calls = [], []
    for n, ind, txt, strs in st:
        while stack and stack[-1][0] >= ind:
            stack.pop()
        for m in ORDER.finditer(txt):
            calls.append((n, m.group(1), txt, [c for _, c in stack], strs))
        # a call to a user function that places orders counts as those orders, in the caller's context
        if not FUNC.match(txt):
            for fname, kinds in order_funcs.items():
                if re.search(r'(?<![\w.])' + fname + r'\s*\(', txt):
                    for k in kinds:
                        calls.append((n, k, txt + '  [via ' + fname + '()]', [c for _, c in stack], strs))
        mi = re.match(r'\s*(?:else\s+)?if\b(.*)$', txt)
        if mi:
            stack.append((ind, mi.group(1)))
        elif re.match(r'\s*else\b', txt):
            stack.append((ind, ''))
        elif re.match(r'\s*(for|while)\b', txt) or txt.rstrip().endswith('=>'):
            stack.append((ind, ''))
        # ternary-driven order calls: cond ? strategy.close(...) : na  -> condition is in txt itself

    if not calls:
        return 'no_orders', '', set(), tainted
    hits = collections.defaultdict(list)
    EXIT_LABEL = re.compile(r'(?i)stop|loss|exit|close|target|profit|\bsl\b|\btp\b|止损|止盈|平')
    for n, kind, txt, conds, strs in calls:
        ctx = txt + ' ' + ' '.join(conds)
        t = (names(ctx) & tainted) | ({'<pnl>'} if PNL_SEED.search(ctx) else set())
        # An exit order with a price argument is an inside-the-bar stop/target whatever its names are:
        # strategy.exit(stop=/limit=/loss=/profit=/trail_*=), or a strategy.order(stop=/limit=) that closes
        # the open position (its qty or its conditions use strategy.position_size).
        kw = set(re.findall(r'\b(stop|limit|loss|profit|trail_points|trail_offset|trail_price)\s*=', txt))
        # 'position_size == 0' means flat (an entry); an open position is position_size >, <, != 0 or its qty
        closes = re.search(r'position_size\s*(\)|[<>]|!=|\*|,)|abs\s*\(\s*strategy\.position_size', ctx) \
            or any(EXIT_LABEL.search(s) for s in strs)
        if kw and (kind == 'exit' or (kind == 'order' and kw & {'stop', 'limit'} and closes)):
            k = {'SL' for x in kw if x in ('stop', 'loss')} | {'TP' for x in kw if x in ('limit', 'profit')} \
                | {'trailing' for x in kw if x.startswith('trail')}
            hits['intrabar_order'].append((n, txt, t | {'<kw:' + '+'.join(sorted(k)) + '>'}))
            continue
        if not t:
            continue
        own = txt
        price_args = PRICE_KW.search(own) and (names(own) & tainted or PNL_SEED.search(own))
        if kind == 'exit':
            # positional: id, from_entry, qty, qty_percent, profit, limit, loss, stop ...
            argtxt = own[own.find('strategy.exit'):]
            npos = len([a for a in re.split(r',(?![^(]*\))', argtxt) if '=' not in a or '==' in a])
            if price_args or npos >= 5:
                hits['intrabar_order'].append((n, own, t)); continue
            if not PRICE_KW.search(own):
                continue  # no profit/limit/loss/stop/trail argument: Pine places no exit order
            hits['close_based_stop'].append((n, own, t)); continue
        if kind in ('order', 'entry') and price_args and re.search(r'\b(stop|limit)\s*=', own):
            if kind == 'order':
                continue  # a priced strategy.order that does not close the position is an entry or add-on
                          # (closing ones were taken above)
            hits['stop_entry'].append((n, own, t)); continue
        if kind in ('close', 'close_all', 'order'):
            hits['close_based_stop'].append((n, own, t)); continue
        if kind == 'entry':
            hits['stop_and_reverse'].append((n, own, t)); continue
    deps = collections.defaultdict(set)
    for lhs, rhs, strs, n in assigns:
        for v in lhs:
            deps[v] |= names(rhs) & tainted
            if PNL_SEED.search(rhs):
                deps[v].add('<pnl>')
    for cls in ('intrabar_order', 'close_based_stop', 'stop_and_reverse', 'stop_entry'):
        if hits[cls]:
            # evidence: prefer a close/exit call over an add-on strategy.order
            ordered = sorted(hits[cls], key=lambda h: 'strategy.order' in h[1])
            n, own, t = ordered[0]
            seen, todo = set(), [x for h in hits[cls] for x in h[2]]
            while todo:
                v = todo.pop()
                if v in seen:
                    continue
                seen.add(v)
                todo += list(deps.get(v, ()))
            seeds = {x for x in seen if x == '<pnl>' or x.startswith('<kw:') or stoppy(x)}
            return cls, f'L{n}: {own.strip()[:160]}', seeds, tainted
    return 'display_or_unused', '', set(), tainted


def title_stoppy(s):
    ws = set(re.findall(r'[a-z]+', s.lower()))
    return bool(STOPPY.search(s)) and not (ws & (NOT_LEVEL_WORDS | {'backtest', 'period', 'session'}))


def stop_kind(ts):
    k = set()
    for t in ts:
        if t == '<pnl>': k.add('entry-relative'); continue
        if t.startswith('<kw:'): k.update(t[4:-1].split('+')); continue
        if re.search(r'trail', t, re.I): k.add('trailing')
        if re.search(r'(tp|take|profit|target|tgt|止盈)', t, re.I): k.add('TP')
        if re.search(r'(stop|stp|sl|loss|止损)', t, re.I) and not re.search(r'trail', t, re.I): k.add('SL')
    return '+'.join(sorted(k)) or 'derived'


if __name__ == '__main__':
    rows = [r for r in csv.DictReader(open(sys.argv[1])) if r['detection'] == 'probable']
    out = []
    for r in rows:
        lang, code = source(REPO + r['file'])
        if r['language'] != 'PineScript':
            out.append({**r, 'recheck': 'manual_js', 'recheck_stop_kind': '', 'evidence': ''})
            continue
        cls, ev, t, _ = classify_pine(code)
        out.append({**r, 'recheck': cls, 'recheck_stop_kind': stop_kind(t) if t else '', 'evidence': ev})
    with open(sys.argv[2], 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), lineterminator='\n')
        w.writeheader(); w.writerows(out)
    print(collections.Counter(o['recheck'] for o in out))
