"""HPotter 2/20 EMA, 2-hour bars: the close above the EMA 20 and above the two-bar extreme on the EMA's far
side goes long, below both goes short; otherwise the last side is kept.
Port of FMZ strategy #428706 "Developing a 2 20 Exponential Moving Average Strategy" (Strategy 2/20 Exponential Moving Average).

FMZ source id: 428706

Source
    https://www.fmz.com/strategy/428706 (PineScript v2, FMZ last modified 2023-10-08 15:14:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 148-162), length 20, reverse false
    nHH = max(high, high[1]); nLL = min(low, low[1]); nXS = (nLL > ema or nHH < ema) ? nLL : nHH
    pos = close > ema and close > nXS ? 1 : close < ema and close < nXS ? -1 : pos[1]
    pos == 1 -> entry long; pos == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to false and is fixed (it only swaps the sides).
    * strategy.entry reverses: REVERSAL INTENDED; a same-direction entry while in a position is
      ignored (pyramiding 0). FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428706_hpotter_2_20_ema"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
}
DEFAULT_PARAMS = {"length": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    hh = pd.concat([h, h.shift(1)], axis=1).max(axis=1, skipna=False)
    ll = pd.concat([lo, lo.shift(1)], axis=1).min(axis=1, skipna=False)
    xs = ll.where((ll > xa) | (hh < xa), hh)
    upc = ((c > xa) & (c > xs)).to_numpy()
    dnc = ((c < xa) & (c < xs)).to_numpy()
    m = len(c)
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if upc[i]:
            q = 1
        elif dnc[i]:
            q = -1
        pos[i] = q
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(pos == 1, index=idx), false, pd.Series(pos == -1, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
