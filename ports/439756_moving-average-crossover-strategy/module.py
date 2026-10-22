"""SMA 45 crossings held eight bars, long only, broker days: the close crossing over the SMA 45 from below goes long; the long closes eight bars after the signal bar.
Port of FMZ strategy #439756 "Moving Average Crossover Strategy" (Moving Average Crossover Strategy).

FMZ source id: 439756

Source
    https://www.fmz.com/strategy/439756 (PineScript v5, FMZ last modified 2024-01-23 15:20:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-189), SMA 45; hold 8 bars (fixed in the code)
    if not in_long and crossover(close, ma) and close[1] < ma[1]: in_long, entry_bar = bar;  if in_long and bar - entry_bar >= 8: in_long := false
    re-entry needs crossover(close, ma) and close[1] > ma[1] (cannot hold);  in_long -> entry Long;  not in_long -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The re-entry test asks for a crossover with the previous close above the average, which a
      crossover never has, so it never fires. The flag drops on the eighth bar after the signal bar, so
      the close is sent then. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings and a bar count.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439756_sma45_cross_hold_8_bars_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [45, 20],
    "hold": [8, 5],
}
DEFAULT_PARAMS = {"ma_length": 45, "hold": 8}


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
    ma = c.rolling(int(p["ma_length"])).mean()
    xo = ((c > ma) & (c.shift(1) <= ma.shift(1)) & ma.shift(1).notna() & (c.shift(1) < ma.shift(1))).to_numpy()
    hold = int(p["hold"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    inl, eb = False, -1
    for i in range(m):
        if not inl and xo[i]:
            inl, eb = True, i
        if inl and i - eb >= hold:
            inl = False
        tgt[i] = 1 if inl else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
