"""A bullish hammer (small body in the top of the range, a lower shadow at least twice the body) with both MACD lines at or below zero and rising volume, 3-hour bars, long only: the hammer buys; both MACD lines above zero close.
Port of FMZ strategy #427138 "Starbucks Bullish Hammer Trading Strategy" (Starbux).

FMZ source id: 427138

Source
    https://www.fmz.com/strategy/427138 (PineScript v4, FMZ last modified 2023-09-18 15:48:15).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 105-166), hammer: body <= 0.33 range, up bar, lower shadow >= 2 bodies, upper shadow <= 0.1 range; MACD 12 / 26 / 9; volume > volume[1]; max position 10
    blh and macdLine <= 0 and signalLine <= 0 and volume > volume[1] -> strategy.order("Buy", long, 1)  (up to max_position_size 10)
    macdLine > 0 and signalLine > 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order adds one unit per signal up to a 10-unit position: the adds are sizing, the port
      holds one position (as the pyramiding reading). The RSI, SMA 50 / 200 and the crossunder "stop" are
      computed but unused. Long only. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, hammer candles in a below-zero MACD with rising volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1-unit orders and max_position_size 10 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427138_bullish_hammer_macd_below_zero_volume_up_long"
FAMILY = "candle_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "shadow_mult": [2.0, 1.5],
    "body_frac": [0.33, 0.25],
}
DEFAULT_PARAMS = {"shadow_mult": 2.0, "body_frac": 0.33}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    abody, arange = (c - o).abs(), (h - lo).abs()
    top, bottom = np.maximum(o, c), np.minimum(o, c)
    blh = ((arange * float(p["body_frac"]) >= abody) & (c > o) & ((bottom - lo) >= abody * float(p["shadow_mult"]))
           & ((h - top) <= arange * 0.1))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = blh & (macd <= 0) & (sig <= 0) & (v > v.shift(1))
    lx = (macd > 0) & (sig > 0)
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
