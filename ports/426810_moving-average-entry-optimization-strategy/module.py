"""Wait for a better entry: the SMA 20 slope sets the side; when it flips, an open position is
closed and the flip's close is stored. From flat, enter on the slope's side once the price is
better than that close by a threshold, or after 3 bars of waiting regardless.
Port of FMZ strategy #426810 "Moving Average Entry Optimization Strategy".

Source
    https://www.fmz.com/strategy/426810 (PineScript v4, FMZ last modified 2023-09-14 16:52:30).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 124-172), period 20, maxwait 3, threshold 0.01
    signal = sma rising ? 1 : falling ? -1 : signal[1]
    if signal != signal[1]: close the open position (signal set opposite the position held),
                            wait = 0, initialentry = close
    else if signal != 0 and flat: wait += 1
    if flat: wait >= 3 -> entry on signal's side
             else signal > 0 and close < initialentry - threshold -> long
                  signal < 0 and close > initialentry + threshold -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "flat" is the position at the bar close; orders fill at the next open, so a close and an
      entry are never issued on the same bar.
    * As written, a flip while long sets signal to -1 and while short to +1 (whatever the slope).
    * Criterion 2: the 0.01 threshold is a price distance (0 ATR on BTC). It becomes
      thr_atr x ATR(14) on the bar.
    * Opposite entries cannot occur (entries only from flat).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426810_delayed_ma_entry"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "period": [20, 50],
    "maxwait": [3, 6],
    "thr_atr": [0.0, 0.25, 0.5],
}
DEFAULT_PARAMS = {"period": 20, "maxwait": 3, "thr_atr": 0.0}


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


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    trend = c.rolling(int(p["period"])).mean().to_numpy()
    thr = (p["thr_atr"] * _atr_pine(bars_df, ATR_LEN)).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    target = np.zeros(m, dtype=int)
    pos = 0          # position held at this bar's close (filled from the previous bar's orders)
    sig_p = np.nan
    trend_p = np.nan
    wait = 0.0
    initial = 0.0
    for i in range(m):
        sig = 0 if np.isnan(sig_p) else sig_p
        tp = 0.0 if np.isnan(trend_p) else trend_p
        if trend[i] > tp:
            sig = 1
        elif trend[i] < tp:
            sig = -1
        new = pos
        if not np.isnan(sig_p) and sig != sig_p:
            if pos > 0:
                new, sig = 0, -1
            elif pos < 0:
                new, sig = 0, 1
            wait, initial = 0.0, cv[i]
        elif sig != 0 and pos == 0:
            wait += 1
        if pos == 0:
            if wait >= p["maxwait"]:
                new = 1 if sig > 0 else (-1 if sig < 0 else 0)
            elif sig > 0 and cv[i] < initial - thr[i]:
                new = 1
            elif sig < 0 and cv[i] > initial + thr[i]:
                new = -1
        target[i] = new
        pos, sig_p, trend_p = new, sig, trend[i]
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
