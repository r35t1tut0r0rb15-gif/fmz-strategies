"""EMA 15 / EMA 30 cross, 4-hour bars: the fast EMA crossing above the slow one goes long, crossing below
goes short (the optional trailing stop, take-profit and stop-loss are off by default).
Port of FMZ strategy #428810 "Moving Average Crossover Multi Timeframe Strategy" (Moving Averages Cross - MTF - Strategy).

FMZ source id: 428810

Source
    https://www.fmz.com/strategy/428810 (PineScript v3, FMZ last modified 2023-10-09 16:41:04).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 259-536), MA 1 EMA 15, MA 2 EMA 30 on close, other resolution off, pyramiding count <= 1
    longCondition = crossover(ma1, ma2) (count of consecutive longs <= 1)
    shortCondition = crossunder(ma1, ma2) (likewise)
    entry long / entry short; close long on longClose, close short on shortClose (TS / TP / SL, all off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: both averages EMA on close, "Use Different Resolution" off, Longs Only / Shorts Only /
      Flip off; the consecutive-signal counter can only reach 1 between opposite crosses, so every
      cross enters. The trailing stop, take-profit and stop-loss switches default to false: their
      closes never fire (stored in original_sizing.txt).
    * The other MA types are input options; only the default EMA is ported. The date window is
      dropped (testPeriod is true).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity, the pyramiding counters and the off-by-default exits stored.
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

NAME = "fmz_428810_ema15_30_cross_mtf"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [15, 10],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 15, "slow": 30}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
