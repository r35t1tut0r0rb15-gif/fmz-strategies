"""Persistent EMA stack entries, 1-minute bars: the stack EMA 10 over EMA 200 and EMA 20 over EMA 50 that has held for ten bars (and was not
in force eleven bars ago) goes long; the mirror goes short; a long closes when EMA 10 falls under EMA 200, or EMA 20 under EMA 50 when the stack was
not in force 11 bars ago (the short mirrors).
Port of FMZ strategy #435955 "Dual Moving Average Range Breakout Strategy" (Advancing Our Basic Strategy).

FMZ source id: 435955

Source
    https://www.fmz.com/strategy/435955 (PineScript v3, FMZ last modified 2023-12-20 13:59:38).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 101-128), EMA 10 / 20 / 50 / 200
    long = ema10 > ema200 and ema20 > ema50;  longcondition = long and long[10] and not long[11];  closelong = ema10 < ema200 or (ema20 < ema50 and not long[11]);  shorts mirror
    entry long (longcondition), entry short (shortcondition), close long (closelong), close short (closeshort)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds tighter than "or": closelong = A or (B and not long[11]). The four orders are
      filled in the script's call order at the next open (entry long, entry short, close long, close
      short). The date window (2018 to 2038) is the author's backtest window: dropped. The fixed size 1
      is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average stack.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed order size stored.
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

NAME = "fmz_435955_ema_stack_persistence"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold": [10, 5],
    "ema200": [200, 100],
}
DEFAULT_PARAMS = {"hold": 10, "ema200": 200}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e10 = c.ewm(span=10, adjust=False).mean()
    e20 = c.ewm(span=20, adjust=False).mean()
    e50 = c.ewm(span=50, adjust=False).mean()
    e200 = c.ewm(span=int(p["ema200"]), adjust=False).mean()
    k = int(p["hold"])
    lg = ((e10 > e200) & (e20 > e50)).fillna(False)
    sh = ((e10 < e200) & (e20 < e50)).fillna(False)
    f = lambda s, n: s.shift(n, fill_value=False)           # noqa: E731
    long_c = (lg & f(lg, k) & ~f(lg, k + 1)).to_numpy()
    short_c = (sh & f(sh, k) & ~f(sh, k + 1)).to_numpy()
    close_l = ((e10 < e200) | ((e20 < e50) & ~f(lg, k + 1))).fillna(False).to_numpy()
    close_s = ((e10 > e200) | ((e20 > e50) & ~f(sh, k + 1))).fillna(False).to_numpy()
    m = len(long_c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            e_l, e_s, c_l, c_s = pend
            if e_l and pos <= 0:
                pos = 1
            if e_s and pos >= 0:
                pos = -1
            if c_l and pos == 1:
                pos = 0
            if c_s and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(long_c[i]), bool(short_c[i]), bool(close_l[i]), bool(close_s[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
