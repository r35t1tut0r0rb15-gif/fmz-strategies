"""Fading momentum loss on the MACD histogram with a larger candle, always in the market, 1-hour bars: a green candle
larger than the previous one while the histogram has fallen two bars in a row goes short; a red larger candle while it
has risen two bars in a row goes long.
Port of FMZ strategy #483020 "动量背离趋势反转量化策略基于MACD柱状图-Momentum-Divergence-Trend-Reversal-Quantitative-Strategy-Based-on-MACD-Histogram" (MACD Momentum Reversal Strategy).

FMZ source id: 483020

Source
    https://www.fmz.com/strategy/483020 (PineScript v5, FMZ last modified 2025-02-21 09:25:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-150), MACD 12 / 26 / 9
    enterShort = close > open and |body| > |previous body| and hist[2] > hist[1] > hist
    enterLong = close < open and |body| > |previous body| and hist[2] < hist[1] < hist
    entries reverse; the closes on the opposite signal are redundant

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries reverse (REVERSAL INTENDED); a long and a short cannot meet on one bar (candle colour). No stops.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram and candle bodies.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_483020_macd_hist_fade_big_candle_reversal"
FAMILY = "macd"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    o, c = bars_df["open"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    body = (c - o).abs()
    bigger = body > body.shift(1)
    falling = (hist.shift(2) > hist.shift(1)) & (hist.shift(1) > hist)
    rising = (hist.shift(2) < hist.shift(1)) & (hist.shift(1) < hist)
    short_e = ((c > o) & bigger & falling).astype(bool)
    long_e = ((c < o) & bigger & rising).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
