"""Three-line strikes and engulfing candles, 1-hour bars: three down candles followed by a close over the last open, or a bullish engulfing candle, goes long; the mirrors go short; reversing.
Port of FMZ strategy #458183 "Multi Moving Average Trend Following and Reversal Pattern Recognition Strategy" (TMA Overlay Strategy).

FMZ source id: 458183

Source
    https://www.fmz.com/strategy/458183 (PineScript v5, FMZ last modified 2024-07-30 16:30:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 211-334), SMMA 21 / 50 / 100 / 200, EMA 2 and the session windows plotted only; 3-line strike; engulfing (open vs the previous open / close)
    bullSig (3 down candles, close > open[1]) or bullishEngulfing (open <= close[1], open < open[1], close > open[1]) -> entry Long
    bearSig or bearishEngulfing -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The smoothed averages, the trend fill and the session windows only colour the chart. A long
      signal needs the close over the previous open and a short one under it, so both cannot hold on a
      bar. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the windows are drawing only).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458183_three_line_strike_engulfing_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, c = bars_df["open"], bars_df["close"]
    up = c > o
    dn = c < o
    o1, c1 = o.shift(1), c.shift(1)
    bear_sig = up.shift(3, fill_value=False) & up.shift(2, fill_value=False) & up.shift(1, fill_value=False) & (c < o1)
    bull_sig = dn.shift(3, fill_value=False) & dn.shift(2, fill_value=False) & dn.shift(1, fill_value=False) & (c > o1)
    bull_e = (o <= c1) & (o < o1) & (c > o1)
    bear_e = (o >= c1) & (o > o1) & (c < o1)
    false = pd.Series(False, index=bars_df.index)
    return bull_sig | bull_e, false, bear_sig | bear_e, false.copy()


def portfolio_kwargs(**params):
    return {}
