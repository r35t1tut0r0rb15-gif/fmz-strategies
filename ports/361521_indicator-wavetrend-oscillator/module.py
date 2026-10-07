"""WaveTrend extremes: short while WT1 is above the overbought level, long while below the
oversold level (always in after the first extreme).
Port of FMZ strategy #361521 "Indicator-WaveTrend-Oscillator" (LazyBear WT_LB).

Source
    https://www.fmz.com/strategy/361521 (PineScript, FMZ last modified 2022-05-08 11:16:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 52-80), n1 10, n2 21, obLevel1 60, osLevel1 -60
    ap = hlc3; esa = ema(ap,n1); d = ema(abs(ap-esa),n1); ci = (ap-esa)/(0.015*d)
    wt1 = ema(ci,n2)
    wt1 > obLevel1 -> entry short;  else wt1 < osLevel1 -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses an opposite position: REVERSAL INTENDED (portfolio_kwargs {};
      the engine's default opposite-entry reversal applies). Repeated same-side entries while in
      a position are ignored (pyramiding 0).
    * The oversold level is the negative of the overbought level (defaults 60 / -60; the backtest
      header sets 40 for obLevel1 only). Level 2 lines are plots only.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361521_wavetrend_extremes_reverse"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n1": [7, 10, 14],
    "ob_level": [40, 53, 60],
}
DEFAULT_PARAMS = {"n1": 10, "n2": 21, "ob_level": 60}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n1, n2 = int(p["n1"]), int(p["n2"])
    ap = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = ((ap - esa) / (0.015 * d)).replace([np.inf, -np.inf], np.nan)
    wt1 = ci.ewm(span=n2, adjust=False, ignore_na=True).mean().to_numpy()
    warm = np.arange(len(ap)) >= n1 + n2

    m = len(ap)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if not warm[i]:
            continue
        if wt1[i] > p["ob_level"]:
            if pos != -1:
                se[i], pos = True, -1
        elif wt1[i] < -p["ob_level"] and pos != 1:
            le[i], pos = True, 1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
