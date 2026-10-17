"""Close crosses of the SMA 20 and SMA 60, broker days, long only: from flat, a close crossing above the SMA 20 opens the
"20" long, closed by a close crossing below the SMA 20; a close crossing above the SMA 60 opens the "60" long, closed by a
close crossing below the SMA 60. One position at a time, so the exit follows the entry that opened it.
Port of FMZ strategy #434701 "Moving Average Crossover Strategy" (Astor SMA20/60 TW).

FMZ source id: 434701

Source
    https://www.fmz.com/strategy/434701 (PineScript v5, FMZ last modified 2023-12-08 15:23:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-158), SMA 20 / 60; quantity 1 each; start 2018-01-01
    crossover(close, sma20) -> entry "open long20";  crossunder(close, sma20) -> close "open long20"
    crossover(close, sma60) -> entry "open long60";  crossunder(close, sma60) -> close "open long60"

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding is 1: while one entry is open the other is not taken, and each close names its own
      entry, so the port tracks which entry opened the trade (both crosses on one flat bar: the 20
      entry is issued first). An entry on the bar of an exit is not taken (the position is still
      open when the bar is calculated). The start date (2018) is the author's window: dropped.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exit follows the opening entry (tracked).
    2 generic: PASS, price against averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 1 stored.
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

NAME = "fmz_434701_sma20_sma60_close_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [60, 120],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 60}


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
    xo = lambda s: ((c > s) & (c.shift(1) <= s.shift(1))).to_numpy()  # noqa: E731
    xu = lambda s: ((c < s) & (c.shift(1) >= s.shift(1))).to_numpy()  # noqa: E731
    s1, s2 = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    o1, u1, o2, u2 = xo(s1), xu(s1), xo(s2), xu(s2)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    who = 0  # 0 flat, 1 the fast entry, 2 the slow entry
    for i in range(m):
        if who == 1 and u1[i]:
            lx[i], who = True, 0
        elif who == 2 and u2[i]:
            lx[i], who = True, 0
        elif who == 0 and o1[i]:
            le[i], who = True, 1
        elif who == 0 and o2[i]:
            le[i], who = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
