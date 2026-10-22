"""Recursive band touches, 1-hour bars: with the lower recursive band (260, classic) rising for 3 bars, a low at or under it goes long; with the upper band falling for 3 bars, a high at or over it goes
short; reversing.
Port of FMZ strategy #440558 "Recursive Momentum Trading Strategy" (Extended Recursive Bands Strategy).

FMZ source id: 440558

Source
    https://www.fmz.com/strategy/440558 (PineScript v5, FMZ last modified 2024-01-31 16:56:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-214), length 260; source close; method Classic; bands hold direction on; look-back 3
    a := max(nz(a[1], close), close) - sc x |close - nz(a[1], close)|;  b := min(nz(b[1], close), close) + sc x |close - nz(b[1], close)|;  sc = 2 / 261
    long when b >= low and b rose on each of the last 3 bars -> entry Long;  short when high >= a and a fell on each of the last 3 bars -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the Classic method the band step is the plain distance to the close. The take-profit at the
      middle line is commented out. strategy.entry reverses: REVERSAL INTENDED. The percent-of-equity
      size, capital and commission are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, recursive bands of past closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity, capital and commission settings.
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

NAME = "fmz_440558_recursive_band_touch_reversal"
FAMILY = "channel_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [260, 100],
    "lookback": [3, 5],
}
DEFAULT_PARAMS = {"length": 260, "lookback": 3}


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


def _bands(c, n):
    cv = c.to_numpy(dtype=float)
    sc = 2 / (n + 1)
    a, b = np.full(len(cv), np.nan), np.full(len(cv), np.nan)
    pa = pb = np.nan
    for i in range(len(cv)):
        x = cv[i]
        ra = x if np.isnan(pa) else pa
        rb = x if np.isnan(pb) else pb
        a[i] = max(ra, x) - sc * abs(x - ra)
        b[i] = min(rb, x) + sc * abs(x - rb)
        pa, pb = a[i], b[i]
    return pd.Series(a, index=c.index), pd.Series(b, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a, b = _bands(c, int(p["length"]))
    k = int(p["lookback"])
    up_b = pd.Series(True, index=c.index)
    dn_a = pd.Series(True, index=c.index)
    for i in range(k):
        up_b &= b.shift(i) > b.shift(i + 1)
        dn_a &= a.shift(i) < a.shift(i + 1)
    lg = (b >= lo) & up_b
    sh = (h >= a) & dn_a
    false = pd.Series(False, index=c.index)
    return lg & ~sh, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
