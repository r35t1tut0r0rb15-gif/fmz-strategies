"""Bullish engulfing candles, 2-hour bars, long only: an engulfing candle buys, and the position closes 17 bars after its entry bar.
Port of FMZ strategy #477529 "Multi Period Trend Linear Engulfing Pattern Quantitative Trading Strategy" (Engulfing Candlestick Strategy).

FMZ source id: 477529

Source
    https://www.fmz.com/strategy/477529 (PineScript v6, FMZ last modified 2025-01-06 11:42:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-134), hold periods 17; pattern Bullish Engulfing, trade type Long (defaults)
    close > open and open < close[1] and close > open[1] and open[1] > close[1] -> entry Long;  position and bar_index - entry_bar_index(0) >= 17 -> close Long / Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default inputs (bullish engulfing, long) are ported. The entry bar is the fill bar, so the
      close is sent on the bar 17 bars after it and fills at the next open (a loop counts the bars). A
      pattern while long is ignored and does not restart the count. Long only. No sizing code. FREQ = "2h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, engulfing candles with a fixed holding time.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477529_bullish_engulfing_hold17_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold_periods": [17, 8, 34],
}
DEFAULT_PARAMS = {"hold_periods": 17}


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
    o, c = bars_df["open"], bars_df["close"]
    eng = ((c > o) & (o < c.shift(1)) & (c > o.shift(1)) & (o.shift(1) > c.shift(1))).to_numpy()
    k = int(p["hold_periods"])
    m = len(eng)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, fill = 0, 0, -1
    for i in range(m):
        if nxt == 1 and pos == 0:
            fill = i
        pos = nxt
        if eng[i] and pos == 0:
            le[i], nxt = True, 1
        if pos == 1 and i - fill >= k:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
