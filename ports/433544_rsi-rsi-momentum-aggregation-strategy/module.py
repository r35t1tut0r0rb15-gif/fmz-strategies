"""RSI 14 level crosses, 1-hour bars: the RSI crossing above 30 goes long, crossing under 70 goes short; always in after the
first signal.
Port of FMZ strategy #433544 "动量策略的RSI指标聚合RSI-Momentum-Aggregation-Strategy" (Crypto Buy & Sell Strategy (Pine Script v5)).

FMZ source id: 433544

Source
    https://www.fmz.com/strategy/433544 (PineScript v5, FMZ last modified 2023-12-01 15:01:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 166-187), RSI 14, oversold 30, overbought 70
    crossover(rsi, 30) -> entry long;  crossunder(rsi, 70) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same rule as #433398 on another bar size (1h here). strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
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

NAME = "fmz_433544_rsi_30_70_cross_1h"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 30}


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
    ch = c.diff()
    n = int(p["length"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    lo_l, hi_l = float(p["oversold"]), 100 - float(p["oversold"])
    le = ((r > lo_l) & (r.shift(1) <= lo_l)).astype(bool)
    se = ((r < hi_l) & (r.shift(1) >= hi_l)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
