"""Elder's bear power state, broker days: the day's low above the EMA 13 holds a long, below it holds a short; reversing.
Port of FMZ strategy #438463 "Bear Power Tracking Strategy" (Elder Ray (Bear Power) Strategy Backtest).

FMZ source id: 438463

Source
    https://www.fmz.com/strategy/438463 (PineScript v2, FMZ last modified 2024-01-12 11:43:08).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 148-163), Length 13, Trigger 0, reverse off
    DayLow = dayofmonth changed ? low : min(low, DayLow[1]);  nRes = DayLow - ema(close, 13);  pos = 1 if nRes > 0, -1 if nRes < 0, else pos[1];  entries by pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * On daily bars every bar starts a new day of the month, so DayLow is the bar's low. The state is a
      level, so the entry is sent on every bar of the state. reverse is off. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, low against an EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430065 (2 members, best partner #430065, Jaccard 0.721); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438463_elder_bear_power_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [13, 26, 8, 50],
}
DEFAULT_PARAMS = {"length": 13, "trigger": 0.0, "reverse": False}


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
    lo, c = bars_df["low"], bars_df["close"]
    res = (lo - c.ewm(span=int(p["length"]), adjust=False).mean()).to_numpy()
    trg = float(p["trigger"])
    m = len(res)
    st = np.zeros(m)
    for i in range(m):
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = 1.0 if res[i] > trg else (-1.0 if res[i] < trg else prev)
    if p["reverse"]:
        st = -st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
