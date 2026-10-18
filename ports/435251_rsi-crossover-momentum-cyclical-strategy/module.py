"""RSI 14 crosses, broker days, long only: RSI crossing above 60 goes long; RSI crossing below 80 closes the long.
Port of FMZ strategy #435251 "RSI Crossover Momentum Cyclical Strategy" (RSI Cross 60/80 Strategy).

FMZ source id: 435251

Source
    https://www.fmz.com/strategy/435251 (PineScript v5, FMZ last modified 2023-12-13 15:41:33).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 131-152), RSI 14; buy threshold 60, sell threshold 80
    crossover(rsi, 60) -> entry long;  crossunder(rsi, 80) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only: the sell cross only closes. A cross under 80 needs the RSI above 80 the bar
      before, so it exits a long that rose over 80 (or one opened while already high); the exit on
      a bar with no position does nothing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435251_rsi_60_80_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_th": [60, 55],
    "sell_th": [80, 70],
}
DEFAULT_PARAMS = {"rsi_len": 14, "buy_th": 60, "sell_th": 80}


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
    r1 = rsi.shift(1)
    buy, sell = float(p["buy_th"]), float(p["sell_th"])
    le = ((rsi > buy) & (r1 <= buy)).fillna(False).astype(bool)
    lx = ((rsi < sell) & (r1 >= sell)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
