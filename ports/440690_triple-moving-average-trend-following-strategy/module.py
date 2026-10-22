"""Triple SMA trend crossings, 3-hour bars: the SMA 8 crossing over the SMA 21 with both above the SMA 55 goes long, the mirror short; the opposite crossing of the 8 / 21 pair closes (a short signal
against a held long only flattens it).
Port of FMZ strategy #440690 "Triple Moving Average Trend Following Strategy" (Triple Moving Average).

FMZ source id: 440690

Source
    https://www.fmz.com/strategy/440690 (PineScript v4, FMZ last modified 2024-02-01 11:02:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-234), SMA 8 / 21 / 55; qty 1 (position sizing input computed but unused); dates from 2016
    enterLong = crossover(sma8, sma21) and sma8 > sma55 and sma21 > sma55 -> entry EL;  enterShort = crossunder(..) and both below -> entry ES
    close_all when crossunder(sma8, sma21) and position > 0;  close_all when crossover and position < 0;  close_all when not window() (window is true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * An opposite entry always comes with the close of the held side, and close_all after an entry
      leaves the bar flat (as #430380), so every trade starts from flat. Opposite entries cannot occur
      (entries only from flat). The quantity 1, capital, per-order commission and slippage are sizing
      and costs. FREQ = "3h" from the backtest header (bars on UTC multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a slow filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1, capital, commission and slippage settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440690_triple_sma_cross_flat_first"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 5],
    "slow": [55, 100],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 55, "medium": 21}


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
    f, md, s = (c.rolling(int(p[k])).mean() for k in ("fast", "medium", "slow"))
    xo = ((f > md) & (f.shift(1) <= md.shift(1))).to_numpy()
    xu = ((f < md) & (f.shift(1) >= md.shift(1))).to_numpy()
    L = xo & ((f > s) & (md > s)).to_numpy()
    S = xu & ((f < s) & (md < s)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        if (xu[i] and pos > 0) or (xo[i] and pos < 0):
            new = 0                                      # close_all also cancels a same-bar entry
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt != 1), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt != -1), index=ix))


def portfolio_kwargs(**params):
    return {}
