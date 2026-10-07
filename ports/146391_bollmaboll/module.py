"""Bollinger band / band-MA cross breakout with band-narrowing exit ("bollmaboll").
Port of FMZ strategy #146391 "bollmaboll".

Source
    https://www.fmz.com/strategy/146391 (Python, author "3piggy", FMZ last modified
    2020-04-23 16:46:09). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 54-91), ma 13, bo 25, ma2 7
    bb = BBANDS(close, bo, 2, 2, SMA); up/mid/dn; mabt = SMA(up, ma); mabd = SMA(dn, ma)
    move = SMA(close, ma2); rsi = RSI(close, 12)
    buy:  up crosses above mabt, dn falling, mid rising, close > move, rsi > 60 -> position += 1
    sell: dn crosses below mabd, up rising, mid falling, close < move, rsi < 40 -> position -= 1
    if band width shrinks:  up crosses below mabt and position > 0 -> position -= 1
                            dn crosses above mabd and position < 0 -> position += 1
    (cross on [-1] vs [-2]; every order is 10 % of balance / stocks)

Interpretation choices
    * records[-1] is FMZ's forming bar; the port evaluates the same rule on completed bar t
      ([-1] -> t, [-2] -> t-1), once per bar (the bot polls every 30 s).
    * The position counter steps by one per order; repeated orders in one direction are adds
      (sizing, not ported). So with the port's single unit: a buy signal opens a long from flat
      and covers a short; a sell signal opens a short from flat and closes a long. The opposite
      signal flattens, it never reverses: opposite entries cannot occur, and portfolio_kwargs
      also returns upon_opposite_entry="ignore" (rule 6).
    * Bar size: the `period` argument defaults to `true` (= 1) -> PERIOD_M1, so FREQ = "1min"
      (the code's own request; options 2-6 are 3/5/15/30/60 min).
    * TA-Lib conventions: BBANDS population stdev, RSI Wilder. CMO is computed but unused.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_146391_boll_band_ma_cross"
FAMILY = "bollinger_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # code requests PERIOD_M1 (argument period = true)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bo": [20, 25, 30],
    "ma": [8, 13, 21],
    "ma2": [5, 7, 10],
}
DEFAULT_PARAMS = {"bo": 25, "ma": 13, "ma2": 7, "nbdev": 2.0, "rsi_period": 12,
                  "rsi_buy": 60, "rsi_sell": 40}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    bo = int(p["bo"])
    mid = close.rolling(bo).mean()
    sd = close.rolling(bo).std(ddof=0)
    up, dn = mid + p["nbdev"] * sd, mid - p["nbdev"] * sd
    mabt = up.rolling(int(p["ma"])).mean()
    mabd = dn.rolling(int(p["ma"])).mean()
    move = close.rolling(int(p["ma2"])).mean()
    rsi = _rsi(close, int(p["rsi_period"]))
    buy = ((up > mabt) & (up.shift(1) < mabt.shift(1)) & (dn < dn.shift(1)) & (mid > mid.shift(1))
           & (close > move) & (rsi > p["rsi_buy"])).to_numpy()
    sell = ((dn < mabd) & (dn.shift(1) > mabd.shift(1)) & (up > up.shift(1)) & (mid < mid.shift(1))
            & (close < move) & (rsi < p["rsi_sell"])).to_numpy()
    narrow = ((up - dn) < (up - dn).shift(1)).to_numpy()
    long_out = (narrow & (up < mabt) & (up.shift(1) > mabt.shift(1))).to_numpy()
    short_out = (narrow & (dn > mabd) & (dn.shift(1) < mabd.shift(1))).to_numpy()

    m = len(close)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if buy[i]:
            if pos == 0:
                le[i], pos = True, 1
            elif pos == -1:
                sx[i], pos = True, 0
        if sell[i]:
            if pos == 0:
                se[i], pos = True, -1
            elif pos == 1:
                lx[i], pos = True, 0
        if long_out[i] and pos == 1:
            lx[i], pos = True, 0
        if short_out[i] and pos == -1:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
