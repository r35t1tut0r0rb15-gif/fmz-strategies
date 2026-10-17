"""RSI 14 trend crosses, broker days, long only: the RSI crossing above 35 goes long, crossing below 75 closes it.
Port of FMZ strategy #435146 "RSI趋势追踪型加密货币策略RSI-Trend-Following-Crypto-Strategy" (RSI Trend Crypto).

FMZ source id: 435146

Source
    https://www.fmz.com/strategy/435146 (PineScript v4, FMZ last modified 2023-12-12 16:26:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 148-185), RSI 14; long cross 35, close cross 75; emergency exit (cross under 10) off
    crossover(rsi, 35) -> entry long;  crossunder(rsi, 75) -> close long;  crossunder(rsi, 10) and emergency on -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The emergency exit is off by default (not ported). Wilder RSI. Long only; an entry while long
      is ignored. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435146_rsi_35_75_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_long": [35, 50],
    "rsi_close": [75, 65],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_long": 35, "rsi_close": 75}


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
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    a, b = float(p["rsi_long"]), float(p["rsi_close"])
    le = ((rsi > a) & (rsi.shift(1) <= a)).astype(bool)
    lx = ((rsi < b) & (rsi.shift(1) >= b)).astype(bool) & ~le
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
