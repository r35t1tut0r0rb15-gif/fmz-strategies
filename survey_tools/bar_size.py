"""Rule 1 (2026-10-07) census: every corpus file with no bar size -> no_bar_size.csv.

Static text only; nothing is executed.

A file HAS a bar size when its source block carries FMZ's backtest header (`/*backtest ... */`;
MyLanguage writes it `(*backtest ... *)`, Python `'''backtest ... '''`) with a
`period:` value that has a unit (`1m`, `15m`, `1h`, `4h`, `1d`, `2d`, ...). It has NO bar size
when there is no such header, the header has no `period:` line, or the period has no unit
(e.g. 61867 `period: 1440`, 40155 `period: 15`). Ports of these files use
FREQ = "bar_size_pending" (unless the author's own code or words fix the bar size: see `note`).

Columns
  id               FMZ id
  language         as in screening.csv
  has_stop_logic   yes/no: comment-stripped code contains stop-loss / take-profit / trailing logic:
                   Pine strategy.exit(...) with stop=/loss=/limit=/profit=/trail_*; or an identifier
                   or call naming a stop, loss, profit target or trail (stop_loss, StopLoss, sl, tp,
                   trail..., 止损, 止盈, 移动止损). A static hint, not a reading.
  note             why there is no bar size, plus any period the code itself requests
                   (e.g. GetRecords(PERIOD_M15), a Pine timeframe input) or the description
                   names (hourly / daily wording)
  screen_outcome   overall outcome in screening.csv (review_decisions.csv wins where present)
  file             corpus file name
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fmzparse import parse  # noqa: E402
from screen import strip_code  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

STOP_PINE_EXIT = re.compile(r'strategy\.exit\s*\([^)]*\b(stop|loss|limit|profit|trail_points|trail_price|trail_offset)\s*=')
STOP_WORDS = re.compile(
    r'(?i)stop[_ ]?loss|stoploss|take[_ ]?profit|takeprofit|trailing|trail_?(stop|offset|points|price|pct|perc)'
    r'|\b(sl|tp|sl_?pct|tp_?pct|sl_?perc|tp_?perc|longstop|shortstop|stop_?price|stoplevel)\b'
    r'|止损|止盈|移动止|跟踪止')
CODE_PERIOD = re.compile(r'PERIOD_(M\d+|H\d+|D\d*|W\d*)')
DESC_PERIOD = re.compile(r'(小时线|日线|分钟线|周线|\b(hourly|daily|\d+\s*-?\s*(min|minute|hour|h)\b)\s*(bars?|chart|candles?|timeframe|k-?lines?))', re.I)


def bar_size(code):
    m = re.search(r'(?:/\*|\(\*|\'\'\'|""")\s*backtest(.*?)(?:\*/|\*\)|\'\'\'|""")', code, re.S)
    if not m:
        return None, 'no backtest header'
    pm = re.search(r'^\s*period\s*:\s*(\S*)', m.group(1), re.M)
    if not pm:
        return None, 'backtest header has no period'
    v = pm.group(1)
    if re.fullmatch(r'\d+(?:[mhdwM]|min|hour|day|week)s?', v):
        return v, ''
    return None, f'period without unit: "{v}"'


def main():
    rows = list(csv.DictReader(open(ROOT / 'screening.csv', encoding='utf-8')))
    decided = {r['fmz_id']: r['final_outcome']
               for r in csv.DictReader(open(ROOT / 'review_decisions.csv', encoding='utf-8'))}
    out = []
    for r in rows:
        p = parse(ROOT / r['file'])
        size, why = bar_size(p['code'])
        if size:
            continue
        lang = p['lang'].lower()
        code = strip_code(p['code'], 'python' if lang == 'python' else ('pine' if lang == 'pinescript' else lang))
        stop = bool(STOP_PINE_EXIT.search(code) or STOP_WORDS.search(code))
        notes = [why]
        req = sorted(set(CODE_PERIOD.findall(code)))
        if req:
            notes.append('code requests PERIOD_' + '/PERIOD_'.join(req))
        tf = re.findall(r'input(?:\.timeframe)?\s*\([^)]*["\'](\d+[SDWM]?|D|W|M)["\'][^)]*timeframe|input\.timeframe\s*\(\s*["\']([^"\']+)', code)
        if tf:
            notes.append('Pine timeframe input ' + ','.join(sorted({a or b for a, b in tf})))
        head = p['text'][:p['text'].find('> Source')] if '> Source' in p['text'] else ''
        dm = DESC_PERIOD.search(head)
        if dm:
            notes.append(f'description mentions "{dm.group(0).strip()}"')
        out.append({'id': r['fmz_id'], 'language': r['lang'], 'has_stop_logic': 'yes' if stop else 'no',
                    'note': '; '.join(notes), 'screen_outcome': decided.get(r['fmz_id'], r['overall']),
                    'file': r['file']})
    out.sort(key=lambda d: int(d['id']))
    with open(ROOT / 'no_bar_size.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f'{len(rows)} files read; {len(out)} with no bar size; '
          f'{sum(d["has_stop_logic"] == "yes" for d in out)} of them with stop logic')


if __name__ == '__main__':
    main()
