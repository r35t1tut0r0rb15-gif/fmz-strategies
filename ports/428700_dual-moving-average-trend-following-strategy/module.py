"""Two channel-midpoint trends, broker days: the close above both the 14- and 21-bar high/low midpoints for
two bars in a row (each) goes long, below both for two bars goes short.
Port of FMZ strategy #428700 "Dual Moving Average Trend Following Strategy" (UniDir Strategy).

FMZ source id: 428700

Source
    https://www.fmz.com/strategy/428700 (PineScript v2, FMZ last modified 2023-10-08 14:25:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 188-224), p1 14, p2 21
    mid = (highest(high,p) + lowest(low,p)) / 2; up = close > mid; down = close < mid
    trend = sma(up,2) == 1 ? 1 : sma(down,2) == 1 ? -1 : trend[1]   (for p1 and p2)
    trend == 1 and trend_2 == 1 -> entry long; both -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest / lowest include the current bar. sma(up, 2) == 1 means this bar and the previous one.
    * strategy.entry reverses: REVERSAL INTENDED; while in a position a same-direction entry is
      ignored (pyramiding 0).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price vs channel midpoints only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() capital, cash quantity, slippage and commission stored.
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

NAME = "fmz_428700_two_midpoint_trends"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p1": [14, 10],
    "p2": [21, 30],
}
DEFAULT_PARAMS = {"p1": 14, "p2": 21}


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


def _trend(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = (h.rolling(n).max() + lo.rolling(n).min()) / 2
    up = (c > mid).to_numpy()
    dn = (c < mid).to_numpy()
    m = len(c)
    out = np.zeros(m, dtype=np.int8)
    t = 0
    for i in range(m):
        if i >= 1 and up[i] and up[i - 1]:
            t = 1
        elif i >= 1 and dn[i] and dn[i - 1]:
            t = -1
        out[i] = t
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t1, t2 = _trend(bars_df, int(p["p1"])), _trend(bars_df, int(p["p2"]))
    idx = bars_df.index
    long_e = pd.Series((t1 == 1) & (t2 == 1), index=idx)
    short_e = pd.Series((t1 == -1) & (t2 == -1), index=idx)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
