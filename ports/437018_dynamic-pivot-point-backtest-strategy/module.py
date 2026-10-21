"""Previous-day floor pivot breakouts, bar size pending: a close above yesterday's R1 (2 x pivot - yesterday's low) is long, under S1 (2 x pivot - yesterday's high) is short, in between the state holds; an optional
switch trades the reverse; entries are sent on every bar of the state, reversing.
Port of FMZ strategy #437018 "Dynamic Pivot Point Backtest Strategy" (Dynamic Pivot Point).

FMZ source id: 437018

Source
    https://www.fmz.com/strategy/437018 (PineScript v2, FMZ last modified 2023-12-29 15:50:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 156-170), reverse off; daily values from security("D", high[1] / low[1] / close[1])
    xHigh / xLow / xClose = security(tickerid, "D", high[1] / low[1] / close[1]);  vPP = (H + L + C) / 3;  vR1 = 2 vPP - L;  vS1 = 2 vPP - H
    pos = 1 if close > vR1, -1 if close < vS1, else pos[1];  possig = -pos when reverse;  entry Long / Short on possig

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no chart period: FREQ = "bar_size_pending" (rule 1),
      bars from the house bar_sizes.build_bars with the driver's bar_size. The [1] makes the daily values
      the last completed day (no future read): the previous broker day's high, low and last close,
      computed from the module's own bars and applied to every bar of the next broker day. The state is a
      level, so the entry is sent on every bar of the state; a same-side entry while in the position is
      ignored (pyramiding 0). REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from the completed day.
    2 generic: PASS, pivot levels from the previous day.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: previous broker day (17:00 America/New_York, DST by the zone) for the pivots; no venue-open rule.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437018_daily_pivot_r1_s1_state"
FAMILY = "breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
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
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lab = broker_day(bars_df.index)
    day = pd.DataFrame({"h": h.groupby(lab).max(), "l": lo.groupby(lab).min(), "c": c.groupby(lab).last()})
    prev = day.shift(1)                                   # the last completed broker day
    ph = prev["h"].reindex(lab).to_numpy()
    pl = prev["l"].reindex(lab).to_numpy()
    pcl = prev["c"].reindex(lab).to_numpy()
    pp = (ph + pl + pcl) / 3
    r1 = pp + (pp - pl)
    s1 = pp - (ph - pp)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    pos = np.zeros(m)
    st = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if cv[i] > r1[i]:
                st = 1.0
            elif cv[i] < s1[i]:
                st = -1.0
            pos[i] = st
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
