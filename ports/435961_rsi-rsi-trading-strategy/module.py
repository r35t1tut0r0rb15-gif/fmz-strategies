"""RSI 14 band crossings, broker days: the RSI crossing over 30 goes long (closing a short); crossing under 70 goes short (closing a long),
so the position reverses.
Port of FMZ strategy #435961 "基于相对强弱指标RSI交易策略RSI-Trading-Strategy" (Estrategia RSI para BTC/USDT).

FMZ source id: 435961

Source
    https://www.fmz.com/strategy/435961 (PineScript v4, FMZ last modified 2023-12-20 14:20:26).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 143-175), RSI 14; levels 30 / 70
    long_signal = crossover(rsi, 30) -> entry long, close short;  short_signal = crossunder(rsi, 70) -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The explicit closes coincide with the reversal. The capital variable is bookkeeping (sizing). REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the initial capital input stored.
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

NAME = "fmz_435961_rsi_30_70_cross_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"length": 14, "oversold": 30}


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
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    lo_lv = float(p["oversold"])
    hi_lv = 100.0 - lo_lv
    r1 = rsi.shift(1)
    le = ((rsi > lo_lv) & (r1 <= lo_lv)).fillna(False).astype(bool)
    se = ((rsi < hi_lv) & (r1 >= hi_lv)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
