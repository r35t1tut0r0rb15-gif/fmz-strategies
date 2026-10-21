"""New-support entries with new-resistance exits, broker days, long only: a bar whose low is the 13-bar low (the support value) goes long; while long, a bar whose high is the 13-bar high (the resistance value) closes it.
Port of FMZ strategy #436877 "Moving Average Rebound Strategy" (Estrategia EMA RESISTENCIA Y SOPORTE).

FMZ source id: 436877

Source
    https://www.fmz.com/strategy/436877 (PineScript v5, FMZ last modified 2023-12-28 15:25:29).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 185-240), support / resistance length 13 (Alligator, fractals and EMAs plotted only); pyramiding 10
    highRS = valuewhen(high >= highest(high, 13), high, 0);  lowRS = valuewhen(low <= lowest(low, 13), low, 0)
    low == lowRS -> entry Long (pyramiding 10);  high == highRS and position_size > 0 -> close Long;  close <= close x 0.95 -> close Long (never true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * lowRS / highRS are followed with valuewhen as written; low == lowRS is true on a new 13-bar low (and,
      rarely, when a later low equals the stored one). The adds of pyramiding 10 are sizing: the port enters
      once and ignores repeats. The stop line compares the close with 95 % of itself, so it can never fire:
      dead code, not ported. The Alligator, fractals, EMAs and lastSupport are plotted or unused. Long
      only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 10 and margin settings stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436877_new_support_buy_resistance_exit"
FAMILY = "mean_reversion"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_rs": [13, 21],
}
DEFAULT_PARAMS = {"length_rs": 13}


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
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["length_rs"])
    new_hi = (h >= h.rolling(n).max()).to_numpy()
    new_lo = (lo <= lo.rolling(n).min()).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hrs = lrs = np.nan
    pos = 0
    for i in range(m):
        if new_hi[i]:
            hrs = hv[i]
        if new_lo[i]:
            lrs = lv[i]
        buy = lv[i] == lrs
        res = hv[i] == hrs
        if pos == 0 and buy:
            le[i] = True
            pos = 1
        elif pos == 1 and res:
            lx[i] = True
            pos = 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
