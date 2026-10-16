"""HPotter relative volatility index, 4-hour bars: the 10-bar standard deviation is split into up-bar and
down-bar parts and smoothed (13/14 decay); the up share above 70 % holds a long, below 30 % a short,
in between the last side is kept.
Port of FMZ strategy #427893 "Relative Volatility Index Backtesting Strategy".

FMZ source id: 427893

Source
    https://www.fmz.com/strategy/427893 (PineScript v2, FMZ last modified 2023-09-26 16:15:44).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 195-235), period 10, zones 30 / 70
    sd = stdev(close, 10); u = close > close[1] ? sd : 0; d = close > close[1] ? 0 : sd
    nU = (13 nz(nU[1]) + u) / 14; nD likewise; rvi = 100 nU / (nU + nD)
    rvi < 30 -> -1; rvi > 70 -> 1; else hold -> entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev is the population deviation (Pine). The first bar's na restarts from 0 (nz).
    * "Trade reverse" (default false) fixed off. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427893 (2 members, best partner #436644, Jaccard 0.757); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427893_hpotter_relative_volatility_index"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 5, 20, 30],
}
DEFAULT_PARAMS = {"period": 10, "buy_zone": 30, "sell_zone": 70}


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
    sd = c.rolling(int(p["period"])).std(ddof=0).to_numpy()
    upbar = (c > c.shift(1)).to_numpy()
    m = len(sd)
    tgt = np.zeros(m, dtype=np.int8)
    nu = nd = np.nan
    pos = 0
    for i in range(m):
        u = sd[i] if upbar[i] else 0.0
        d = 0.0 if upbar[i] else sd[i]
        nu = (13 * (0.0 if np.isnan(nu) else nu) + u) / 14
        nd = (13 * (0.0 if np.isnan(nd) else nd) + d) / 14
        with np.errstate(invalid="ignore", divide="ignore"):
            r = 100 * nu / (nu + nd)
        if r < p["buy_zone"]:
            pos = -1
        elif r > p["sell_zone"]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
