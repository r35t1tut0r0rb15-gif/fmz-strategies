"""Close crossings of the EMA 5, 3-hour bars: the close crossing over the EMA 5 goes long, under it goes short; reversing.
Port of FMZ strategy #453648 "Elliott-Wave-Stochastic-EMA-Strategy-Elliott-波动随机EMA策略" (Elliott Wave with Stochastic and Exponential Averages).

FMZ source id: 453648

Source
    https://www.fmz.com/strategy/453648 (PineScript v5, FMZ last modified 2024-06-07 14:56:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-138), EMA 5 (EMA 10 / 20 / 50 / 200 and the stochastic plotted only)
    crossover(close, ema5) -> entry Buy;  crossunder(close, ema5) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The other EMAs and the stochastic are only plotted. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header
      (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / EMA 5 crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453648_close_ema5_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [5, 10, 20],
}
DEFAULT_PARAMS = {"ema_len": 5}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    c1, e1 = c.shift(1), e.shift(1)
    le = (c > e) & (c1 <= e1)
    se = (c < e) & (c1 >= e1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
