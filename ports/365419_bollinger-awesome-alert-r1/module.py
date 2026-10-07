"""Bollinger Awesome: EMA 3 crossing above the Bollinger basis (SMA 20) with a rising Awesome
Oscillator goes long; crossing below with a falling AO goes short (always in).
Port of FMZ strategy #365419 "Bollinger Awesome Alert R1.1 by JustUncleL".

Source
    https://www.fmz.com/strategy/365419 (PineScript v4, FMZ last modified 2022-05-24 18:31:33).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 138-243), basis SMA 20 of close, fast EMA 3, AO 5 / 34
    AO = sma(hl2, 5) - sma(hl2, 34);  |state| == 1 when AO rises, 2 when it falls
    break_up   = crossover(ema3, basis) and close > basis and AO rising -> entry long
    break_down = crossunder(ema3, basis) and close < basis and AO falling -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Bollinger and squeeze filters default to off; the bands only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365419_bb_basis_cross_ao"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 34],
    "fast_ma": [3, 5],
}
DEFAULT_PARAMS = {"bb_length": 20, "fast_ma": 3, "ao_fast": 5, "ao_slow": 34}


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
    c = bars_df["close"]
    basis = c.rolling(int(p["bb_length"])).mean()
    fast = c.ewm(span=int(p["fast_ma"]), adjust=False).mean()
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    ao = hl2.rolling(int(p["ao_fast"])).mean() - hl2.rolling(int(p["ao_slow"])).mean()
    rising = (ao > ao.shift(1)).to_numpy()
    defined = (ao.notna() & ao.shift(1).notna()).to_numpy()
    up = ((fast > basis) & (fast.shift(1) <= basis.shift(1)) & (c > basis)).to_numpy() & rising
    dn = ((fast < basis) & (fast.shift(1) >= basis.shift(1)) & (c < basis)).to_numpy() & ~rising & defined
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
