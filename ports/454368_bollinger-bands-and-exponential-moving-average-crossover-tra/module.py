"""Bars opening beyond a Bollinger band (20 / 2) that close back across the EMA 5, 1-hour bars: an open under the lower band with a close over the EMA 5 goes long, an open over the upper band with a close under the EMA 5 goes short; reversing.
Port of FMZ strategy #454368 "Bollinger Bands and Exponential Moving Average Crossover Trading Strategy" (Bollinger Bands and EMA Strategy (open beyond the band, close back over the EMA 5)).

FMZ source id: 454368

Source
    https://www.fmz.com/strategy/454368 (PineScript v5, FMZ last modified 2024-06-17 16:58:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-196), Bollinger 20 / 2; EMA 5; trade_direction flag
    open > upper and close < ema5 and direction != short -> entry Short;  open < lower and close > ema5 and direction != long -> entry Long
    (the later close-and-reverse blocks test the direction already updated on the bar and never act)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The direction flag only skips a repeat entry on the held side (which Pine would ignore anyway);
      the later 'close and reverse' and 'close on the opposite signal' blocks test the flag after the
      entry blocks have already updated it on the same bar, so they never act: every signal is a plain
      entry, reversing. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-open reversal bars with an EMA 5 close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454368_open_beyond_band_close_back_ema5_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
    "ema_len": [5, 9],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "ema_len": 5}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    se = (o > basis + dev) & (c < ema)
    le = (o < basis - dev) & (c > ema)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
