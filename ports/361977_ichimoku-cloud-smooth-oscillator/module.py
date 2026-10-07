"""Ichimoku-style cloud built from T3 averages: long while the T3 conversion line is above the
(displaced) cloud by more than half its height, short while below (always in).
Port of FMZ strategy #361977 "Ichimoku-Cloud-Smooth-Oscillator".

Source
    https://www.fmz.com/strategy/361977 (PineScript, FMZ last modified 2022-05-09 12:22:38).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 45-95), 9 / 26 / 52, displacement 26, T3 b = 0.7
    conv = t3(close,9); base = t3(close,26)
    lead1 = avg(conv, base)[26]; lead2 = t3(close,52)[26]; middle = avg(lead1, lead2)
    dist = conv - middle; h = |lead1 - lead2|
    ccd = dist - h/2 if |dist| > h/2 else 0
    ccd > 0 -> entry long;  else ccd < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud is read 26 bars back ([26]): past values only.
    * For a negative distance the source also subtracts h/2 (dist - h/2), as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361977_t3_cloud_oscillator_side"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [7, 9, 12],
    "base": [20, 26, 34],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "span2": 52, "displacement": 26, "b": 0.7}


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


def _t3(x, n, b):
    e = [x]
    for _ in range(6):
        e.append(e[-1].ewm(span=n, adjust=False).mean())
    c1 = -b ** 3
    c2 = 3 * b * b + 3 * b ** 3
    c3 = -6 * b * b - 3 * b - 3 * b ** 3
    c4 = 1 + 3 * b + b ** 3 + 3 * b * b
    return c1 * e[6] + c2 * e[5] + c3 * e[4] + c4 * e[3]


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = int(p["displacement"])
    conv = _t3(c, int(p["conversion"]), p["b"])
    base = _t3(c, int(p["base"]), p["b"])
    lead1 = ((conv + base) / 2).shift(d)
    lead2 = _t3(c, int(p["span2"]), p["b"]).shift(d)
    dist = (conv - (lead1 + lead2) / 2).to_numpy()
    half = ((lead1 - lead2).abs() / 2).to_numpy()
    ccd = np.where(np.abs(dist) > half, dist - half, 0.0)
    warm = np.arange(len(c)) >= int(p["span2"]) + d
    return _always_in(warm & (ccd > 0), warm & (ccd < 0), bars_df.index)


def portfolio_kwargs(**params):
    return {}
