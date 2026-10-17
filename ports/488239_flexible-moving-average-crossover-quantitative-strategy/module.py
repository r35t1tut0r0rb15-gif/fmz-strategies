"""SMA 20 / SMA 200 crosses, 2-minute bars: the fast SMA 20 crossing above the SMA 200 goes long; crossing below the slow
MA (SMA 200 by default) goes short; in the long-only variant the cross down closes the long instead.
Port of FMZ strategy #488239 "灵活双均线交叉量化策略-Flexible-Moving-Average-Crossover-Quantitative-Strategy" (MA crossover strategy).

FMZ source id: 488239

Source
    https://www.fmz.com/strategy/488239 (PineScript v6, FMZ last modified 2025-03-26 11:01:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 188-226), fast SMA 20, slow SMA 200, direction LongShort
    crossover(fastMA, ta.sma(close, 200)) -> entry long (or, in Short-only mode, close the short)
    crossunder(fastMA, slowMA) -> entry short (or, in Long-only mode, close the long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long test uses ta.sma(close, 200), not the slow-MA input, as written (the same line by default).
    * The direction input is a GRID variant (LongShort, the default, and Long); MA types stay SMA (the VWMA option
      uses volume, check 8).
    * Closes act on the position held at the bar's start (#430850). Entries reverse in LongShort (REVERSAL INTENDED).
    * FREQ = "2min" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_488239_sma20_200_cross_direction"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "direction": ["LongShort", "Long"],
    "fast": [20, 50],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 200, "long_ref": 200, "direction": "LongShort"}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = c.rolling(int(p["long_ref"])).mean()
    up = ((f > r) & (f.shift(1) <= r.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    longs = p["direction"] in ("LongShort", "Long")
    shorts = p["direction"] in ("LongShort", "Short")
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if up[i]:
            if longs:
                pos = 1
            elif start == -1 and pos == -1:
                pos = 0
        if dn[i]:
            if shorts:
                pos = -1
            elif start == 1 and pos == 1:
                pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
