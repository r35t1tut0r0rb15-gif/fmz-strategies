"""Two-sd Bollinger (20) breakouts, daily bars: the close crossing over the upper band goes long, crossing under the lower band goes short; the close crossing back through the SMA closes; reversing.
Port of FMZ strategy #449965 "Bollinger-Bands-Breakout-Strategy-布林带突破策略" (BB Strategy (Bollinger Bands Strategy, 2-sd breakout)).

FMZ source id: 449965

Source
    https://www.fmz.com/strategy/449965 (PineScript v5, FMZ last modified 2024-04-30 17:21:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-131), SMA 20; bands 2 sd
    crossover(close, upper) -> entry Long;  crossunder(close, lower) -> entry Short;  crossunder(close, basis) -> close Long;  crossover(close, basis) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules of #449961 with two-sd bands on daily bars. The closes come after the entries: a
      close after a reversing entry on the same bar leaves the reversal. Pine's stdev is the population
      deviation. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts with basis exits.
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

NAME = "fmz_449965_two_sd_band_breakout_basis_exit_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper = basis + float(p["mult"]) * sd
    lower = basis - float(p["mult"]) * sd
    c1 = c.shift(1)
    le = (c > upper) & (c1 <= upper.shift(1))
    se = (c < lower) & (c1 >= lower.shift(1))
    xb_dn = (c < basis) & (c1 >= basis.shift(1))
    xb_up = (c > basis) & (c1 <= basis.shift(1))
    return le, xb_dn & ~se, se, xb_up & ~le


def portfolio_kwargs(**params):
    return {}
