"""Vegas wave: when the close and EMAs 144 / 169 all stand more than 0.1 % above EMA 233, go long
from flat or short; a long is reversed to short once the close is under all three EMAs with
EMA 144 <= EMA 233. Shorts open only by reversing a long.
Port of FMZ strategy #426367 "Vegas Trend Wave Strategy".

Source
    https://www.fmz.com/strategy/426367 (PineScript v3, FMZ last modified 2023-09-11 15:23:35).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 65-102), 0.1 / 0.1 / 0.1 %
    pDiff(x, y) = (x - y) / x * 100
    pDiff(close, ema233) > 0.1 and pDiff(ema144, ema233) > 0.1 and pDiff(ema169, ema233) > 0.1
        -> entry long when position_size <= 0
    close < ema144, ema169, ema233 and ema144 <= ema233 -> entry short when position_size > 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, the short entry needs an open long, so from flat only longs open and a short
      ends only by the next long: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426367_vegas_wave"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "upd": [0.05, 0.1, 0.2],
}
DEFAULT_PARAMS = {"upd": 0.1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    c = bars_df["close"]
    e144, e169, e233 = (c.ewm(span=n, adjust=False).mean() for n in (144, 169, 233))
    pdiff = lambda x, y: (x - y) / x * 100
    up = ((pdiff(c, e233) > p["upd"]) & (pdiff(e144, e233) > p["upd"])
          & (pdiff(e169, e233) > p["upd"])).to_numpy()
    dn = ((c < e144) & (c < e169) & (c < e233) & (e144 <= e233)).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        before = pos
        if up[i] and before <= 0:
            pos = 1
        if dn[i] and before > 0:
            pos = -1
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
