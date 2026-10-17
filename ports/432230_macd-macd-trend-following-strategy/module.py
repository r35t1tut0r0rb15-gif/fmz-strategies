"""Noro's MACD histogram trend, long only, broker days: the MACD histogram (12 / 26 / 9) crossing above zero sets the
trend up and goes long; crossing below zero sets it down and closes the long (the short side is switched off).
Port of FMZ strategy #432230 "MACD-趋势跟随策略MACD-Trend-Following-Strategy" (Noro's MACD Strategy v1.0).

FMZ source id: 432230

Source
    https://www.fmz.com/strategy/432230 (PineScript v2, FMZ last modified 2023-11-15 17:08:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 177-202), MACD 12 / 26 / 9, long on, short off, EMA filter off
    trend = crossover(delta, 0) ? 1 : crossunder(delta, 0) ? -1 : trend[1]
    trend == 1 -> entry long;  trend == -1 -> entry short with qty 0 (needshort false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * needshort = false gives the short entry a quantity of 0: it only closes the long (Noro's idiom,
      as earlier ports), so the port is long only and flat in a down trend. The EMA filter is off
      (usefil false). Opposite entries cannot occur.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the qty-0 short stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432230_noro_macd_trend_long"
FAMILY = "macd_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 17],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    up = ((delta > 0) & (delta.shift(1) <= 0)).to_numpy()
    dn = ((delta < 0) & (delta.shift(1) >= 0)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    trend = 0
    for i in range(m):
        if up[i]:
            trend = 1
        elif dn[i]:
            trend = -1
        tgt[i] = 1 if trend == 1 else 0
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, false, false.copy()))


def portfolio_kwargs(**params):
    return {}
