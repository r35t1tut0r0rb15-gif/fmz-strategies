"""Slope-adaptive moving average (MZ SAMA): an adaptive MA whose alpha grows when price sits near
the edge of its 201-bar range; its slope angle turning above +17 degrees goes long, below -17 goes
short (always in).
Port of FMZ strategy #366930 "Slope Adaptive Moving Average (MZ SAMA)".

Source
    https://www.fmz.com/strategy/366930 (PineScript v5, FMZ last modified 2022-05-31 18:24:37).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 82-197), length 200, major 14, minor 6, slope 34 / 25,
flat 17, chart resolution ""
    mult = |2 close - ll - hh| / (hh - ll)   (hh / ll = highest high / lowest low of 201 bars)
    alpha = (mult (2/7 - 2/15) + 2/15)^2;  ama := (close - nz(ama[1])) alpha + nz(ama[1])
    slope_range = 25 / (hh34 - ll34) * ll34;  dt = (ama[2] - ama) / close * slope_range
    angle = round(degrees(acos(1 / sqrt(1 + dt^2)))), negative when dt > 0
    colour bull when angle > 17, bear when angle <= -17; a new bull colour sets sig 1, bear -1
    sig turns 1 -> entry long; sig turns -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Resolution "" is the chart. Before 201 bars exist mult is 0 (an na test is false), and the
      average starts from 0 (nz), as coded.
    * The slope is a ratio of price changes (scale-free).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366930_sama_slope_colour"
FAMILY = "slope_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 200],
    "slope_period": [20, 34],
    "flat": [10, 17, 25],
}
DEFAULT_PARAMS = {"length": 200, "maj_len": 14, "min_len": 6, "slope_period": 34, "slope_range": 25,
                  "flat": 17}


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
    hs, ls, cs = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"]) + 1
    hh, ll = hs.rolling(n).max().to_numpy(), ls.rolling(n).min().to_numpy()
    c = cs.to_numpy(dtype=float)
    with np.errstate(all="ignore"):
        mult = np.where((hh - ll) != 0, np.abs(2 * c - ll - hh) / (hh - ll), 0.0)
    mult = np.where(np.isnan(hh - ll), 0.0, mult)
    a_min, a_maj = 2 / (p["min_len"] + 1), 2 / (p["maj_len"] + 1)
    alpha = (mult * (a_min - a_maj) + a_maj) ** 2
    ama = np.zeros(len(c))
    for i in range(len(c)):
        prev = ama[i - 1] if i else 0.0
        ama[i] = (c[i] - prev) * alpha[i] + prev
    k = int(p["slope_period"])
    hk, lk = hs.rolling(k).max().to_numpy(), ls.rolling(k).min().to_numpy()
    rng = p["slope_range"] / (hk - lk) * lk
    ama2 = np.concatenate([[np.nan] * 2, ama[:-2]])
    dt = (ama2 - ama) / c * rng
    with np.errstate(all="ignore"):
        x_angle = np.round(180 * np.arccos(1 / np.sqrt(1 + dt * dt)) / np.pi)
    angle = np.where(dt > 0, -x_angle, x_angle)
    bull, bear = angle > p["flat"], angle <= -p["flat"]
    lag = lambda a: np.concatenate([[False], a[:-1]])
    buy, sell = bull & ~lag(bull), bear & ~lag(bear)
    m = len(c)
    sig = np.zeros(m)
    s = 0
    for i in range(m):
        if buy[i] and s <= 0:
            s = 1
        if sell[i] and s >= 0:
            s = -1
        sig[i] = s
    prev = np.concatenate([[0.0], sig[:-1]])
    return _always_in((sig == 1) & (prev != 1), (sig == -1) & (prev != -1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
