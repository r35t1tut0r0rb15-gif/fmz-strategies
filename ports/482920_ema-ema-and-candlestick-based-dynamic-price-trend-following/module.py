"""Pin bars and engulfing candles in the EMA 8 / 21 trend, always in the market, 1-hour bars: a bullish pin bar or
bullish engulfing bar with EMA 8 above EMA 21 and the close above EMA 21 goes long; the bearish mirror goes short.
Port of FMZ strategy #482920 "基于EMA和蜡烛图的动态价格跟踪趋势交易策略-EMA-and-Candlestick-Based-Dynamic-Price-Trend-Following-Strategy" (Candlestick Bible: Dynamic Price Follower (Corrected)).

FMZ source id: 482920

Source
    https://www.fmz.com/strategy/482920 (PineScript v6, FMZ last modified 2025-02-20 17:43:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-138), EMA 8 / 21
    bullish pin = lower shadow >= 2 body and upper shadow <= body / 2; bullish engulf = red then green with
    close > open[1] and open < close[1] (bearish mirrored)
    long = (pin or engulf) and ema8 > ema21 and close > ema21; short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR is computed but unused. Entries reverse (REVERSAL INTENDED); no exits, no stops. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle shapes and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_482920_pin_engulf_ema_trend_reversal"
FAMILY = "candlestick"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 21}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (c - o).abs()
    up_sh = h - np.maximum(c, o)
    lo_sh = np.minimum(c, o) - lo
    bull_pin = (lo_sh >= 2 * body) & (up_sh <= body / 2)
    bear_pin = (up_sh >= 2 * body) & (lo_sh <= body / 2)
    o1, c1 = o.shift(1), c.shift(1)
    bull_eng = (c1 < o1) & (c > o) & (c > o1) & (o < c1)
    bear_eng = (c1 > o1) & (c < o) & (c < o1) & (o > c1)
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    short_e = ((bear_pin | bear_eng) & (f <= s) & (c < s)).astype(bool)
    long_e = ((bull_pin | bull_eng) & (f > s) & (c > s) & ~short_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
