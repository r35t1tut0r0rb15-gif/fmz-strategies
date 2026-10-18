"""Hull moving average slope, broker days, long only: a Hull average (55) above its value two bars back buys; below it, the "Pause" short order is not allowed (long-only
mode), so it closes the long.
Port of FMZ strategy #436100 "Trend Trading Strategy Based on Dynamic Moving Average" (Position Investing by SirSeff).

FMZ source id: 436100

Source
    https://www.fmz.com/strategy/436100 (PineScript v5, FMZ last modified 2023-12-21 11:33:50).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 185-231), Hull variation Hma, length 55; strategy direction input long
    HULL = Hma(close, 55) (or Ehma / Thma);  HULL[0] > HULL[2] -> entry "Invest" (long);  HULL[0] < HULL[2] -> entry "Pause" (short)   with strategy.risk.allow_entry_in(long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.risk.allow_entry_in(long) forbids short entries: an entry in the forbidden direction
      while a long is open only closes it. The port follows that reading: the falling Hull closes the long, no
      short opens. The date window is the default (always true). The three Hull variants are in the grid.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull average slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and slippage stored.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND365727 (2 members, best partner #365727, Jaccard 0.652); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436100_hull_slope_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 100],
    "mode": ["Hma", "Ehma", "Thma"],
}
DEFAULT_PARAMS = {"length": 55, "mode": "Hma"}


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


def _wma(s, n):
    n = max(int(n), 1)
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def _ema(s, n):
    return s.ewm(span=max(int(n), 1), adjust=False).mean()


def _hull(src, n, mode):
    r = int(round(np.sqrt(n)))
    if mode == "Hma":
        return _wma(2 * _wma(src, n // 2) - _wma(src, n), r)
    if mode == "Ehma":
        return _ema(2 * _ema(src, n // 2) - _ema(src, n), r)
    k = n // 2                                            # Thma(src, len / 2)
    return _wma(_wma(src, k // 3) * 3 - _wma(src, k // 2) - _wma(src, k), k)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    hull = _hull(c, int(p["length"]), p["mode"])
    le = (hull > hull.shift(2)).fillna(False).astype(bool)
    lx = (hull < hull.shift(2)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
