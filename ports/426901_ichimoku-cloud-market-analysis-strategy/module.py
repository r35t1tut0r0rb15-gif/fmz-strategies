"""Easymoku: with the close above both displaced cloud spans and above both spans twice the
displacement back, the Tenkan / Kijun state turning up goes long and turning down closes it;
below both, the mirror goes short. Periods are the "occidental" 7 / 22 / 44 / 22 set x 5.9.
Port of FMZ strategy #426901 "Ichimoku Cloud Market Analysis Strategy".

Source
    https://www.fmz.com/strategy/426901 (PineScript v4, FMZ last modified 2023-12-01 14:58:48).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 182-227), multiplier 5.9, occidental settings
    tenkan / kijun / senkouB periods round(7 / 22 / 44 x 5.9) = 41 / 130 / 260, displacement 130
    KUMO = close above both spans [disp - 1] ? 1 : below both ? 0 : na
    CHIKOU = close above both spans [2 disp] ? 1 : below both ? 0 : na
    TK = crossover(tenkan, kijun) ? 1 : crossunder ? -1 : TK[1]
    KUMO == 1 and CHIKOU == 1: TK == 1 -> entry long; TK == -1 -> close long
    KUMO == 0 and CHIKOU == 0: TK == -1 -> entry short; TK == 1 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * KUMO / CHIKOU / TK are declared `var bool` but assigned 1 / 0 / na and -1; the port uses
      the evident numeric reading (1 above, 0 below, na inside) (decision owed: under a bool
      cast na and 0 would both read as "below").
    * Fills in issue order; an entry reversing the other side stands. REVERSAL INTENDED
      (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426901_easymoku"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [1.0, 3.0, 5.9],
}
DEFAULT_PARAMS = {"multiplier": 5.9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    per = lambda n: int(round(n * p["multiplier"]))
    tp, kp, bp, disp = per(7), per(22), per(44), per(22)
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    don = lambda n: (l.rolling(n).min() + h.rolling(n).max()) / 2
    tenkan, kijun = don(tp), don(kp)
    sa, sb = (tenkan + kijun) / 2, don(bp)
    above = lambda k: (c > sa.shift(k)) & (c > sb.shift(k))
    below = lambda k: (c < sa.shift(k)) & (c < sb.shift(k))
    bull = (above(disp - 1) & above(2 * disp)).to_numpy()
    bear = (below(disp - 1) & below(2 * disp)).to_numpy()
    d = tenkan - kijun
    tk = _always_in(((d > 0) & (d.shift(1) <= 0)).to_numpy(), ((d < 0) & (d.shift(1) >= 0)).to_numpy(), bars_df.index)
    tk_state = np.zeros(len(c))
    s = 0
    for i, (u, w) in enumerate(zip(tk[0].to_numpy(), tk[2].to_numpy())):
        s = 1 if u else (-1 if w else s)
        tk_state[i] = s
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        before = pos
        if bull[i]:
            if tk_state[i] == 1 and before <= 0:
                pos = 1
            elif tk_state[i] == -1 and before == 1:
                pos = 0
        if bear[i]:
            if tk_state[i] == -1 and before >= 0:
                pos = -1
            elif tk_state[i] == 1 and before == -1:
                pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
