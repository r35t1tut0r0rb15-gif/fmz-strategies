"""Engulfing candles, stop-and-reverse: bullish engulfing goes long, bearish engulfing short.
Port of FMZ strategy #361783 "Engulfing-Candles".

Source
    https://www.fmz.com/strategy/361783 (PineScript v3, FMZ last modified 2022-05-08 10:57:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 38-66)
    bullish = open <= close[1] and open < open[1] and close > open[1]
    bearish = open >= close[1] and open > open[1] and close < open[1]
    bullish -> entry long;  else bearish -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The commented-out block (fixed qty, profit = 1000 / loss = 50 ticks, date window) is not
      active; only the two strategy.entry lines at the end trade.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * The source has no inputs. Declared variants add a minimum body size in ATR(14):
      min_body_atr = 0 is the source exactly.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361783_engulfing_reverse"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "min_body_atr": [0.0, 0.25, 0.5],
}
DEFAULT_PARAMS = {"min_body_atr": 0.0, "atr_length": 14}


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
    big = ((c - o).abs() >= p["min_body_atr"] * _atr_pine(bars_df, int(p["atr_length"])).fillna(0)).to_numpy()
    bull = ((o <= c.shift(1)) & (o < o.shift(1)) & (c > o.shift(1))).to_numpy() & big
    bear = ((o >= c.shift(1)) & (o > o.shift(1)) & (c < o.shift(1))).to_numpy() & big
    return _always_in(bull, bear, bars_df.index)


def portfolio_kwargs(**params):
    return {}
