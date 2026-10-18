"""Daily moves of half a percent, broker days: a close 0.5 % or more over the previous close goes long (when not already long by the
script's own record); a close 0.5 % or more under it goes short (reversing).
Port of FMZ strategy #435720 "基于05赫氏变化的短周期交易策略Heikin-Ashi-05-Change-Short-Period-Trading-Strategy" (Heikin-Ashi - Change 0.5% short Time Period).

FMZ source id: 435720

Source
    https://www.fmz.com/strategy/435720 (PineScript v4, FMZ last modified 2023-12-18 12:13:56).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 124-143), threshold 0.5 %
    priceChange = close / close[1] - 1;  buy = priceChange >= 0.005 and (position is na or -1) -> entry long, position = 1;  sell = priceChange <= -0.005 and (position is na or 1) -> entry short, position = -1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "position" variable records the last signal side (it is set when the condition holds), so a
      second same-side move adds nothing and the next opposite move reverses: REVERSAL INTENDED. The
      title mentions Heikin-Ashi but the script uses plain closes. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent change.
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

NAME = "fmz_435720_half_percent_move_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [0.005, 0.01],
}
DEFAULT_PARAMS = {"threshold": 0.005}


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
    chg = (c / c.shift(1) - 1).to_numpy()
    th = float(p["threshold"])
    m = len(chg)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = 0
    for i in range(m):
        if chg[i] >= th and last != 1:
            le[i], last = True, 1
        elif chg[i] <= -th and last != -1:
            se[i], last = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
