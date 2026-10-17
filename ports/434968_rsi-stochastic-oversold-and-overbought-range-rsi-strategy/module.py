"""RSI 6 multi-level crosses, broker days, long only: the RSI 6 crossing above any of 5, 7, 8, 9, 10, 15, 20, 25 or 30 goes
long; crossing below any of 70, 75, 80, 85, 90, 95 or 99 closes the long.
Port of FMZ strategy #434968 "随机超买超卖区间RSI策略Stochastic-Oversold-and-Overbought-Range-RSI-Strategy" (imrich).

FMZ source id: 434968

Source
    https://www.fmz.com/strategy/434968 (PineScript v3, FMZ last modified 2023-12-11 13:19:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-272), RSI 6 on close; oversold levels 5 / 7 / 8 / 9 / 10 / 15 / 20 / 25 / 30, overbought 70 / 75 / 80 / 85 / 90 / 95 / 99
    long = crossover(rsi, any oversold level) -> entry long (else cancel the pending entry);  close_long = crossunder(rsi, any overbought level) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.cancel only withdraws an entry order not yet filled; with bar-close orders it has no
      effect. Wilder RSI. Long only; an entry while long is ignored. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434968_rsi6_multi_level_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [6, 14],
}
DEFAULT_PARAMS = {"rsi_len": 6}

OVERSOLD = (5, 10, 15, 20, 25, 30, 7, 8, 9)
OVERBOUGHT = (70, 75, 80, 85, 90, 95, 99)


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
    le = pd.Series(False, index=c.index)
    lx = pd.Series(False, index=c.index)
    for lv in OVERSOLD:
        le = le | ((rsi > lv) & (r1 <= lv))
    for lv in OVERBOUGHT:
        lx = lx | ((rsi < lv) & (r1 >= lv))
    false = pd.Series(False, index=c.index)
    return le.astype(bool), (lx & ~le).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
