"""HPotter percent-change zones, broker days: a one-bar change above +0.33 % turns the state long, below -0.33 % short,
otherwise it stays; the strategy is always in the state's direction.
Port of FMZ strategy #432210 "Percent Change Bar Chart Backtest Strategy" (Percent change bar chart Backtest (HPotter)).

FMZ source id: 432210

Source
    https://www.fmz.com/strategy/432210 (PineScript v2, FMZ last modified 2023-11-15 15:41:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-205), look back 1, buy zone 0.33 %, sell zone -0.33 %, reverse false
    chg = (close - close[1]) x 100 / close[1]
    pos = chg > 0.33 ? 1 : chg < -0.33 ? -1 : pos[1];  pos == 1 -> entry long;  pos == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The look-back input is 1 (the argument table prints it as "true"); "Price Change" is false, so
      the change is in percent; reverse is false. The thresholds are percent changes of the close,
      scale-free as written.
    * strategy.entry reverses: REVERSAL INTENDED (always in after the first zone touch). Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent-change zones.
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

NAME = "fmz_432210_percent_change_zones"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "zone": [0.33, 1.0],
    "lookback": [1, 3],
}
DEFAULT_PARAMS = {"zone": 0.33, "lookback": 1}


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
    n = int(p["lookback"])
    chg = ((c - c.shift(n)) * 100 / c.shift(n)).to_numpy()
    z = float(p["zone"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if chg[i] > z:
            pos = 1
        elif chg[i] < -z:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
