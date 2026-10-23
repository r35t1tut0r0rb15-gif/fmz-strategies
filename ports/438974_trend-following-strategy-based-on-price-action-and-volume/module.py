"""Hourly bars: the SMA 50 crossing over the SMA 25 on a bar whose volume is above its 25-bar average (close above the 30-bar low) goes long; crossing under on above-average volume (close below the 30-bar high) goes short; reversing.
Port of FMZ strategy #438974 "Trend Following Strategy Based on Price Action and Volume" (PVSRA Strategy).

FMZ source id: 438974

Source
    https://www.fmz.com/strategy/438974 (PineScript v4, FMZ last modified 2024-01-16 17:34:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 164-194), short MA 50, long MA 25 (as written); volume SMA 25; support / resistance = 30-bar low / high
    longCondition = crossover(sma(close, 50), sma(close, 25)) and volume > sma(volume, 25) and close > lowest(low, 30)
    shortCondition = crossunder(...) and volume > volMa and close < highest(high, 30);  entry Long / entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "short" MA is the 50 and the "long" the 25, as written (a crossover of the slower average
      over the faster: weird case). The 30-bar low / high include the current bar, so the close test only
      fails when the close is the window's extreme. REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings on above-average volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 25; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438974_sma50_sma25_cross_volume_above_average_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ma": [50, 10],
    "vol_len": [25, 50],
}
DEFAULT_PARAMS = {"short_ma": 50, "long_ma": 25, "vol_len": 25, "range_len": 30}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    a = c.rolling(int(p["short_ma"])).mean()
    b = c.rolling(int(p["long_ma"])).mean()
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    n = int(p["range_len"])
    co = (a > b) & (a.shift(1) <= b.shift(1))
    cu = (a < b) & (a.shift(1) >= b.shift(1))
    le = co & vol_ok & (c > lo.rolling(n).min())
    se = cu & vol_ok & (c < h.rolling(n).max())
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
