"""Breaks of the latest one-bar swing high, daily bars, long only: a bar trading above the last swing high after opening below it goes long; a bar trading below the last swing low after opening above it
closes.
Port of FMZ strategy #449724 "GBS高低点确认策略-GBS-TOP-BOTTOM-Confirmed-Strategy" (GBS TOP BOTTOM Confirmed).

FMZ source id: 449724

Source
    https://www.fmz.com/strategy/449724 (PineScript v5, FMZ last modified 2024-04-28 14:42:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-124), swing high / low of one bar each side
    high < high[1] and high[1] > high[2] -> entryHigh = high[1];  high > entryHigh and open < entryHigh -> entry Buy
    low > low[1] and low[1] < low[2] -> exitLow = low[1];  low < exitLow and open > exitLow -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing levels are known once the bar after the swing closes; the break tests use the bar's
      own open, high and low at its close, and the orders fill at the next open. A same-bar close acts
      only on a held long. Long only. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing levels from completed bars.
    2 generic: PASS, swing-high breaks with swing-low exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449724_swing_high_break_swing_low_exit_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    swh = ((h < h.shift(1)) & (h.shift(1) > h.shift(2))).to_numpy()
    swl = ((lo > lo.shift(1)) & (lo.shift(1) < lo.shift(2))).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    eh = el = np.nan
    held = False
    for i in range(m):
        if swh[i]:
            eh = hv[i - 1]
        if swl[i]:
            el = lv[i - 1]
        buy = not np.isnan(eh) and hv[i] > eh and ov[i] < eh
        sell = not np.isnan(el) and lv[i] < el and ov[i] > el
        if buy and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif sell and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
