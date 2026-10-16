"""Woodie pivot (HPotter), broker days: the pivot (H + L + 2 C) / 4 of the previous day; a close
crossing up through it goes long, any close below it goes short (always in the market after the
first signal).
Port of FMZ strategy #427397 "Woodie Pivot Points Backtest Strategy".

FMZ source id: 427397

Source
    https://www.fmz.com/strategy/427397 (PineScript v2, FMZ last modified 2023-09-20 17:08:11).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 167-181), reverse off
    xPP = (high[1] + low[1] + 2 close[1]) / 4 of the daily series (security 'D' with [1])
    pos = close[1] < xPP[1] and close > xPP ? 1 : close < xPP ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily chart, security(ticker, 'D', x[1]) is the previous day's value x[1] (completed).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the pivot uses the completed previous day.
    2 generic: PASS, comparisons with a pivot of the instrument's own prices.
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

NAME = "fmz_427397_woodie_pivot"
FAMILY = "pivot_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "close_weight": [2, 1],
}
DEFAULT_PARAMS = {"close_weight": 2}


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
    w = float({**DEFAULT_PARAMS, **params}["close_weight"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pp = (h.shift(1) + lo.shift(1) + w * c.shift(1)) / (2 + w)
    up = ((c.shift(1) < pp.shift(1)) & (c > pp)).to_numpy()
    dn = (c < pp).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
