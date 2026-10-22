"""Donchian 20 trend state, broker days: a close over the previous 20-bar high sets the trend up and holds long, a close under the previous 20-bar low sets it down and holds short; reversing.
Port of FMZ strategy #483040 "Multi Period Donchian Channel Trend Following and Divergence Trading Strategy" (Donchian Trend Ribbon Strategy).

FMZ source id: 483040

Source
    https://www.fmz.com/strategy/483040 (PineScript v6, FMZ last modified 2025-02-21 10:38:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-180), Donchian period 20 (ribbon of 20..11 for colours only)
    tr = close > highest(high, 20)[1] ? 1 : close < lowest(low, 20)[1] ? -1 : nz(tr[1]);  maintrend == 1 -> entry Long;  maintrend == -1 -> entry Short;  closes on the opposite trend

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ribbon's shorter channels only colour the plots. The trend is a state; a repeat entry on the
      side held adds nothing and the other side reverses (the closes coincide with the opposite entries):
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian channel trend state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483040_donchian20_trend_state_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dlen": [20, 40, 10],
}
DEFAULT_PARAMS = {"dlen": 20}


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
    n = int(p["dlen"])
    up = (c > h.rolling(n).max().shift(1)).to_numpy()
    dn = (c < lo.rolling(n).min().shift(1)).to_numpy()
    m = len(up)
    tr = np.zeros(m)
    t = 0
    for i in range(m):
        t = 1 if up[i] else (-1 if dn[i] else t)
        tr[i] = t
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(tr == 1, index=idx), false, pd.Series(tr == -1, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
