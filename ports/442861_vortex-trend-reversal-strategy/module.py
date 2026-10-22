"""A "vortex" of the EMA 14 of the close's distance from its SMA 14 against the EMA 14 of absolute changes, 1-hour bars, directions inverted as written: the first line crossing over the second with the
close above its EMA 20 goes short, crossing under with the close below goes long; reversing.
Port of FMZ strategy #442861 "Vortex Trend Reversal Strategy" (Vortex Strategy [AstroHub] (VS)).

FMZ source id: 442861

Source
    https://www.fmz.com/strategy/442861 (PineScript v5, FMZ last modified 2024-02-26 16:45:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-164), length 14; multiplier 1 and threshold 0.5 (unused); EMA 20
    shl = ema(close - sma(close, 14), 14);  svl = ema(abs(close - close[1]), 14);  buy = crossover(shl, svl) and close > ema20;  sell = crossunder(shl, svl) and close < ema20
    buySignal -> entry "Sell" (short);  sellSignal -> entry "Buy" (long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "buy" signal enters the short id and the "sell" signal the long id, as written (as #442641).
      The trend-change tests are implied by the crossings. The multiplier and threshold inputs are
      unused. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed deviation vs smoothed change crossings (directions as written).
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

NAME = "fmz_442861_deviation_vs_change_cross_inverted_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 30],
    "ema_length": [20, 50],
}
DEFAULT_PARAMS = {"length": 14, "ema_length": 20}


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
    n = int(p["length"])
    shl = (c - c.rolling(n).mean()).ewm(span=n, adjust=False).mean()
    svl = (c - c.shift(1)).abs().ewm(span=n, adjust=False).mean()
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    buy = (shl > svl) & (shl.shift(1) <= svl.shift(1)) & (c > e)
    sell = (shl < svl) & (shl.shift(1) >= svl.shift(1)) & (c < e)
    false = pd.Series(False, index=c.index)
    return sell, false, buy, false.copy()


def portfolio_kwargs(**params):
    return {}
