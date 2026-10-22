"""SMA 10 / 100 crossings between 12:00 and 17:00 UTC, 2-minute bars: the cross up goes long, the cross down goes short, each with a 100-point target and 100-point stop from the signal close; reversing.
Port of FMZ strategy #458276 "Dual Moving Average Momentum Trading Strategy Time Optimized Trend Following System" (Gold Trend Trader).

FMZ source id: 458276

Source
    https://www.fmz.com/strategy/458276 (PineScript v5, FMZ last modified 2024-07-31 14:50:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-261), SMA 10 / 100; UTC window 12:00-17:00 (bar open, end excluded); entries _1 (target 100, stop 100) and _2 (target 150, stop 1500 / 150), price units
    crossover(sma10, sma100) in window -> entry Buy_1 + exit(limit = close + 100, stop = close - 100);  entry Buy_2 + exit(limit = close + 150, stop = close - 1500)
    crossunder in window -> entry Sell_1 + exit(limit = close - 100, stop = close + 100);  entry Sell_2 + exit(limit = close - 150, stop = close + 150)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default pyramiding of 1 the second entry of each pair never fills (#441137), so each
      trade is the _1 order with its 100-point target and stop. The points are price amounts, ported as
      fractions of 42000 (0.00238 of the fill). The window is the bar's UTC open time, minutes 720 to
      1019. The labels are drawing only. The title names gold; the rules are generic. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "2min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fractions of the fill.
    2 generic: PASS, SMA crossings in set hours with a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only (gold named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 12:00-17:00 UTC on the bar open (end excluded).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458276_sma10_100_cross_utc_window_point_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [10, 20],
    "long_len": [100, 50],
    "bracket": [0.00238, 0.005],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 100, "bracket": 0.00238, "start_h": 12, "end_h": 17}


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
    ix = bars_df.index
    mins = pd.Series(ix.hour * 60 + ix.minute, index=ix)
    win = (mins >= int(p["start_h"]) * 60) & (mins < int(p["end_h"]) * 60)
    a, b = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & win
    se = (a < b) & (a.shift(1) >= b.shift(1)) & win
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    b = float(p["bracket"])
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
