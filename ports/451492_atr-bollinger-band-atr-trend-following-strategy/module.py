"""Bollinger 20 / 2 band crossings with a close-to-close ATR trailing line, 4-hour bars: the close crossing under the lower band goes long and over the upper band goes short; a close over (under) the basis closes the long (short); the close crossing the trailing line also enters long / short; reversing.
Port of FMZ strategy #451492 "布林带ATR趋势跟踪策略-Bollinger-Band-ATR-Trend-Following-Strategy" (Bollinger Bands and ATR Strategy).

FMZ source id: 451492

Source
    https://www.fmz.com/strategy/451492 (PineScript v5, FMZ last modified 2024-05-15 10:50:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-155), Bollinger 20 / 2 (hand-written, population deviation); 'ATR' = mean |close - close[1]| over 10; key value 1
    crossunder(close, lower) -> entry Long;  crossover(close, upper) -> entry Short
    close > basis -> close Long;  close < basis -> close Short
    close > trail[1] and close[1] <= trail[1] -> entry Long;  close < trail[1] and close[1] >= trail[1] -> entry Short
    trail: close > trail[1] -> max(trail[1], close - atr);  close < trail[1] -> min(trail[1], close + atr);  else close - atr

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands, the 'ATR' (a mean of close-to-close moves, not a true range) and the trailing line
      are computed as written; the trailing line never flips to the other side of price on a cross
      (the max / min keeps the old level), and its na start takes the 'else' branch. The calls run in
      source order: an entry on the held side is ignored, an opposite entry reverses, and a close acts
      only on the trade held into the bar when no earlier call reversed it; a close followed by a
      same-side entry on one bar leaves the position on. A long opened above the basis is closed on the
      next bar still above it. The symbol / timeframe variables are unused. REVERSAL INTENDED. No
      sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band crossings with a trailing-line trigger.
    3 crypto-exchange-only: no (exchange pair in the header only (the 'AAPL' variable is unused)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451492_bollinger_cross_close_atr_trail_reversal"
FAMILY = "bollinger"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "mult": [2.0, 2.5],
    "atr_len": [10, 20],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "atr_len": 10, "key": 1.0}


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
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * dev, basis - float(p["mult"]) * dev
    atr = c.diff().abs().rolling(int(p["atr_len"])).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    k = float(p["key"])
    m = len(cv)
    trail = np.full(m, np.nan)
    for i in range(m):
        prev = trail[i - 1] if i > 0 else np.nan
        if not np.isnan(prev) and cv[i] > prev:
            trail[i] = max(prev, cv[i] - k * atr[i])
        elif not np.isnan(prev) and cv[i] < prev:
            trail[i] = min(prev, cv[i] + k * atr[i])
        else:
            trail[i] = cv[i] - k * atr[i]
    t1 = pd.Series(trail, index=c.index).shift(1)
    c1 = c.shift(1)
    lc = ((c < lower) & (c1 >= lower.shift(1))).to_numpy()
    sc = ((c > upper) & (c1 <= upper.shift(1))).to_numpy()
    cl = (c > basis).to_numpy()
    cs = (c < basis).to_numpy()
    buy = ((c > t1) & (c1 <= t1)).to_numpy()
    sell = ((c < t1) & (c1 >= t1)).to_numpy()
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if lc[i] and cur != 1:
            cur = 1
        if sc[i] and cur != -1:
            cur = -1
        if cl[i] and pos == 1 and cur == 1:
            cur = 0
        if cs[i] and pos == -1 and cur == -1:
            cur = 0
        if buy[i] and cur != 1:
            cur = 1
        if sell[i] and cur != -1:
            cur = -1
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
