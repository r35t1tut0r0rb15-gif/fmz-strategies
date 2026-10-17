"""EMA 10 / 20 bullish crosses on a green candle with the stop at that candle's low, long only, 1-hour bars: EMA 10
crossing above EMA 20 on a green bar goes long; the only exit is a stop at the signal bar's low.
Port of FMZ strategy #488014 "动态仓位与入场K线止损的EMA交叉策略-Dynamic-Position-Sizing-and-Entry-Candle-Stop-Loss-EMA-Crossover-Strategy" (EMA Crossover with Tiny Triangle Signal & Dynamic Quantity).

FMZ source id: 488014

Source
    https://www.fmz.com/strategy/488014 (PineScript v6, FMZ last modified 2025-03-24 14:04:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 168-197), EMA 10 / 20
    long = crossover(ema10, ema20) and close > open -> entryCandleLow = low, qty = 1000 / (close - low)
    entry long (qty) + exit(stop = entryCandleLow)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the signal bar's low: sl_stop = (close - low) / close of the signal bar, shifted one bar inside
      stops() and re-based on the fill (house rule). A later signal while held moves the stop to the new low: mark
      trailing_stop_pending; the port keeps the entry's stop.
    * The risk-based quantity is sizing (quoted). Long only: opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop from the signal bar (moves marked).
    2 generic: PASS, EMAs and the signal bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1000 / (close - low) quantity quoted; the stop ported via stops() and quoted in
      original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488014_ema10_20_cross_candle_low_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 5],
    "slow": [20, 30],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > o)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    c = bars_df["close"]
    return {"sl_stop": ((c - bars_df["low"]) / c).shift(1)}


def portfolio_kwargs(**params):
    return {}
