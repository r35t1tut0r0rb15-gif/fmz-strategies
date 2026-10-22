"""Three closes in a row outside the Bollinger 20 / 2 bands, hourly bars: the third close under the lower band goes long (when not long), the third over the upper band goes short (when not short); a close crossing the middle band either way closes the position.
Port of FMZ strategy #474630 "Triple Bollinger Bands Touch Trend Following Quantitative Trading Strategy" (Bollinger Bands Strategy - 3 Crossings).

FMZ source id: 474630

Source
    https://www.fmz.com/strategy/474630 (PineScript v6, FMZ last modified 2024-12-11 11:01:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-143), BB 20, 2 sd; three closes outside; exit on a basis cross
    close < lower -> longCount += 1, shortCount := 0;  close > upper -> shortCount += 1, longCount := 0;  neither -> both 0;  longCount >= 3 and size <= 0 -> entry Long, longCount := 0;  shortCount >= 3 and size >= 0 -> entry Short, shortCount := 0;  cross(close, basis) -> close the held side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters and the position are followed in a loop in the written order: the counts reset after
      an entry, a count keeps growing while that side is already held, and the basis-cross close acts
      only on the side held into the bar and not reversed on it (#437773). REVERSAL INTENDED (a short
      entry from a long reverses it). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three closes outside the bands with a basis-cross exit.
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

NAME = "fmz_474630_bb20_three_closes_outside_basis_cross_exit"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "count": 3}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    below = (c < basis - dev).to_numpy()
    above = (c > basis + dev).to_numpy()
    ex = (((c > basis) & (c.shift(1) <= basis.shift(1))) | ((c < basis) & (c.shift(1) >= basis.shift(1)))).to_numpy()
    k = int(p["count"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lc = scn = 0
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if below[i]:
            lc, scn = lc + 1, 0
        if above[i]:
            scn, lc = scn + 1, 0
        if not below[i] and not above[i]:
            lc = scn = 0
        if lc >= k and pos <= 0:
            if nxt != 1:
                le[i], nxt = True, 1
            lc = 0
        if scn >= k and pos >= 0:
            if nxt != -1:
                se[i], nxt = True, -1
            scn = 0
        if ex[i] and pos == 1 and nxt == 1:
            lx[i], nxt = True, 0
        if ex[i] and pos == -1 and nxt == -1:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
