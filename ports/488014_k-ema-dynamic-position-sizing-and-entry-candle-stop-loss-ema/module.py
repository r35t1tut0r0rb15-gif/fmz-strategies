"""EMA 10 / 20 up-crossings on a rising candle, hourly bars, long only, with a stop at the signal candle's low and no other exit.
Port of FMZ strategy #488014 "动态仓位与入场K线止损的EMA交叉策略-Dynamic-Position-Sizing-and-Entry-Candle-Stop-Loss-EMA-Crossover-Strategy" (EMA Crossover with Tiny Triangle Signal & Dynamic Quantity).

FMZ source id: 488014

Source
    https://www.fmz.com/strategy/488014 (PineScript v6, FMZ last modified 2025-03-24 14:04:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-197), EMA 10 / 20; quantity 1000 / (close - low)
    crossover(ema10, ema20) and close > open -> entry Buy (qty = 1000 / (close - low)) + exit(stop = low)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the signal bar's low, sent as a fraction of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256). A later up-crossing while held re-sends the stop at
      its new low; the port keeps the opening stop, mark trailing_stop_pending (as #434428). Long only.
      Stop module: portfolio_kwargs {} (driver D4). The risk-sized quantity is sizing. MPL 2.0 source
      (the notice is kept: Mozilla Public License 2.0, © nadeemred19). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar low stop as a fraction of the fill.
    2 generic: PASS, EMA crossings with a candle-low stop.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488014_ema10_20_cross_bull_candle_low_stop_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 5],
    "slow": [20, 50],
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


def _signals(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > o)
    return le, lo


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, sl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    false = pd.Series(False, index=o.index)
    return le, lf & (sl.shift(1) >= o) & ~le, false, false.copy()    # marketable at the fill


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, sl = _signals(bars_df, p)
    f = 1 - sl.shift(1) / bars_df["open"]
    return {"sl_stop": f.where(f > 0)}


def portfolio_kwargs(**params):
    return {}
