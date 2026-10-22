"""EMA 10 / 20 / 30 "perfect order", broker days: the bar the EMAs first stack upward goes long, the bar they first stack downward goes short, and the first bar the stack breaks closes everything.
Port of FMZ strategy #489007 "Multi EMA Trend Reversal Trading Strategy" (Perfect Order Strategy).

FMZ source id: 489007

Source
    https://www.fmz.com/strategy/489007 (PineScript v6, FMZ last modified 2025-04-01 10:02:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-193), EMA 10 / 20 / 30
    up stack and not was-up -> entry Long, was-up;  down stack and not was-down -> entry Short, was-down
    else (not up and was-up) or (not down and was-down) -> close all once (end), flags cleared;  else neither -> flags and end cleared

Interpretation choices (Pine rules in SURVEY_README.md)
    * The was-up / was-down / end flags are followed in a loop, as written; after the close the flags are
      cleared, so a stack that returns re-enters. A new stack on the other side reverses (REVERSAL
      INTENDED). No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA stack onsets with a stack-break exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_489007_ema10_20_30_perfect_order_onset_break_exit_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "aPeriod": [10, 5],
    "cPeriod": [30, 50],
}
DEFAULT_PARAMS = {"aPeriod": 10, "cPeriod": 30, "bPeriod": 20}


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
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    a, b, cc = ema(p["aPeriod"]), ema(p["bPeriod"]), ema(p["cPeriod"])
    c1 = ((a > b) & (b > cc)).to_numpy()
    c2 = ((a < b) & (b < cc)).to_numpy()
    m = len(c1)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    w1 = w2 = end = False
    for i in range(m):
        if c1[i] and not w1:
            le[i], w1, w2, end = True, True, False, False
        elif c2[i] and not w2:
            se[i], w2, w1, end = True, True, False, False
        elif (not c1[i] and w1) or (not c2[i] and w2):
            if not end:
                lx[i] = sx[i] = True
                end = True
            w1 = w2 = False
        elif not c1[i] and not c2[i]:
            w1 = w2 = end = False
    idx = c.index
    S = lambda a_: pd.Series(a_, index=idx)  # noqa: E731
    return S(le), S(lx), S(se), S(sx)


def portfolio_kwargs(**params):
    return {}
