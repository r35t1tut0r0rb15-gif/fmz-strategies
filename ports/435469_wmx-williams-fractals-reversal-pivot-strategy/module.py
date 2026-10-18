"""Williams fractals on closes, 1-hour bars: a close crossing over the level taken at the fourth-latest change of the down-fractal
state, on a rising bar, goes long; a close crossing under the level of the fourth-latest up-fractal change, on a falling
bar, goes short (reversing).
Port of FMZ strategy #435469 "WMX Williams Fractals Reversal Pivot Strategy" (WMX Williams Fractals strategy V4).

FMZ source id: 435469

Source
    https://www.fmz.com/strategy/435469 (PineScript v4, FMZ last modified 2023-12-15 10:37:01).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 175-207), fractal periods n 2; highs and lows both taken from the close; valuewhen occurrence 3
    upFractal = High[n] over the n + 2 .. n + 6 earlier bars (ties allowed) and High[n-1], High[n-2] (the bars after);  dnFractal the mirror;  h = l = close
    U = valuewhen(upFractal != upFractal[1], close, 3);  L = valuewhen(dnFractal != dnFractal[1], close, 3)
    crossover(close, L) and close > open -> entry long (when position_size <= 0);  crossunder(close, U) and close < open -> entry short (when position_size >= 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both fractal series are built on the CLOSE (h = l = close), as written. The fractal at n bars
      back is confirmed by the n - 1 later bars and the current one: it uses bars up to the current
      bar only. valuewhen(cond, src, 3) is the value at the 4th-latest bar on which the state CHANGED
      (a start or an end of a fractal), the current bar included. strategy.entry reverses (the
      position_size tests only skip a same-side entry): REVERSAL INTENDED. The 100 % equity size and
      pyramiding 10 are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, commission and pyramiding stored.
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

NAME = "fmz_435469_fractal_level_cross_on_close"
FAMILY = "fractal_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [2, 3],
    "occurrence": [3, 1],
}
DEFAULT_PARAMS = {"n": 2, "occurrence": 3}


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


def _fractal(x, n, up):
    """Pine's five-pattern fractal on series x, centred n bars back (bars after it: n - 1 and n - 2 back)."""
    def S(k):
        return x.shift(k)
    cmp_ = (lambda a, b: a < b) if up else (lambda a, b: a > b)       # strictly beyond the centre
    cmpe = (lambda a, b: a <= b) if up else (lambda a, b: a >= b)     # beyond or equal
    c0 = S(n)
    after = cmp_(S(n - 1), c0) & cmp_(S(n - 2), c0)
    pats = [
        cmp_(S(n + 2), c0) & cmp_(S(n + 1), c0),
        cmp_(S(n + 3), c0) & cmp_(S(n + 2), c0) & (S(n + 1) == c0),
        cmp_(S(n + 4), c0) & cmp_(S(n + 3), c0) & (S(n + 2) == c0) & cmpe(S(n + 1), c0),
        cmp_(S(n + 5), c0) & cmp_(S(n + 4), c0) & (S(n + 3) == c0) & (S(n + 2) == c0) & cmpe(S(n + 1), c0),
        cmp_(S(n + 6), c0) & cmp_(S(n + 5), c0) & (S(n + 4) == c0) & cmpe(S(n + 3), c0) & (S(n + 2) == c0)
        & cmpe(S(n + 1), c0),
    ]
    out = pats[0]
    for q in pats[1:]:
        out = out | q
    return (out & after).fillna(False).to_numpy()


def _valuewhen(change, src, occ):
    """Pine valuewhen(change, src, occ): src at the (occ + 1)-th latest bar where change was true (NaN before)."""
    out = np.full(len(src), np.nan)
    hist = []
    for i in range(len(src)):
        if change[i]:
            hist.append(src[i])
        if len(hist) > occ:
            out[i] = hist[-1 - occ]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["n"])
    upf, dnf = _fractal(c, n, True), _fractal(c, n, False)
    chg_u = np.concatenate(([False], upf[1:] != upf[:-1]))
    chg_d = np.concatenate(([False], dnf[1:] != dnf[:-1]))
    cv = c.to_numpy(dtype=float)
    U = pd.Series(_valuewhen(chg_u, cv, int(p["occurrence"])), index=c.index)
    L = pd.Series(_valuewhen(chg_d, cv, int(p["occurrence"])), index=c.index)
    le = ((c > L) & (c.shift(1) <= L.shift(1)) & (c > o)).fillna(False).astype(bool)
    se = ((c < U) & (c.shift(1) >= U.shift(1)) & (c < o)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
