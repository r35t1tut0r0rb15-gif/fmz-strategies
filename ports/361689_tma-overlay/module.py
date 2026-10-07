"""Three-line strike traded as written: three down candles then a close above the prior open
goes SHORT; three up candles then a close below the prior open goes LONG (always in).
Port of FMZ strategy #361689 "TMA-Overlay" (TMA Overlay indicator, orders added).

Source
    https://www.fmz.com/strategy/361689 (PineScript v4, FMZ last modified 2022-05-07 21:08:06).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 93-104)
    bearSig = close[3] > open[3] and close[2] > open[2] and close[1] > open[1] and close < open[1]
    bullSig = close[3] < open[3] and close[2] < open[2] and close[1] < open[1] and close > open[1]
    bullSig -> entry short;  else bearSig -> entry long
    (the four smoothed MAs and EMA(2) are plotted only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The indicator labels bullSig "3s-Bull"; the added orders go short on it. Ported as written
      (flagged in PORT_NOTES).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}; the engine's default
      opposite-entry reversal applies).
    * The source has no tunable inputs for the orders; the declared variants change the number
      of prior same-colour candles (3 in the source).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361689_three_line_strike_faded"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_bars": [2, 3, 4],
}
DEFAULT_PARAMS = {"n_bars": 3}


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
    k = int(p["n_bars"])
    o, c = bars_df["open"], bars_df["close"]
    ups = pd.Series(True, index=o.index)
    downs = pd.Series(True, index=o.index)
    for j in range(1, k + 1):
        ups &= (c.shift(j) > o.shift(j)).fillna(False)
        downs &= (c.shift(j) < o.shift(j)).fillna(False)
    bear = (ups & (c < o.shift(1))).to_numpy()
    bull = (downs & (c > o.shift(1))).to_numpy()

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if bull[i]:
            if pos != -1:
                se[i], pos = True, -1
        elif bear[i] and pos != 1:
            le[i], pos = True, 1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
