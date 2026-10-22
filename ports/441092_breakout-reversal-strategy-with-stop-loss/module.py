"""100-bar closing-high breakouts with a 25-bar time exit, broker days, long only: the close above the highest close of the previous 100 bars (and above the last close) goes long; 25 bars after the
latest breakout signal the long closes.
Port of FMZ strategy #441092 "Breakout Reversal Strategy with Stop Loss" (Breakout Strategy).

FMZ source id: 441092

Source
    https://www.fmz.com/strategy/441092 (PineScript v5, FMZ last modified 2024-02-05 14:56:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 217-251), breakout period 100; date inputs 2022-2023 (unused by the orders)
    enterLong = close > highest(close, 100)[1] and close > close[1] -> entry Long;  barssince(enterLong) >= 25 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince counts from the latest signal, so a new breakout while long restarts the 25 bars. The
      date timestamps are computed but never used by the orders. Long only. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, closing-high breakout and bar count.
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

NAME = "fmz_441092_close_high_100_breakout_25_bar_exit_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "breakout_period": [100, 50],
    "hold_bars": [25, 10],
}
DEFAULT_PARAMS = {"breakout_period": 100, "hold_bars": 25}


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
    hc = c.rolling(int(p["breakout_period"])).max().shift(1)
    sig = ((c > hc) & (c > c.shift(1))).to_numpy()
    k = int(p["hold_bars"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, last = 0, None
    for i in range(m):
        if sig[i]:
            last = i
        if sig[i] and held == 0 and i + 1 < m:
            le[i], held = True, 1
        elif held == 1 and last is not None and i - last >= k:
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
