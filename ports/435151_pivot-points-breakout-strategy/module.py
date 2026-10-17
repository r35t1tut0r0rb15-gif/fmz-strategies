"""HPotter floor pivots, broker days: a close above R1 = 2 PP - L of the previous broker day goes long, a close below
S1 = 2 PP - H goes short; held in between and reversed on the opposite break.
Port of FMZ strategy #435151 "Pivot Points Breakout Strategy" (Floor Pivot Points Backtest).

FMZ source id: 435151

Source
    https://www.fmz.com/strategy/435151 (PineScript v2, FMZ last modified 2023-12-12 16:47:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 203-218), daily high[1] / low[1] / close[1]; reverse false
    PP = (H + L + C) / 3 of the previous day;  pos = close > 2 PP - L ? 1 : close < 2 PP - H ? -1 : pos[1];  1 -> entry long;  -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily header chart security('D', x[1]) is the previous broker day. strategy.entry
      reverses: REVERSAL INTENDED. reverse is false. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, prior-day pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435151_floor_pivot_r1_s1_side"
FAMILY = "pivot_levels"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
}
DEFAULT_PARAMS = {"reverse": False}


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
    ph, pl, pc = h.shift(1), lo.shift(1), c.shift(1)
    pp = (ph + pl + pc) / 3
    up, dn = (c > 2 * pp - pl).to_numpy(), (c < 2 * pp - ph).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    if bool(p["reverse"]):
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
