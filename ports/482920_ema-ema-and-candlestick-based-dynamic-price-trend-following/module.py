"""Pin bars and engulfing candles with the EMA 8 / 21 trend, hourly bars: a bullish pin or engulfing with EMA 8 over EMA 21 and the close over EMA 21 goes long, the bearish mirror goes short; reversing, no other exit.
Port of FMZ strategy #482920 "基于EMA和蜡烛图的动态价格跟踪趋势交易策略-EMA-and-Candlestick-Based-Dynamic-Price-Trend-Following-Strategy" (Candlestick Bible: Dynamic Price Follower (Corrected)).

FMZ source id: 482920

Source
    https://www.fmz.com/strategy/482920 (PineScript v6, FMZ last modified 2025-02-20 17:43:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-146), pin bar (shadow 2x body, other shadow <= half body); engulfing; EMA 8 / 21; ATR 14 (unused); pyramiding 0; 100 % of equity, capital 10000
    (bullish pin or bullish engulfing) and ema8 > ema21 and close > ema21 -> entry Long;  (bearish pin or bearish engulfing) and ema8 < ema21 and close < ema21 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only: each reverses the other side (REVERSAL INTENDED), no other exit; a repeat on the side
      held adds nothing (pyramiding 0). The ATR is computed but feeds nothing. The 100 % of equity size
      and the capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle patterns with an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
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

NAME = "fmz_482920_pin_engulf_ema8_21_trend_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 5],
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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    body = (c - o).abs()
    up_sh = h - np.maximum(c, o)
    dn_sh = np.minimum(c, o) - lo
    bull_pin = (dn_sh >= 2 * body) & (up_sh <= body / 2)
    bear_pin = (up_sh >= 2 * body) & (dn_sh <= body / 2)
    o1, c1 = o.shift(1), c.shift(1)
    bull_eng = (c1 < o1) & (c > o) & (c > o1) & (o < c1)
    bear_eng = (c1 > o1) & (c < o) & (c < o1) & (o > c1)
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (bull_pin | bull_eng) & (ef > es) & (c > es)
    se = (bear_pin | bear_eng) & ~(ef > es) & (c < es)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
