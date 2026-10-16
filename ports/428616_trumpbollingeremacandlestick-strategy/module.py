"""Day-direction follower, broker days: after a day that closes more than 0.01 % up hold a long, after a
day more than 0.01 % down hold a short (in between, the last side is kept).
Port of FMZ strategy #428616 "TrumpBollingerEMAcandlestick Strategy" (TrumpShipper Long Short V26).

FMZ source id: 428616

Source
    https://www.fmz.com/strategy/428616 (PineScript v4, FMZ last modified 2023-10-07 15:30:27).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 250-264), dt 0.0001
    confidence = (close_D - close_D[1]) / close_D[1] (security 'D' on the daily chart = the close)
    prediction = confidence > dt ? true : confidence < -dt ? false : prediction[1]
    prediction -> entry long; not prediction -> entry short (the exits have no levels: inert)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'D' securities equal the daily chart's own series. The Bollinger band, Fibonacci levels,
      EMA signals and pivots are drawn only. No order before the first move beyond dt (na).
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percentage change only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_428616_day_direction_follower"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dt": [0.0001, 0.005, 0.01, 0.02],
}
DEFAULT_PARAMS = {"dt": 0.0001}


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
    conf = ((c - c.shift(1)) / c.shift(1)).to_numpy()
    dt = float(p["dt"])
    m = len(conf)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if conf[i] > dt:
            pos = 1
        elif conf[i] < -dt:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
