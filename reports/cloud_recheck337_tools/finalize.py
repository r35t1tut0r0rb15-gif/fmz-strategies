"""Apply the hand review (overrides below, hand_checked.txt) to classify337.py's output and write the deliverable CSV.
   Run from this folder:  python3 finalize.py ../cloud_recheck337_2026-10-01.csv   (reads recheck.csv)"""
import csv, re, sys, collections
sys.path.insert(0, '.')
import classify337 as c

OVERRIDES = {  # id: (class, stop_kind, reason)
    '429476': ('no_stop_exit', '', "'TP' is typical price (Finite Volume Elements), not a target"),
    '435887': ('no_stop_exit', '', "'TP' is typical price (Finite Volume Elements), not a target"),
    '477607': ('no_stop_exit', '', 'targetBuy is a band level that triggers entries'),
    '432765': ('no_stop_exit', '', 'long-only; entry-price test only adds to the position'),
    '468335': ('no_stop_exit', '', 'stop distance only sizes the position; long-only, no stop exit'),
    '473940': ('no_stop_exit', '', 'stopLoss computed, never used; reEntryAfterSL is an entry signal'),
    '449709': ('no_stop_exit', '', "'sltp' is the RSI band's 'Minimum Difference' input"),
    '366404': ('no_stop_exit', '', "'sl' is a peak-detection threshold that triggers entries"),
    '427263': ('no_stop_exit', '', "'tp' is a ROC period (best-hour strategy)"),
    '380530': ('no_stop_exit', '', "'tp' is a ROC period (best-hour strategy)"),
    '483038': ('no_stop_exit', '', "'sl' is the lowest value of an oscillator (snake line), not a stop"),
    '430850': ('no_stop_exit', '', "'takeProfitLevel' is an RSI-oscillator level; the exit is a signal, not a price target"),
    '428975': ('stop_and_reverse', 'trailing', 'PB-SAR elastic stop: reverses on the SAR trigger (its TP means trigger price); its strategy.exit calls have no price and do nothing'),
    '438036': ('close_based_stop', 'SL', "unnamed stop level (log midpoint) plotted as 'StopLoss'; exit when close is below it"),
}
JS = {  # hand review of the 10 JavaScript files
    '12348':  ('live_price_stop', 'SL', 'ticker.Buy/Sell vs entryPrice*(1±StopLossRatio), checked every poll'),
    '275287': ('live_price_stop', 'TP', 'position profit > step closes (TP); loss adds to the position (martingale), no stop-loss'),
    '299799': ('no_stop_exit', '', 'DCA; sells when the ahr999 index falls below a line, not a price stop'),
    '311968': ('live_price_stop', 'SL+TP', 'account floating-PnL stop and take-profit; both OFF by default (EnableStopLoss/EnableStopWin false)'),
    '339344': ('close_based_stop', 'SL+entry-relative', 'uses the last CLOSED bar: r[len-2].Close vs holdPrice*(1±stopLoss)'),
    '353659': ('intrabar_order', 'TP', 'resting limit sell at position price + profitTarget'),
    '356471': ('live_price_stop', 'SL+TP', 'position profit vs target; stop when loss exceeds the margin'),
    '394112': ('live_price_stop', 'SL+TP', 'order-book best bid/ask vs stopLossPrice/stopProfitPrice'),
    '405725': ('live_price_stop', 'SL+TP', "checks the forming bar's Close (live price) against hl2 ± ATR grid, every checkTime seconds"),
}
FILLS = {
    'intrabar_order': 'inside the bar (stop/limit order)',
    'live_price_stop': 'inside the bar (live price checked each poll)',
    'close_based_stop': "next bar's open (condition read at bar close)",
    'stop_and_reverse': "next bar's open, by an opposite entry",
    'stop_entry': 'no stop exit; the entry itself is a stop/limit order',
    'no_stop_exit': 'no stop exit',
}
Y14C = {'intrabar_order': 'yes', 'live_price_stop': 'yes', 'close_based_stop': 'no',
        'stop_and_reverse': 'no', 'stop_entry': 'no', 'no_stop_exit': 'no'}

hand = set(open('hand_checked.txt').read().split())
OFF = re.compile(r'^\s*(?:var\s+)?(\w+)\s*=\s*input(?:\.bool)?\s*\((?=[^\n]*(?:defval\s*=\s*(?:false|"No"|\'No\'|"Off")|^\s*false\b|\(\s*false\b))', re.M | re.I)

out = []
for r in csv.DictReader(open('recheck.csv')):
    sid = r['strategy_id']
    cls, kind, ev = r['recheck'], r['recheck_stop_kind'], r['evidence']
    review, note = ('hand-checked' if sid in hand else 'auto'), ''
    if cls == 'display_or_unused':
        cls = 'no_stop_exit'
        note = 'stop/target names found, but none reaches an order call'
    if cls == 'stop_entry':
        note = 'stop=/limit= on strategy.entry makes the ENTRY a stop/limit order; there is no stop exit'
    if sid in OVERRIDES:
        cls, kind, note = OVERRIDES[sid]; review = 'hand-override'
    if r['language'] != 'PineScript':
        cls, kind, note = JS[sid]; review = 'hand-checked'; ev = ''
    off = ''
    if r['language'] == 'PineScript' and cls in ('intrabar_order', 'close_based_stop', 'stop_and_reverse'):
        _, code = c.source(c.REPO + r['file'])
        nocomment = '\n'.join(l.split('//')[0] for l in code.split('\n'))
        flags = [m.group(1) for m in OFF.finditer(nocomment) if c.stoppy(m.group(1)) or re.search(r'(?i)stop|trail|profit|tp|sl', m.group(1))]
        # enable-style "Yes"/"No" option inputs defaulting to No
        flags += re.findall(r'(?im)^\s*(\w*(?:stop|trail|target|profit|sl|tp)\w*)\s*=\s*input\([^\n]*defval\s*=\s*"No"', nocomment)
        if flags:
            off = 'check: ' + ','.join(sorted(set(flags)))[:80]
    if sid == '311968':
        off = 'yes (EnableStopLoss, EnableStopWin default false)'
    out.append({
        'strategy_id': sid, 'bar_size': r['bar_size'], 'language': r['language'], 'base_period': r['base_period'],
        'batch5f_stop_type': r['stop_type'], 'recheck_class': cls, 'recheck_stop_kind': kind,
        'stop_fills': FILLS[cls], 'y14c_affected': Y14C[cls], 'stop_default_off': off,
        'review': review, 'note': note, 'evidence': ev, 'file': r['file'],
    })

with open(sys.argv[1], 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(out)
C = collections.Counter(o['recheck_class'] for o in out)
print(C, sum(C.values()))
print(collections.Counter(o['review'] for o in out))
print('y14c yes:', sum(o['y14c_affected'] == 'yes' for o in out), ' default-off flagged:', sum(bool(o['stop_default_off']) for o in out))
