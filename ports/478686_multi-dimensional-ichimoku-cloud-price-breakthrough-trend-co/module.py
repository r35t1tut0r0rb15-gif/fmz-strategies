"""Close crossings of the base line and leading span A together (SMA-based Ichimoku of hl2, 9 / 26 / 52), 10-minute bars, long only: crossing over both with the close above the conversion line buys, crossing under both below it closes.
Port of FMZ strategy #478686 "Multi Dimensional Ichimoku Cloud Price Breakthrough Trend Confirmation Trading Strategy" (Ichimoku Cloud Buy Strategy (Non-Repainting)).

FMZ source id: 478686

Source
    https://www.fmz.com/strategy/478686 (PineScript v5, FMZ last modified 2025-01-17 14:21:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-145), conversion / base / span B = SMA 9 / 26 / 52 of hl2; span A = their average (undisplaced in the tests)
    crossover(close, base) and crossover(close, spanA) and close > conv -> entry Buy;  crossunder(close, base) and crossunder(close, spanA) and close < conv -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are simple moving averages of hl2, as written (not Donchian midpoints), and the tests read
      span A at the current bar; the displaced copies only plot. The bar_index test always holds. Long
      only. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku-style line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478686_sma_ichimoku_base_spanA_cross_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 20],
    "base": [26, 60],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    conv = hl2.rolling(int(p["conversion"])).mean()
    base = hl2.rolling(int(p["base"])).mean()
    span_a = (conv + base) / 2

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    le = xo(c, base) & xo(c, span_a) & (c > conv)
    lx = xo(base, c) & xo(span_a, c) & (c < conv)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
