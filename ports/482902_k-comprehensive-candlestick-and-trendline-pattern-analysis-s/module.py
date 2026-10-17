"""A basket of bullish / bearish candle and three-bar patterns, always in the market, 1-hour bars: any bullish
pattern (engulfing, hammer, morning star, piercing line, bullish harami, double bottom, inverse head and shoulders)
goes long; any bearish one (engulfing, hanging man, evening star, dark cloud, bearish harami, double top, head and
shoulders) goes short.
Port of FMZ strategy #482902 "综合K线图形态与趋势线技术分析策略-Comprehensive-Candlestick-and-Trendline-Pattern-Analysis-Strategy" (Advanced Candlestick and Line Chart Patterns with Head and Shoulders).

FMZ source id: 482902

Source
    https://www.fmz.com/strategy/482902 (PineScript v6, FMZ last modified 2025-02-27 17:25:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-196), the pattern definitions as written (lines 105-148)
    long = any bullish pattern -> entry long; short = any bearish pattern -> entry short
    exit(stop = low - 10, limit = high + 10) for the long, (stop = high + 10, limit = low - 10) for the short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The patterns are ported literally, including the hammer's 0.001 price-unit guard in its ratios.
    * The 10-point stop and target are price units: on the author's market (Binance DOGE_USDT, price about 0.25) they
      sit at negative prices or far out of reach, so they are dropped as inert (as #492009, #490798).
    * Entries reverse (REVERSAL INTENDED); with both patterns on one bar the later short wins. No exits, no stops.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle shapes (the price-unit exits are inert and dropped).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the inert exits quoted in original_sizing.txt.
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

NAME = "fmz_482902_candle_pattern_basket_reversal"
FAMILY = "candlestick"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o1, o2, c1, c2 = o.shift(1), o.shift(2), c.shift(1), c.shift(2)
    h1, h2, l1, l2 = h.shift(1), h.shift(2), lo.shift(1), lo.shift(2)
    bull_eng = (c > o1) & (o < c1)
    bear_eng = (c < o1) & (o > c1)
    hammer = ((h - lo) > 2 * (o - c)) & ((c - lo) / (0.001 + h - lo) > 0.6) & ((o - lo) / (0.001 + h - lo) > 0.6)
    hanging = hammer & (c < o)
    morning = (c2 < o2) & (c1 > o1) & (c > o) & (c > c2) & (o1 > c2)
    evening = (c2 > o2) & (c1 < o1) & (c < o) & (c < c2) & (o1 < c2)
    piercing = (c > o) & (c1 < o1) & (c > o1) & (o < c1)
    dark = (c < o) & (c1 > o1) & (c < o1) & (o > c1)
    bull_har = (c > o1) & (o < c1) & (c > o) & (c1 > o)
    bear_har = (c < o1) & (o > c1) & (c < o) & (c1 < o)
    dbl_top = (h2 > h1) & (h1 < h) & (c < o1)
    dbl_bot = (l2 < l1) & (l1 > lo) & (c > o1)
    hs = (h2 > h1) & (h1 < h) & (c < o1)
    ihs = (l2 < l1) & (l1 > lo) & (c > o1)
    long_c = bull_eng | hammer | morning | piercing | bull_har | dbl_bot | ihs
    short_c = bear_eng | hanging | evening | dark | bear_har | dbl_top | hs
    short_e = short_c.astype(bool)
    long_e = (long_c & ~short_c).astype(bool)          # both on one bar: the later short entry wins
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
