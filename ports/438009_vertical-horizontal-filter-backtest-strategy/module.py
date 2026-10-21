"""Vertical Horizontal Filter level state, broker days: the VHF 28 above 0.4 holds a long, below 0.4 holds a short; reversing.
Port of FMZ strategy #438009 "Vertical Horizontal Filter Backtest Strategy" (Vertical Horizontal Filter Backtest).

FMZ source id: 438009

Source
    https://www.fmz.com/strategy/438009 (PineScript v2, FMZ last modified 2024-01-08 10:20:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 118-134), Length 28, Signal 0.4, reverse off
    VHF = (highest(high, 28) - lowest(low, 28)) / sum(abs(close - close[1]), 28);  pos = 1 if VHF > 0.4, -1 if VHF < 0.4, else pos[1];  pos 1 -> entry Long, pos -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level, so the entry is sent on every bar of the state; pos 0 (before the VHF exists)
      sends nothing. A trending phase goes long and a congestion phase short, as written. reverse is off.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VHF level.
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

NAME = "fmz_438009_vhf_level_state"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [28, 14],
    "signal": [0.4, 0.3],
}
DEFAULT_PARAMS = {"length": 28, "signal": 0.4, "reverse": False}


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
    n = int(p["length"])
    num = (h.rolling(n).max() - lo.rolling(n).min()).abs()
    den = c.diff().abs().rolling(n).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        vhf = (num / den).to_numpy(dtype=float)
    sig = float(p["signal"])
    m = len(c)
    st = np.zeros(m)
    for i in range(m):
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = 1.0 if vhf[i] > sig else (-1.0 if vhf[i] < sig else prev)
    if p["reverse"]:
        st = -st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
