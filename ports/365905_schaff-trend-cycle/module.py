"""Schaff Trend Cycle: STC (MACD 23 / 50 through two 10-bar stochastic stages) crossing above 25
goes long; crossing below 75 goes short (always in).
Port of FMZ strategy #365905 "Schaff Trend Cycle".

Source
    https://www.fmz.com/strategy/365905 (PineScript v4, FMZ last modified 2022-05-26 17:20:52).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 51-107), MACD 23 / 50, cycle 10, %D 3 / 3, bands 75 / 25
    macd = ema(close, 23) - ema(close, 50)
    k = nz(fixnan(stoch(macd, macd, macd, 10)));  d = ema(k, 3)
    kd = nz(fixnan(stoch(d, d, d, 10)));  stc = clamp(ema(kd, 3), 0, 100)
    crossover(stc, 25) -> entry long; else crossunder(stc, 75) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A flat window (zero range) gives na in stoch(), carried forward by fixnan, else 0 (nz).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365905_schaff_trend_cycle"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 23],
    "slow": [26, 50],
    "cycle": [10, 20],
}
DEFAULT_PARAMS = {"fast": 23, "slow": 50, "cycle": 10, "d1": 3, "d2": 3, "upper": 75, "lower": 25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


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


def _stoch_self(x, n):
    lo, hi = x.rolling(n).min(), x.rolling(n).max()
    with np.errstate(all="ignore"):
        v = (100 * (x - lo) / (hi - lo)).replace([np.inf, -np.inf], np.nan).to_numpy()
    return pd.Series(np.nan_to_num(_fixnan(v), nan=0.0), index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["cycle"])
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    d = _stoch_self(macd, n).ewm(span=int(p["d1"]), adjust=False).mean()
    stc = _stoch_self(d, n).ewm(span=int(p["d2"]), adjust=False).mean().clip(0, 100)
    up = ((stc > p["lower"]) & (stc.shift(1) <= p["lower"])).to_numpy()
    dn = ((stc < p["upper"]) & (stc.shift(1) >= p["upper"])).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
