"""EMA 3 / 30 difference outside a small dead band, 1-hour bars: the EMA 3 above the EMA 30 by more than the threshold goes long, below it by more than the threshold goes short; reversing; inside the band the
position is held.
Port of FMZ strategy #437794 "短期长期EMA决策合并策略Merged-Short-Term-and-Long-Term-EMA-Decision-Strategy" (MergedEMA).

FMZ source id: 437794

Source
    https://www.fmz.com/strategy/437794 (PineScript v5, FMZ last modified 2024-01-05 16:07:58).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 124-151), EMA 3 / 30; thresholds +0.0005 / -0.0005 (price units)
    diff = ema 3 - ema 30;  diff > 0.0005 -> entry Buy, close Sell;  diff < -0.0005 -> entry Sell, close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the threshold 0.0005 is in price units; the port uses thr_frac x close: 1.2e-08 is the
      reading (0.0005 on BTC near 42000: practically zero), 0.001 a real dead band. The closes of the
      opposite side and the reversing entries give the same position: REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit threshold -> fraction of the close.
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

NAME = "fmz_437794_ema3_30_difference_band"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "thr_frac": [1.2e-08, 0.001],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"thr_frac": 1.2e-08, "slow": 30, "fast": 3}


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
    diff = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    thr = float(p["thr_frac"]) * c
    false = pd.Series(False, index=bars_df.index)
    return diff > thr, false, diff < -thr, false.copy()


def portfolio_kwargs(**params):
    return {}
