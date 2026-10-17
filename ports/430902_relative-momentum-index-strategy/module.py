"""Altman's relative momentum index (HPotter), 2-hour bars: the RMI (an RSI of 20-bar momentum, smoothed as written) under
40 holds a long, over 70 holds a short.
Port of FMZ strategy #430902 "Relative Momentum Index Strategy" (Relative Momentum Index).

FMZ source id: 430902

Source
    https://www.fmz.com/strategy/430902 (PineScript v2, FMZ last modified 2023-11-02 17:21:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 140-181), length 20, BuyZone 40, SellZone 70
    xMom = close - close[20]
    xMU = xMom >= 0 ? nz(xMU[1], 1) - nz(xMU[1], 1) / 20 + xMom : nz(xMU[1], 1)
    xMD = xMom <= 0 ? nz(xMD[1], 1) - nz(xMD[1], 1) / 20 + |xMom| : nz(xMD[1], 0)
    RMI = 100 xMU / xMD / (1 + xMU / xMD);  RMI < 40 -> 1;  RMI > 70 -> -1;  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recursions are ported as written, including the nz seeds (1 and 0) and the up / down sums
      that are not decayed on bars of the other sign. A zero xMD gives na (no change of state).
      "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a momentum oscillator's levels.
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

NAME = "fmz_430902_relative_momentum_index"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10],
    "buy_zone": [40, 30],
}
DEFAULT_PARAMS = {"length": 20, "buy_zone": 40, "sell_zone": 70}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    mom = (c - c.shift(n)).to_numpy(dtype=float)
    m = len(mom)
    tgt = np.zeros(m, dtype=np.int8)
    mu, md, pos = np.nan, np.nan, 0
    for i in range(m):
        pmu = 1.0 if np.isnan(mu) else mu
        mu = pmu - pmu / n + mom[i] if mom[i] >= 0 else pmu
        if mom[i] <= 0:
            pmd = 1.0 if np.isnan(md) else md
            md = pmd - pmd / n + abs(mom[i])
        else:
            md = 0.0 if np.isnan(md) else md
        if md != 0:
            rm = mu / md
            res = 100 * rm / (1 + rm)
            if res < p["buy_zone"]:
                pos = 1
            elif res > p["sell_zone"]:
                pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
