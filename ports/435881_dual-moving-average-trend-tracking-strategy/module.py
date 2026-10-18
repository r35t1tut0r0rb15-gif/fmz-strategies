"""Two moving averages sloping together, broker days: both the SMA 10 and the SMA 30 of ohlc4 rising holds a long, both falling a short
(reversing); when they disagree the last side is kept.
Port of FMZ strategy #435881 "Dual Moving Average Trend Tracking Strategy" (Noro's TrendMA Strategy).

FMZ source id: 435881

Source
    https://www.fmz.com/strategy/435881 (PineScript v4, FMZ last modified 2023-12-19 14:49:52).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 153-193), SMA 10 / 30 of ohlc4; type SMA
    trend1 = fastma > fastma[1] ? 1 : -1;  trend2 = slowma > slowma[1] ? 1 : -1;  trend = trend1 == 1 and trend2 == 1 ? 1 : trend1 == -1 and trend2 == -1 ? -1 : trend[1]
    trend == 1 -> entry long;  trend == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signal is sent on the change of trend only (a same-side entry adds nothing). The first bar's
      slopes are -1 (the comparison with na is false). strategy.entry reverses: REVERSAL INTENDED. The
      full-equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average slopes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435881_noro_trendma"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [30, 50],
    "type": ["SMA", "EMA"],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "type": "SMA"}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    if p["type"] == "EMA":
        fast = src.ewm(span=int(p["fast"]), adjust=False).mean()
        slow = src.ewm(span=int(p["slow"]), adjust=False).mean()
    else:
        fast = src.rolling(int(p["fast"])).mean()
        slow = src.rolling(int(p["slow"])).mean()
    up1 = (fast > fast.shift(1)).to_numpy()
    up2 = (slow > slow.shift(1)).to_numpy()
    m = len(up1)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up1[i] and up2[i]:
            q = 1
        elif (not up1[i]) and (not up2[i]):
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
