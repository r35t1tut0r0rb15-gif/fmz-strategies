"""Chaloke ATR-shifted EMA lines, 1-hour bars: three EMAs (9 / 15 / 24) less one ATR(5), each taken from the previous close unless the close is a 3-bar high; the short line crossing over the middle line with
the close above it goes long, the short line crossing under the long line or the close under the long line goes short; reversing.
Port of FMZ strategy #440320 "Moving Average Trend Tracking Strategy" (Chaloke System Strategy).

FMZ source id: 440320

Source
    https://www.fmz.com/strategy/440320 (PineScript v4, FMZ last modified 2024-01-29 11:46:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-141), periods 9 / 15 / 24; investment term (ATR length) 5; ATR period 5 (multiplier 2 x 5 / 10 = 1)
    ATRX = (2 x 5 / 10) x atr(5);  Sht = close == highest(close, 3) ? ema(close, 9) - ATRX : ema(close[1], 9) - ATRX  (Mid 15, Lng 24 alike)
    long = crossover(Sht, Mid) and close > Sht -> entry Long;  short = crossunder(Sht, Lng) or close < Lng -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry is written after the long one and wins on a bar with both (as #437773).
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR-shifted EMA lines.
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

NAME = "fmz_440320_chaloke_atr_shifted_ema_lines"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p1": [9, 5],
    "p3": [24, 50],
}
DEFAULT_PARAMS = {"p1": 9, "p2": 15, "p3": 24, "p4": 5, "p5": 5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    atrx = (2 * float(p["p5"]) / 10) * _atr(bars_df, p["p4"])
    top = c == c.rolling(3).max()

    def line(n):
        now = c.ewm(span=n, adjust=False).mean() - atrx
        prev = c.shift(1).ewm(span=n, adjust=False).mean() - atrx
        return now.where(top, prev)

    sht, mid, lng = line(int(p["p1"])), line(int(p["p2"])), line(int(p["p3"]))
    long_ = (sht > mid) & (sht.shift(1) <= mid.shift(1)) & (c > sht)
    short_ = ((sht < lng) & (sht.shift(1) >= lng.shift(1))) | (c < lng)
    false = pd.Series(False, index=c.index)
    return long_ & ~short_, false, short_, false.copy()


def portfolio_kwargs(**params):
    return {}
