"""Candle meter: the fifth green bar in a row goes long, the fifth red bar in a row goes short; each
entry has a target and a stop (60 / 30 price units in the source) from the signal close.
Port of FMZ strategy #426996 "K Moving Average Candle Count Trend Following Strategy".

Source
    https://www.fmz.com/strategy/426996 (PineScript v4, FMZ last modified 2023-09-16 19:04:02).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 161-281), bar counter 5, TP 60, SL 30
    isLong = green-bar run == 5; isShort = red-bar run == 5
    isLong -> entry long; isShort -> close long, entry short
    exit(limit = signal close + 60, stop = signal close - 30) while the last signal was long
    (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 60 / 30 are price units ("USD"; x1 off forex) and become tp = 2 x sl_atr and
      sl_atr x ATR(14) at the signal bar, as fractions of the signal close applied to the fill.
    * Entries do not depend on the position: no mirroring. REVERSAL INTENDED (portfolio_kwargs {}).
    * The test-period function returns true. FREQ = "4h" from the backtest header; stops on 4h
      bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426996_candle_meter"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)
TP_RATIO = 2.0  # target 60 / stop 30

GRID = {
    "bar_counter": [3, 5],
    "sl_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"bar_counter": 5, "sl_atr": 0.25}


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


def _runs(flag):
    out = np.zeros(len(flag))
    r = 0
    for i, f in enumerate(flag):
        r = r + 1 if f else 0
        out[i] = r
    return out


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    k = int(p["bar_counter"])
    le = pd.Series(_runs((c > o).to_numpy()) == k, index=bars_df.index)
    se = pd.Series(_runs((c < o).to_numpy()) == k, index=bars_df.index)
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    f = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(le | se)
    return {"sl_stop": f.shift(1), "tp_stop": (TP_RATIO * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
