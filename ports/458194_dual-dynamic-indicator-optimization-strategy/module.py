"""Close crossings of the SMA 14, 1-hour bars: the close crossing over goes long, crossing under goes short; reversing (the RSI strategy is switched off by default).
Port of FMZ strategy #458194 "Dual Dynamic Indicator Optimization Strategy" (Multiple Strategies with On/Off Buttons).

FMZ source id: 458194

Source
    https://www.fmz.com/strategy/458194 (PineScript v5, FMZ last modified 2024-07-30 17:03:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-213), strategy 1 on: SMA 14 of close (EMA option); strategy 2 off: RSI 14 crossings of 30 / 70
    crossover(close, ma) -> entry Long S1;  crossunder(close, ma) -> entry Short S1;  (off: crossover(rsi, 30) -> Long S2, crossunder(rsi, 70) -> Short S2)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default switches are ported: strategy 1 on, strategy 2 off. There is no exit: positions
      end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458194_close_sma14_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [14, 50],
}
DEFAULT_PARAMS = {"ma_len": 14}


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
    ma = c.rolling(int(p["ma_len"])).mean()
    le = (c > ma) & (c.shift(1) <= ma.shift(1))
    se = (c < ma) & (c.shift(1) >= ma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
