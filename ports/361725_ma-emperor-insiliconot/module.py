"""Ehlers-style low-pass filter cross (13 vs 21), stop-and-reverse.
Port of FMZ strategy #361725 "MA-Emperor-insiliconot" (insiliconot's MA Emperor, orders added).

Source
    https://www.fmz.com/strategy/361725 (PineScript v3, FMZ last modified 2022-05-08 00:11:51).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 99-311), type "LowPass", MA 2 = 13, MA 3 = 21
    variant_lowPass(src, len): a = 2/(1+len)
      LP := (a - a*a/4)*src + a*a/2*nz(src[1]) - (a - 0.75*a*a)*nz(src[2])
            + 2*(1-a)*nz(LP[1]) - (1-a)*(1-a)*nz(LP[2])
    crossover(ma2, ma3) -> entry long;  else crossunder(ma2, ma3) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default filter type (LowPass) is ported; the others are input options. ha = false,
      so the source is the plain close.
    * The filter starts from zero (nz) as written; the port emits nothing for the first 100 bars.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361725_lowpass_filter_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_fast": [8, 13, 21],
    "len_slow": [21, 34, 55],
}
DEFAULT_PARAMS = {"len_fast": 13, "len_slow": 21, "warmup": 100}


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


def _lowpass(src, length):
    s = src.to_numpy(dtype=float)
    a = 2.0 / (1.0 + length)
    out = np.zeros(len(s))
    for t in range(len(s)):
        s1 = s[t - 1] if t >= 1 else 0.0
        s2 = s[t - 2] if t >= 2 else 0.0
        l1 = out[t - 1] if t >= 1 else 0.0
        l2 = out[t - 2] if t >= 2 else 0.0
        out[t] = ((a - 0.25 * a * a) * s[t] + 0.5 * a * a * s1 - (a - 0.75 * a * a) * s2
                  + 2.0 * (1.0 - a) * l1 - (1.0 - a) * (1.0 - a) * l2)
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = _lowpass(bars_df["close"], int(p["len_fast"]))
    s = _lowpass(bars_df["close"], int(p["len_slow"]))
    f1, s1 = np.roll(f, 1), np.roll(s, 1)
    warm = np.arange(len(f)) >= int(p["warmup"])
    up = warm & (f > s) & (f1 <= s1)
    dn = warm & (f < s) & (f1 >= s1)
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
