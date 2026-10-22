"""Close crossings out of the Bollinger 20 / 2 bands, 3-hour bars: over the upper band goes long, under the lower band goes short, each with a 5 % target and a 2 % stop from the fill; reversing.
Port of FMZ strategy #488541 "Dynamic Bollinger Bands Breakout Trend Tracking Strategy" (Bollinger Bands Breakout Strategy).

FMZ source id: 488541

Source
    https://www.fmz.com/strategy/488541 (PineScript v6, FMZ last modified 2025-03-28 17:24:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-157), BB 20 / 2; TP 5 %, SL 2 % of the average price
    crossover(close, upper) -> entry Long;  crossunder(close, lower) -> entry Short
    every bar: exit(limit = avg x 1.05, stop = avg x 0.98) for Long;  mirror for Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The brackets are re-sent every bar from strategy.position_avg_price, which is na on the flat signal
      bar and the fill price after it, so they are fixed percents of the fill, active from the fill bar (as
      #440797). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No sizing code. FREQ = "3h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, Bollinger breakouts with a percent bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488541_bb20_2_breakout_tp5_sl2_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "takeProfitPerc": [5.0, 3.0],
    "stopLossPerc": [2.0, 1.0],
}
DEFAULT_PARAMS = {"takeProfitPerc": 5.0, "stopLossPerc": 2.0, "length": 20, "mult": 2.0}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    le = (c > upper) & (c.shift(1) <= upper.shift(1))
    se = (c < lower) & (c.shift(1) >= lower.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stopLossPerc"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["takeProfitPerc"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
