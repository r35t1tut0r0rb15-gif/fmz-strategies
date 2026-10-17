"""Noro's anti-saw MA trend flips, broker days: the trend turns up when a whole bar (its low) is above the SMA 30 and down
when a whole bar (its high) is below it; a flip from down to up goes long, from up to down short.
Port of FMZ strategy #433441 "Cross Moving Average Price Strategy" (Noro's CrossMA).

FMZ source id: 433441

Source
    https://www.fmz.com/strategy/433441 (PineScript v4, FMZ last modified 2023-11-27 16:52:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 185-259), MA type SMA, length 30, offset 0, anti-saw on; longs and shorts on
    trend = low > ma ? 1 : high < ma ? -1 : trend[1]  (anti-saw)
    trend == 1 and trend[1] == -1 -> entry long;  trend == -1 and trend[1] == 1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lot (equity share, recomputed on position changes) is sizing. The close-alls apply only when a
      side is disabled or after the date window. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bars entirely above / below an average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot formula and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433441_noro_cross_ma_antisaw"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [30, 15, 60],
}
DEFAULT_PARAMS = {"length": 30}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["length"])).mean()
    upb, dnb = (lo > ma).to_numpy(), (h < ma).to_numpy()
    m = len(c)
    tr = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if upb[i]:
            q = 1
        elif dnb[i]:
            q = -1
        tr[i] = q
    t1 = np.concatenate(([0], tr[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tr == 1) & (t1 == -1), index=ix), false,
            pd.Series((tr == -1) & (t1 == 1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
