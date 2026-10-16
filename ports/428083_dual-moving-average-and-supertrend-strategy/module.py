"""EMA trend entries, broker days, long only: EMA 21 crossing above EMA 55, or the close above both with
EMA 21 above EMA 55 and the close above EMA 233, goes long; the close crossing under EMA 55 closes it.
Port of FMZ strategy #428083 "Dual Moving Average and Supertrend Strategy" (EMA & Supertrend).

FMZ source id: 428083

Source
    https://www.fmz.com/strategy/428083 (PineScript v4, FMZ last modified 2023-09-28 15:12:50).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-249), EMAs 21 / 55 / 200 / 233
    Enterlong = crossover(ema21, ema55) or (close > ema21 and close > ema55 and ema21 > ema55) and close > ema233
              (Pine: `and` binds tighter, so the cross alone also enters)
    Exitlong = crossunder(close, ema55)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend, EMA 200 and the short conditions are computed but no order uses them.
    * Operator precedence as written. The 2008 start is always met. An entry and a close on one bar:
      the close acts only on an open position.
    * Long only. Daily bars are broker days, stamped with their first minute. FREQ = "1D".

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA lengths only.
    3 crypto-exchange-only: no (spot pair in the header only).
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

NAME = "fmz_428083_ema_trend_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [21, 13],
    "len2": [55, 34],
}
DEFAULT_PARAMS = {"len1": 21, "len2": 55, "len4": 233}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    e1, e2, e4 = e(p["len1"]), e(p["len2"]), e(p["len4"])
    cross = (e1 > e2) & (e1.shift(1) <= e2.shift(1))
    stack = (c > e1) & (c > e2) & (e1 > e2) & (c > e4)
    enter = (cross | stack).to_numpy()
    exit_ = ((c < e2) & (c.shift(1) >= e2.shift(1))).to_numpy()
    m = len(enter)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and exit_[i]:
            pos = 0
        if start == 0 and enter[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
