"""EMA 5 / SMA 20 crossings on 1-hour and 4-hour bars at once, 1-hour bars, long only: the 1-hour EMA 5 crossing over the SMA 20 on the same bar as the completed 4-hour EMA 5 crossing over its SMA 20 buys;
the next-bar close names an id that never trades, so the first long is held.
Port of FMZ strategy #439079 "基于EMA和SMA交叉的趋势跟踪策略Trend-Following-Strategy-Based-on-EMA-and-SMA-Crossover" (Shashank Cross).

FMZ source id: 439079

Source
    https://www.fmz.com/strategy/439079 (PineScript v5, FMZ last modified 2024-01-17 15:42:22).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 131-154), EMA 5 / SMA 20 on the chart and on "240"
    condition1 = crossover(ema(close, 5), sma(close, 20));  condition2 = crossover(security("240", ema 5), security("240", sma 20));  both -> entry Buy;  barssince(buy) == 1 -> close("Exit")

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 security() without lookahead is read as the last completed higher bar: the previous
      4-hour bar's EMA 5 and SMA 20 (4-hour bars on UTC multiples of 4 hours, from the module's own bars),
      so condition 2 can only change on the first hour of a 4-hour bar. strategy.close("Exit") names an
      entry id that is never used, so it closes nothing: the first long is held to the end of the data,
      as written (owed: close("Buy")). Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 4-hour values from completed bars.
    2 generic: PASS, EMA / SMA crossings on two bar sizes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439079_ema5_sma20_1h_4h_cross_held"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 9],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 20}


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
    f, s = int(p["fast"]), int(p["slow"])
    e1, s1 = c.ewm(span=f, adjust=False).mean(), c.rolling(s).mean()
    cond1 = (e1 > s1) & (e1.shift(1) <= s1.shift(1))
    key = bars_df.index.floor("4h")
    c4 = c.groupby(key).last()
    e4 = c4.ewm(span=f, adjust=False).mean().shift(1).reindex(key).to_numpy()   # last completed 4-hour bar
    s4 = c4.rolling(s).mean().shift(1).reindex(key).to_numpy()
    e4s, s4s = pd.Series(e4, index=c.index), pd.Series(s4, index=c.index)
    cond2 = (e4s > s4s) & (e4s.shift(1) <= s4s.shift(1))
    buy = (cond1 & cond2).to_numpy()
    m = len(c)
    le = np.zeros(m, dtype=bool)
    hits = np.flatnonzero(buy[:-1]) if m > 1 else np.array([], dtype=int)
    if len(hits):
        le[hits[0]] = True                               # never closed: later buys are ignored
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
