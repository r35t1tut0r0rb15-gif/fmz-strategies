"""Follow Line (Zer3192): a trend line set to low - ATR(5) on closes above the upper Bollinger band
(21, 1 sd) and to high + ATR(5) below the lower band, never moving against itself; the line
turning up goes long, turning down goes short (always in).
Port of FMZ strategy #368736 "Follow Line Indicator".

Source
    https://www.fmz.com/strategy/368736 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-12 17:01:09). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 41-98), BB 21 x 1, ATR filter on, ATR 5
    BBSignal = close > upper ? 1 : close < lower ? -1 : 0
    1: TL = max(low - atr, TL[1]);  -1: TL = min(high + atr, TL[1]);  0: TL = TL[1]
    iTrend = TL > TL[1] ? 1 : TL < TL[1] ? -1 : iTrend[1]
    iTrend -1 -> 1 -> entry long; 1 -> -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Comparisons with an na history are false, as in Pine (the first bars keep their value).
    * Same family as #362256 (Follow Line). strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_368736_follow_line_flip"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_period": [14, 21, 34],
    "bb_dev": [1.0, 1.5],
    "atr_period": [5, 10],
}
DEFAULT_PARAMS = {"bb_period": 21, "bb_dev": 1.0, "atr_period": 5}


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
    c = bars_df["close"]
    n = int(p["bb_period"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0) * p["bb_dev"]
    sig = np.where(c > mid + sd, 1, np.where(c < mid - sd, -1, 0))
    atr = _atr_pine(bars_df, int(p["atr_period"])).to_numpy()
    h, l = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(c)
    tl = np.full(m, np.nan)
    it = np.full(m, np.nan)
    for i in range(m):
        t1 = tl[i - 1] if i else np.nan
        if sig[i] == 1:
            v = l[i] - atr[i]
            tl[i] = t1 if v < t1 else v
        elif sig[i] == -1:
            v = h[i] + atr[i]
            tl[i] = t1 if v > t1 else v
        else:
            tl[i] = t1
        prev = it[i - 1] if i else np.nan
        it[i] = 1.0 if tl[i] > t1 else (-1.0 if tl[i] < t1 else prev)
    pi = np.concatenate([[np.nan], it[:-1]])
    return _always_in((it == 1) & (pi == -1), (it == -1) & (pi == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
