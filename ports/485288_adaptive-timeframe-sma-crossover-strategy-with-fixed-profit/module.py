"""SMA 20 crosses held for one bar, 5-hour bars: the close crossing above the SMA 20 goes long, below it short; because
the script's timeframe check fails on its own 5-hour chart, close_all runs on every bar, so each trade closes at the
open after its fill bar (a reversal on that bar stands).
Port of FMZ strategy #485288 "均线突破固定利润目标自适应时间周期量化交易策略-Adaptive-Timeframe-SMA-Crossover-Strategy-with-Fixed-Profit-Targets" (NDX Scalping Strategy).

FMZ source id: 485288

Source
    https://www.fmz.com/strategy/485288 (PineScript v6, FMZ last modified 2025-03-07 09:49:32).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 164-199), SMA 20, profit target 20 points, timeframes "1,3,5"
    long = close > sma and crossover(close, sma) -> entry long;  short mirrored -> entry short
    high >= avg price + 20 -> close long;  low <= avg price - 20 -> close short
    not str.contains("1,3,5", timeframe.period) -> close_all (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the 5-hour header chart timeframe.period ("300") is not in "1,3,5": close_all fires on every bar. It acts on
      the position held at the bar's start and never undoes an entry on that bar (#430850): every trade is closed on
      the bar after its fill; a same-side signal on that bar is ignored, an opposite one reverses (REVERSAL INTENDED).
    * The 20-point target can only fire on a bar where close_all also fires (same exit): redundant, not ported
      separately.
    * Five-hour bars restart each UTC day at 00:00 (00, 05, 10, 15, 20 h; the last one 4 hours), as a 24-hour chart
      does; FREQ = "5h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders; one-bar holds as written.
    2 generic: PASS, a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (UTC day boundaries only for the 5-hour bins).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485288_sma20_cross_one_bar_hold"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5h"  # backtest header period: 5h (bins restart each UTC day)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [20, 50],
}
DEFAULT_PARAMS = {"ma_length": 20}


def precompute(raw_1m_df, symbol_key, **params):
    ohlc = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    idx = ohlc.index.tz_convert("UTC")
    key = idx.normalize() + pd.to_timedelta((idx.hour // 5) * 5, unit="h")   # bin start, left-labelled
    bars = ohlc.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    return bars.dropna(how="all")  # an empty bin is not a bar; never forward-filled


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.rolling(int(p["ma_length"])).mean()
    go_l = ((c > ma) & (c.shift(1) <= ma.shift(1))).to_numpy()
    go_s = ((c < ma) & (c.shift(1) >= ma.shift(1))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if start != 0 and pos == start:                  # close_all on every bar
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
