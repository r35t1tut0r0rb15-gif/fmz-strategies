"""Daily close comparison, broker days: a close above the previous day's close turns the state long, a close below it turns
it short (an unchanged close keeps it); always in the state's direction.
Port of FMZ strategy #432782 "Quantitative Trading Strategy Based on Daily Close Price Comparison" (Daily Close Comparison Strategy (by ChartArt) correct results).

FMZ source id: 432782

Source
    https://www.fmz.com/strategy/432782 (PineScript v2, FMZ last modified 2023-11-21 14:34:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 150-174), threshold 0
    diff = (close - security('D', close[1])) / security('D', close[1])
    buying = diff > 0 ? true : diff < 0 ? false : buying[1];  buying -> entry long;  not buying -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily header chart security('D', close[1]) is the previous day's close (the [1] reads
      the last completed day, so there is no look-ahead; unlike #427066, which had no [1]). The
      threshold is 0, so any change counts. buying starts false (Pine v2 na), so the first bar goes
      short unless it is up.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the previous completed day.
    2 generic: PASS, the sign of the daily change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND427066 (2 members, best partner #427066, Jaccard 0.756); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432782_daily_close_comparison"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [0.0, 0.004, 0.008],
}
DEFAULT_PARAMS = {"threshold": 0.0}


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
    diff = ((c - c.shift(1)) / c.shift(1)).to_numpy()
    th = float(p["threshold"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    buying = False
    for i in range(1, m):
        if diff[i] > th:
            buying = True
        elif diff[i] < -th:
            buying = False
        tgt[i] = 1 if buying else -1
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
