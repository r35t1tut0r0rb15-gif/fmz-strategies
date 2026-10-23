"""One-minute bars: the close crossing down through the upper band (linear regression 150 of the close plus 2 standard deviations) goes long, crossing up through the lower band goes short; reversing (the volume-price SuperTrend only feeds plots and alerts).
Port of FMZ strategy #435095 "Volatility Price Channel Moving Average Trading Strategy" (Vol ST VM).

FMZ source id: 435095

Source
    https://www.fmz.com/strategy/435095 (PineScript v4, FMZ last modified 2023-12-12 11:44:15).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 152-279), TP multiplier 2, TP length 150; SuperTrend 1 x 10 on an EMA of a volume-price "shadow" line (plots / alerts only)
    vwap1 = intercept + slope x 150 of the 150-close regression (calcSlope);  z1 = vwap1 + 2 stdev(close, 150), x1 = vwap1 - 2 stdev
    high1 = crossunder(close, z1) -> entry Enter Long MA;  low1 = crossover(close, x1) -> entry Short Entry MA

Interpretation choices (Pine rules in SURVEY_README.md)
    * calcSlope's line at x = len + 1 is the least-squares value at the newest bar, linreg(close, 150, 0).
      The entries are the "TP" markers, inverted as written: falling back through the upper band buys and
      rising back through the lower band sells (weird case). The volume-price shadow line, its EMAs and the
      SuperTrend feed only plots and alerts: volume is not used. stdev is the population form. REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression band re-entries.
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

NAME = "fmz_435095_linreg150_2sd_band_reentry_1m_reversal"
FAMILY = "regression_bands"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len5": [150, 60],
    "multiplier": [2.0, 3.0],
}
DEFAULT_PARAMS = {"len5": 150, "multiplier": 2.0}


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["len5"])
    mid = _linreg(c, n)
    dev = float(p["multiplier"]) * c.rolling(n).std(ddof=0)
    z1, x1 = mid + dev, mid - dev
    high1 = (c < z1) & (c.shift(1) >= z1.shift(1))
    low1 = (c > x1) & (c.shift(1) <= x1.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return high1 & ~low1, false, low1, false.copy()


def portfolio_kwargs(**params):
    return {}
