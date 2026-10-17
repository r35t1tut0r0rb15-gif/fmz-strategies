"""RSI 14 level crosses, broker days: the RSI crossing above 30 goes long, the RSI crossing under 70 goes short; always in
after the first signal.
Port of FMZ strategy #433398 "Relative Strength Index Flat Reversal Strategy" (RSI OverTrend Strategy (by Marcoweb) v1.0).

FMZ source id: 433398

Source
    https://www.fmz.com/strategy/433398 (PineScript v2, FMZ last modified 2023-11-27 11:25:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 146-175), RSI 14, trigger 30, overbought 70
    crossover(rsi, 30) -> entry long (else cancel);  crossunder(rsi, 70) -> entry short (else cancel)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cancel calls only withdraw unfilled orders. The unused buyEntry / sellEntry compare the
      price with 30 and drive nothing. strategy.entry reverses: REVERSAL INTENDED. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433398_rsi_30_70_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "levels": [30, 20],
}
DEFAULT_PARAMS = {"length": 14, "levels": 30}


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
    ch = c.diff()
    n = int(p["length"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    lo_l, hi_l = float(p["levels"]), 100 - float(p["levels"])
    le = ((r > lo_l) & (r.shift(1) <= lo_l)).astype(bool)
    se = ((r < hi_l) & (r.shift(1) >= hi_l)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
