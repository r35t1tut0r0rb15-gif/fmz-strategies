"""Full-body candles beyond the EMA 9 and EMA 15, 2-hour bars: a bullish candle whose body is at least 75 % of its range closing over both EMAs goes long, the bearish mirror goes short; reversing.
Port of FMZ strategy #472974 "Dual EMA Momentum Trend Trading Strategy with Full Body Candle Signal System" (9 & 15 EMA with Full Body Candle Strategy).

FMZ source id: 472974

Source
    https://www.fmz.com/strategy/472974 (PineScript v5, FMZ last modified 2024-11-25 17:30:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-135), EMA 9 / 15; full body = body >= 75 % of the range
    bullish full body and close > ema9 and close > ema15 -> entry Buy (and close Sell);  bearish mirror -> entry Sell (and close Buy)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come with the reversing entries (#437773). There is no other exit. REVERSAL INTENDED.
      No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, full-body candles beyond two EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_472974_full_body_candle_beyond_ema9_15_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_frac": [0.75, 0.6],
    "ema_slow": [15, 50],
}
DEFAULT_PARAMS = {"body_frac": 0.75, "ema_slow": 15}


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
    e9 = c.ewm(span=9, adjust=False).mean()
    e15 = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    k = float(p["body_frac"])
    bull = (c > o) & (c - o >= (h - lo) * k)
    bear = (c < o) & (o - c >= (h - lo) * k)
    le = bull & (c > e9) & (c > e15)
    se = bear & (c < e9) & (c < e15)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
