"""Stochastic momentum index extremes, 1-minute bars: an SMI (5, 3) under -45 goes long, over 45 goes short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439266 "基于Stochastic-Index指标的短线交易策略Short-term-Trading-Strategy-Based-on-Stochastic-Index" (SMIndex Strategy).

FMZ source id: 439266

Source
    https://www.fmz.com/strategy/439266 (PineScript v2, FMZ last modified 2024-01-18 16:14:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-170), sm1 5, sm2 3; level inputs 55 / 35 / -55 / -35 (unused)
    smi = ema(ema(close - (highest + lowest) / 2, 3), 3) / (ema(ema(highest - lowest, 3), 3) / 2) x 100 (0 when the range average is 0)
    longEntry = smi < -75 or < -65 or < -55 or < -45  (= smi < -45);  shortEntry = smi > 45;  entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The OR chains reduce to smi < -45 and smi > 45; the level inputs are never read. A same-side
      entry while in the position is ignored (pyramiding 0). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMI levels.
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

NAME = "fmz_439266_smi_45_extremes_state"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sm1": [5, 10],
    "level": [45.0, 60.0],
}
DEFAULT_PARAMS = {"sm1": 5, "level": 45.0, "sm2": 3}


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
    n, k = int(p["sm1"]), int(p["sm2"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()

    def dema(x):
        return x.ewm(span=k, adjust=False).mean().ewm(span=k, adjust=False).mean()

    e1, e2 = dema(c - (hh + ll) / 2), dema(hh - ll)
    with np.errstate(divide="ignore", invalid="ignore"):
        smi = (e1 / (e2 / 2) * 100).where(e2 != 0, 0.0)
    smi = smi.where(e1.notna() & e2.notna())
    lvl = float(p["level"])
    false = pd.Series(False, index=c.index)
    return smi < -lvl, false, smi > lvl, false.copy()


def portfolio_kwargs(**params):
    return {}
