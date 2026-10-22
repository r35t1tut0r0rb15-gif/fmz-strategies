"""UT Bot ATR trailing line (key 1, ATR 10), 1-hour bars: the close crossing over the line goes long, under it goes short; reversing (the ATR stop exits name ids that are never entered and never act).
Port of FMZ strategy #452716 "基于ATR和EMA的动态止盈止损自适应策略-ATR-and-EMA-based-Dynamic-Take-Profit-and-Stop-Loss-Adaptive-Strategy" (UT MB&SS Bot).

FMZ source id: 452716

Source
    https://www.fmz.com/strategy/452716 (PineScript v5, FMZ last modified 2024-05-28 14:15:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-146), key value 1; ATR 10; Heikin Ashi off; stop 2 ATR beyond the line (on 'UT Long' / 'UT Short')
    line: close > line[1] and close[1] > line[1] -> max(line[1], close - atr);  both under -> min(line[1], close + atr);  else close -+ atr
    close > line and crossover(close, line) -> entry Enter Long;  else close < line and crossover(line, close) -> entry Enter Short
    exit('Exit Long', 'UT Long', stop) / exit('Exit Short', 'UT Short', stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit's from_entry names 'UT Long' / 'UT Short', ids never entered (the entries are
      'Enter Long' / 'Enter Short'), so the stops never act: positions end at the opposite entry (as
      #451395). ema(src, 1) is the close itself. The line starts from 0 (nz) as written. Heikin Ashi
      is off by default. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, UT Bot line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452716_ut_bot_atr_line_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_len": [10, 14],
}
DEFAULT_PARAMS = {"key": 1.0, "atr_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nl = (float(p["key"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    for i in range(m):
        prev = line[i - 1] if i > 0 and not np.isnan(line[i - 1]) else 0.0
        c1 = cv[i - 1] if i > 0 else np.nan
        if np.isnan(nl[i]):
            continue                          # math.max / min with an na ATR give na
        if cv[i] > prev and c1 > prev:
            line[i] = max(prev, cv[i] - nl[i])
        elif cv[i] < prev and c1 < prev:
            line[i] = min(prev, cv[i] + nl[i])
        else:
            line[i] = cv[i] - nl[i] if cv[i] > prev else cv[i] + nl[i]
    ln = pd.Series(line, index=c.index)
    c1s, l1 = c.shift(1), ln.shift(1)
    above = (c > ln) & (c1s <= l1)
    below = (ln > c) & (l1 <= c1s)
    le = (c > ln) & above
    se = (c < ln) & below & ~le
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
