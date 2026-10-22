"""Aroon 15 crossings confirmed by the LSMA 20, long only, broker days: Aroon up crossing over Aroon down with the close above the 20-bar least-squares line goes long; the reverse cross with the close under it
closes.
Port of FMZ strategy #439696 "A Dual Moving Average Confirmation Advantage Line Strategy" (Aroon Strategy long only).

FMZ source id: 439696

Source
    https://www.fmz.com/strategy/439696 (PineScript v4, FMZ last modified 2024-01-23 10:49:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-165), Aroon 15; LSMA 20 of close, offset 0; date window true
    upper = 100 (highestbars(high, 16) + 15) / 15;  lower = 100 (lowestbars(low, 16) + 15) / 15;  long = crossover(upper, lower) and close > linreg(close, 20, 0);  longexit = crossunder and close < lsma

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars / lowestbars give the offset of the newest extreme in the last 16 bars. The entry and
      the close cannot share a bar. Long only. The 100 % of equity size and commission are sizing. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Aroon crossings and a regression line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_439696_aroon_cross_lsma_confirm_long"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [15, 25],
    "lengthx": [20, 50],
}
DEFAULT_PARAMS = {"length": 15, "lengthx": 20}


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


def _linreg(y, n):
    """Pine's linreg(y, n, 0): the least-squares line over the last n bars, read at the newest bar."""
    k = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sky = (k * y).rolling(n).sum()
    x0 = k - (n - 1)                                   # x = k - x0 runs 0 .. n-1 inside the window
    sxy = sky - x0 * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    w = n + 1
    hb = -h.rolling(w).apply(lambda a: np.argmax(a[::-1]), raw=True)     # highestbars: offset of the newest high
    lb = -lo.rolling(w).apply(lambda a: np.argmin(a[::-1]), raw=True)
    up = 100 * (hb + n) / n
    dn = 100 * (lb + n) / n
    ls = _linreg(c, int(p["lengthx"]))
    le = (up > dn) & (up.shift(1) <= dn.shift(1)) & (c > ls)
    lx = (up < dn) & (up.shift(1) >= dn.shift(1)) & (c < ls)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
