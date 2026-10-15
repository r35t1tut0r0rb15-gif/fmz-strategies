"""T7 JNSAR: the line is the mean of EMA 5 of high, low and close over the current and four previous
bars (15 terms); a close above it goes long, a close below it goes short (always in the market).
Port of FMZ strategy #427122 "T7-JNSAR Quantitative Trading Strategy".

FMZ source id: 427122

Source
    https://www.fmz.com/strategy/427122 (PineScript v2, FMZ last modified 2023-09-18 14:05:19).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 166-185)
    sum = sum over k = 0..4 of ema(high[k], 5) + ema(low[k], 5) + ema(close[k], 5)
    jnsar = round(sum / 15)
    close > jnsar -> entry long; close < jnsar -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: round() to a whole price unit is an instrument-specific artefact (it erases the
      line on an FX pair near 1.10); the port uses sum / 15 unrounded.
    * ema(high[k], 5) is the EMA of the series high shifted k bars, i.e. ema(high, 5)[k].
    * strategy.entry reverses: REVERSAL INTENDED (no other exit); "Enable Backtest" is on.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the rounding to whole price units is dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427122_t7_jnsar"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [5, 3, 10],
    "lags": [5, 3],
}
DEFAULT_PARAMS = {"ema_length": 5, "lags": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, lags = int(p["ema_length"]), int(p["lags"])
    e = sum(bars_df[k].ewm(span=n, adjust=False).mean() for k in ("high", "low", "close"))
    total = sum(e.shift(j) for j in range(lags))
    jnsar = total / (3 * lags)
    c = bars_df["close"]
    long_c, short_c = (c > jnsar).to_numpy(), (c < jnsar).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i]:
            pos = 1
        elif short_c[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
