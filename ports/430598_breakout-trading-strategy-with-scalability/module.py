"""Swing-level breakouts (deperp), 1-hour bars: the close crossing above the last confirmed 20-bar swing high goes long,
crossing below the last swing low goes short; each position takes profit 5 % away (fixed at the fill; the source
re-sizes it from each bar's close).
Port of FMZ strategy #430598 "Breakout Trading Strategy with Scalability" (Range Breaker).

FMZ source id: 430598

Source
    https://www.fmz.com/strategy/430598 (PineScript v5, FMZ last modified 2023-10-30 17:25:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 164-234), swing look-back 20, target 5 %
    swingHigh := high[20] when high[20] > highest(20); swingLow := low[20] when low[20] < lowest(20)
    crossover(close, swingHigh) -> entry long;  crossunder(close, swingLow) -> entry short
    every bar: exit(limit = close x 1.05) for longs, (limit = close x 0.95) for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * A swing is confirmed 20 bars after it: high[20] above the highest high of the 20 bars since
      (bars 0-19), so only past bars are read.
    * The targets are re-issued every bar from the CURRENT close (moving levels): rule 2, mark
      trailing_stop_pending; the port fixes them at 5 % of the fill (tp_stop 0.05).
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      The date filter is unused (inTradeWindow = true). strategy.entry reverses: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving target fixed at the fill (rule 2).
    2 generic: PASS, swing levels and a percentage target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 10 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430598_swing_range_breaker"
FAMILY = "pivot_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing_lookback": [20, 10],
    "target_pct": [5.0, 2.5],
}
DEFAULT_PARAMS = {"swing_lookback": 20, "target_pct": 5.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _carry(cond, val):
    out = np.full(len(val), np.nan)
    last = np.nan
    for i in range(len(val)):
        if cond[i]:
            last = val[i]
        out[i] = last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["swing_lookback"])
    hn, ln = h.shift(n), lo.shift(n)
    sh = pd.Series(_carry((hn > h.rolling(n).max()).to_numpy(), hn.to_numpy()), index=c.index)
    sl = pd.Series(_carry((ln < lo.rolling(n).min()).to_numpy(), ln.to_numpy()), index=c.index)
    long_e = ((c > sh) & (c.shift(1) <= sh.shift(1))).astype(bool)
    short_e = ((c < sl) & (c.shift(1) >= sl.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["target_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
