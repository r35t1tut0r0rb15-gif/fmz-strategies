"""Smoothed 200-bar range centre with ATR bands, 1-hour bars, long only: the 3-bar SMA of the close crossing over the centre plus 1.5 ATR 10 goes long; crossing under the centre minus 1.5 ATR closes it.
Port of FMZ strategy #436878 "Highest Lowest Center Lookback Strategy" (Highest/Lowest Center Lookback Strategy).

FMZ source id: 436878

Source
    https://www.fmz.com/strategy/436878 (PineScript v4, FMZ last modified 2023-12-28 15:42:10).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 161-180), lookback 200, smoother 5, ATR 10 x 1.5
    l = ema(lowest(low, 200), 5), h = ema(highest(high, 200), 5);  center = (h + l) / 2;  upper / lower = center +- 1.5 atr(10);  price = sma(close, 3)
    crossover(price, upper) -> entry Buy;  crossunder(price, lower) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMAs start at the first full 200-bar extreme (Pine's ema of a series that begins na). Long only.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range centre with ATR bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436878_range_center_atr_band_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [200, 100],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"lookback": 200, "atr_mult": 1.5, "smoother": 5, "atr_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, s = int(p["lookback"]), int(p["smoother"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    vola = _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    price = c.rolling(3).mean()
    lw = lo.rolling(n).min().ewm(span=s, adjust=False).mean()
    hg = h.rolling(n).max().ewm(span=s, adjust=False).mean()
    center = (hg + lw) * 0.5
    upper, lower = center + vola, center - vola
    up = (price > upper) & (price.shift(1) <= upper.shift(1))
    dn = (price < lower) & (price.shift(1) >= lower.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
