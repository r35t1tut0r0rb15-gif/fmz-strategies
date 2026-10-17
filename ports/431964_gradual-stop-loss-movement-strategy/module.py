"""SMA 14 / 28 cross-ups with a stepped stop (ShanghaiCryto), 1-hour bars, long only: the SMA 14 crossing above the SMA 28
goes long with a stop 5 % under the entry; the source then steps the stop up by 5 % of the entry each time the 7-bar
low clears the next step.
Port of FMZ strategy #431964 "Gradual Stop Loss Movement Strategy" (Move Up Stops).

FMZ source id: 431964

Source
    https://www.fmz.com/strategy/431964 (PineScript v3, FMZ last modified 2023-11-13 17:30:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 132-182), SMA 14 / 28, steps 0.95 / 1.00 / 1.05 ... 1.30 of the entry, trigger lowest(low, 7)
    crossover(sma14, sma28) -> entry long
    stop = the highest step (0.95, 1.00, ..., 1.30 x avg price) that lowest(low, 7) is above (else 0.95 x avg) -> exit(stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stepped stop follows the 7-bar low, which also falls back, so the level moves both ways (not
      a best-price trail): rule 2, mark trailing_stop_pending; the port keeps the first step, a fixed
      5 % stop from the entry (sl_stop 0.05). Long only; Opposite entries cannot occur (a new cross
      while long adds nothing). Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stepped stop's first step fixed (rule 2).
    2 generic: PASS, SMA crosses and percentage steps.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_431964_sma_cross_stepped_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [14, 7],
    "first_step": [5.0, 2.5],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "first_step": 5.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["first_step"]) / 100}


def portfolio_kwargs(**params):
    return {}
