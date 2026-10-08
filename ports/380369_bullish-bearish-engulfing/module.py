"""Bullish / bearish engulfing (Zer3192): a candle whose body is at least 3 times the opposite-colour
previous body, closing beyond that body's open and large enough, goes long (or short).
Port of FMZ strategy #380369 "Bullish & Bearish Engulfing".

Source
    https://www.fmz.com/strategy/380369 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-28 13:17:09). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 28-70), scale 3, minimum size 30 pips (= 3.0 price units)
    bull = red[1] and green and close >= open[1] and body >= 3 body[1] and body >= 30 / 10
    bear mirrors;  bull -> entry long; else bear -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the minimum body 30 / 10 = 3.0 is in price units. It becomes min_atr x ATR(14)
      (on BTC 3.0 is about 0 ATR).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_380369_engulfing_scaled"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "scale": [1.5, 2.0, 3.0],
    "min_atr": [0.0, 0.25, 0.5],
}
DEFAULT_PARAMS = {"scale": 3.0, "min_atr": 0.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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
    o, c = bars_df["open"], bars_df["close"]
    o1, c1 = o.shift(1), c.shift(1)
    min_body = p["min_atr"] * _atr_pine(bars_df, ATR_LEN)
    bull = (o1 > c1) & (o < c) & (c >= o1) & ((c - o) >= (o1 - c1) * p["scale"]) & ((c - o) >= min_body)
    bear = (o1 < c1) & (o > c) & (c <= o1) & ((o - c) >= (c1 - o1) * p["scale"]) & ((o - c) >= min_body)
    return _always_in(bull.to_numpy(), bear.to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
