"""Bull-market support band crossings, 4-hour bars: the close crossing over the SMA 20 goes long, crossing under the EMA 21 goes short; reversing.
Port of FMZ strategy #442921 "Dual Moving Average Crossover Strategy" (BMSB Breakout Strategy).

FMZ source id: 442921

Source
    https://www.fmz.com/strategy/442921 (PineScript v5, FMZ last modified 2024-02-27 13:51:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-168), SMA 20, EMA 21 (requested on the chart's own time frame)
    buy = crossover(close, sma20) -> entry Long, close Short;  sell = crossunder(close, ema21) -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The requests use timeframe.period, the chart itself. The "not na" tests on the booleans always
      pass. The closes repeat the reversals; when both cross on one bar the later short wins (as
      #437773). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA / EMA band crossings.
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

NAME = "fmz_442921_bmsb_sma20_ema21_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [20, 50],
    "ema_length": [21, 50],
}
DEFAULT_PARAMS = {"sma_length": 20, "ema_length": 21}


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
    s = c.rolling(int(p["sma_length"])).mean()
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    buy = (c > s) & (c.shift(1) <= s.shift(1))
    sell = (c < e) & (c.shift(1) >= e.shift(1))
    false = pd.Series(False, index=c.index)
    return buy & ~sell, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
