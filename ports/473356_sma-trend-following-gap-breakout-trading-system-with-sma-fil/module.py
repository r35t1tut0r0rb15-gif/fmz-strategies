"""Opening gaps up of at least 0.1 % over the previous close, daily bars, long only (the default "Long Up Gap" option, SMA filter off): each buy is closed once 10 bars have passed since its fill.
Port of FMZ strategy #473356 "趋势型跳空突破SMA过滤交易系统-Trend-Following-Gap-Breakout-Trading-System-with-SMA-Filter" (Simplified Gap Strategy with SMA Filter).

FMZ source id: 473356

Source
    https://www.fmz.com/strategy/473356 (PineScript v5, FMZ last modified 2024-11-29 15:07:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-143), gap threshold 0.1 %; hold 10 bars; option Long Up Gap; SMA 200 filter off
    open > close[1] and gap >= 0.1 % -> entry Long;  opentrades > 0 and bar_index - entry_bar_index(0) >= 10 -> close Long, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The gap is the bar's own open against the previous close, known at the bar's close. The hold
      counts from the fill bar (entry_bar_index), so the close is sent on the 10th bar after the fill;
      a loop follows the open trade, and new gaps while long are ignored (pyramiding 1). The other three
      gap options (short up / short down / long down) and the SMA filter are separate settings, not
      ported. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, gap-up entries with a fixed hold.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473356_gap_up_0p1pct_hold10_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gap_pct": [0.1, 0.5],
    "hold": [10, 5],
}
DEFAULT_PARAMS = {"gap_pct": 0.1, "hold": 10}


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
    o, c = bars_df["open"], bars_df["close"]
    c1 = c.shift(1)
    gap = (o - c1) / c1 * 100
    up = ((o > c1) & (gap >= float(p["gap_pct"]))).to_numpy()
    hold = int(p["hold"])
    m = len(o)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, fill = 0, 0, -1
    for i in range(m):
        if pend == 1:
            pos, pend, fill = 1, 0, i
        elif pend == 2:
            pos, pend = 0, 0
        if up[i] and pos == 0 and pend == 0:
            le[i], pend = True, 1
        if pos == 1 and pend == 0 and i - fill >= hold:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
