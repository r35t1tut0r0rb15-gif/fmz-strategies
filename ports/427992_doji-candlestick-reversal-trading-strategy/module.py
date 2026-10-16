"""Doji reversal, broker days: after a doji whose high is under SMA 10, a green bar closing above the
doji's high goes long; after a doji whose low is over the SMA, a red bar closing below its low goes
short.
Port of FMZ strategy #427992 "Doji Candlestick Reversal Trading Strategy".

FMZ source id: 427992

Source
    https://www.fmz.com/strategy/427992 (PineScript v4, FMZ last modified 2023-09-27 16:40:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 223-244), SMA 10, tolerance 0.1, look-back end 2
    for i = 1 .. end: doji[i] = |close[i] - open[i]| / (high[i] - low[i]) < 0.1
    long |= doji[i] and (close[i-1] <= high[i] or i == 1) and close[i-1] > high[i] and high[i] < sma
            and close > open; short mirrors
    -> entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: for i >= 2 the two close[i-1] conditions contradict each other, so only i = 1 can
      fire and the look-back "End" has no effect (fixed). The SMA is the current bar's.
    * A zero-range bar gives na (no doji). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle ratios and MA length.
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

NAME = "fmz_427992_doji_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_period": [10, 20],
    "tolerance": [0.1, 0.05],
}
DEFAULT_PARAMS = {"sma_period": 10, "tolerance": 0.1}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    avg = c.rolling(int(p["sma_period"])).mean()
    o1, h1, l1, c1 = o.shift(1), h.shift(1), lo.shift(1), c.shift(1)
    doji = ((c1 - o1).abs() / (h1 - l1)) < p["tolerance"]
    long_s = (doji & (c > h1) & (h1 < avg) & (c > o)).to_numpy()
    short_s = (doji & (c < l1) & (l1 > avg) & (c < o)).to_numpy()
    m = len(long_s)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_s[i]:
            pos = 1
        elif short_s[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
