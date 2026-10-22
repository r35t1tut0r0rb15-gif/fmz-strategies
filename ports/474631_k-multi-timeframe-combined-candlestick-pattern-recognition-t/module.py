"""Ten candlestick patterns, 2-hour bars: a hammer, bullish engulfing, piercing line, morning star or three white soldiers goes long; a hanging man, bearish engulfing, dark cloud cover, evening star or three black crows goes short (the short wins a bar with both); reversing.
Port of FMZ strategy #474631 "多周期组合K线形态识别交易策略-Multi-Timeframe-Combined-Candlestick-Pattern-Recognition-Trading-Strategy" (Ubaton - Candlestick Pattern Strategy).

FMZ source id: 474631

Source
    https://www.fmz.com/strategy/474631 (PineScript v5, FMZ last modified 2024-12-11 11:04:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-187), all ten patterns switched on
    hammer or bullEngulf or piercing or morningStar or threeWhite -> entry Bullish Entry;  hangingMan or bearEngulf or darkCloud or eveningStar or threeBlack -> entry Bearish Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * The patterns are as written (a shadow test with na is false). Both entries can be sent on one bar;
      the later call, the short, wins (#437773). There is no exit: positions end at the opposite entry.
      REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candlestick patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474631_ten_candlestick_patterns_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o1, h1, l1, c1 = o.shift(1), h.shift(1), lo.shift(1), c.shift(1)
    o2, c2 = o.shift(2), c.shift(2)
    body = (o - c).abs()
    bot = np.minimum(o, c)
    shadow = (bot - lo).where(lo < bot)          # na when there is no lower shadow
    small_top = (h - np.maximum(o, c)) <= body
    hammer = (shadow >= 2 * body) & small_top
    hanging = (shadow >= 2 * body) & small_top & (c < o)
    bull_eng = (c1 < o1) & (c > o) & (o <= c1) & (c >= o1)
    piercing = (c1 < o1) & (c > c1 + (o1 - c1) * 0.5) & (c < o1)
    morning = (c2 < o2) & ((c1 - o1).abs() < (h1 - l1) * 0.3) & (c > o)
    soldiers = (c > o) & (c1 > o1) & (c2 > o2) & (o > c1) & (o1 > c2)
    bear_eng = (c1 > o1) & (c < o) & (o >= c1) & (c <= o1)
    dark = (c1 > o1) & (o > c1) & (c < o1) & (c < c1 + (o1 - c1) * 0.5)
    evening = (c2 > o2) & ((c1 - o1).abs() < (h1 - l1) * 0.3) & (c < o)
    crows = (c < o) & (c1 < o1) & (c2 < o2) & (o < c1) & (o1 < c2)
    bull = hammer | bull_eng | piercing | morning | soldiers
    bear = hanging | bear_eng | dark | evening | crows
    false = pd.Series(False, index=bars_df.index)
    return bull & ~bear, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
