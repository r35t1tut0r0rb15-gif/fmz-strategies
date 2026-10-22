"""A gamma-weighted average of the last 60 closes (weights 0.75^i) with two rising or falling closes, 6-hour bars: a close over the average after two higher closes goes long, a close under it after two lower closes goes short; reversing.
Port of FMZ strategy #482474 "Gamma Weighted Momentum Based Bitcoin Futures Intelligent Trading Strategy" (BTC Future Gamma-Weighted Momentum Model (BGMM)).

FMZ source id: 482474

Source
    https://www.fmz.com/strategy/482474 (PineScript v6, FMZ last modified 2025-02-18 15:45:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-131), length 60; gamma 0.75; cash size 50000; slippage 1, commission 0.01
    from bar_index 60: GWAP = sum(close[i] x 0.75^i) / sum(0.75^i), i = 0 .. 59
    close > GWAP and close[1] > close[2] > close[3] -> entry Long;  close < GWAP and close[1] < close[2] < close[3] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The arrays are filled only from bar index 60, so the average is na before it, as written. The typical
      price is computed but unused. Entries only; each reverses the other side. REVERSAL INTENDED. The cash
      size is sizing; slippage and commission are costs and are not ported (house cost model). FREQ = "6h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, weighted-average side with a close momentum filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash 50000 stored, not ported; slippage and commission not ported.
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

NAME = "fmz_482474_gamma075_weighted_avg60_close_side_3bar_momentum_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [60, 30],
    "gamma_factor": [0.75, 0.9],
}
DEFAULT_PARAMS = {"length": 60, "gamma_factor": 0.75}


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
    w = float(p["gamma_factor"]) ** np.arange(n, dtype=float)
    v = c.to_numpy(dtype=float)
    m = len(v)
    g = np.full(m, np.nan)
    if m > n:
        g[n:] = (np.convolve(v, w)[:m] / w.sum())[n:]            # filled from bar index n
    gw = pd.Series(g, index=c.index)
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    le = (c > gw) & (c1 > c2) & (c2 > c3)
    se = (c < gw) & (c1 < c2) & (c2 < c3)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
