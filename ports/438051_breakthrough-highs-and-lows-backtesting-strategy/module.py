"""Previous-day level state, broker days: a close above the previous day's low holds a long, a close under the previous day's high (and not above its low) holds a short; reversing.
Port of FMZ strategy #438051 "Breakthrough Highs and Lows Backtesting Strategy" (HL Levels).

FMZ source id: 438051

Source
    https://www.fmz.com/strategy/438051 (PineScript v2, FMZ last modified 2024-01-08 16:13:44).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 171-185), SelectPeriod D, LookBack 1 (on a 1-day chart); reverse off
    xHigh = security(tickerid, D, high[1]);  xLow = security(tickerid, D, low[1]);  vS1 = xHigh, vR1 = xLow;  pos = 1 if close > vR1, -1 if close < vS1, else pos[1];  entries by pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("D", high[1]) on a daily chart is the chart's own previous high (no look-ahead). The
      labels are swapped as written (vR1 is the low), so a close above the previous low goes long and
      almost every other close goes short. The state is a level, so the entry is sent on every bar of
      the state. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, previous-day levels.
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

NAME = "fmz_438051_previous_day_level_state"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [1, 2, 3, 5],
}
DEFAULT_PARAMS = {"lookback": 1, "reverse": False}


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
    k = int(p["lookback"])
    vs1 = h.shift(k).to_numpy(dtype=float)
    vr1 = lo.shift(k).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    st = np.zeros(m)
    for i in range(m):
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = 1.0 if cv[i] > vr1[i] else (-1.0 if cv[i] < vs1[i] else prev)
    if p["reverse"]:
        st = -st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
