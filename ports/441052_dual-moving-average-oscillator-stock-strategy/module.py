"""True Strength Index signal crossings, broker days, long only: the TSI (12, 9) crossing over its 12-bar EMA signal goes long, crossing under closes.
Port of FMZ strategy #441052 "Dual Moving Average Oscillator Stock Strategy" (TSI).

FMZ source id: 441052

Source
    https://www.fmz.com/strategy/441052 (PineScript v5, FMZ last modified 2024-02-05 10:47:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-177), TSI long 12, short 9, signal 12; initial capital and risk inputs (unused by the orders)
    tsi = 100 ema(ema(change(close), 12), 9) / ema(ema(abs(change(close)), 12), 9);  signal = ema(tsi, 12);  tsi crossing over signal -> entry Long;  crossing under -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * riskAmount is computed but never passed to an order, so the inputs are unused. Long only. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TSI signal crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (risk amount unused).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG441052 (2 members, best partner #441134, Jaccard 0.913); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441052_tsi_signal_cross_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_length": [12, 25],
    "short_length": [9, 13],
}
DEFAULT_PARAMS = {"long_length": 12, "short_length": 9, "signal_length": 12}


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
    c = bars_df["close"]
    pc = c.diff()
    lg, sh = int(p["long_length"]), int(p["short_length"])

    def ds(x):
        return x.ewm(span=lg, adjust=False).mean().ewm(span=sh, adjust=False).mean()

    den = ds(pc.abs())
    tsi = 100 * ds(pc) / den.where(den != 0)
    sig = tsi.ewm(span=int(p["signal_length"]), adjust=False).mean()
    up = (tsi > sig) & (tsi.shift(1) <= sig.shift(1))
    dn = (tsi < sig) & (tsi.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
