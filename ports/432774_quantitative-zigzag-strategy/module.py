"""A counter of candle-colour changes on the daily bars that steps by +1 or -1 and turns back each time it reaches 28 in size: the count at +28 goes short, at -28 goes long; broker days, reversing.
Port of FMZ strategy #432774 "Quantitative Zigzag Strategy" (Sine Wave Theory (Gentleman-Goat)).

FMZ source id: 432774

Source
    https://www.fmz.com/strategy/432774 (PineScript v5, FMZ last modified 2023-12-01 15:01:07).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 121-190), Bar Change: start direction 1, wave number 28, resolution D, trade on; Volume and Coin Flip parts: trade off
    bar_color = close > open ? green : red (security "D");  on a colour change: count += direction;  abs(count) == 28 on a change -> direction := -direction
    count == 28 -> entry short;  count == -28 -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security() call asks for "D" on the header's 1-day chart: the chart bar's own colour. The
      volume and coin-flip counters are computed but their Trade inputs are off, so volume is not used
      and the random draw sends nothing. The count starts at 0 on the first loaded bar, so where the
      waves fall depends on where the data starts (weird case). A count at +-28 holds until the next colour
      change; a repeated same-side entry adds nothing (pyramiding default). REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-colour change counting.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): capital 1000 only, not ported.
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

NAME = "fmz_432774_candle_colour_change_wave_count_28_reversal"
FAMILY = "bar_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wave_number": [28, 14],
    "start_direction": [1, -1],
}
DEFAULT_PARAMS = {"wave_number": 28, "start_direction": 1}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    green = (bars_df["close"] > bars_df["open"]).to_numpy()
    wn, dr = int(p["wave_number"]), int(p["start_direction"])
    m = len(green)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cnt, pos = 0, 0
    for i in range(m):
        chg = i > 0 and green[i] != green[i - 1]
        if chg:
            cnt += dr
            if abs(cnt) == wn:
                dr = -dr
        if cnt == wn and pos != -1:
            se[i], pos = True, -1
        elif cnt == -wn and pos != 1:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
