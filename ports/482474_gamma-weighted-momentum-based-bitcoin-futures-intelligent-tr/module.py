"""The close above a 60-bar gamma-weighted (0.75^i) average of closes after two rising closes goes long; below it
after two falling closes goes short, always in, six-hour bars.
Port of FMZ strategy #482474 "基于伽马权重和动量的比特币期货智能交易策略-Gamma-Weighted-Momentum-Based-Bitcoin-Futures-Intelligent-Trading-Strategy" (BTC Future Gamma-Weighted Momentum Model (BGMM)).

FMZ source id: 482474

Source
    https://www.fmz.com/strategy/482474 (PineScript v6, FMZ last modified 2025-02-18 15:45:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 90-131), length 60, gamma 0.75
    GWAP = sum(close[i] x 0.75^i) / sum(0.75^i), i = 0..59, from bar 60 on (na before)
    close > GWAP and close[1] > close[2] > close[3] -> entry long; mirrored -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weights use lags 0-59 of the close (the typical-price line is unused); GWAP is na until bar 60, as written.
    * Every bar in a condition is an entry signal (same-side ignored while held); entries reverse (REVERSAL
      INTENDED), always in. Signal module, no stops. FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a weighted average and close sequences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50000 cash per trade, quoted in original_sizing.txt.
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

NAME = "fmz_482474_gamma_weighted_avg_side_two_bar_momentum"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gamma": [0.75, 0.9],
    "length": [60, 30],
}
DEFAULT_PARAMS = {"length": 60, "gamma": 0.75}


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
    w = p["gamma"] ** np.arange(n, dtype=float)
    v = c.to_numpy(dtype=float)
    g = np.convolve(v, w)[:len(v)] / w.sum()                 # g[t] = sum_i v[t - i] w[i] / sum w
    g[:n] = np.nan                                           # bar_index >= length before the arrays are filled
    gwap = pd.Series(g, index=c.index)
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    long_e = ((c > gwap) & (c1 > c2) & (c2 > c3)).astype(bool)
    short_e = ((c < gwap) & (c1 < c2) & (c2 < c3)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
