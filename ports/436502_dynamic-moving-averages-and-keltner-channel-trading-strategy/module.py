"""Breakout bars above the 20-bar average, 1-hour bars: a bar with a higher high, higher low and a close over the previous high, with the close over the moving average, goes long; the mirror goes short; the close
back across the average closes the side.
Port of FMZ strategy #436502 "Dynamic Moving Averages and Keltner Channel Trading Strategy" (Intraday Trend Identifier (ITI Keltner)).

FMZ source id: 436502

Source
    https://www.fmz.com/strategy/436502 (PineScript v5, FMZ last modified 2023-12-25 13:36:40).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 150-189), SMA 20 (or EMA 20)
    bullish = high > high[1] and low > low[1] and close > high[1];  bearish = high < high[1] and low < low[1] and close < low[1];  longCondition = bullish and not bearish and close > ma;  shortCondition = bearish and not bullish and close < ma
    entry Buy / Sell;  close Buy when close < ma;  close Sell when close > ma;  the Keltner, Super Trend, support / resistance and arrows are only drawn

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four rules of one bar are filled at the next open in the script's call order (Buy, Sell, close
      Buy, close Sell); a close only acts on a position of its own side. The Keltner and Super Trend
      signals only draw arrows. REVERSAL INTENDED. The default quantity (1 contract) is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, breakout bar and moving-average side.
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

NAME = "fmz_436502_breakout_bar_ma_side"
FAMILY = "trend_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": ["SMA", "EMA"],
    "length": [20, 50],
}
DEFAULT_PARAMS = {"ma_type": "SMA", "length": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ma = c.rolling(n).mean() if p["ma_type"] == "SMA" else c.ewm(span=n, adjust=False).mean()
    bull = (h > h.shift(1)) & (lo > lo.shift(1)) & (c > h.shift(1))
    bear = (h < h.shift(1)) & (lo < lo.shift(1)) & (c < lo.shift(1))
    long_c = (bull & ~bear & (c > ma)).fillna(False).to_numpy()
    short_c = (bear & ~bull & (c < ma)).fillna(False).to_numpy()
    xl = (c < ma).fillna(False).to_numpy()
    xs = (c > ma).fillna(False).to_numpy()
    m = len(c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "XL" and pos > 0:
                    pos = 0
                elif op == "XS" and pos < 0:
                    pos = 0
        held[i] = pos
        ops = []
        if long_c[i]:
            ops.append("eL")
        if short_c[i]:
            ops.append("eS")
        if xl[i]:
            ops.append("XL")
        if xs[i]:
            ops.append("XS")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
