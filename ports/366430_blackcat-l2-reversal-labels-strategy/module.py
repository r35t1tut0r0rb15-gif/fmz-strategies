"""blackcat L2 reversal labels: a MACD line crossing above its signal at a lower close but a higher
MACD than at the previous such cross (bullish divergence) goes long; the bearish mirror at a
crossunder goes short (always in).
Port of FMZ strategy #366430 "[blackcat] L2 Reversal Labels Strategy".

Source
    https://www.fmz.com/strategy/366430 (PineScript v5, author Zer3192 on FMZ, FMZ last modified
    2022-05-29 11:35:50). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 34-59), MACD 12 / 26 / 9
    a1 = barssince(crossover(diff, dea)[1]);  close[a1 + 1] / diff[a1 + 1] = values at the previous
    crossover bar
    bottom = close[a1+1] > close and diff > diff[a1+1] and crossover(diff, dea) -> entry long
    top    = close[a2+1] < close and diff[a2+1] > diff and crossunder(diff, dea) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince of the cross shifted one bar points at the previous cross (not the current one).
    * The labels and alerts only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366430_macd_cross_divergence"
FAMILY = "macd_divergence"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [21, 26],
    "signal": [9, 12],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cs = bars_df["close"]
    diff = cs.ewm(span=int(p["fast"]), adjust=False).mean() - cs.ewm(span=int(p["slow"]), adjust=False).mean()
    dea = diff.ewm(span=int(p["signal"]), adjust=False).mean()
    x_up = ((diff > dea) & (diff.shift(1) <= dea.shift(1))).to_numpy()
    x_dn = ((diff < dea) & (diff.shift(1) >= dea.shift(1))).to_numpy()
    c, dv = cs.to_numpy(dtype=float), diff.to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    k_up = k_dn = -1  # previous crossover / crossunder bar
    for i in range(m):
        if x_up[i] and k_up >= 0:
            le[i] = c[k_up] > c[i] and dv[i] > dv[k_up]
        if x_dn[i] and k_dn >= 0:
            se[i] = c[k_dn] < c[i] and dv[k_dn] > dv[i]
        if x_up[i]:
            k_up = i
        if x_dn[i]:
            k_dn = i
    return _always_in(le, se, bars_df.index)


def portfolio_kwargs(**params):
    return {}
