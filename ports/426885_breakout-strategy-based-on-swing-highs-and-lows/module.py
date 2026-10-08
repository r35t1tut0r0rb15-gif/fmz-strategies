"""JetzGiantz swing reversal: from flat, a green bar engulfing past the previous red bar's open
just after a 3-bar low undercut the 50-bar low goes long; the short mirror (as written) needs a
red bar closing above the previous green bar's open after a 3-bar high above the 50-bar high.
Each trade has a fixed stop and a target 10 times as far.
Port of FMZ strategy #426885 "Breakout Strategy Based on Swing Highs and Lows".

Source
    https://www.fmz.com/strategy/426885 (PineScript v4, FMZ last modified 2023-09-15 11:47:13).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 128-152), stop 10, target 100 (ticks)
    buy  = close[1] < open[1] and close > open and close > open[1]
           and (low3 < low50[1] or low3 < low50[2] or low3 < low50[3])
    sell = close[1] > open[1] and close < open and close > open[1]
           and (high3 > high50[1] or high3 > high50[2] or high3 > high50[3])
    flat: buy -> strategy.order long;  sell -> strategy.order short
    exit(loss = 10, profit = 100) for either side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Kept as written: the sell rule's close > open[1] (a mirror would read close < open[1];
      decision owed).
    * Criterion 2: 10 / 100 ticks become sl_atr x ATR(14) at the signal bar and a target 10 x
      that (the source's ratio), applied to the fill.
    * Entries need a flat position (strategy.order when flat), so simulate() mirrors the
      engine's stop and target. Opposite entries cannot occur. The month / year start filter is
      a backtest window: dropped.
    * FREQ = "4h" from the backtest header; stops on 4h bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426885_jetzgiantz_swing_reversal"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)
TP_RATIO = 10.0  # profit 100 / loss 10 ticks

GRID = {
    "sl_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.25}


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


def _setups(bars_df):
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    low3, low50 = l.rolling(3).min(), l.rolling(50).min()
    high3, high50 = h.rolling(3).max(), h.rolling(50).max()
    o1, c1 = o.shift(1), c.shift(1)
    under = (low3 < low50.shift(1)) | (low3 < low50.shift(2)) | (low3 < low50.shift(3))
    over = (high3 > high50.shift(1)) | (high3 > high50.shift(2)) | (high3 > high50.shift(3))
    buy = (c1 < o1) & (c > o) & (c > o1) & under
    sell = (c1 > o1) & (c < o) & (c > o1) & over
    return buy.to_numpy(), sell.to_numpy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _setups(bars_df)
    fr = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).to_numpy()
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, f, stop, target = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, e = pending, o[i]
            stop, target = e * (1 - pos * f), e * (1 + pos * TP_RATIO * f)
            pending = 0
        if pos == 1 and (lo[i] <= stop or h[i] >= target):
            pos = 0
        elif pos == -1 and (h[i] >= stop or lo[i] <= target):
            pos = 0
        if pos == 0 and not pending:
            if buy[i]:
                le[i], pending, f = True, 1, fr[i]
            elif sell[i]:
                se[i], pending, f = True, -1, fr[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = simulate(bars_df, **params)
    f = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(le | se)
    return {"sl_stop": f.shift(1), "tp_stop": (TP_RATIO * f).shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
