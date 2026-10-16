"""ChartArt consecutive bars, broker days: four closes in a row above the previous close go long, four
in a row not above it go short (the moving average is off by default, so it is the close itself).
Port of FMZ strategy #428093 "Moving Average Direction Reversal Trading Strategy" (MA Consecutive Up/Down).

FMZ source id: 428093

Source
    https://www.fmz.com/strategy/428093 (PineScript v2, FMZ last modified 2023-09-28 15:50:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 236-298), consecutive 4, MA length 1 (off), EMA
    trend = ema(close, 1) > ema(close[1], 1) ? 1 : 0   (= close > close[1])
    up count >= 4 -> entry long; down count (trend 0, including equal closes) >= 4 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * MA length 1 is the source's "off": the averages are the close and the previous close.
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close comparisons only.
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

NAME = "fmz_428093_chartart_consecutive_bars"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "consecutive": [4, 2, 3, 5],
}
DEFAULT_PARAMS = {"consecutive": 4}


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
    up = (c > c.shift(1)).to_numpy()
    k = int(p["consecutive"])
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    nu = nd = 0
    pos = 0
    for i in range(m):
        if up[i]:
            nu, nd = nu + 1, 0
        else:
            nu, nd = 0, nd + 1
        if nu >= k:
            pos = 1
        elif nd >= k:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
