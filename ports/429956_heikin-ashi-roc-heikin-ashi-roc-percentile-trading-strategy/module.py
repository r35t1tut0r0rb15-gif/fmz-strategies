"""Heikin Ashi ROC against percentile kill lines, hourly bars: the 100-bar ROC of the SMA 100 of the HA close crossing
above the lower kill line goes long (and closes a short); crossing below the upper kill line goes short (and closes
a long).
Port of FMZ strategy #429956 "基于Heikin-Ashi-ROC百分位数的交易策略Heikin-Ashi-ROC-Percentile-Trading-Strategy" (Heikin Ashi ROC Percentile Strategy).

FMZ source id: 429956

Source
    https://www.fmz.com/strategy/429956 (PineScript v5, FMZ last modified 2023-10-23 15:41:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 100-134), ROC length 100, highest / lowest ROC 50, percentiles 75 / 25 over 10 bars
    roc = roc(sma(haClose, 100), 100); rocHigh / rocLow = highest / lowest(roc, 50)
    upper = percentile_linear_interpolation(rocHigh, 10, 75); lower = the same of rocLow at 25
    crossover(roc, lower) -> entry long, close short; crossunder(roc, upper) -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * haClose = ohlc4. The percentile uses linear interpolation between the closest ranks of the last 10
      values (numpy's linear method; stated reading of TradingView's definition).
    * The stop-loss input is never used. The start date (2015) is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rates of change and their percentiles.
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

NAME = "fmz_429956_ha_roc_percentile"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "roc_length": [100, 50],
    "hl_len": [50, 25],
}
DEFAULT_PARAMS = {"roc_length": 100, "hl_len": 50, "pct_len": 10, "upper_pct": 75, "lower_pct": 25}


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
    ha = (o + h + lo + c) / 4
    n = int(p["roc_length"])
    s = ha.rolling(n).mean()
    roc = 100 * (s - s.shift(n)) / s.shift(n)
    k = int(p["hl_len"])
    rh, rl = roc.rolling(k).max(), roc.rolling(k).min()
    pl = int(p["pct_len"])
    up = rh.rolling(pl).apply(lambda v: np.percentile(v, p["upper_pct"]), raw=True)
    dn = rl.rolling(pl).apply(lambda v: np.percentile(v, p["lower_pct"]), raw=True)
    long_e = ((roc > dn) & (roc.shift(1) <= dn.shift(1))).astype(bool)
    short_e = ((roc < up) & (roc.shift(1) >= up.shift(1)) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
