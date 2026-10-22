"""Vortex indicator (14, SMA-smoothed) crossings, broker days: VI+ crossing over VI- goes long, crossing under goes short; reversing.
Port of FMZ strategy #481351 "Advanced Vortex Momentum Analysis and Trading Strategy" (Vortex Strategy with Signals).

FMZ source id: 481351

Source
    https://www.fmz.com/strategy/481351 (PineScript v5, FMZ last modified 2025-02-10 14:38:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-156), period 14; VM and TR smoothed with SMAs
    vi+ = sma(|high - low[1]|, 14) / sma(tr, 14);  vi- = sma(|low - high[1]|, 14) / sma(tr, 14);  crossover(vi+, vi-) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script smooths with SMAs (the classic Vortex uses sums; the ratio is the same). REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Vortex crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481351_vortex14_cross_reversal"
FAMILY = "vortex"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21, 7],
}
DEFAULT_PARAMS = {"length": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    vmp = (h - lo.shift(1)).abs().rolling(n).mean()
    vmm = (lo - h.shift(1)).abs().rolling(n).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False).rolling(n).mean()
    vip, vim = vmp / tr, vmm / tr
    le = (vip > vim) & (vip.shift(1) <= vim.shift(1))
    se = (vip < vim) & (vip.shift(1) >= vim.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
