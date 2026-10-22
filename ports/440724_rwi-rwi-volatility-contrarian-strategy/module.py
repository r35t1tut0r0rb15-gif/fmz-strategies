"""Random Walk Index direction, 1-hour bars: when either RWI (14) is at or above 1 (not a random walk), the RWI high above the RWI low goes long, the RWI low above the RWI high goes short; reversing.
Port of FMZ strategy #440724 "RWI波动率反转策略RWI-Volatility-Contrarian-Strategy" (RWI Strategy).

FMZ source id: 440724

Source
    https://www.fmz.com/strategy/440724 (PineScript v4, FMZ last modified 2024-02-01 14:56:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-163), length 14; threshold 1.0
    rwi_high = (high - low[14]) / (atr(14) x sqrt(14));  rwi_low = (high[14] - low) / (atr(14) x sqrt(14));  is_rw = both < 1
    long = not is_rw and rwi_high > rwi_low -> entry Long;  short = not is_rw and rwi_low > rwi_high -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The look-back values use nz() (0 before the 14th bar), as written; the ATR is undefined there, so
      no early signal comes. The conditions are levels; an entry while already in that direction does
      nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Random Walk Index.
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

NAME = "fmz_440724_random_walk_index_direction"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 30],
    "threshold": [1.0, 1.5],
}
DEFAULT_PARAMS = {"length": 14, "threshold": 1.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    den = _rma(tr, n) * np.sqrt(n)
    rh = (h - lo.shift(n).fillna(0.0)) / den
    rl = (h.shift(n).fillna(0.0) - lo) / den
    th = float(p["threshold"])
    trend = ~((rh < th) & (rl < th)) & rh.notna() & rl.notna()
    long_ = trend & (rh > rl)
    short_ = trend & (rl > rh)
    false = pd.Series(False, index=c.index)
    return long_, false, short_, false.copy()


def portfolio_kwargs(**params):
    return {}
