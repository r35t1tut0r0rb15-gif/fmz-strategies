"""Two-hour bars, long only: the VWMA 66 of the close moving above the VWMA 66 of the open goes long, moving back below closes it.
Port of FMZ strategy #440372 "Trend Tracking Moving Average Crossover Strategy" (Close v Open Moving Averages Strategy (divonn1994)).

FMZ source id: 440372

Source
    https://www.fmz.com/strategy/440372 (PineScript v5, FMZ last modified 2024-01-29 16:52:46).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 132-196), MA length 66; MA type VWMA
    maMomentum = vwma(close, 66) > vwma(open, 66) ? 1 : -1
    crossover(maMomentum, 0) -> entry long;  crossunder(maMomentum, 0) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * vwma(x, n) = sma(x x volume, n) / sma(volume, n); before both exist the state is -1. The date
      inputs feed nothing (inDateRange is true). 100 % of equity and the commission are sizing and costs.
      Long only. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-weighted close average against the open average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 100, commission 0.1 %, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of both VWMA 66; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440372_vwma66_close_vs_open_2h_long_only"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars": [66, 35],
}
DEFAULT_PARAMS = {"bars": 66}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    n = int(p["bars"])
    sv = v.rolling(n).mean()
    vc = (c * v).rolling(n).mean() / sv.where(sv != 0)
    vo = (o * v).rolling(n).mean() / sv.where(sv != 0)
    mom = pd.Series(np.where(vc > vo, 1, -1), index=c.index)
    up = (mom > 0) & (mom.shift(1) <= 0)
    dn = (mom < 0) & (mom.shift(1) >= 0)
    upv, dnv = up.to_numpy(), dn.to_numpy()
    m = len(upv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and dnv[i]:
            lx[i], pos = True, 0
        elif pos == 0 and upv[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
