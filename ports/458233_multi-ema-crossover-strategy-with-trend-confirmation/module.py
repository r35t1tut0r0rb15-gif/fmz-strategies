"""EMA 8 / 21 crossings above the EMA 200, daily bars, long only: the cross up with the EMA 8, 21 and 50 all over the EMA 200 buys; the cross down sells.
Port of FMZ strategy #458233 "Multi EMA Crossover Strategy with Trend Confirmation" (Multi EMA Strategy with Alerts).

FMZ source id: 458233

Source
    https://www.fmz.com/strategy/458233 (PineScript v5, FMZ last modified 2024-07-31 11:08:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-203), EMA 8 / 21 / 50 / 200; barstate.isconfirmed
    crossover(ema8, ema21) and confirmed and ema8, ema21, ema50 > ema200 -> entry Buy;  crossunder(ema8, ema21) and confirmed -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * barstate.isconfirmed holds on every historical bar. Long only. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings above a long EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458233_ema8_21_cross_above_ema200_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 5],
    "slow": [21, 34],
    "trend": [200, 100],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 21, "trend": 200, "mid": 50}


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
    a, b, mid, t = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "slow", "mid", "trend"))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (a > t) & (b > t) & (mid > t)
    lx = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
