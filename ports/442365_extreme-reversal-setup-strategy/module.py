"""Outsized-candle reversals, 1-minute bars: after a large red candle (body at least 75 % of a range twice the 20-bar average, body above the average) a green candle goes long; after the mirrored large
green candle a red candle goes short; reversing.
Port of FMZ strategy #442365 "Extreme Reversal Setup Strategy" (Extreme Reversal Setup).

FMZ source id: 442365

Source
    https://www.fmz.com/strategy/442365 (PineScript v4, FMZ last modified 2024-02-21 14:08:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-167), body share 0.75; lookback 20 (RMA averages); range multiplier 2
    long = open[1] - close[1] >= 0.75 (high[1] - low[1]) and high[1] - low[1] > 2 rma(range, 20) and open[1] - close[1] > rma(body, 20) and close > open -> entry LONG;  short mirrored -> entry SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages are RMAs over 20 bars, as written. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, outsized-candle reversal.
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

NAME = "fmz_442365_outsized_candle_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars_back": [20, 50],
    "body_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"bars_back": 20, "body_mult": 2.0, "body_size": 0.75}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bars_back"])
    ab = _rma((c - o).abs(), n)
    ac = _rma(h - lo, n)
    bs, bm = float(p["body_size"]), float(p["body_mult"])
    o1, c1, r1 = o.shift(1), c.shift(1), (h - lo).shift(1)
    le = (o1 - c1 >= bs * r1) & (r1 > ac * bm) & (o1 - c1 > ab) & (c > o)
    se = (c1 - o1 >= bs * r1) & (r1 > ac * bm) & (c1 - o1 > ab) & (o > c)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
