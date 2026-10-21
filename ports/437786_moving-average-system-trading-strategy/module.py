"""Side changes of the close against an SMA 17 of ohlc4, 1-hour bars: the first close above the MA after the last close below it goes long, the first close below after the last close above goes short; reversing.
Port of FMZ strategy #437786 "Moving Average System Trading Strategy" (Simple 17 BF ?).

FMZ source id: 437786

Source
    https://www.fmz.com/strategy/437786 (PineScript v4, FMZ last modified 2024-01-05 15:36:00).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 186-238), MA source ohlc4, type sma (options ema, swma, wma, vwma, rma), length 17; capital 10000, 100 % of equity, commission 0; date window true
    last_long := close > MA ? time : last_long[1];  last_short := close < MA ? time : last_short[1];  crossover(last_long, last_short) -> entry L;  crossover(last_short, last_long) -> entry S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two time stamps hold the newest bar on each side of the MA, so a crossover is the first close on
      one side after the last close on the other (a close equal to the MA moves neither). Both start at 0,
      so the first close above (below) a valid MA fires. The port keeps bar numbers instead of times (the
      same order). The MA type is swept over sma and ema (the vwma option needs volume and is not swept).
      testPeriod() is true. strategy.entry reverses: REVERSAL INTENDED. The capital, size and commission
      are sizing / costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close sides of a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital, percent-of-equity size and commission stored.
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

NAME = "fmz_437786_ma17_side_change"
FAMILY = "ma_trend"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [17, 34],
    "ma_type": ["sma", "ema"],
}
DEFAULT_PARAMS = {"length": 17, "ma_type": "sma"}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = (o + h + lo + c) / 4.0
    n = int(p["length"])
    if p["ma_type"] == "ema":
        ma = src.ewm(span=n, adjust=False).mean()
    else:
        ma = src.rolling(n).mean()
    above = (c > ma).to_numpy()
    below = (c < ma).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ll = ls = 0                                         # bar number + 1 of the newest close on each side
    for i in range(m):
        pl, ps = ll, ls
        if above[i]:
            ll = i + 1
        if below[i]:
            ls = i + 1
        if i > 0:
            le[i] = ll > ls and pl <= ps
            se[i] = ls > ll and ps <= pl
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
