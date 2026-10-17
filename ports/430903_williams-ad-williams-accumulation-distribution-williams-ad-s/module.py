"""Williams accumulation / distribution sign (HPotter), 1-hour bars: the running A/D sum (close minus the previous low on up
closes, minus the previous high on down closes, reset to 0 on an unchanged close) above zero holds a long, below zero
holds a short.
Port of FMZ strategy #430903 "威廉姆累积-分配指标Williams-AD策略Williams-Accumulation-Distribution-Williams-AD-Strategy" (Williams AD).

FMZ source id: 430903

Source
    https://www.fmz.com/strategy/430903 (PineScript v2, FMZ last modified 2023-11-02 17:25:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 215-247), no parameters
    xWAD = close > close[1] ? xWAD[1] + close - low[1] : close < close[1] ? xWAD[1] + close - high[1] : 0
    pos = xWAD > 0 ? 1 : xWAD < 0 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: the previous bar's low / high (not the true low / high), and an unchanged close
      resets the sum to 0 (which keeps the previous position). Only the sign is traded. "Trade
      reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the sign of a cumulative price sum.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: ND430903 (2 members, best partner #434609, Jaccard 0.792); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430903_williams_ad_sign"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    wad, pos = np.nan, 0
    for i in range(m):
        prev = 0.0 if np.isnan(wad) else wad          # nz(xWAD[1], 0)
        c1 = c[i - 1] if i else 0.0                    # nz(close[1], 0)
        if c[i] > c1:
            wad = prev + c[i] - (lo[i - 1] if i else np.nan)
        elif c[i] < c1:
            wad = prev + c[i] - h[i - 1]
        else:
            wad = 0.0
        if wad > 0:
            pos = 1
        elif wad < 0:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
